#!/bin/bash
set -e

echo "=== Haroo Unified Startup ==="
echo "PORT=$PORT"
echo "DJANGO_SETTINGS_MODULE=$DJANGO_SETTINGS_MODULE"
echo "DATABASE_URL is set: $([ -n "$DATABASE_URL" ] && echo 'yes' || echo 'NO')"

# Run migrations (don't block startup if DB is waking up)
echo "=== Running migrations ==="
python manage.py migrate --noinput 2>&1 || echo "WARNING: migrations failed, continuing anyway"

echo "=== Starting gunicorn on port $PORT ==="
exec gunicorn haroo.wsgi:application \
    --bind 0.0.0.0:${PORT} \
    --workers 2 \
    --timeout 120 \
    --access-logfile - \
    --error-logfile -
