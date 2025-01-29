from django.db import models
from solo.models import SingletonModel  # Використовується для збереження єдиного екземпляра конфігурації

class BotConfiguration(SingletonModel):
    start_message = models.TextField("Start message")
    subscribe_message = models.TextField("Subscribe message")
    subscribe_button_text = models.CharField("Subscribe button text", max_length=255)
    subscribe_button_link = models.URLField("Subscribe button link")
    admin_chat_id = models.CharField("Admin chat id", max_length=255)
    android_app_link = models.URLField("Android app link")
    is_send_delay_message = models.BooleanField("Send delay message", default=False)
    delay_seconds = models.PositiveIntegerField("Delay seconds", default=0)
    media = models.CharField("Media type", max_length=10, choices=[('photo', 'Photo'), ('video', 'Video')])
    media_file = models.FileField("Media file", upload_to='media_files')
    message = models.TextField("Message")
    button_text = models.CharField("Button text", max_length=255, blank=True, null=True)
    button_link = models.URLField("Button link", blank=True, null=True)
    media_id = models.CharField("Media ID", max_length=255, blank=True, null=True)

    class Meta:
        verbose_name = "Bot Configuration"

    def __str__(self):
        return self.start_message
