from __future__ import absolute_import
import os
from celery import Celery
from django.conf import settings
from celery.schedules import crontab

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'quickcheck.settings')

app = Celery('quickcheck')

app.config_from_object('django.conf:settings', namespace="CELERY")

app.autodiscover_tasks()