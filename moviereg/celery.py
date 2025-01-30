import os
from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'moviereg.settings')
app = Celery('moviereg')

# Налаштування Celery для використання Redis як брокера та бекенду
app.conf.update(
    broker_url=os.getenv('REDIS_URL'),
    result_backend=os.getenv('REDIS_URL')
)

app.autodiscover_tasks()
