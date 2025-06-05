from django.conf import settings
from storages.backends.s3boto3 import S3Boto3Storage


class StaticStorage(S3Boto3Storage):
    location = settings.STATICFILES_LOCATION
    default_acl = 'public-read'
    file_overwrite = True
    querystring_auth = False


class MediaStorage(S3Boto3Storage):
    location = settings.MEDIAFILES_LOCATION
    default_acl = 'private'
    file_overwrite = False
    querystring_auth = True


class LogoStorage(S3Boto3Storage):
    location = settings.LOGOFILES_LOCATION
    default_acl = 'public-read'
    file_overwrite = False
    querystring_auth = False


class PDFStorage(S3Boto3Storage):
    location = settings.PDFFILES_LOCATION
    default_acl = 'public-read'
    file_overwrite = False
    querystring_auth = True
    custom_domain = False
