# React-Django-on-AWS-Architecture
React+Django-on-AWS-Architecture

SQLite for development (DEBUG=True)

PostgreSQL (RDS) for production (DEBUG=False)

Readable files: settings/base.py, settings/dev.py, settings/prod.py

Local:

```shell
DJANGO_SETTINGS_MODULE=backend.settings.dev python manage.py runserver
```

In production (ECS):

```shell
DJANGO_SETTINGS_MODULE=backend.settings.prod gunicorn backend.wsgi:application
```

Or in Docker:

```shell
ENV DJANGO_SETTINGS_MODULE=backend.settings.prod
```

logging

### An example in any views.py, tasks.py, utils.py

```python
import logging

logger = logging.getLogger('app')

def my_view(request):
    logger.info("User visited the dashboard")
    logger.warning("Low disk space")
    logger.error("Something went wrong", exc_info=True)
    return ...
```

Add exc_info=True to see traceback in the logs:

```python
logger.error(“Database error”, exc_info=True)
```

```shell
LOGLEVEL=INFO python manage.py runserver
LOGLEVEL=DEBUG gunicorn backend.wsgi:application
```

example

```text
[03/Jun/2025 12:22:03] "GET /admin/auth/ HTTP/1.1" 302 0
[03/Jun/2025 12:22:03] "GET /admin/login/?next=/admin/auth/ HTTP/1.1" 200 4183
[03/Jun/2025 12:22:03] "GET /static/admin/css/base.css HTTP/1.1" 304 0
[03/Jun/2025 12:22:03] "GET /static/admin/js/theme.js HTTP/1.1" 304 0
[03/Jun/2025 12:22:03] "GET /static/admin/css/nav_sidebar.css HTTP/1.1" 304 0
[03/Jun/2025 12:22:03] "GET /static/admin/css/dark_mode.css HTTP/1.1" 304 0
[03/Jun/2025 12:22:03] "GET /static/admin/css/responsive.css HTTP/1.1" 304 0
[03/Jun/2025 12:22:03] "GET /static/admin/css/login.css HTTP/1.1" 304 0
[03/Jun/2025 12:22:03] "GET /static/admin/js/nav_sidebar.js HTTP/1.1" 304 0
[03/Jun/2025 12:22:04] "GET /admin/login/?next=/admin/auth/ HTTP/1.1" 200 4183
[03/Jun/2025 12:22:05] "GET /admin/login/?next=/admin/auth/ HTTP/1.1" 200 4183
[03/Jun/2025 12:22:05] "GET /admin/login/?next=/admin/auth/ HTTP/1.1" 200 4183
[03/Jun/2025 12:22:05] "GET /admin/login/?next=/admin/auth/ HTTP/1.1" 200 4183
```