from celery import Celery
import os

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'crypto_exchange.settings')

app = Celery('crypto_exchange')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks() 