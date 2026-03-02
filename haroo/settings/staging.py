"""
Configuration de staging pour Haroo
"""

from .base import *

# Debug désactivé en staging
DEBUG = False

# Hosts autorisés (à configurer via variables d'environnement)
ALLOWED_HOSTS = env.list('ALLOWED_HOSTS', default=[])

# CORS stricte en staging
CORS_ALLOW_ALL_ORIGINS = False
CORS_ALLOWED_ORIGINS = env.list('CORS_ALLOWED_ORIGINS', default=[])

# Email réel en staging
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'

# Sécurité renforcée
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_SSL_REDIRECT = True
SECURE_HSTS_SECONDS = 31536000  # 1 an
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True

# Logging en staging
LOGGING['root']['level'] = 'INFO'
LOGGING['loggers']['django']['level'] = 'INFO'

# Fedapay en mode sandbox pour staging
FEDAPAY_ENVIRONMENT = 'sandbox'
