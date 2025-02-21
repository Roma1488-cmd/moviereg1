import os
import sys
import django

sys.path.append('/root/PythonProject7')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'moviereg.settings')
django.setup()

import logging
import telebot
from django.conf import settings
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from bot.models import TelegramUser, Button, BotConfiguration

logger = logging.getLogger(__name__)
bot = telebot.TeleBot(settings.TELEGRAM_BOT_TOKEN, threaded=False)

def create_keyboard(buttons, include_back_button=False):
    keyboard = InlineKeyboardMarkup()
    for btn in buttons:
        if btn.button_type == 'link':
            keyboard.add(InlineKeyboardButton(btn.text, url=btn.content))
        else:
            keyboard.add(InlineKeyboardButton(btn.text, callback_data=btn.key))
    if include_back_button:
        keyboard.add(InlineKeyboardButton("Назад", callback_data="back_to_start"))
    return keyboard

def send_media_content(chat_id, button):
    try:
        if not button.media_file:
            bot.send_message(chat_id, button.content)
            return

        # Перевіряємо чи файл існує та не порожній
        if not button.media_file.size:
            logger.error(f"Empty media file for button: {button.key}")
            bot.send_message(chat_id, button.content)
            return

        try:
            with button.media_file.open('rb') as file:
                if button.media_file.name.lower().endswith(('.png', '.jpg', '.jpeg')):
                    bot.send_photo(chat_id, file, caption=button.content)
                elif button.media_file.name.lower().endswith(('.mp4', '.avi', '.mov')):
                    bot.send_video(chat_id, file, caption=button.content)
                else:
                    bot.send_document(chat_id, file, caption=button.content)
        except FileNotFoundError:
            logger.error(f"File not found for button: {button.key}")
            bot.send_message(chat_id, button.content)

    except Exception as e:
        logger.error(f"Error sending media: {str(e)}")
        bot.send_message(chat_id, button.content)


def send_media_group(chat_id, button):
    try:
        media_files = []
        for media in button.media_group.all():
            if media.media_file and media.media_file.size > 0:
                try:
                    with media.media_file.open('rb') as file:
                        if media.media_file.name.lower().endswith(('.png', '.jpg', '.jpeg')):
                            media_files.append(telebot.types.InputMediaPhoto(file, caption=media.content if media.content else None))
                        elif media.media_file.name.lower().endswith('.mp4'):
                            media_files.append(telebot.types.InputMediaVideo(file, caption=media.content if media.content else None))
                except FileNotFoundError:
                    logger.error(f"File not found in media group for button: {button.key}")
                    continue

        if media_files:
            bot.send_media_group(chat_id, media_files)
        else:
            bot.send_message(chat_id, "Помилка: немає доступних медіафайлів!")

    except Exception as e:
        logger.error(f"Error sending media group: {str(e)}")
        bot.send_message(chat_id, "Помилка відправки медіагрупи")

@bot.message_handler(commands=['start'])
def start(message):
    chat_id = message.chat.id
    username = message.from_user.username
    first_name = message.from_user.first_name
    language_code = message.from_user.language_code
    logger.info(f"Received /start command from {username} ({chat_id})")

    try:
        TelegramUser.objects.update_or_create(
            chat_id=chat_id,
            defaults={
                'username': username,
                'first_name': first_name,
                'language_code': language_code
            }
        )

        start_button = Button.objects.get(key='start_button')

        if start_button.button_type == 'navigation':
            keyboard = create_keyboard([start_button])
            if start_button.media_file:
                send_media_content(chat_id, start_button)
            else:
                bot.send_message(chat_id, start_button.content, reply_markup=keyboard)
        else:
            bot.send_message(chat_id, "👋 Ласкаво просимо! Ось ваші кнопки:", reply_markup=keyboard)

    except Button.DoesNotExist:
        bot.send_message(chat_id, "Стартова кнопка не знайдена!")
    except Exception as e:
        logger.error(f"Error in start handler: {str(e)}")
        bot.send_message(chat_id, f"Помилка: {str(e)}")

@bot.callback_query_handler(func=lambda call: True)
def handle_callback(call):
    try:
        if call.data == "back_to_start":
            start_button = Button.objects.get(key='start_button')
            keyboard = create_keyboard([start_button])
            if start_button.media_file:
                send_media_content(call.message.chat.id, start_button)
            else:
                bot.send_message(call.message.chat.id, start_button.content, reply_markup=keyboard)
            bot.answer_callback_query(call.id)
            return

        try:
            current_button = Button.objects.get(key=call.data)
        except Button.DoesNotExist:
            bot.answer_callback_query(call.id, "Кнопка не знайдена!")
            return

        if current_button.button_type == 'link':
            bot.answer_callback_query(call.id, url=current_button.content)
            return

        child_buttons = Button.objects.filter(previous=current_button)

        if child_buttons.exists():
            keyboard = create_keyboard(child_buttons, include_back_button=True)
            bot.send_message(
                chat_id=call.message.chat.id,
                text=current_button.message_text if current_button.message_text else current_button.text,
                reply_markup=keyboard
            )
        else:
            if current_button.media_file:
                send_media_content(call.message.chat.id, current_button)
            else:
                bot.send_message(call.message.chat.id, current_button.message_text if current_button.message_text else current_button.content)

        bot.answer_callback_query(call.id)  # Завжди відповідаємо

    except Exception as e:
        logger.error(f"Error handling callback: {str(e)}")
        bot.answer_callback_query(call.id, "Сталася помилка")

if __name__ == "__main__":
    bot.polling(none_stop=True, timeout=60, long_polling_timeout=60)


while True:
    try:
        bot.polling(none_stop=True, timeout=60, long_polling_timeout=60)
    except ReadTimeout as e:
        logger.error(f"ReadTimeout error: {str(e)}")
        time.sleep(15)
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        time.sleep(15)