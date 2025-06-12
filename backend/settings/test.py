from .base import *
import os

DEBUG = True
SECRET_KEY = os.getenv("SECRET_KEY", "insecure-test-secret")

ALLOWED_HOSTS = ["*"]

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.getenv('POSTGRES_DB', 'test_db'),
        'USER': os.getenv('POSTGRES_USER', 'test_user'),
        'PASSWORD': os.getenv('POSTGRES_PASSWORD', 'test_password'),
        'HOST': os.getenv('POSTGRES_HOST', 'localhost'),
        'PORT': os.getenv('POSTGRES_PORT', '5432'),
    }
}

AWS_ACCESS_KEY_ID = ""
AWS_SECRET_ACCESS_KEY = ""
AWS_REGION = ""
AWS_ACCOUNT_ID = ""
SQS_QUEUE_NAME = ""

CELERY_BROKER_URL = "memory://"
CELERY_RESULT_BACKEND = None
CELERY_TASK_QUEUES = None
CELERY_BEAT_SCHEDULER = 'django_celery_beat.schedulers:DatabaseScheduler'

CSRF_TRUSTED_ORIGINS = []
CORS_ALLOWED_ORIGINS = ["http://localhost:3000"]

STATICFILES_LOCATION = "static"
MEDIAFILES_LOCATION = "media"
LOGOFILES_LOCATION = "invoices/logos"
PDFFILES_LOCATION = "invoices/pdfs"
PDF_OUTPUT_DIR = BASE_DIR / "pdf_output"
