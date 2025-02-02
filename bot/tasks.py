from celery import shared_task
from .models import ScheduledMessage
import telebot
from django.conf import settings
import logging
import os

logger = logging.getLogger(__name__)

@shared_task
def send_scheduled_message(message_id: int):
    logger.info(f"Starting task for message {message_id}")
    try:
        instance = ScheduledMessage.objects.get(id=message_id)
        bot = telebot.TeleBot(settings.TELEGRAM_BOT_TOKEN)

        logger.info(f"Fetched message {message_id} with type {instance.message_type}")

        # Перевірка існування файлу
        if instance.media_file and not os.path.exists(instance.media_file.path):
            logger.error(f"File not found: {instance.media_file.path}")
            return

        logger.info(f"File exists: {instance.media_file.path}")

        # Логіка відправки повідомлення з кнопками
        keyboard = telebot.types.InlineKeyboardMarkup()
        if instance.button_text and instance.button_link:
            keyboard.add(telebot.types.InlineKeyboardButton(
                text=instance.button_text,
                url=instance.button_link
            ))

        if instance.message_type == "photo" and instance.media_file:
            bot.send_photo(
                chat_id=instance.bot_configuration.channel_id,
                photo=instance.media_file,
                caption=instance.text,
                reply_markup=keyboard
            )
            logger.info(f"Sent photo message {message_id}")
        elif instance.message_type == "video" and instance.media_file:
            bot.send_video(
                chat_id=instance.bot_configuration.channel_id,
                video=instance.media_file,
                caption=instance.text,
                reply_markup=keyboard
            )
            logger.info(f"Sent video message {message_id}")
        elif instance.message_type == "text":
            bot.send_message(
                chat_id=instance.bot_configuration.channel_id,
                text=instance.text,
                reply_markup=keyboard
            )
            logger.info(f"Sent text message {message_id}")

        instance.is_send = True
        instance.save()
        logger.info(f"Message {message_id} sent successfully and status updated")

    except Exception as e:
        logger.error(f"Error sending message {message_id}: {str(e)}")
