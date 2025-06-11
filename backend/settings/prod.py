from .base import *
from urllib.parse import quote

DEBUG = False
ALLOWED_HOSTS = os.getenv("ALLOWED_HOSTS", "*").split(",")

CSRF_TRUSTED_ORIGINS = os.getenv("CSRF_TRUSTED_ORIGINS", "https://api.projectnext.uk").split(",")
CSRF_COOKIE_SAMESITE = "Lax"
CSRF_COOKIE_PATH = "/"

CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "https://app.projectnext.uk",
]

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.getenv('POSTGRES_DB', 'postgres'),
        'USER': os.getenv('POSTGRES_USER', 'postgres'),
        'PASSWORD': os.getenv('POSTGRES_PASSWORD', 'postgres'),
        'HOST': os.getenv('POSTGRES_HOST', 'postgres'),
        'PORT': os.getenv('POSTGRES_PORT', '5432'),
    }
}

PDF_OUTPUT_DIR = BASE_DIR / "pdf_output"

STATICFILES_LOCATION = "static"
MEDIAFILES_LOCATION = "media"
LOGOFILES_LOCATION = "invoices/logos"
PDFFILES_LOCATION = "invoices/pdfs"

AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID", "")
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY", "")
AWS_REGION = os.getenv("AWS_SQS_REGION", "us-east-1")
AWS_ACCOUNT_ID = os.getenv("AWS_ACCOUNT_ID", "272509770066")
SQS_QUEUE_NAME = os.getenv("SQS_QUEUE_NAME", "celery-prod-queue.fifo")

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

CELERY_TASK_DEFAULT_QUEUE = 'celery-prod-queue.fifo'
CELERY_TASK_DEFAULT_EXCHANGE_TYPE = 'direct'
CELERY_TASK_DEFAULT_ROUTING_KEY = 'celery-prod-queue.fifo'
CELERY_TASK_QUEUES = None  # если используется, должен соответствовать predefined_queues
CELERY_RESULT_BACKEND ='disabled://'

CELERY_BROKER_URL = "sqs://{access_key}:{secret_key}@sqs.us-east-1.amazonaws.com/{account_id}/{queue}".format(
    access_key=quote(AWS_ACCESS_KEY_ID or "", safe=""),
    secret_key=quote(AWS_SECRET_ACCESS_KEY or "", safe=""),
    account_id=AWS_ACCOUNT_ID,
    queue=SQS_QUEUE_NAME,
)
# Celery с SQS (IAM Role — без ключей)
# CELERY_BROKER_URL = "sqs://"

# CELERY_BROKER_URL = os.getenv('CELERY_BROKER_URL', 'redis://redis:6379/0')

# BROKER_TRANSPORT_OPTIONS = {
#     'region': os.getenv('AWS_REGION', 'us-east-1'),
#     'visibility_timeout': 3600,             # сколько сек скрывать сообщение после получения
#     'polling_interval': 10,                 # опрос SQS (чем меньше — тем быстрее)
#     'queue_name_prefix': os.getenv('CELERY_QUEUE_PREFIX', ''),  # если нужно
#     'wait_time_seconds': 20,                # long polling
#     'is_secure': True,
#     'predefined_queues': {
#         'celery-prod-queue.fifo': {
#             'url': 'https://sqs.us-east-1.amazonaws.com/272509770066/celery-prod-queue.fifo'
#         }
#     },
# }


# IAM Role будет использоваться автоматически в ECS (если не заданы ACCESS_KEY)
# AWS_ACCESS_KEY_ID = None
# AWS_SECRET_ACCESS_KEY = None

CELERY_RESULT_BACKEND = None


CELERY_BEAT_SCHEDULER = 'django_celery_beat.schedulers:DatabaseScheduler'


# from urllib.parse import quote
# import os


# AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
# AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
# AWS_REGION = os.getenv("AWS_SQS_REGION", "us-east-1")
# AWS_ACCOUNT_ID = "272509770066"
# SQS_QUEUE_NAME = "celery-prod-queue.fifo"



# BROKER_TRANSPORT_OPTIONS = {
#     "region": "us-east-1",
#     "visibility_timeout": 3600,
#     "polling_interval": 10,
#     "wait_time_seconds": 20,
#     "is_secure": True,
# }

# BROKER_TRANSPORT_OPTIONS = {
#     "region": AWS_REGION,
#     "is_secure": True,
#     "visibility_timeout": 3600,
#     "polling_interval": 10,
#     "wait_time_seconds": 20,
#     "is_secure": True,
#     "predefined_queues": {
#         SQS_QUEUE_NAME: {
#             "url": f"https://sqs.{AWS_REGION}.amazonaws.com/{AWS_ACCOUNT_ID}/{SQS_QUEUE_NAME}"
#         }
#     },
# }

# CELERY_BROKER_URL = "sqs://{access_key}:{secret_key}@sqs.us-east-1.amazonaws.com/272509770066/celery-prod-queue.fifo".format(
#     access_key=quote(AWS_ACCESS_KEY_ID, safe=""),
#     secret_key=quote(AWS_SECRET_ACCESS_KEY, safe=""),
# )

# CELERY_BROKER_URL = "sqs://"

# BROKER_TRANSPORT_OPTIONS = {
#     "region": os.getenv("AWS_REGION"),
#     "is_secure": True,
#     "visibility_timeout": 3600,
#     "polling_interval": 10,
#     "wait_time_seconds": 20,
#     "predefined_queues": {
#         "celery-prod-queue.fifo": {
#             "url": "https://sqs.us-east-1.amazonaws.com/272509770066/celery-prod-queue.fifo"
#         }
#     }
# }