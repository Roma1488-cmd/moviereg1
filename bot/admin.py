import telebot
from django.conf import settings
from django.contrib import admin
from django.contrib import messages
from telebot import TeleBot
import logging

from solo.admin import SingletonModelAdmin
from bot.models import BotConfiguration, DelayMessage, ScheduledMessage, TelegramUser

logger = logging.getLogger(__name__)

@admin.register(BotConfiguration)
class BotConfigurationAdmin(SingletonModelAdmin):
    fieldsets = [
        (None, {"fields": ['channel_id', 'admin_chat_id']}),
    ]

    def save_model(self, request, instance, form, change):
        bot = TeleBot("7283206544:AAHQzhdTykJwtGmqLvkS4tY8uR_QhI45XhQ")
        admin_chat_id = instance.admin_chat_id

        try:
            bot.send_message(chat_id=admin_chat_id, text="Тестове повідомлення")  # Відправка тестового повідомлення
        except Exception as error:
            messages.add_message(request, messages.ERROR, str(error))
            return

        super().save_model(request, instance, form, change)


@admin.register(DelayMessage)
class DelayMessageAdmin(admin.ModelAdmin):
    list_display = ('message_type', 'text', 'scheduled_time', 'is_send')
    fieldsets = [
        (None, {"fields": ['message_type', 'text', 'media_file', 'scheduled_time', 'button_text', 'button_link', 'additional_media', 'is_send']}),
    ]
    readonly_fields = ('media_id',)

    def save_model(self, request, instance, form, change):
        instance.bot_configuration = BotConfiguration.get_solo()

        bot = TeleBot("7283206544:AAHQzhdTykJwtGmqLvkS4tY8uR_QhI45XhQ")
        try:
            if instance.message_type == "photo" and instance.media_file:
                message = bot.send_photo(chat_id=instance.bot_configuration.admin_chat_id, photo=instance.media_file, caption=instance.text)
                instance.media_id = message.photo[0].file_id
            elif instance.message_type == "video" and instance.media_file:
                message = bot.send_video(chat_id=instance.bot_configuration.admin_chat_id, video=instance.media_file, caption=instance.text)
                instance.media_id = message.video.file_id
            elif instance.message_type == "text":
                message = bot.send_message(chat_id=instance.bot_configuration.admin_chat_id, text=instance.text)
            super().save_model(request, instance, form, change)  # Зберігаємо зміни після надсилання
        except Exception as error:
            messages.add_message(request, messages.ERROR, str(error))
            logger.error(f'Error sending message: {error}')  # Логування помилок
            return


@admin.register(ScheduledMessage)
class ScheduledMessageAdmin(admin.ModelAdmin):
    list_display = ('message_type', 'text', 'scheduled_time', 'is_send')
    fieldsets = [
        (None, {"fields": ['message_type', 'text', 'media_file', 'scheduled_time', 'button_text', 'button_link', 'additional_media', 'is_send']}),
    ]
    readonly_fields = ('media_id',)

    def save_model(self, request, instance, form, change):
        bot = TeleBot("7283206544:AAHQzhdTykJwtGmqLvkS4tY8uR_QhI45XhQ")
        channel_id = BotConfiguration.get_solo().channel_id
        try:
            if instance.message_type == "photo" and instance.media_file:
                message = bot.send_photo(chat_id=channel_id, photo=instance.media_file, caption=instance.text)
                instance.media_id = message.photo[0].file_id
            elif instance.message_type == "video" and instance.media_file:
                message = bot.send_video(chat_id=channel_id, video=instance.media_file, caption=instance.text)
                instance.media_id = message.video.file_id
            elif instance.message_type == "text":
                message = bot.send_message(chat_id=channel_id, text=instance.text)
            super().save_model(request, instance, form, change)  # Зберігаємо зміни після відправлення
        except Exception as error:
            messages.add_message(request, messages.ERROR, str(error))
            logger.error(f'Error sending message: {error}')  # Логування помилок
            return


@admin.register(TelegramUser)
class TelegramUserAdmin(admin.ModelAdmin):
    list_display = ('chat_id', 'username', 'first_name', 'language_code', 'created_at')
    list_filter = ('created_at', 'language_code')
    search_fields = ('chat_id', 'username', 'first_name')
    readonly_fields = ('chat_id', 'username', 'first_name', 'language_code', 'created_at')


bot = telebot.TeleBot("7283206544:AAHQzhdTykJwtGmqLvkS4tY8uR_QhI45XhQ")

@bot.message_handler(commands=['start'])  # Переконайтеся, що цей рядок не відступає
def start(message):
    chat_id = message.chat.id
    username = message.from_user.username
    first_name = message.from_user.first_name
    language_code = message.from_user.language_code

    # Зберігаємо нового користувача або оновлюємо інформацію про існуючого
    TelegramUser.objects.update_or_create(
        chat_id=chat_id,
        defaults={'username': username, 'first_name': first_name, 'language_code': language_code}
    )

    bot.send_message(chat_id, "Вітаю! Бот активовано.")
