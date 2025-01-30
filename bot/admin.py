import telebot
from django.conf import settings
from django.contrib import admin
from django.contrib import messages
from django.http import HttpResponse
from django.urls import path
from solo.admin import SingletonModelAdmin
import logging
import datetime
from bot.models import BotConfiguration, DelayMessage, ScheduledMessage, TelegramUser, Button

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
        (None, {"fields": [
            'bot_configuration',
            'message_type',
            'text',
            'media_file',
            'scheduled_time',
            'button_text',  # Додано поле для кнопки
            'button_link',  # Додано поле для посилання
            'is_send'
        ]}),
    ]
    readonly_fields = ('media_id',)

    def save_model(self, request, instance, form, change):
        # Отримуємо конфігурацію бота
        bot_configuration = BotConfiguration.get_solo()
        if not bot_configuration:
            messages.error(request, "BotConfiguration не встановлено!")
            return

        instance.bot_configuration = bot_configuration

        # Зберігаємо модель спочатку
        super().save_model(request, instance, form, change)

        # Якщо повідомлення ще не відправлено - плануємо відправку
        if not instance.is_send and instance.scheduled_time > timezone.now():
            self.schedule_message(instance)

    def schedule_message(self, instance):
        """Плануємо відправку через Celery/APScheduler"""
        from .tasks import send_scheduled_message  # Імпортуємо асинхронне завдання

        # Розраховуємо затримку
        eta = instance.scheduled_time

        try:
            # Використовуємо Celery для планування
            send_scheduled_message.apply_async(
                args=[instance.id],
                eta=eta
            )
            logger.info(f"Повідомлення {instance.id} заплановано на {eta}")
        except Exception as e:
            logger.error(f"Помилка планування: {str(e)}")

@admin.register(TelegramUser)
class TelegramUserAdmin(admin.ModelAdmin):
    list_display = ('chat_id', 'username', 'first_name', 'language_code', 'created_at')
    fields = ('chat_id', 'username', 'first_name', 'language_code', 'status')  # Додайте потрібні поля
    readonly_fields = ('created_at',)  # Тільки для нередагованих полів

    def get_urls(self):
        urls = super().get_urls()
        my_urls = [
            path("download/", self.download_users)
        ]
        return my_urls + urls

    def download_users(self, request):
        content = ""
        users = TelegramUser.objects.all()
        for user in users:
            content += f"{user.chat_id}\n"

        now = datetime.datetime.now()
        string_date = now.strftime('%Y_%m_%d_%H_%M')
        filename = f"{string_date}-botusers-{len(users)}.txt"

        response = HttpResponse(content, content_type='text/plain')
        response['Content-Disposition'] = f"attachment; filename={filename}"
        return response

class ButtonInline(admin.TabularInline):
    fields = ('name', 'next_support')
    autocomplete_fields = ('support', 'next_support')
    fk_name = 'support'
    model = Button
    extra = 1

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