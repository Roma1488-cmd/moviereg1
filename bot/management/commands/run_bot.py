from django.core.management.base import BaseCommand
from telebot import TeleBot
from bot.models import TelegramUser  # Виправлений шлях імпорту

# Інші імпорти

bot = TeleBot('7283206544:AAHQzhdTykJwtGmqLvkS4tY8uR_QhI45XhQ')

class Command(BaseCommand):
    help = 'Runs the bot'

    def handle(self, *args, **options):
        @bot.message_handler(commands=['start'])
        def start(message):
            TelegramUser.objects.update_or_create(
                chat_id=message.chat.id,
                defaults={
                    'username': message.from_user.username,
                    'first_name': message.from_user.first_name,
                    'language_code': message.from_user.language_code,
                }
            )
            bot.reply_to(message, "Привіт! Ви зареєстровані.")

        bot.polling(none_stop=True)
