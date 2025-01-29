from django.db import models
from django.utils import timezone  # У першу допомогу імпорт додано
from solo.models import SingletonModel  # Переконайтеся, що 'SingletonModel' імпортовано

class Button(models.Model):
    name = models.CharField(max_length=100)
    support = models.ForeignKey('self', null=True, blank=True, related_name='support_buttons', on_delete=models.CASCADE)
    next_support = models.ForeignKey('self', null=True, blank=True, related_name='next_support_buttons', on_delete=models.CASCADE)

    def __str__(self):
        return self.name

class BotConfiguration(SingletonModel):
    channel_id = models.CharField("Channel ID", max_length=255, default="")
    admin_chat_id = models.CharField("Admin Chat ID", max_length=255)

    class Meta:
        verbose_name = "Bot Configuration"
        verbose_name_plural = "Bot Configurations"

    def __str__(self):
        return self.channel_id

class DelayMessage(models.Model):
    bot_configuration = models.ForeignKey(BotConfiguration, on_delete=models.CASCADE, related_name="delay_messages")
    message_type = models.CharField("Message Type", max_length=5, choices=[('text', 'Text'), ('photo', 'Photo'), ('video', 'Video')])
    text = models.TextField("Text", blank=True, null=True)
    media_file = models.FileField("Media File", upload_to='media_files', blank=True, null=True)
    scheduled_time = models.DateTimeField("Scheduled Time", default=timezone.now)
    button_text = models.CharField("Button Text", max_length=100, blank=True, null=True)
    button_link = models.URLField("Button Link", blank=True, null=True)
    additional_media = models.FileField("Additional Media", upload_to='media_files', blank=True, null=True)
    is_send = models.BooleanField("Send", default=False)
    media_id = models.CharField("Media ID", max_length=255, blank=True, null=True)

    class Meta:
        verbose_name = "Delay Message"
        verbose_name_plural = "Delay Messages"

    def __str__(self):
        return f"{self.message_type} message scheduled for {self.scheduled_time}"

class ScheduledMessage(models.Model):
    bot_configuration = models.ForeignKey(BotConfiguration, on_delete=models.CASCADE, related_name="scheduled_messages")
    message_type = models.CharField("Message Type", max_length=5, choices=[('text', 'Text'), ('photo', 'Photo'), ('video', 'Video')])
    text = models.TextField("Text", blank=True, null=True)
    media_file = models.FileField("Media File", upload_to='media_files', blank=True, null=True)
    scheduled_time = models.DateTimeField("Scheduled Time", default=timezone.now)
    button_text = models.CharField("Button Text", max_length=100, blank=True, null=True)
    button_link = models.URLField("Button Link", blank=True, null=True)
    additional_media = models.FileField("Additional Media", upload_to='media_files', blank=True, null=True)
    is_send = models.BooleanField("Send", default=False)
    media_id = models.CharField("Media ID", max_length=255, blank=True, null=True)

    class Meta:
        verbose_name = "Scheduled Message"
        verbose_name_plural = "Scheduled Messages"

    def __str__(self):
        return f"{self.message_type} message scheduled for {self.scheduled_time}"

class TelegramUser(models.Model):
    chat_id = models.BigIntegerField(unique=True)
    username = models.CharField(max_length=50)
    first_name = models.CharField(max_length=50)
    language_code = models.CharField(max_length=10, default="unknown")  # Додано стандартне значення
    status = models.CharField(max_length=20, default="active")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


    class Meta:
        verbose_name = "Telegram User"
        verbose_name_plural = "Telegram Users"

    def __str__(self):
        return self.chat_id
