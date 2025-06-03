from .base import *

DEBUG = True
ALLOWED_HOSTS = []

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

INSTALLED_APPS += ['backend.api']

# CELERY_BROKER_URL = 'redis://redis:6379/0' #docker

CELERY_BROKER_URL = 'redis://localhost:6379/0'

CELERY_RESULT_BACKEND = 'redis://localhost:6379/1'


LOGLEVEL = os.getenv('LOGLEVEL', 'INFO').upper()
