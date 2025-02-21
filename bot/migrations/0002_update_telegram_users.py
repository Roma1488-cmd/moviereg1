from django.db import migrations

def update_telegram_users(apps, schema_editor):
    TelegramUser = apps.get_model('bot', 'TelegramUser')
    TelegramUser.objects.filter(is_active__isnull=True).update(is_active=True)

class Migration(migrations.Migration):
    dependencies = [
        ('bot', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(update_telegram_users),
    ]