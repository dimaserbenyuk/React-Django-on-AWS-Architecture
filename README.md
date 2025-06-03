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

```shell
DJANGO_SETTINGS_MODULE=backend.settings.dev celery -A backend worker --loglevel=info
```
 
```shell
 -------------- celery@MacBook-Pro-Dima.local v5.5.3 (immunity)
--- ***** ----- 
-- ******* ---- macOS-15.5-arm64-arm-64bit-Mach-O 2025-06-03 13:05:02
- *** --- * --- 
- ** ---------- [config]
- ** ---------- .> app:         backend:0x1047e3cb0
- ** ---------- .> transport:   redis://localhost:6379/0
- ** ---------- .> results:     disabled://
- *** --- * --- .> concurrency: 8 (prefork)
-- ******* ---- .> task events: OFF (enable -E to monitor tasks in this worker)
--- ***** ----- 
 -------------- [queues]
                .> celery           exchange=celery(direct) key=celery
                

[tasks]
  . backend.api.tasks.generate_pdf

[2025-06-03 13:05:03,122: INFO/MainProcess] Connected to redis://localhost:6379/0
[2025-06-03 13:05:03,124: INFO/MainProcess] mingle: searching for neighbors
[2025-06-03 13:05:04,132: INFO/MainProcess] mingle: all alone
[2025-06-03 13:05:04,159: INFO/MainProcess] celery@MacBook-Pro-Dima.local ready.
```