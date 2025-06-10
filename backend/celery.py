import os
from celery import Celery
from django.conf import settings

app = Celery('backend')

# Настройки брокера
app.conf.broker_url = settings.CELERY_BROKER_URL
app.conf.broker_transport_options = settings.BROKER_TRANSPORT_OPTIONS

# Загрузка конфигурации Celery из Django settings
app.config_from_object('django.conf:settings', namespace='CELERY')

# Автоматический импорт задач
app.autodiscover_tasks()

# Планировщик beat
app.conf.beat_scheduler = 'django_celery_beat.schedulers:DatabaseScheduler'
