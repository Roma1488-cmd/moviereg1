from django.db import models
from django.utils import timezone
from solo.models import SingletonModel

class Button(models.Model):
    name = models.CharField(max_length=100)
    support = models.ForeignKey(
        'self',
        null=True,
        blank=True,
        related_name='support_buttons',
        on_delete=models.SET_NULL  # Змінено CASCADE на SET_NULL для безпеки
    )
    next_support = models.ForeignKey(
        'self',
        null=True,
        blank=True,
        related_name='next_support_buttons',
        on_delete=models.SET_NULL
    )

    def __str__(self):
        return self.name

class BotConfiguration(SingletonModel):
    channel_id = models.BigIntegerField("Channel ID", default=0)  # Змінено на BigIntegerField
    admin_chat_id = models.BigIntegerField("Admin Chat ID", default=0)  # Змінено на BigIntegerField

    class Meta:
        verbose_name = "Bot Configuration"
        verbose_name_plural = "Bot Configurations"

    def __str__(self):
        return str(self.channel_id)  # Конвертація у рядок для коректного відображення

class BaseMessage(models.Model):
    """Базова модель для спільних полів повідомлень"""
    bot_configuration = models.ForeignKey(
        BotConfiguration,
        on_delete=models.SET_NULL,  # Заборона видалення конфігурації з пов'язаними повідомленнями
        null=True,
        blank=True,
        related_name="%(class)s_messages"  # Динамічне ім'я related_name
    )
    message_type = models.CharField(
        "Message Type",
        max_length=5,
        choices=[('text', 'Text'), ('photo', 'Photo'), ('video', 'Video')]
    )
    text = models.TextField("Text", blank=True, null=True)
    media_file = models.FileField("Media File", upload_to='media_files', blank=True, null=True)
    scheduled_time = models.DateTimeField("Scheduled Time", default=timezone.now)
    is_send = models.BooleanField("Send", default=False)
    media_id = models.CharField("Media ID", max_length=512, blank=True, null=True)  # Збільшено довжину

    class Meta:
        abstract = True  # Позначаємо як абстрактну модель

class DelayMessage(BaseMessage):
    button_text = models.CharField("Button Text", max_length=100, blank=True, null=True)
    button_link = models.URLField("Button Link", blank=True, null=True)
    additional_media = models.FileField("Additional Media", upload_to='media_files', blank=True, null=True)

    class Meta:
        verbose_name = "Delay Message"
        verbose_name_plural = "Delay Messages"

    def __str__(self):
        return f"{self.message_type} message (delay) scheduled for {self.scheduled_time}"

class ScheduledMessage(models.Model):
    bot_configuration = models.ForeignKey(BotConfiguration, on_delete=models.CASCADE, related_name="scheduled_messages")
    message_type = models.CharField("Message Type", max_length=5, choices=[('text', 'Text'), ('photo', 'Photo'), ('video', 'Video')])
    text = models.TextField("Text", blank=True, null=True)
    media_file = models.FileField("Media File", upload_to='media_files', blank=True, null=True)
    scheduled_time = models.DateTimeField("Scheduled Time", default=timezone.now)
    is_send = models.BooleanField("Send", default=False)
    media_id = models.CharField("Media ID", max_length=255, blank=True, null=True)

    # Додайте ці поля, якщо вони потрібні
    button_text = models.CharField("Button Text", max_length=100, blank=True, null=True)
    button_link = models.URLField("Button Link", blank=True, null=True)
    additional_media = models.FileField("Additional Media", upload_to='media_files', blank=True, null=True)

    class Meta:
        verbose_name = "Scheduled Message"
        verbose_name_plural = "Scheduled Messages"

    def __str__(self):
        return f"{self.message_type} message scheduled for {self.scheduled_time}"

class TelegramUser(models.Model):
    chat_id = models.BigIntegerField(unique=True)
    username = models.CharField(
        max_length=50,
        null=True,
        blank=True  # Дозволяємо пусті значення
    )
    first_name = models.CharField(
        max_length=50,
        null=True,
        blank=True  # Дозволяємо пусті значення
    )
    language_code = models.CharField(
        max_length=10,
        default="",
        blank=True  # Замість "unknown" — пустий рядок
    )
    status = models.CharField(
        max_length=20,
        default="active",
        choices=[('active', 'Active'), ('inactive', 'Inactive')]  # Додано вибіркові значення
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Telegram User"
        verbose_name_plural = "Telegram Users"
        ordering = ['-created_at']  # Сортування за замовчуванням

    def __str__(self):
        return str(self.chat_id)  # Конвертація у рядок