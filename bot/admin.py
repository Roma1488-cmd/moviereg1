from django.contrib import admin
from django.contrib import messages
from solo.admin import SingletonModelAdmin
from .models import BotConfiguration, DelayMessage, ScheduledMessage, TelegramUser
import telebot


@admin.register(BotConfiguration)
class BotConfigurationAdmin(SingletonModelAdmin):
    fieldsets = [
        (None, {"fields": ['channel_id', 'admin_chat_id']}),
    ]

    def save_model(self, request, instance, form, change):
        bot = telebot.TeleBot("7283206544:AAHQzhdTykJwtGmqLvkS4tY8uR_QhI45XhQ")
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
        (None, {"fields": ['message_type', 'text', 'media_file', 'scheduled_time', 'button_text', 'button_link',
                           'additional_media', 'is_send']}),
    ]
    readonly_fields = ('media_id',)

    def save_model(self, request, instance, form, change):
        bot = telebot.TeleBot("7283206544:AAHQzhdTykJwtGmqLvkS4tY8uR_QhI45XhQ")
        try:
            if instance.message_type == "photo" and instance.media_file:
                bot.send_photo(chat_id=BotConfiguration.get_solo().admin_chat_id, photo=instance.media_file,
                               caption=instance.text)
                instance.media_id = message.photo[0].file_id
            elif instance.message_type == "video" and instance.media_file:
                bot.send_video(chat_id=BotConfiguration.get_solo().admin_chat_id, video=instance.media_file,
                               caption=instance.text)
                instance.media_id = message.video.file_id
            elif instance.message_type == "text":
                bot.send_message(chat_id=BotConfiguration.get_solo().admin_chat_id, text=instance.text)
        except Exception as error:
            messages.add_message(request, messages.ERROR, str(error))
            return
        super().save_model(request, instance, form, change)


@admin.register(ScheduledMessage)
class ScheduledMessageAdmin(admin.ModelAdmin):
    list_display = ('message_type', 'text', 'scheduled_time', 'is_send')
    fieldsets = [
        (None, {"fields": ['message_type', 'text', 'media_file', 'scheduled_time', 'button_text', 'button_link',
                           'additional_media', 'is_send']}),
    ]
    readonly_fields = ('media_id',)

    def save_model(self, request, instance, form, change):
        bot = telebot.TeleBot("7283206544:AAHQzhdTykJwtGmqLvkS4tY8uR_QhI45XhQ")
        channel_id = BotConfiguration.get_solo().channel_id
        try:
            if instance.message_type == "photo" and instance.media_file:
                bot.send_photo(chat_id=channel_id, photo=instance.media_file, caption=instance.text)
                instance.media_id = message.photo[0].file_id
            elif instance.message_type == "video" and instance.media_file:
                bot.send_video(chat_id=channel_id, video=instance.media_file, caption=instance.text)
                instance.media_id = message.video.file_id
            elif instance.message_type == "text":
                bot.send_message(chat_id=channel_id, text=instance.text)
        except Exception as error:
            messages.add_message(request, messages.ERROR, str(error))
            return
        super().save_model(request, instance, form, change)


@admin.register(TelegramUser)
class TelegramUserAdmin(admin.ModelAdmin):
    list_display = ('chat_id', 'username', 'first_name', 'language_code', 'created_at')
    list_filter = ('created_at', 'language_code')
    search_fields = ('chat_id', 'username', 'first_name')
    readonly_fields = ('chat_id', 'username', 'first_name', 'language_code', 'created_at')
