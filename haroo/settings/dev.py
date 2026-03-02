"""
Configuration de développement pour Haroo
"""

from .base import *

# Debug activé en développement
DEBUG = True

# Hosts autorisés en développement
ALLOWED_HOSTS = ['localhost', '127.0.0.1', '0.0.0.0']

# Utiliser SQLite en dev (sans PostGIS) pour simplifier le développement
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}

# Désactiver django.contrib.gis en dev si GDAL n'est pas disponible
INSTALLED_APPS = [app for app in INSTALLED_APPS if app != 'django.contrib.gis']

# CORS permissif en développement
CORS_ALLOW_ALL_ORIGINS = True

# Email en console pour le développement
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'

# Désactiver HTTPS en développement
SESSION_COOKIE_SECURE = False
CSRF_COOKIE_SECURE = False

# Utiliser le cache en mémoire au lieu de Redis en développement
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'unique-snowflake',
    }
}

# Django Debug Toolbar (optional)
try:
    import debug_toolbar
    INSTALLED_APPS += [
        'debug_toolbar',
    ]
    MIDDLEWARE = [
        'debug_toolbar.middleware.DebugToolbarMiddleware',
    ] + MIDDLEWARE
    INTERNAL_IPS = [
        '127.0.0.1',
        'localhost',
    ]
except ImportError:
    pass

# Logging plus verbeux en développement
LOGGING['root']['level'] = 'DEBUG'
LOGGING['loggers']['django']['level'] = 'DEBUG'

# Désactiver la vérification de mot de passe en développement (optionnel)
# AUTH_PASSWORD_VALIDATORS = []
