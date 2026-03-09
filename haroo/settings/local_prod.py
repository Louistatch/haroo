"""
Configuration "production locale" pour Haroo
Simule la production sans Docker, sans HTTPS, avec SQLite

Usage: DJANGO_SETTINGS_MODULE=haroo.settings.local_prod
"""

from .base import *

# Production-like: DEBUG off
DEBUG = False

# Hosts locaux
ALLOWED_HOSTS = env.list('ALLOWED_HOSTS', default=['localhost', '127.0.0.1', '0.0.0.0', '10.20.30.14'])

# CORS stricte (comme en prod)
CORS_ALLOW_ALL_ORIGINS = False
CORS_ALLOWED_ORIGINS = env.list('CORS_ALLOWED_ORIGINS', default=[
    'http://localhost:5173',
    'http://localhost:5000',
    'http://localhost:3000',
    'http://127.0.0.1:5173',
    'http://10.20.30.14:5173',
])

# CSRF Trusted Origins
CSRF_TRUSTED_ORIGINS = env.list('CSRF_TRUSTED_ORIGINS', default=[
    'http://localhost:5173',
    'http://localhost:5000',
    'http://localhost:8000',
    'http://127.0.0.1:5173',
    'http://127.0.0.1:8000',
    'http://10.20.30.14:5173',
    'http://10.20.30.14:8000',
])

# Base de données — SQLite pour local, PostGIS en vrai prod
if env.bool('USE_SQLITE', default=True):
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }
    # Désactiver PostGIS si SQLite
    INSTALLED_APPS = [app for app in INSTALLED_APPS if app != 'django.contrib.gis']

# Pas de SSL en local
SECURE_SSL_REDIRECT = False
SESSION_COOKIE_SECURE = False
CSRF_COOKIE_SECURE = False
SECURE_HSTS_SECONDS = 0

# Cookies
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = 'Lax'
CSRF_COOKIE_HTTPONLY = True
CSRF_COOKIE_SAMESITE = 'Lax'

# FedaPay sandbox
FEDAPAY_ENVIRONMENT = env('FEDAPAY_ENVIRONMENT', default='sandbox')

# Email en console
EMAIL_BACKEND = env(
    'EMAIL_BACKEND',
    default='django.core.mail.backends.console.EmailBackend'
)

# Sentry désactivé
SENTRY_DSN = ''

# Stockage — Supabase ou local
USE_S3 = env.bool('USE_S3', default=False)
USE_SUPABASE = env.bool('USE_SUPABASE', default=False)

if USE_SUPABASE:
    SUPABASE_URL = env('SUPABASE_URL', default='')
    SUPABASE_SERVICE_KEY = env('SUPABASE_SERVICE_KEY', default='')
    SUPABASE_ANON_KEY = env('SUPABASE_ANON_KEY', default='')
    SUPABASE_STORAGE_BUCKET = env('SUPABASE_STORAGE_BUCKET', default='documents')
    DEFAULT_FILE_STORAGE = 'apps.core.supabase_storage.SupabaseStorage'

# Cache — Redis si dispo, sinon local memory
try:
    import redis as _redis
    _r = _redis.Redis(host='localhost', port=6379, socket_connect_timeout=1)
    _r.ping()
    # Redis disponible, garder la config de base
except Exception:
    CACHES = {
        'default': {
            'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
            'LOCATION': 'haroo-local-prod',
        }
    }

# Logging
LOGGING['root']['level'] = 'INFO'

# Whitenoise pour servir les fichiers statiques sans nginx
MIDDLEWARE.insert(1, 'whitenoise.middleware.WhiteNoiseMiddleware')
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'
