from urllib.parse import quote
from .base import *
import os

DEBUG = True

ALLOWED_HOSTS = os.getenv("ALLOWED_HOSTS", "*").split(",")

CSRF_TRUSTED_ORIGINS = os.getenv("CSRF_TRUSTED_ORIGINS", "https://api.projectnext.uk").split(",")
CSRF_COOKIE_SAMESITE = "Lax"
CSRF_COOKIE_PATH = "/"

CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "https://app.projectnext.uk",
]

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}

PDF_OUTPUT_DIR = BASE_DIR / "pdf_output"

STATICFILES_LOCATION = "static"
MEDIAFILES_LOCATION = "media"
LOGOFILES_LOCATION = "invoices/logos"
PDFFILES_LOCATION = "invoices/pdfs"

# AWS credentials from env
AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
AWS_REGION = os.getenv("AWS_SQS_REGION", "us-east-1")

CELERY_BROKER_URL = f"sqs://{quote(AWS_ACCESS_KEY_ID)}:{quote(AWS_SECRET_ACCESS_KEY)}@"

BROKER_TRANSPORT_OPTIONS = {
    "region": AWS_REGION,
    "is_secure": True,
    "visibility_timeout": 3600,
    "wait_time_seconds": 20,
    "polling_interval": 10,
    "predefined_queues": {
        "celery-prod-queue.fifo": {
            "url": "https://sqs.us-east-1.amazonaws.com/272509770066/celery-prod-queue.fifo"
        }
    },
}

CELERY_TASK_DEFAULT_QUEUE = "celery-prod-queue.fifo"
CELERY_TASK_QUEUES = None  # если используется, должен соответствовать predefined_queues
