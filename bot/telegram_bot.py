import logging
import telebot
from django.conf import settings
from .models import TelegramUser

logger = logging.getLogger(__name__)

bot = telebot.TeleBot(settings.TELEGRAM_BOT_TOKEN)

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
            defaults={'username': username, 'first_name': first_name, 'language_code': language_code}
        )
        logger.info(f"User {username} ({chat_id}) has been added/updated in the database.")
        bot.send_message(chat_id, "Вітаю! Бот активовано.")
    except Exception as e:
        logger.error(f"Error saving user {username} ({chat_id}): {str(e)}")

def start_bot():
    bot.polling(none_stop=True)

if __name__ == "__main__":
    start_bot()
