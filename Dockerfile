
FROM debian:bookworm


WORKDIR /usr/src/app

RUN apt-get update && apt-get install -y \
    python3 python3-pip python3-dev python3-venv \
    build-essential gcc \
    libcairo2 libpango-1.0-0 libpangocairo-1.0-0 \
    libgdk-pixbuf-2.0-0 libffi-dev shared-mime-info \
    libxml2 libxslt1.1 libjpeg-dev libpq-dev \
    libglib2.0-0 fonts-liberation \
 && rm -rf /var/lib/apt/lists/*


COPY requirements.txt .

RUN python3 -m venv /opt/venv && \
    /opt/venv/bin/pip install --upgrade pip && \
    /opt/venv/bin/pip install -r requirements.txt

ENV PATH="/opt/venv/bin:$PATH"

COPY manage.py .
COPY backend/ backend/
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

RUN groupadd -g 1000 appgroup && \
    useradd -r -u 1000 -g appgroup appuser

RUN mkdir -p /usr/src/app/.cache/fontconfig && \
    chown -R 1000:1000 /usr/src/app

USER appuser

EXPOSE 8000

ENV DJANGO_SU_NAME=admin
ENV DJANGO_SU_EMAIL=admin@my.company
ENV DJANGO_SU_PASSWORD=dummy

ENV DJANGO_SETTINGS_MODULE=backend.settings.dev
ENV DJANGO_ENV=dev
ENV XDG_CACHE_HOME=/usr/src/app/.cache

ENTRYPOINT ["/entrypoint.sh"]
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
