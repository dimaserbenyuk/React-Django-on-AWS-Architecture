FROM python:3.13-slim

# Set env early to use non-interactive apt
ENV DEBIAN_FRONTEND=noninteractive \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    DJANGO_ENV=dev \
    DJANGO_SETTINGS_MODULE=backend.settings.dev \
    XDG_CACHE_HOME=/usr/src/app/.cache

WORKDIR /usr/src/app

# Install system dependencies in a single layer
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    gcc \
    libcairo2 \
    libpango-1.0-0 \
    libpangocairo-1.0-0 \
    libgdk-pixbuf-2.0-0 \
    libffi-dev \
    shared-mime-info \
    libxml2 \
    libxslt1.1 \
    libjpeg-dev \
    libglib2.0-0 \
    fonts-liberation \
 && apt-get clean && rm -rf /var/lib/apt/lists/*

# Install Python dependencies into a virtualenv
COPY requirements.txt .
RUN python3 -m venv /opt/venv && \
    . /opt/venv/bin/activate && \
    pip install --upgrade pip && \
    pip install -r requirements.txt

ENV PATH="/opt/venv/bin:$PATH"

# Copy source code
COPY manage.py .
COPY backend/ backend/
COPY entrypoint.sh /entrypoint.sh

RUN chmod +x /entrypoint.sh && \
    mkdir -p /usr/src/app/.cache/fontconfig && \
    groupadd -r appgroup -g 1000 && \
    useradd -r -u 1000 -g appgroup appuser && \
    chown -R appuser:appgroup /usr/src/app

USER appuser

EXPOSE 8000

ENTRYPOINT ["/entrypoint.sh"]

# CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]

# CMD ["gunicorn", "backend.wsgi:application", "--bind", "0.0.0.0:8000", "--workers=3", "--threads=2", "--timeout=120", "--log-level=debug"]


# DJANGO_SETTINGS_MODULE=backend.settings.dev DJANGO_ENV=dev gunicorn backend.wsgi:application --bind 0.0.0.0:8000 --workers=2 --reload --log-level=debug
