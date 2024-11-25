from celery import Celery
import os

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'crypto_exchange.settings')

app = Celery('crypto_exchange')

# Load configuration from Django settings with CELERY_ prefix
app.config_from_object('django.conf:settings', namespace='CELERY')

# Explicitly set broker_connection_retry_on_startup to True
app.conf.broker_connection_retry_on_startup = True

# Autodiscover tasks from all registered Django app configs
app.autodiscover_tasks()
