
FROM debian:bookworm


WORKDIR /usr/src/app

RUN apt-get update && apt-get install -y \
    python3 python3-pip python3-dev python3-venv \
    build-essential gcc \
    libcairo2 libpango-1.0-0 libpangocairo-1.0-0 \
    libgdk-pixbuf-2.0-0 libffi-dev shared-mime-info \
    libxml2 libxslt1.1 libjpeg-dev libpq-dev \
    libglib2.0-0 libgobject-2.0-dev fonts-liberation \
 && rm -rf /var/lib/apt/lists/*


COPY requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt

COPY manage.py .
COPY backend/ backend/

RUN groupadd -g 1000 appgroup && \
    useradd -r -u 1000 -g appgroup appuser
USER 1000:1000

EXPOSE 8000

ENV DJANGO_SETTINGS_MODULE=backend.settings.prod
ENV DJANGO_ENV=prod

# CMD [ "sleep","30000" ]
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]

