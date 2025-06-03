import os

# Default to development settings if DJANGO_SETTINGS_MODULE is not set
# This allows `backend.settings` to be importable by manage.py, wsgi.py and asgi.py
if not os.environ.get('DJANGO_SETTINGS_MODULE'):
    from .dev import *  # noqa: F401,F403
else:
    # When DJANGO_SETTINGS_MODULE points to another module like backend.settings.prod
    module = os.environ['DJANGO_SETTINGS_MODULE']
    if module != 'backend.settings':
        _mod = __import__(module, fromlist=['*'])
        for setting in dir(_mod):
            if setting.isupper():
                globals()[setting] = getattr(_mod, setting)
    else:
        from .dev import *  # noqa: F401,F403
