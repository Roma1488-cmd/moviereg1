from django.db import models

class DelayMessage(models.Model):
    message = models.TextField("Message")
    delay = models.DurationField("Delay")

class ScheduledMessage(models.Model):
    message = models.TextField("Message")
    scheduled_time = models.DateTimeField("Scheduled time")

class SubscribeChannel(models.Model):
    channel_name = models.CharField("Channel Name", max_length=255)
    subscribe_link = models.URLField("Subscribe Link")

class TelegramUser(models.Model):
    user_id = models.CharField("User ID", max_length=255)
    username = models.CharField("Username", max_length=255)

class UserCode(models.Model):
    code = models.CharField("Code", max_length=255)
    user = models.ForeignKey(TelegramUser, on_delete=models.CASCADE, related_name="codes")
