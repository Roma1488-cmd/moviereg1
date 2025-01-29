import telegram
from django.conf import settings

# Функція для ініціалізації бота
def start_telegram_bot():
    bot = telegram.Bot(token=settings.TG_BOT_TOKEN)
    bot.send_message(chat_id='your-chat-id', text="Bot started!")
