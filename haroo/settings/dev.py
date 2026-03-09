"""
Configuration de développement pour Haroo
"""

from .base import *

# Debug activé en développement
DEBUG = True

# Hosts autorisés en développement
ALLOWED_HOSTS = ['localhost', '127.0.0.1', '0.0.0.0', '.replit.dev', '.replit.app', '.repl.co']

# Base de données - SQLite pour dev local, PostgreSQL pour Replit
if env.bool('USE_SQLITE', default=False):
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }
else:
    # PostgreSQL Neon (sans PostGIS — backend standard)
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': env('DB_NAME', default='neondb'),
            'USER': env('DB_USER', default='neondb_owner'),
            'PASSWORD': env('DB_PASSWORD', default=''),
            'HOST': env('DB_HOST', default='localhost'),
            'PORT': env('DB_PORT', default='5432'),
            'OPTIONS': {
                'sslmode': env('DB_SSL', default='require'),
            },
        }
    }

# Désactiver django.contrib.gis (PostGIS non disponible sur Neon)
INSTALLED_APPS = [app for app in INSTALLED_APPS if app != 'django.contrib.gis']

# CORS permissif en développement
CORS_ALLOW_ALL_ORIGINS = True

# Email configuré via variables d'environnement (EMAIL_BACKEND, EMAIL_HOST, etc.)

# Désactiver HTTPS en développement
SESSION_COOKIE_SECURE = False
CSRF_COOKIE_SECURE = False

# Désactiver le cache en développement pour éviter les réponses périmées
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.dummy.DummyCache',
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
