import os
from celery import Celery
from dotenv import load_dotenv

load_dotenv()  # Завантаження змінних середовища з файлу .env

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'moviereg.settings')
app = Celery('moviereg')

# Переконайтеся, що змінна середовища налаштована
rabbitmq_url = os.getenv('RABBITMQ_URL')
postgres_url = os.getenv('DATABASE_URL')

if not rabbitmq_url:
    raise ValueError("RABBITMQ_URL не налаштована у середовищі")

if not postgres_url:
    raise ValueError("DATABASE_URL не налаштована у середовищі")

# Налаштування Celery для використання RabbitMQ як брокера та PostgreSQL як бекенду
app.conf.update(
    broker_url=rabbitmq_url,
    result_backend=postgres_url,
    broker_connection_retry_on_startup=True
)

app.autodiscover_tasks()
