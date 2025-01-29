from django.contrib import admin
from .models import DelayMessage, ScheduledMessage, SubscribeChannel, TelegramUser, UserCode

admin.site.register(DelayMessage)
admin.site.register(ScheduledMessage)
admin.site.register(SubscribeChannel)
admin.site.register(TelegramUser)
admin.site.register(UserCode)
