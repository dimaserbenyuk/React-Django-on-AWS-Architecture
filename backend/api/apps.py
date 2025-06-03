from django.apps import AppConfig

class ApiConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'backend.api'

    def ready(self):
        import backend.api.signals  # noqa: F401
