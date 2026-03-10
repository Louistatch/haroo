#!/bin/bash

echo "=== Haroo Unified Startup ==="
echo "PORT=${PORT:-8000}"
echo "DJANGO_SETTINGS_MODULE=${DJANGO_SETTINGS_MODULE:-NOT SET}"
echo "DATABASE_URL set: $([ -n "$DATABASE_URL" ] && echo 'yes' || echo 'NO')"
echo "SECRET_KEY set: $([ -n "$SECRET_KEY" ] && echo 'yes' || echo 'NO')"

# Use default port if not set
export PORT=${PORT:-8000}

# Quick Python sanity check
python -c "
import os, sys
print('Python:', sys.version)
print('CWD:', os.getcwd())
print('Settings:', os.environ.get('DJANGO_SETTINGS_MODULE', 'NOT SET'))
try:
    import django
    django.setup()
    print('Django setup: OK')
except Exception as e:
    print(f'Django setup FAILED: {e}')
    import traceback
    traceback.print_exc()
" 2>&1

# Run migrations (don't block startup if DB is slow/unavailable)
echo "=== Running migrations ==="
timeout 20 python manage.py migrate --noinput 2>&1 || echo "WARNING: migrations failed or timed out"

echo "=== Starting gunicorn on 0.0.0.0:$PORT ==="
exec gunicorn haroo.wsgi:application \
    --bind 0.0.0.0:${PORT} \
    --workers 2 \
    --timeout 120 \
    --access-logfile - \
    --error-logfile - \
    --log-level info
