import os
from celery import Celery
from dotenv import load_dotenv

load_dotenv()  # Завантаження змінних середовища з файлу .env

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'moviereg.settings')
app = Celery('moviereg')

# Переконайтеся, що змінна середовища встановлена
redis_url = os.getenv('REDIS_URL')
if not redis_url:
    raise ValueError("REDIS_URL не налаштована у середовищі")

# Налаштування Celery для використання Redis як брокера та бекенду
ssl_options = {
    'ssl_cert_reqs': os.getenv('SSL_CERT_REQS', 'CERT_NONE')
}
app.conf.update(
    broker_url=redis_url,
    result_backend=redis_url,
    broker_use_ssl=ssl_options,
    redis_backend_use_ssl=ssl_options,
    broker_connection_retry_on_startup=True
)

app.autodiscover_tasks()
