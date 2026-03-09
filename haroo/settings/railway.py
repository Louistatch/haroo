"""
Configuration pour déploiement sur Railway.
Railway fournit PostgreSQL et Redis en addons.
Variables d'environnement injectées automatiquement par Railway.
"""

from .base import *
import os

DEBUG = False

# Railway injecte RAILWAY_PUBLIC_DOMAIN
RAILWAY_DOMAIN = os.environ.get('RAILWAY_PUBLIC_DOMAIN', '')
FRONTEND_DOMAIN = os.environ.get('FRONTEND_DOMAIN', '')

ALLOWED_HOSTS = env.list('ALLOWED_HOSTS', default=[
    RAILWAY_DOMAIN,
    'localhost',
])
# Filtrer les vides
ALLOWED_HOSTS = [h for h in ALLOWED_HOSTS if h]

# CORS — autoriser le frontend Vercel/Netlify
CORS_ALLOW_ALL_ORIGINS = False
CORS_ALLOWED_ORIGINS = env.list('CORS_ALLOWED_ORIGINS', default=[])
if FRONTEND_DOMAIN:
    for scheme in ['https://', 'http://']:
        origin = f"{scheme}{FRONTEND_DOMAIN}"
        if origin not in CORS_ALLOWED_ORIGINS:
            CORS_ALLOWED_ORIGINS.append(origin)

CORS_ALLOW_CREDENTIALS = True

CSRF_TRUSTED_ORIGINS = env.list('CSRF_TRUSTED_ORIGINS', default=[])
if RAILWAY_DOMAIN:
    CSRF_TRUSTED_ORIGINS.append(f"https://{RAILWAY_DOMAIN}")
if FRONTEND_DOMAIN:
    CSRF_TRUSTED_ORIGINS.append(f"https://{FRONTEND_DOMAIN}")

FRONTEND_URL = f"https://{FRONTEND_DOMAIN}" if FRONTEND_DOMAIN else env('FRONTEND_URL', default='')

# Database — Railway fournit DATABASE_URL
DATABASE_URL = os.environ.get('DATABASE_URL', '')
if DATABASE_URL:
    import dj_database_url
    DATABASES = {
        'default': dj_database_url.parse(DATABASE_URL, conn_max_age=600)
    }
    # Si PostGIS n'est pas dispo, utiliser PostgreSQL standard
    if DATABASES['default']['ENGINE'] == 'django.db.backends.postgresql':
        pass  # OK
    # Forcer PostGIS si disponible
    if env.bool('USE_POSTGIS', default=False):
        DATABASES['default']['ENGINE'] = 'django.contrib.gis.db.backends.postgis'
    else:
        # Désactiver GIS si pas PostGIS
        INSTALLED_APPS = [app for app in INSTALLED_APPS if app != 'django.contrib.gis']
else:
    # Fallback SQLite (ne devrait pas arriver sur Railway)
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }
    INSTALLED_APPS = [app for app in INSTALLED_APPS if app != 'django.contrib.gis']

# Redis — Railway fournit REDIS_URL
REDIS_URL = os.environ.get('REDIS_URL', '')
if REDIS_URL:
    CACHES = {
        'default': {
            'BACKEND': 'django_redis.cache.RedisCache',
            'LOCATION': REDIS_URL,
            'OPTIONS': {
                'CLIENT_CLASS': 'django_redis.client.DefaultClient',
            },
            'KEY_PREFIX': 'haroo',
            'TIMEOUT': 300,
        }
    }
    CELERY_BROKER_URL = REDIS_URL
    CELERY_RESULT_BACKEND = REDIS_URL
else:
    CACHES = {
        'default': {
            'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        }
    }

# SSL — Railway gère le TLS au niveau du proxy
SECURE_SSL_REDIRECT = False  # Railway proxy gère ça
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = 'Lax'
CSRF_COOKIE_HTTPONLY = True
CSRF_COOKIE_SAMESITE = 'Lax'

# Whitenoise pour les fichiers statiques
MIDDLEWARE.insert(1, 'whitenoise.middleware.WhiteNoiseMiddleware')
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'

# Email
EMAIL_BACKEND = env('EMAIL_BACKEND', default='django.core.mail.backends.console.EmailBackend')

# Sentry
SENTRY_DSN = env('SENTRY_DSN', default='')
if SENTRY_DSN:
    import sentry_sdk
    from sentry_sdk.integrations.django import DjangoIntegration
    sentry_sdk.init(
        dsn=SENTRY_DSN,
        integrations=[DjangoIntegration()],
        traces_sample_rate=0.1,
        send_default_pii=False,
        environment='production',
    )

# Stockage
USE_SUPABASE = env.bool('USE_SUPABASE', default=False)
if USE_SUPABASE:
    SUPABASE_URL = env('SUPABASE_URL', default='')
    SUPABASE_SERVICE_KEY = env('SUPABASE_SERVICE_KEY', default='')
    SUPABASE_ANON_KEY = env('SUPABASE_ANON_KEY', default='')
    SUPABASE_STORAGE_BUCKET = env('SUPABASE_STORAGE_BUCKET', default='documents')
    DEFAULT_FILE_STORAGE = 'apps.core.supabase_storage.SupabaseStorage'

# FedaPay
FEDAPAY_ENVIRONMENT = env('FEDAPAY_ENVIRONMENT', default='sandbox')

# Logging simplifié pour Railway (stdout)
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
