from django.core.management.base import BaseCommand
from bot import telegram_bot  # Імпортуємо ваш бот

class Command(BaseCommand):
    help = "Запуск Telegram бота"

    def handle(self, *args, **kwargs):
        telegram_bot.start_bot()
