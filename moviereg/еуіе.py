from django.db import connections
from django.db.utils import OperationalError

db_conn = connections['default']
try:
    c = db_conn.cursor()
    print("Підключення успішне!")
except OperationalError:
    print("Не вдалося підключитися до бази даних.")
