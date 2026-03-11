"""
Unified Railway deployment: Django API + React SPA served from one process.
React build output is served via WhiteNoise from staticfiles/frontend/.
API at /api/*, SPA catch-all for everything else.
"""

from .base import *
import os

DEBUG = False

# --- Hosts ---
RAILWAY_DOMAIN = os.environ.get('RAILWAY_PUBLIC_DOMAIN', 'haroo-production.up.railway.app')
ALLOWED_HOSTS = env.list('ALLOWED_HOSTS', default=[
    RAILWAY_DOMAIN, 'localhost', 'healthcheck.railway.app',
    'haroo.railway.internal', 'haroo-production.up.railway.app',
])
ALLOWED_HOSTS = [h for h in ALLOWED_HOSTS if h]

# --- CORS / CSRF ---
# Same-origin: frontend served from same domain, no CORS needed for API calls.
# Keep CORS config for external tools (Swagger, mobile app, etc.)
CORS_ALLOW_ALL_ORIGINS = False
CORS_ALLOWED_ORIGINS = env.list('CORS_ALLOWED_ORIGINS', default=[])
if RAILWAY_DOMAIN:
    origin = f"https://{RAILWAY_DOMAIN}"
    if origin not in CORS_ALLOWED_ORIGINS:
        CORS_ALLOWED_ORIGINS.append(origin)
CORS_ALLOW_CREDENTIALS = True

CSRF_TRUSTED_ORIGINS = env.list('CSRF_TRUSTED_ORIGINS', default=[])
if RAILWAY_DOMAIN:
    CSRF_TRUSTED_ORIGINS.append(f"https://{RAILWAY_DOMAIN}")

FRONTEND_URL = f"https://{RAILWAY_DOMAIN}" if RAILWAY_DOMAIN else env('FRONTEND_URL', default='')

# --- Database (Neon free tier via DATABASE_URL) ---
DATABASE_URL = os.environ.get('DATABASE_URL', '')
if DATABASE_URL:
    import dj_database_url
    DATABASES = {'default': dj_database_url.parse(DATABASE_URL, conn_max_age=600)}
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': env('DB_NAME', default='neondb'),
            'USER': env('DB_USER', default=''),
            'PASSWORD': env('DB_PASSWORD', default=''),
            'HOST': env('DB_HOST', default='localhost'),
            'PORT': env('DB_PORT', default='5432'),
            'OPTIONS': {'sslmode': env('DB_SSL', default='require')},
        }
    }

# Remove PostGIS and django_redis (not available/needed on Railway free tier)
INSTALLED_APPS = [app for app in INSTALLED_APPS if app not in ('django.contrib.gis', 'django_redis')]

# --- Cache: in-memory (no Redis needed) ---
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'haroo-cache',
    }
}
SESSION_ENGINE = 'django.contrib.sessions.backends.db'

# Override Redis URL to prevent any connection attempts
REDIS_URL = ''

# --- Celery disabled: tasks run inline (no Redis broker) ---
CELERY_TASK_ALWAYS_EAGER = True
CELERY_TASK_EAGER_PROPAGATES = True
CELERY_BROKER_URL = 'memory://'
CELERY_RESULT_BACKEND = 'cache+memory://'

# --- SSL / Security ---
SECURE_SSL_REDIRECT = False  # Railway proxy handles TLS
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = 'Lax'
CSRF_COOKIE_HTTPONLY = True
CSRF_COOKIE_SAMESITE = 'Lax'

# --- WhiteNoise: serve static + React SPA ---
MIDDLEWARE.insert(1, 'whitenoise.middleware.WhiteNoiseMiddleware')
STATICFILES_STORAGE = 'whitenoise.storage.CompressedStaticFilesStorage'

# SPA catch-all: serve React index.html for non-API 404s
MIDDLEWARE.append('apps.core.spa_middleware.SPAMiddleware')

# Django static files dirs (admin CSS, etc.)
STATICFILES_DIRS = []
_static_dir = BASE_DIR / 'static'
if _static_dir.is_dir():
    STATICFILES_DIRS.append(_static_dir)

# WhiteNoise root: serves files from frontend_dist/ at the site root.
# This means frontend_dist/index.html → /, frontend_dist/assets/* → /assets/*
# index.html won't be hashed by collectstatic since it's served via WHITENOISE_ROOT.
WHITENOISE_ROOT = BASE_DIR / 'frontend_dist'

# --- Storage ---
USE_SUPABASE = env.bool('USE_SUPABASE', default=False)
if USE_SUPABASE:
    SUPABASE_URL = env('SUPABASE_URL', default='')
    SUPABASE_SERVICE_KEY = env('SUPABASE_SERVICE_KEY', default='')
    SUPABASE_ANON_KEY = env('SUPABASE_ANON_KEY', default='')
    SUPABASE_STORAGE_BUCKET = env('SUPABASE_STORAGE_BUCKET', default='documents')
    DEFAULT_FILE_STORAGE = 'apps.core.supabase_storage.SupabaseStorage'

# --- FedaPay ---
FEDAPAY_ENVIRONMENT = env('FEDAPAY_ENVIRONMENT', default='sandbox')

# --- Email ---
EMAIL_BACKEND = env('EMAIL_BACKEND', default='django.core.mail.backends.console.EmailBackend')

# --- Sentry ---
SENTRY_DSN = env('SENTRY_DSN', default='')
if SENTRY_DSN and SENTRY_DSN.startswith('https://'):
    import sentry_sdk
    from sentry_sdk.integrations.django import DjangoIntegration
    sentry_sdk.init(
        dsn=SENTRY_DSN,
        integrations=[DjangoIntegration()],
        traces_sample_rate=0.1,
        send_default_pii=False,
        environment='production',
    )

# --- Logging: stdout only (Railway captures it) ---
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'simple': {'format': '%(levelname)s %(asctime)s %(name)s %(message)s'},
    },
    'handlers': {
        'console': {'class': 'logging.StreamHandler', 'formatter': 'simple'},
    },
    'root': {'handlers': ['console'], 'level': 'INFO'},
    'loggers': {
        'django': {'handlers': ['console'], 'level': 'INFO', 'propagate': False},
        'django.request': {'handlers': ['console'], 'level': 'ERROR', 'propagate': True},
        'haroo.requests': {'handlers': ['console'], 'level': 'INFO', 'propagate': False},
        'haroo.security': {'handlers': ['console'], 'level': 'WARNING', 'propagate': False},
    },
}
