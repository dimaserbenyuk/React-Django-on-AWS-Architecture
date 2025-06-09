#!/bin/bash
set -e

echo "⏳ Waiting for database to become available..."

# Проверка подключения к PostgreSQL
if [[ "$DATABASE_URL" == postgres* ]]; then
    until pg_isready -h "$DB_HOST" -p "$DB_PORT" -U "$DB_USER"; do
        echo "🔄 Waiting for PostgreSQL at $DB_HOST:$DB_PORT..."
        sleep 2
    done
    echo "✅ PostgreSQL is available"
fi

# Проверка файла SQLite, если он указан
if [[ "$DJANGO_DB_ENGINE" == "sqlite3" ]]; then
    DB_PATH="${DJANGO_DB_PATH:-/usr/src/app/db.sqlite3}"
    if [[ ! -f "$DB_PATH" ]]; then
        echo "⚠️ SQLite database not found at $DB_PATH. It will be created automatically."
    else
        echo "✅ SQLite database found at $DB_PATH"
    fi
fi

echo "🧩 Applying Django migrations..."
python manage.py migrate

echo "🔐 Creating superuser if not exists..."
python << END
import os
import django
from django.contrib.auth import get_user_model

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "backend.settings.dev")
django.setup()

User = get_user_model()
username = os.environ.get("DJANGO_SU_NAME")
email = os.environ.get("DJANGO_SU_EMAIL")
password = os.environ.get("DJANGO_SU_PASSWORD")

if username and password and not User.objects.filter(username=username).exists():
    User.objects.create_superuser(username=username, email=email, password=password)
    print(f"✅ Superuser '{username}' created")
else:
    print(f"⚠️ Superuser '{username}' already exists or env vars missing")
END


echo "🚀 Starting Django server..."
exec "$@"
