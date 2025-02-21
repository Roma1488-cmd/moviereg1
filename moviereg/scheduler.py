from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.date import DateTrigger
from django_apscheduler.jobstores import DjangoJobStore, register_events, register_job

import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'moviereg.settings')
django.setup()

scheduler = BackgroundScheduler()
scheduler.add_jobstore(DjangoJobStore(), "default")

register_events(scheduler)
scheduler.start()

@scheduler.scheduled_job("interval", minutes=1, id="my_job", replace_existing=True)
def test_job():
    print("The job is running!")
