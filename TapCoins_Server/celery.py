from __future__ import absolute_import, unicode_literals
import os
from celery import Celery
from celery.schedules import crontab
from django.conf import settings

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'TapCoins_Server.settings')

app = Celery('TapCoins_Server')
app.conf.enable_utc = False

app.conf.update(timezone = 'America/New_York')

app.config_from_object(settings, namespace='CELERY')

# Celery Beat Settings
app.conf.beat_schedule = {
    'check-users-are-active-no-wallet': {
        'task': 'TapCoins_API.task.check_users_are_active_no_wallet',
        'schedule': crontab(minute='*/5'),
        # args: (2,)
    }
}

app.autodiscover_tasks()

@app.task(bind=True)
def debug_task(self):
    print(f'Request: {self.request!r}')