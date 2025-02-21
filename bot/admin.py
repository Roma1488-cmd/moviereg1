from django.contrib import admin
import telebot
import logging
from django.urls import path
from django.conf import settings
from django.contrib import messages
from solo.admin import SingletonModelAdmin
from bot.models import BotConfiguration, DelayMessage, ScheduledMessage, TelegramUser, Button, PostButton, PostMedia
from django.http import HttpResponse
import datetime
from django.utils import timezone

logger = logging.getLogger(__name__)

class PostButtonInline(admin.TabularInline):
    model = PostButton
    fields = ('text', 'link')
    extra = 1

class PostMediaInline(admin.TabularInline):
    model = PostMedia
    fields = ('media_type', 'media_file')
    extra = 1

@admin.register(DelayMessage)
class DelayMessageAdmin(admin.ModelAdmin):
    list_display = ('message_type', 'text', 'scheduled_time', 'is_send')
    fieldsets = [
        (None, {"fields": [
            'bot_configuration',
            'message_type',
            'text',
            'media_file',
            'scheduled_time',
            'is_send'
        ]}),
    ]
    inlines = [PostButtonInline, PostMediaInline]

    def save_model(self, request, instance, form, change):
        super().save_model(request, instance, form, change)
        
        # Перевіряємо умови для планування
        if not instance.is_send and instance.scheduled_time > timezone.now():
            # Додаємо затримку для точності
            adjusted_time = instance.scheduled_time + timezone.timedelta(seconds=1)
            
            # Імпортуємо та викликаємо функцію планування
            from .tasks import schedule_delay_message
            schedule_delay_message(instance, adjusted_time)

        # Відправляємо попередній перегляд
        bot = telebot.TeleBot(settings.TELEGRAM_BOT_TOKEN, parse_mode="HTML")
        chat_id = BotConfiguration.get_instance().admin_chat_id
        text = instance.text
        file = instance.media_file
        markup = None

        if instance.post_buttons.exists():
            from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
            markup = InlineKeyboardMarkup()
            for button in instance.post_buttons.all():
                markup.add(InlineKeyboardButton(text=button.text, url=button.link))

        try:
            if instance.message_type == "photo":
                with file.open('rb') as photo:
                    message = bot.send_photo(
                        chat_id=chat_id,
                        caption=text,
                        photo=photo,
                        reply_markup=markup
                    )
                    instance.media_id = message.photo[0].file_id
            elif instance.message_type == "video":
                with file.open('rb') as video:
                    message = bot.send_video(
                        chat_id=chat_id,
                        caption=text,
                        video=video,
                        reply_markup=markup
                    )
                    instance.media_id = message.video.file_id
            else:
                bot.send_message(chat_id=chat_id, text=text, reply_markup=markup)
        except Exception as error:
            messages.add_message(request, messages.ERROR, f"❌ Помилка надсилання: {error}")
            return

        super().save_model(request, instance, form, change)

@admin.register(Button)
class ButtonAdmin(admin.ModelAdmin):
    list_display = ('text', 'key', 'button_type', 'prev_next_info', 'description', 'message_text')
    search_fields = ('text', 'key', 'content', 'description', 'message_text')
    list_filter = ('button_type',)

    fieldsets = (
        ("Основні налаштування", {
            'fields': (
                'key',
                'text',
                'button_type',
                'content',
                'media_file',
                'description'
            )
        }),
        ("Послідовність кнопок", {
            'fields': (
                'previous',
                'next'
            ),
            'classes': ('collapse',)
        }),
    )

    def prev_next_info(self, obj):
        return f"← {obj.previous.key if obj.previous else ''} → {obj.next.key if obj.next else ''}"

    prev_next_info.short_description = "Послідовність"

@admin.register(BotConfiguration)
class BotConfigurationAdmin(SingletonModelAdmin):
    fieldsets = [
        (None, {"fields": ['channel_id', 'admin_chat_id', 'chat_id']}),
    ]

    def save_model(self, request, instance, form, change):
        super().save_model(request, instance, form, change)
        bot = telebot.TeleBot(settings.TELEGRAM_BOT_TOKEN)
        admin_chat_id = instance.admin_chat_id
        if admin_chat_id:
            try:
                bot.send_message(chat_id=admin_chat_id, text="✅ Налаштування збережено!")
                messages.success(request, "Тестове повідомлення успішно надіслано!")
            except Exception as error:
                messages.error(request, f"❌ Помилка надсилання тестового повідомлення: {error}")

logger = logging.getLogger(__name__)

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
            'is_send'
        ]}),
    ]
    inlines = [PostButtonInline, PostMediaInline]

    def save_model(self, request, instance, form, change):
        super().save_model(request, instance, form, change)
        if not instance.is_send and instance.scheduled_time > timezone.now():
            instance.schedule()  # Викликаємо планування одразу після збереження

        bot = telebot.TeleBot(settings.TELEGRAM_BOT_TOKEN, parse_mode="HTML")
        chat_id = BotConfiguration.get_instance().admin_chat_id
        text = instance.text
        file = instance.media_file
        markup = None

        if instance.post_buttons.exists():  # Перевіряємо чи є кнопки
            from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
            markup = InlineKeyboardMarkup()
            for button in instance.post_buttons.all():
                markup.add(InlineKeyboardButton(text=button.text, url=button.link))

        try:
            if instance.message_type == "photo":
                message = bot.send_photo(chat_id=chat_id, caption=text, photo=file, reply_markup=markup)
                instance.media_id = message.photo[0].file_id
            elif instance.message_type == "video":
                message = bot.send_video(chat_id=chat_id, caption=text, video=file, reply_markup=markup)
                instance.media_id = message.video.file_id
            else:
                bot.send_message(chat_id=chat_id, text=text, reply_markup=markup)
        except Exception as error:
            messages.add_message(request, messages.ERROR, f"❌ Помилка надсилання: {error}")
            return

        super().save_model(request, instance, form, change)

    def schedule_message(self, instance):
        from .tasks import schedule_message
        try:
            schedule_message(instance)
        except Exception as e:
            logger.error(f"Помилка планування: {str(e)}")

@admin.register(TelegramUser)
class TelegramUserAdmin(admin.ModelAdmin):
    list_display = ('chat_id', 'username', 'language_code', 'created_at')
    fields = ('chat_id', 'username', 'first_name', 'language_code')
    readonly_fields = ('created_at',)

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
