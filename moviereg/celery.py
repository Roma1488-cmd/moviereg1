import os
from celery import Celery
from dotenv import load_dotenv
import ssl

load_dotenv()  # Завантаження змінних середовища з файлу .env

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'moviereg.settings')
app = Celery('moviereg')

# Переконайтеся, що змінна середовища встановлена
redis_url = os.getenv('REDIS_URL')
if not redis_url:
    raise ValueError("REDIS_URL не налаштована у середовищі")

# Налаштування Celery для використання Redis як брокера та бекенду з параметрами SSL
ssl_context = ssl.create_default_context()
ssl_context.check_hostname = False
ssl_context.verify_mode = ssl.CERT_NONE

ssl_options = {
    'ssl_cert_reqs': ssl.CERT_NONE
}
app.conf.update(
    broker_url=redis_url,
    result_backend=redis_url,
    broker_use_ssl={
        'ssl_cert_reqs': ssl.CERT_NONE
    },
    redis_backend_use_ssl={
        'ssl_cert_reqs': ssl.CERT_NONE
    },
    broker_connection_retry_on_startup=True
)

app.autodiscover_tasks()
