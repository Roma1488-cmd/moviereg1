from apscheduler.schedulers.background import BackgroundScheduler
from django.utils import timezone
from .models import ScheduledMessage, BotConfiguration, TelegramUser, DelayMessage, PostMedia
import telebot
from django.conf import settings
import logging
import time
from telebot.apihelper import ApiException
from requests.exceptions import RequestException

# Налаштування логера
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

bot = telebot.TeleBot(settings.TELEGRAM_BOT_TOKEN, parse_mode="HTML")

scheduler = BackgroundScheduler()
scheduler.start()

def send_scheduled_message(instance_id):
    try:
        message = ScheduledMessage.objects.filter(id=instance_id).first()
        if not message:
            logger.error(f"ScheduledMessage with ID {instance_id} doesn't exist. Perhaps it was deleted?")
            return

        bot_config = BotConfiguration.get_instance()

        users = TelegramUser.objects.all()
        for user in users:
            try:
                if message.message_type == "text":
                    bot.send_message(user.chat_id, message.text, reply_markup=create_markup(message))
                elif message.message_type == "media_group":
                    media_files = list(message.post_medias.all())
                    if media_files:
                        media_group = []
                        for media in media_files:
                            if media.media_file and media.media_file.size > 0:
                                try:
                                    with media.media_file.open('rb') as file:
                                        if media.media_type == "photo":
                                            media_group.append(telebot.types.InputMediaPhoto(file))
                                        elif media.media_type == "video":
                                            media_group.append(telebot.types.InputMediaVideo(file))
                                except FileNotFoundError:
                                    logger.error(f"File not found for media in message {instance_id}")
                                    continue
                        if media_group:
                            bot.send_media_group(user.chat_id, media_group)
            except Exception as e:
                logger.error(f"Failed to send message to {user.chat_id}: {str(e)}")
    except Exception as e:
        logger.error(f"Failed to send scheduled message: {str(e)}")


def send_delay_message(instance_id):
    logger.info(f"Starting send_delay_message for ID: {instance_id}")
    max_retries = 3
    retry_delay = 2
    
    try:
        message = DelayMessage.objects.filter(id=instance_id).first()
        if not message:
            logger.error(f"DelayMessage with ID {instance_id} doesn't exist.")
            return

        logger.info(f"Found message: {message.message_type} scheduled for {message.scheduled_time}")
        bot_config = BotConfiguration.get_instance()
        markup = create_markup(message)

        logger.info(f"Starting to send message {instance_id}")
        logger.info(f"Message type: {message.message_type}")

        for attempt in range(max_retries):
            try:
                if message.message_type == "media_group":
                    media_files = list(message.post_medias.all())
                    logger.info(f"Found {len(media_files)} media files in group")
                    
                    if media_files:
                        media_contents = []
                        media_group = []
                        
                        for media in media_files:
                            if not media.media_file:
                                logger.warning(f"Skipping empty media file")
                                continue
                                
                            try:
                                with media.media_file.open('rb') as file:
                                    content = file.read()
                                    media_contents.append({
                                        'content': content,
                                        'type': media.media_type,
                                        'caption': message.text if media == media_files[0] else None
                                    })
                                    logger.info(f"Read file: {media.media_file.name}, size: {len(content)} bytes")
                            except Exception as e:
                                logger.error(f"Error reading media file: {str(e)}")
                                continue
                        
                        for media_content in media_contents:
                            if media_content['type'] == "photo":
                                media_group.append(
                                    telebot.types.InputMediaPhoto(
                                        media=media_content['content'],
                                        caption=media_content['caption']
                                    )
                                )
                            elif media_content['type'] == "video":
                                media_group.append(
                                    telebot.types.InputMediaVideo(
                                        media=media_content['content'],
                                        caption=media_content['caption']
                                    )
                                )
                        
                        if media_group:
                            logger.info(f"Sending media group with {len(media_group)} items")
                            # Спочатку відправляємо медіа групу
                            bot.send_media_group(bot_config.channel_id, media_group)
                            logger.info("Media group sent successfully")
                            # Потім відправляємо кнопки окремим повідомленням, якщо вони є
                            if markup:
                                bot.send_message(bot_config.channel_id, "Додаткові опції:", reply_markup=markup)
                        else:
                            logger.warning("No valid media files to send")
                            bot.send_message(bot_config.channel_id, message.text, reply_markup=markup)
                    else:
                        logger.warning("No media files found")
                        bot.send_message(bot_config.channel_id, message.text, reply_markup=markup)
                    break
                
                elif message.message_type in ["photo", "video"]:
                    if not message.media_file:
                        raise ValueError(f"No media file provided for {message.message_type} message")
                    
                    # Читаємо файл для кожної спроби
                    with message.media_file.open('rb') as file:
                        file_content = file.read()
                        
                        logger.info(f"File size: {len(file_content)} bytes")
                        logger.info(f"File path: {message.media_file.path}")

                    if message.message_type == "photo":
                        bot.send_photo(
                            chat_id=bot_config.channel_id,
                            photo=file_content,
                            caption=message.text,
                            reply_markup=markup
                        )
                    else:  # video
                        bot.send_video(
                            chat_id=bot_config.channel_id,
                            video=file_content,
                            caption=message.text,
                            reply_markup=markup
                        )
                    break
                
                else:  # text
                    bot.send_message(bot_config.channel_id, message.text, reply_markup=markup)
                    break
                
            except (ApiException, RequestException, ConnectionError) as e:
                logger.error(f"Attempt {attempt + 1}/{max_retries} failed: {str(e)}")
                if attempt < max_retries - 1:
                    time.sleep(retry_delay)
                    continue
                raise
                
    except Exception as e:
        logger.error(f"Failed to process delay message: {str(e)}")
        try:
            bot.send_message(
                bot_config.channel_id,
                f"{message.text}\n\n❌ Помилка при відправці медіа: {str(e)}",
                reply_markup=markup
            )
        except Exception as text_error:
            logger.error(f"Failed to send even text message: {str(text_error)}")

def schedule_message(instance):
    bot_config = BotConfiguration.get_instance()
    if not bot_config.admin_chat_id:
        logger.error(f"Admin chat ID is missing, cannot send preview for {instance.id}.")
        return

    delay_seconds = (instance.scheduled_time - timezone.now()).total_seconds()

    scheduler.add_job(
        func=send_scheduled_message,
        trigger="date",
        run_date=instance.scheduled_time,
        args=[instance.id],
        id=f"send_scheduled_message_{instance.id}",
        replace_existing=True
    )

    instance.is_send = True  # Встановлюємо статус "Відправлено"
    instance.save()
    logger.info(f"✅ ScheduledMessage {instance.id} заплановано на {instance.scheduled_time}")

def schedule_delay_message(instance, adjusted_time=None):
    try:
        scheduler.add_job(
            func=send_delay_message,
            trigger="date",
            run_date=adjusted_time or instance.scheduled_time,
            args=[instance.id],
            id=f"send_delay_message_{instance.id}",
            replace_existing=True
        )
        logger.info(f"Message {instance.id} scheduled for {adjusted_time or instance.scheduled_time}")
    except Exception as e:
        logger.error(f"Error scheduling message: {str(e)}")

def handle_media_group(media_group, instance, bot_config):
    try:
        media_list = []
        for media_type, media_file in media_group:
            if media_type == 'photo':
                media_list.append(telebot.types.InputMediaPhoto(media_file))
            elif media_type == 'video':
                media_list.append(telebot.types.InputMediaVideo(media_file))

        if media_list:
            bot.send_media_group(bot_config.channel_id, media_list)  # Відправляємо в канал
    except Exception as e:
        logger.error(f"Помилка при обробці media_group: {str(e)}")
        raise  # Повторно викидаємо виняток

def create_markup(instance):
    from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
    markup = InlineKeyboardMarkup()

    buttons = instance.post_buttons.all()  # Використовуємо `.all()`
    if buttons.exists():
        for button in buttons:
            markup.add(InlineKeyboardButton(text=button.text, url=button.link))

    return markup if buttons.exists() else None


def send_preview_message(instance):
    bot_config = BotConfiguration.get_instance()

    logger.info(f"Отправка попереднього перегляду для instance {instance.id}")

    if instance.message_type == "text":
        bot.send_message(bot_config.admin_chat_id, instance.text, reply_markup=create_markup(instance))
    elif instance.message_type == "photo":
        bot.send_photo(bot_config.admin_chat_id, instance.media_file, caption=instance.text, reply_markup=create_markup(instance))
    elif instance.message_type == "video":
        bot.send_video(bot_config.admin_chat_id, instance.media_file, caption=instance.text, reply_markup=create_markup(instance))
    elif instance.message_type == "media_group":
        media_files = list(PostMedia.objects.filter(scheduled_message=instance))
        handle_media_group(media_files, instance, bot_config)
    else:
        logger.error(f"Unknown message type: {instance.message_type}")

    logger.info(f"Preview message for instance {instance.id} sent to admin {bot_config.admin_chat_id}")

def main():
    # Add your code to start the bot and handle incoming messages
    pass

if __name__ == "__main__":
    main()
