# Generated by Django 4.2.3 on 2025-01-29 09:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bot', '0004_telegramuser_status_telegramuser_updated_at_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='telegramuser',
            name='language_code',
            field=models.CharField(default='unknown', max_length=10),
        ),
    ]
