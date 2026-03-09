"""
Configuration de production pour Haroo
"""

from .base import *

# Debug TOUJOURS désactivé en production
DEBUG = False

# Hosts autorisés (OBLIGATOIRE en production)
ALLOWED_HOSTS = env.list('ALLOWED_HOSTS', default=[])

if not ALLOWED_HOSTS:
    raise ValueError("ALLOWED_HOSTS doit être défini en production")

# CORS stricte en production
CORS_ALLOW_ALL_ORIGINS = False
CORS_ALLOWED_ORIGINS = env.list('CORS_ALLOWED_ORIGINS', default=[])

# CSRF Trusted Origins (obligatoire Django 4.x pour POST cross-origin via HTTPS)
CSRF_TRUSTED_ORIGINS = env.list('CSRF_TRUSTED_ORIGINS', default=CORS_ALLOWED_ORIGINS)

# Email réel en production
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'

# Sécurité maximale en production
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_SSL_REDIRECT = True
SECURE_HSTS_SECONDS = 31536000  # 1 an
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

# Configuration TLS 1.3
# Note: La configuration TLS se fait au niveau du serveur web (Nginx/Apache)
# Ces paramètres Django assurent que l'application exige HTTPS
SECURE_SSL_HOST = None  # Utiliser le même host
SECURE_REDIRECT_EXEMPT = []  # Pas d'exemptions

# Cookies sécurisés
SESSION_COOKIE_SECURE = True
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = 'Strict'
CSRF_COOKIE_SECURE = True
CSRF_COOKIE_HTTPONLY = True
CSRF_COOKIE_SAMESITE = 'Strict'

# ============================================
# TASK-7.1: Sentry Monitoring
# ============================================

SENTRY_DSN = env('SENTRY_DSN', default='')

if SENTRY_DSN:
    import sentry_sdk
    from sentry_sdk.integrations.django import DjangoIntegration
    from sentry_sdk.integrations.celery import CeleryIntegration
    from sentry_sdk.integrations.redis import RedisIntegration
    from sentry_sdk.integrations.logging import LoggingIntegration
    import logging as _logging

    # Données sensibles à filtrer dans les events Sentry
    SENTRY_SENSITIVE_FIELDS = [
        'password', 'secret', 'token', 'access_token', 'refresh_token',
        'authorization', 'cookie', 'csrf', 'api_key', 'apikey',
        'phone_number', 'phone', 'email', 'ssn', 'credit_card',
        'two_factor_secret', 'backup_codes', 'encryption_key',
        'sentry_dsn', 'aws_secret', 'fedapay',
    ]

    def filter_sensitive_data(event, hint):
        """
        Filtre les données sensibles avant envoi à Sentry.
        Supprime mots de passe, tokens, PII des events.
        """
        # Filtrer les headers de requête
        if 'request' in event:
            req = event['request']
            if 'headers' in req:
                for key in list(req['headers'].keys()):
                    if any(s in key.lower() for s in SENTRY_SENSITIVE_FIELDS):
                        req['headers'][key] = '[Filtered]'
            if 'cookies' in req:
                req['cookies'] = '[Filtered]'
            # Filtrer le body
            if 'data' in req and isinstance(req['data'], dict):
                for key in list(req['data'].keys()):
                    if any(s in key.lower() for s in SENTRY_SENSITIVE_FIELDS):
                        req['data'][key] = '[Filtered]'

        # Filtrer les variables locales dans les frames
        if 'exception' in event:
            for exc in event['exception'].get('values', []):
                for frame in exc.get('stacktrace', {}).get('frames', []):
                    if 'vars' in frame and isinstance(frame['vars'], dict):
                        for key in list(frame['vars'].keys()):
                            if any(s in key.lower() for s in SENTRY_SENSITIVE_FIELDS):
                                frame['vars'][key] = '[Filtered]'

        # Filtrer les tags et extra
        for section in ('tags', 'extra'):
            if section in event and isinstance(event[section], dict):
                for key in list(event[section].keys()):
                    if any(s in key.lower() for s in SENTRY_SENSITIVE_FIELDS):
                        event[section][key] = '[Filtered]'

        return event

    sentry_sdk.init(
        dsn=SENTRY_DSN,
        integrations=[
            DjangoIntegration(
                transaction_style='url',
                middleware_spans=True,
            ),
            CeleryIntegration(monitor_beat_tasks=True),
            RedisIntegration(),
            LoggingIntegration(
                level=_logging.WARNING,
                event_level=_logging.ERROR,
            ),
        ],
        # Performance monitoring
        traces_sample_rate=float(env('SENTRY_TRACES_SAMPLE_RATE', default='0.1')),
        profiles_sample_rate=float(env('SENTRY_PROFILES_SAMPLE_RATE', default='0.1')),
        # Sécurité
        send_default_pii=False,
        before_send=filter_sensitive_data,
        # Environnement
        environment=env('SENTRY_ENVIRONMENT', default='production'),
        release=env('SENTRY_RELEASE', default='haroo@1.0.0'),
        # Ignorer certaines erreurs courantes non critiques
        ignore_errors=[
            KeyboardInterrupt,
            ConnectionResetError,
            BrokenPipeError,
        ],
    )

# Fedapay en mode production
FEDAPAY_ENVIRONMENT = 'live'

# Stockage cloud en production
USE_S3 = env.bool('USE_S3', default=False)
USE_SUPABASE = env.bool('USE_SUPABASE', default=False)

if USE_SUPABASE:
    SUPABASE_URL = env('SUPABASE_URL')
    SUPABASE_SERVICE_KEY = env('SUPABASE_SERVICE_KEY')
    SUPABASE_STORAGE_BUCKET = env('SUPABASE_STORAGE_BUCKET', default='documents')
    DEFAULT_FILE_STORAGE = 'apps.core.supabase_storage.SupabaseStorage'

elif USE_S3:
    # Configuration AWS S3
    AWS_ACCESS_KEY_ID = env('AWS_ACCESS_KEY_ID')
    AWS_SECRET_ACCESS_KEY = env('AWS_SECRET_ACCESS_KEY')
    AWS_STORAGE_BUCKET_NAME = env('AWS_STORAGE_BUCKET_NAME')
    AWS_S3_REGION_NAME = env('AWS_S3_REGION_NAME', default='eu-west-1')
    AWS_S3_CUSTOM_DOMAIN = f'{AWS_STORAGE_BUCKET_NAME}.s3.amazonaws.com'
    AWS_S3_OBJECT_PARAMETERS = {
        'CacheControl': 'max-age=86400',
    }
    AWS_DEFAULT_ACL = 'private'
    AWS_S3_FILE_OVERWRITE = False
    
    # Utiliser S3 pour les fichiers statiques et media
    DEFAULT_FILE_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'
    STATICFILES_STORAGE = 'storages.backends.s3boto3.S3StaticStorage'
    
    STATIC_URL = f'https://{AWS_S3_CUSTOM_DOMAIN}/static/'
    MEDIA_URL = f'https://{AWS_S3_CUSTOM_DOMAIN}/media/'

else:
    raise ValueError("En production, USE_S3=True ou USE_SUPABASE=True est obligatoire")
