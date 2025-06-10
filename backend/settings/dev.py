from .base import *

DEBUG = True
ALLOWED_HOSTS = ['*']

CSRF_TRUSTED_ORIGINS = ['https://api.projectnext.uk/', 'https://projectnext.uk/']
CSRF_COOKIE_SAMESITE = 'Lax'
CSRF_COOKIE_PATH = "/"

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / "db.sqlite3",
    }
}

# CELERY_BROKER_URL = 'redis://localhost:6379/0'
# CELERY_RESULT_BACKEND = 'redis://localhost:6379/1'

PDF_OUTPUT_DIR = BASE_DIR / "pdf_output"

STATICFILES_LOCATION = "static"
MEDIAFILES_LOCATION = "media"
LOGOFILES_LOCATION = "invoices/logos"
PDFFILES_LOCATION = "invoices/pdfs"

CELERY_BROKER_URL = "sqs://"

BROKER_TRANSPORT_OPTIONS = {
    "region": os.getenv("AWS_SQS_REGION"),
    "is_secure": True,
    "visibility_timeout": 3600,
    "polling_interval": 10,
    "wait_time_seconds": 20,
    "predefined_queues": {
        "celery-prod-queue.fifo": {
            "url": "https://sqs.us-east-1.amazonaws.com/272509770066/celery-prod-queue.fifo"
        }
    }
}

AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
AWS_REGION = os.getenv("AWS_SQS_REGION", "us-east-1")
AWS_ACCOUNT_ID = "272509770066"
SQS_QUEUE_NAME = "celery-prod-queue.fifo"

# CELERY_BROKER_URL = "sqs://{access_key}:{secret_key}@sqs.us-east-1.amazonaws.com/272509770066/celery-prod-queue.fifo".format(
#     access_key=quote(AWS_ACCESS_KEY_ID, safe=""),
#     secret_key=quote(AWS_SECRET_ACCESS_KEY, safe=""),
# )