"""
Configuration de base Django pour Haroo - Plateforme Agricole Intelligente du Togo
"""

import os
from pathlib import Path
import environ

# Initialiser environ
env = environ.Env(
    DEBUG=(bool, False)
)

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent.parent

# Lire le fichier .env
environ.Env.read_env(os.path.join(BASE_DIR, '.env'))

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = env('SECRET_KEY', default='django-insecure-change-this-in-production')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = env('DEBUG', default=False)

ALLOWED_HOSTS = env.list('ALLOWED_HOSTS', default=[])


# Application definition

DJANGO_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.gis',  # PostGIS support
]

THIRD_PARTY_APPS = [
    'rest_framework',
    'corsheaders',
    'django_redis',
    'storages',
    'django_filters',
]

LOCAL_APPS = [
    'apps.core',
    'apps.users',
    'apps.locations',
    'apps.documents',
    'apps.payments',
    'apps.missions',
    'apps.institutional',
    'apps.compliance',
    'apps.ratings',
]

INSTALLED_APPS = DJANGO_APPS + THIRD_PARTY_APPS + LOCAL_APPS

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.locale.LocaleMiddleware',  # i18n support
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'apps.users.middleware.RateLimitMiddleware',
    'apps.users.middleware.SecurityHeadersMiddleware',
    'apps.users.middleware.SessionActivityMiddleware',  # Exigences: 40.1
]

ROOT_URLCONF = 'haroo.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'haroo.wsgi.application'


# Database
# https://docs.djangoproject.com/en/4.2/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.contrib.gis.db.backends.postgis',
        'NAME': env('DB_NAME', default='haroo_db'),
        'USER': env('DB_USER', default='haroo_user'),
        'PASSWORD': env('DB_PASSWORD', default=''),
        'HOST': env('DB_HOST', default='localhost'),
        'PORT': env('DB_PORT', default='5432'),
    }
}


# Password validation
# https://docs.djangoproject.com/en/4.2/ref/settings/#auth-password-validators

# Password Hashers - Utiliser bcrypt comme hasher principal
PASSWORD_HASHERS = [
    'django.contrib.auth.hashers.BCryptSHA256PasswordHasher',  # bcrypt avec SHA256
    'django.contrib.auth.hashers.PBKDF2PasswordHasher',  # Fallback
    'django.contrib.auth.hashers.PBKDF2SHA1PasswordHasher',
]

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
        'OPTIONS': {
            'min_length': 8,
        }
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
    {
        'NAME': 'apps.users.validators.CustomPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/4.2/topics/i18n/

LANGUAGE_CODE = 'fr'  # Français par défaut

# Langues supportées
LANGUAGES = [
    ('fr', 'Français'),
    # Langues futures pour extension
    # ('ee', 'Ewe'),
    # ('kbp', 'Kabyè'),
]

# Répertoires de traduction
LOCALE_PATHS = [
    BASE_DIR / 'locale',
]

TIME_ZONE = 'Africa/Lome'

USE_I18N = True

USE_L10N = True

USE_TZ = True

# Utiliser les formats personnalisés
FORMAT_MODULE_PATH = [
    'haroo.formats',
]

# Utiliser les formats personnalisés pour les nombres et dates
USE_THOUSAND_SEPARATOR = True

# Format de date français (JJ/MM/AAAA)
DATE_FORMAT = 'd/m/Y'
SHORT_DATE_FORMAT = 'd/m/Y'
DATETIME_FORMAT = 'd/m/Y H:i'
SHORT_DATETIME_FORMAT = 'd/m/Y H:i'

# Format de nombre français (virgule comme séparateur décimal)
DECIMAL_SEPARATOR = ','
THOUSAND_SEPARATOR = ' '  # Espace insécable pour les milliers
NUMBER_GROUPING = 3


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.2/howto/static-files/

STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_DIRS = [BASE_DIR / 'static']

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'


# Default primary key field type
# https://docs.djangoproject.com/en/4.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


# Custom User Model
AUTH_USER_MODEL = 'users.User'


# REST Framework
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'apps.users.authentication.JWTAuthentication',
        'rest_framework.authentication.SessionAuthentication',
    ],
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 50,
    'DEFAULT_RENDERER_CLASSES': [
        'rest_framework.renderers.JSONRenderer',
    ],
    'DEFAULT_PARSER_CLASSES': [
        'rest_framework.parsers.JSONParser',
        'rest_framework.parsers.MultiPartParser',
        'rest_framework.parsers.FormParser',
    ],
}


# CORS Configuration
CORS_ALLOWED_ORIGINS = env.list('CORS_ALLOWED_ORIGINS', default=[])
CORS_ALLOW_CREDENTIALS = True


# Redis Configuration
REDIS_URL = env('REDIS_URL', default='redis://localhost:6379/0')

CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': env('REDIS_CACHE_URL', default='redis://localhost:6379/1'),
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
        },
        'KEY_PREFIX': 'haroo',
        'TIMEOUT': 300,  # 5 minutes par défaut
    }
}

# Session Configuration
SESSION_ENGINE = 'django.contrib.sessions.backends.cache'
SESSION_CACHE_ALIAS = 'default'
SESSION_COOKIE_AGE = 86400  # 24 heures
SESSION_COOKIE_SECURE = not DEBUG
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = 'Lax'


# Celery Configuration
CELERY_BROKER_URL = env('CELERY_BROKER_URL', default='redis://localhost:6379/2')
CELERY_RESULT_BACKEND = env('CELERY_RESULT_BACKEND', default='redis://localhost:6379/3')
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE = TIME_ZONE


# Fedapay Configuration
FEDAPAY_API_KEY = env('FEDAPAY_API_KEY', default='')
FEDAPAY_SECRET_KEY = env('FEDAPAY_SECRET_KEY', default='')
FEDAPAY_ENVIRONMENT = env('FEDAPAY_ENVIRONMENT', default='sandbox')
FEDAPAY_WEBHOOK_SECRET = env('FEDAPAY_WEBHOOK_SECRET', default='')


# SMS Gateway Configuration
SMS_GATEWAY_API_KEY = env('SMS_GATEWAY_API_KEY', default='')
SMS_GATEWAY_SENDER_ID = env('SMS_GATEWAY_SENDER_ID', default='HAROO')


# Email Configuration
EMAIL_BACKEND = env('EMAIL_BACKEND', default='django.core.mail.backends.console.EmailBackend')
EMAIL_HOST = env('EMAIL_HOST', default='localhost')
EMAIL_PORT = env.int('EMAIL_PORT', default=587)
EMAIL_USE_TLS = env.bool('EMAIL_USE_TLS', default=True)
EMAIL_HOST_USER = env('EMAIL_HOST_USER', default='')
EMAIL_HOST_PASSWORD = env('EMAIL_HOST_PASSWORD', default='')
DEFAULT_FROM_EMAIL = env('DEFAULT_FROM_EMAIL', default='noreply@haroo.tg')


# JWT Configuration
JWT_SECRET_KEY = env('JWT_SECRET_KEY', default=SECRET_KEY)
JWT_ACCESS_TOKEN_LIFETIME = env.int('JWT_ACCESS_TOKEN_LIFETIME', default=3600)  # 1 heure
JWT_REFRESH_TOKEN_LIFETIME = env.int('JWT_REFRESH_TOKEN_LIFETIME', default=86400)  # 24 heures


# Commission Rates (en pourcentage)
COMMISSION_AGRONOME = env.int('COMMISSION_AGRONOME', default=10)
COMMISSION_PREVENTE = env.int('COMMISSION_PREVENTE', default=5)
COMMISSION_TRANSPORT = env.int('COMMISSION_TRANSPORT', default=8)


# Salaire minimum légal (FCFA par heure)
SALAIRE_MINIMUM_HORAIRE = env.int('SALAIRE_MINIMUM_HORAIRE', default=500)


# File Upload Configuration
FILE_UPLOAD_MAX_MEMORY_SIZE = 10485760  # 10 MB
DATA_UPLOAD_MAX_MEMORY_SIZE = 10485760  # 10 MB

ALLOWED_UPLOAD_EXTENSIONS = [
    'pdf', 'jpg', 'jpeg', 'png', 'xlsx', 'xls', 'docx', 'doc'
]

# Cloud Storage Configuration
USE_S3 = env.bool('USE_S3', default=False)
USE_CLOUDINARY = env.bool('USE_CLOUDINARY', default=False)

# AWS S3 Configuration (si USE_S3=True)
if USE_S3:
    AWS_ACCESS_KEY_ID = env('AWS_ACCESS_KEY_ID', default='')
    AWS_SECRET_ACCESS_KEY = env('AWS_SECRET_ACCESS_KEY', default='')
    AWS_STORAGE_BUCKET_NAME = env('AWS_STORAGE_BUCKET_NAME', default='')
    AWS_S3_REGION_NAME = env('AWS_S3_REGION_NAME', default='eu-west-1')
    AWS_S3_CUSTOM_DOMAIN = f'{AWS_STORAGE_BUCKET_NAME}.s3.amazonaws.com'
    AWS_S3_OBJECT_PARAMETERS = {
        'CacheControl': 'max-age=86400',
    }
    AWS_DEFAULT_ACL = 'private'
    AWS_S3_FILE_OVERWRITE = False
    AWS_S3_SIGNATURE_VERSION = 's3v4'
    
    # Utiliser S3 pour les fichiers media
    DEFAULT_FILE_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'
    
    MEDIA_URL = f'https://{AWS_S3_CUSTOM_DOMAIN}/media/'

# Cloudinary Configuration (si USE_CLOUDINARY=True)
elif USE_CLOUDINARY:
    CLOUDINARY_CLOUD_NAME = env('CLOUDINARY_CLOUD_NAME', default='')
    CLOUDINARY_API_KEY = env('CLOUDINARY_API_KEY', default='')
    CLOUDINARY_API_SECRET = env('CLOUDINARY_API_SECRET', default='')
    
    # Utiliser Cloudinary pour les fichiers media
    DEFAULT_FILE_STORAGE = 'apps.core.cloudinary_storage.CloudinaryStorage'


# Security Settings
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'

# Encryption Settings
# Clé de chiffrement pour les données sensibles (AES-256)
# Générer avec: python -c 'import secrets; print(secrets.token_urlsafe(32))'
ENCRYPTION_KEY = env('ENCRYPTION_KEY', default='')


# Logging Configuration
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
        'file': {
            'class': 'logging.FileHandler',
            'filename': BASE_DIR / 'logs' / 'haroo.log',
            'formatter': 'verbose',
        },
    },
    'root': {
        'handlers': ['console', 'file'],
        'level': 'INFO',
    },
    'loggers': {
        'django': {
            'handlers': ['console', 'file'],
            'level': 'INFO',
            'propagate': False,
        },
    },
}
