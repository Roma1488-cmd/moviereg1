import telebot
from django.conf import settings
from django.contrib import admin
from django.contrib import messages
from solo.admin import SingletonModelAdmin
import logging
from bot.models import BotConfiguration, DelayMessage, ScheduledMessage, TelegramUser

logger = logging.getLogger(__name__)


@admin.register(BotConfiguration)
class BotConfigurationAdmin(SingletonModelAdmin):
    fieldsets = [
        (None, {"fields": ['channel_id', 'admin_chat_id']}),
    ]

    def save_model(self, request, instance, form, change):
        bot = telebot.TeleBot(settings.TELEGRAM_BOT_TOKEN)
        admin_chat_id = instance.admin_chat_id

        try:
            bot.send_message(chat_id=admin_chat_id, text="Тестове повідомлення")
        except Exception as error:
            messages.add_message(request, messages.ERROR, str(error))
            return

        super().save_model(request, instance, form, change)


@admin.register(DelayMessage)
class DelayMessageAdmin(admin.ModelAdmin):
    list_display = ('message_type', 'text', 'scheduled_time', 'is_send')
    fieldsets = [
        (None, {"fields": ['bot_configuration', 'message_type', 'text', 'media_file', 'scheduled_time', 'button_text',
                           'button_link', 'additional_media', 'is_send']}),
    ]
    readonly_fields = ('media_id',)

    def save_model(self, request, instance, form, change):
        bot_configuration = BotConfiguration.get_solo()
        if not bot_configuration:
            messages.add_message(request, messages.ERROR, "BotConfiguration не встановлено.")
            return
        instance.bot_configuration = bot_configuration

        bot = telebot.TeleBot(settings.TELEGRAM_BOT_TOKEN)

        # Створення клавіатури з кнопкою
        keyboard = telebot.types.InlineKeyboardMarkup()
        if instance.button_text and instance.button_link:
            button = telebot.types.InlineKeyboardButton(text=instance.button_text, url=instance.button_link)
            keyboard.add(button)

        try:
            if instance.message_type == "photo" and instance.media_file:
                message = bot.send_photo(chat_id=bot_configuration.channel_id, photo=instance.media_file,
                                         caption=instance.text, reply_markup=keyboard)
                instance.media_id = message.photo[0].file_id
            elif instance.message_type == "video" and instance.media_file:
                message = bot.send_video(chat_id=bot_configuration.channel_id, video=instance.media_file,
                                         caption=instance.text, reply_markup=keyboard)
                instance.media_id = message.video.file_id
            elif instance.message_type == "text":
                message = bot.send_message(chat_id=bot_configuration.channel_id, text=instance.text,
                                           reply_markup=keyboard)
            super().save_model(request, instance, form, change)
        except Exception as error:
            messages.add_message(request, messages.ERROR, str(error))
            logger.error(f'Error sending message: {error}')
            return


@admin.register(ScheduledMessage)
class ScheduledMessageAdmin(admin.ModelAdmin):
    list_display = ('message_type', 'text', 'scheduled_time', 'is_send')
    fieldsets = [
        (None, {"fields": ['bot_configuration', 'message_type', 'text', 'media_file', 'scheduled_time', 'button_text',
                           'button_link', 'additional_media', 'is_send']}),
    ]
    readonly_fields = ('media_id',)

    def save_model(self, request, instance, form, change):
        bot_configuration = BotConfiguration.get_solo()
        if not bot_configuration:
            messages.add_message(request, messages.ERROR, "BotConfiguration не встановлено.")
            return
        instance.bot_configuration = bot_configuration

        bot = telebot.TeleBot(settings.TELEGRAM_BOT_TOKEN)

        # Створення клавіатури з кнопкою
        keyboard = telebot.types.InlineKeyboardMarkup()
        if instance.button_text and instance.button_link:
            button = telebot.types.InlineKeyboardButton(text=instance.button_text, url=instance.button_link)
            keyboard.add(button)

        try:
            if instance.message_type == "photo" and instance.media_file:
                message = bot.send_photo(chat_id=bot_configuration.admin_chat_id, photo=instance.media_file,
                                         caption=instance.text, reply_markup=keyboard)
                instance.media_id = message.photo[0].file_id
            elif instance.message_type == "video" and instance.media_file:
                message = bot.send_video(chat_id=bot_configuration.admin_chat_id, video=instance.media_file,
                                         caption=instance.text, reply_markup=keyboard)
                instance.media_id = message.video.file_id
            elif instance.message_type == "text":
                message = bot.send_message(chat_id=bot_configuration.admin_chat_id, text=instance.text,
                                           reply_markup=keyboard)
            super().save_model(request, instance, form, change)
        except Exception as error:
            messages.add_message(request, messages.ERROR, str(error))
            logger.error(f'Error sending message: {error}')
            return


@admin.register(TelegramUser)
class TelegramUserAdmin(admin.ModelAdmin):
    list_display = ('chat_id', 'username', 'first_name', 'language_code', 'created_at')
    list_filter = ('created_at', 'language_code')
    search_fields = ('chat_id', 'username', 'first_name')
    readonly_fields = ('chat_id', 'username', 'first_name', 'language_code', 'created_at')


bot = telebot.TeleBot(settings.TELEGRAM_BOT_TOKEN)


@bot.message_handler(commands=['start'])
def start(message):
    chat_id = message.chat.id
    username = message.from_user.username
    first_name = message.from_user.first_name
    language_code = message.from_user.language_code

    TelegramUser.objects.update_or_create(
        chat_id=chat_id,
        defaults={'username': username, 'first_name': first_name, 'language_code': language_code}
    )

    bot.send_message(chat_id, "Вітаю! Бот активовано.")
