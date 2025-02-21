from django.db import models
from django.utils import timezone
from solo.models import SingletonModel


class PostMedia(models.Model):
    MEDIA_TYPES = (
        ('photo', 'Photo'),
        ('video', 'Video')
    )

    media_type = models.CharField(max_length=50, choices=MEDIA_TYPES)
    media_file = models.FileField("Media File", upload_to='media_files', blank=True, null=True)
    delay_message = models.ForeignKey('bot.DelayMessage', related_name='post_medias', on_delete=models.CASCADE,
                                      blank=True, null=True)
    scheduled_message = models.ForeignKey('bot.ScheduledMessage', related_name='post_medias', on_delete=models.CASCADE,
                                          blank=True, null=True)  # Додаємо поле для зв'язку з ScheduledMessage

    class Meta:
        verbose_name = "Post Media"
        verbose_name_plural = "Post Medias"

    def __str__(self):
        return f"{self.media_type} - {self.media_file.name if self.media_file else 'No file'}"


class PostButton(models.Model):
    text = models.CharField("Button Text", max_length=255, default="")
    link = models.URLField("Button Link", blank=True, default="")
    delay_message = models.ForeignKey('bot.DelayMessage', related_name='post_buttons', on_delete=models.CASCADE,
                                      blank=True, null=True)
    scheduled_message = models.ForeignKey('bot.ScheduledMessage', related_name='post_buttons', on_delete=models.CASCADE,
                                          blank=True, null=True)  # Додаємо поле для зв'язку з ScheduledMessage

    class Meta:
        verbose_name = "Post Button"
        verbose_name_plural = "Post Buttons"

    def __str__(self):
        return self.text

class Button(models.Model):
    BUTTON_TYPES = (
        ('navigation', 'Навігаційна кнопка'),
        ('link', 'Посилання'),
    )

    key = models.CharField("Унікальний ідентифікатор", max_length=50, unique=True)
    text = models.CharField(max_length=255, default="")
    button_type = models.CharField("Тип кнопки", max_length=20, choices=BUTTON_TYPES)
    content = models.TextField(blank=True, default="")
    next_message_content = models.TextField("Текст наступного повідомлення", blank=True, default="")
    previous = models.ForeignKey(
        'self',
        null=True,
        blank=True,
        related_name='previous_buttons',
        on_delete=models.SET_NULL,
        verbose_name="Попередня кнопка"
    )
    next = models.ForeignKey(
        'self',
        null=True,
        blank=True,
        related_name='next_buttons',
        on_delete=models.SET_NULL,
        verbose_name="Наступна кнопка"
    )
    media_file = models.FileField("Медіа-файл", upload_to='buttons/', blank=True, null=True)
    description = models.TextField("Опис", blank=True, default="")
    message_text = models.TextField("Текст повідомлення", blank=True, default="")
    delay_message = models.ForeignKey('bot.DelayMessage', related_name='buttons', on_delete=models.CASCADE, null=True, blank=True)  # Додано зовнішній ключ

    class Meta:
        verbose_name = "Button"
        verbose_name_plural = "Buttons"

    def __str__(self):
        return f"{self.text} ({self.key})"

class BotConfiguration(SingletonModel):
    channel_id = models.BigIntegerField("Channel ID", default=0)
    admin_chat_id = models.BigIntegerField("Admin Chat ID", default=1850284945)
    chat_id = models.CharField(max_length=100, null=True, blank=True)

    class Meta:
        verbose_name = "Bot Configuration"
        verbose_name_plural = "Bot Configurations"

    def __str__(self):
        return f"Admin ID: {self.admin_chat_id} | Channel ID: {self.channel_id}"

    @classmethod
    def get_instance(cls):
        instance, created = cls.objects.get_or_create()
        return instance

    @classmethod
    def set_admin_chat_id(cls, new_chat_id):
        instance = cls.get_instance()
        instance.admin_chat_id = new_chat_id
        instance.save()
        return instance

    @classmethod
    def set_channel_id(cls, new_channel_id):
        instance = cls.get_instance()
        instance.channel_id = new_channel_id
        instance.save()
        return instance

class BaseMessage(models.Model):
    bot_configuration = models.ForeignKey(
        BotConfiguration,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="%(class)s_messages"
    )
    message_type = models.CharField(
        "Message Type",
        max_length=12,
        choices=[('text', 'Text'), ('photo', 'Photo'), ('video', 'Video'), ('video_notice', 'video_notice')]
    )
    text = models.TextField("Text", blank=True, null=True)
    media_file = models.FileField("Media File", upload_to='media_files', blank=True, null=True)
    scheduled_time = models.DateTimeField("Scheduled Time", default=timezone.now)
    is_send = models.BooleanField("Send", default=False)
    media_id = models.CharField("Media ID", max_length=512, blank=True, null=True)

    class Meta:
        abstract = True


from django.utils import timezone

class DelayMessage(models.Model):
    MESSAGE_TYPES = (
        ('text', 'Text'),
        ('photo', 'Photo'),
        ('video', 'Video'),
        ('video_notice', 'Video Notice'),
        ('media_group', 'Media Group')
    )

    bot_configuration = models.ForeignKey('bot.BotConfiguration', on_delete=models.CASCADE, default=1)
    message_type = models.CharField(max_length=50, choices=MESSAGE_TYPES)
    text = models.TextField(default="")
    scheduled_time = models.DateTimeField(default=timezone.now)
    media_file = models.FileField(
        "Media File",
        upload_to='media_files',
        blank=True,
        null=True,
        help_text="Upload media file for photo or video messages"
    )
    is_send = models.BooleanField(default=False)
    additional_media = models.FileField("Additional Media", upload_to='media_files', blank=True, null=True)
    media_id = models.CharField("Media ID", max_length=512, blank=True, null=True)

    class Meta:
        verbose_name = "Delay Message"
        verbose_name_plural = "Delay Messages"

    def clean(self):
        from django.core.exceptions import ValidationError
        # Очищаємо непотрібні дані при зміні типу
        if self.message_type != 'media_group':
            # Видаляємо всі пов'язані медіа файли
            self.post_medias.all().delete()
        if self.message_type == 'text':
            # Очищаємо поле media_file для текстових повідомлень
            self.media_file = None

    def __str__(self):
        return f"{self.message_type} message (delay) scheduled for {self.scheduled_time}"

    def save(self, *args, **kwargs):
        # Зберігаємо поточний час
        current_time = timezone.now()
        
        # Якщо повідомлення ще не відправлене і час відправки в майбутньому
        if not self.is_send and self.scheduled_time > current_time:
            # Зберігаємо об'єкт
            super().save(*args, **kwargs)
            
            # Додаємо невелику затримку для точності
            adjusted_time = self.scheduled_time + timezone.timedelta(seconds=1)
            
            # Плануємо відправку
            from .tasks import schedule_delay_message
            schedule_delay_message(self, adjusted_time)

class ScheduledMessage(models.Model):
    MESSAGE_TYPES = (
        ('text', 'Text'),
        ('photo', 'Photo'),
        ('video', 'Video'),
        ('video_notice', 'Video Notice'),
        ('media_group', 'Media Group')
    )

    bot_configuration = models.ForeignKey('bot.BotConfiguration', on_delete=models.CASCADE, default=1)
    message_type = models.CharField(max_length=50, choices=MESSAGE_TYPES)
    text = models.TextField(default="")
    scheduled_time = models.DateTimeField()
    media_file = models.FileField("Media File", upload_to='media_files', blank=True, null=True)
    is_send = models.BooleanField(default=False)
    additional_media = models.FileField("Additional Media", upload_to='media_files', blank=True, null=True)
    media_id = models.CharField("Media ID", max_length=512, blank=True, null=True)

    class Meta:
        verbose_name = "Scheduled Message"
        verbose_name_plural = "Scheduled Messages"

    def __str__(self):
        return f"{self.message_type} message scheduled for {self.scheduled_time}"

    def schedule(self):
        from .tasks import schedule_message
        schedule_message(self)

    def save(self, *args, **kwargs):
        if not self.is_send and self.scheduled_time > timezone.now():
            super().save(*args, **kwargs)  # Спочатку зберігаємо в БД
            self.schedule()  # Викликаємо планування

class TelegramUser(models.Model):
    chat_id = models.CharField(max_length=255, unique=True)
    username = models.CharField(max_length=255, blank=True, null=True)
    first_name = models.CharField(max_length=255, blank=True, null=True)
    last_name = models.CharField(max_length=255, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    language_code = models.CharField(max_length=10, blank=True, null=True)

    def __str__(self):
        return self.username or str(self.chat_id)
