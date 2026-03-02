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

# Logging en production
LOGGING['root']['level'] = 'WARNING'
LOGGING['loggers']['django']['level'] = 'WARNING'

# Ajouter Sentry pour le monitoring en production
SENTRY_DSN = env('SENTRY_DSN', default='')
if SENTRY_DSN:
    import sentry_sdk
    from sentry_sdk.integrations.django import DjangoIntegration
    
    sentry_sdk.init(
        dsn=SENTRY_DSN,
        integrations=[DjangoIntegration()],
        traces_sample_rate=0.1,
        send_default_pii=False,
    )

# Fedapay en mode production
FEDAPAY_ENVIRONMENT = 'live'

# Stockage cloud obligatoire en production
USE_S3 = env.bool('USE_S3', default=True)

if USE_S3:
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
