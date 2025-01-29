from django.contrib import admin
from solo.admin import SingletonModelAdmin
from .models import BotConfiguration


@admin.register(BotConfiguration)
class BotConfigurationAdmin(SingletonModelAdmin):
    fieldsets = [
        (None, {"fields": ['start_message', 'subscribe_message', 'subscribe_button_text', 'subscribe_button_link',
                           'admin_chat_id', 'android_app_link']}),
        ("Delay Message", {"classes": ['collapse'],
                           "fields": ['is_send_delay_message', 'media', 'media_file', 'message', 'button_text',
                                      'button_link', 'delay_seconds', 'media_id']})
    ]
    readonly_fields = ['media_id']

    def save_model(self, request, instance, form, change):
        if not instance.is_send_delay_message:
            super().save_model(request, instance, form, change)
            return

        bot = telebot.TeleBot("7283206544:AAHQzhdTykJwtGmqLvkS4tY8uR_QhI45XhQ")
        chat_id = BotConfiguration.get_solo().admin_chat_id
        text = instance.message
        file = instance.media_file
        try:
            if instance.media == "photo":
                message = bot.send_photo(chat_id=chat_id, caption=text, photo=file)
                instance.media_id = message.photo[0].file_id
            elif instance.media == "video":
                message = bot.send_video(chat_id=chat_id, caption=text, video=file)
                instance.media_id = message.video.file_id
            else:
                bot.send_message(chat_id=chat_id, text=text)
        except Exception as error:
            messages.add_message(request, messages.ERROR, str(error))
            return

        super().save_model(request, instance, form, change)
