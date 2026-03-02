# Haroo - Plateforme Agricole Intelligente du Togo

## Project Overview

Haroo is a Django REST API backend for an intelligent agricultural platform in Togo. It manages users, agronomists, missions, payments, documents, and compliance tracking.

## Architecture

- **Framework**: Django 4.2.7 with Django REST Framework
- **Language**: Python 3.12
- **Database**: SQLite (dev) / PostgreSQL with PostGIS (prod)
- **Cache**: In-memory (dev) / Redis (prod)
- **Task Queue**: Celery with Redis broker
- **Authentication**: Custom JWT authentication
- **Storage**: Local (dev) / AWS S3 or Cloudinary (prod)

## Project Structure

```
haroo/                  # Django project config
  settings/
    base.py             # Shared settings
    dev.py              # Development settings (SQLite, in-memory cache)
    prod.py             # Production settings
    staging.py          # Staging settings
  urls.py               # Root URL configuration
  celery.py             # Celery configuration

apps/                   # Django applications
  core/                 # Core utilities and shared models
  users/                # User authentication, profiles, agronomists
  locations/            # Geographic data management
  documents/            # Technical document management
  payments/             # Payment processing (Fedapay)
  missions/             # Mission/task management
  institutional/        # Institutional management
  compliance/           # Regulatory compliance
  ratings/              # User rating system

templates/              # Email templates
requirements/
  base.txt              # Core dependencies
  dev.txt               # Development dependencies
  prod.txt              # Production dependencies
```

## API Endpoints

All API endpoints are prefixed with `/api/v1/`. Access requires JWT authentication.

- `/admin/` - Django admin panel
- `/api/v1/` - Users, auth endpoints
- `/api/v1/locations/` - Location data
- `/api/v1/documents/` - Document management
- `/api/v1/payments/` - Payment endpoints
- `/api/v1/missions/` - Mission management
- `/api/v1/institutional/` - Institutional endpoints
- `/api/v1/compliance/` - Compliance endpoints
- `/api/v1/ratings/` - Rating endpoints

## Running the Application

Development server: `DJANGO_SETTINGS_MODULE=haroo.settings.dev python3 manage.py runserver 0.0.0.0:5000`

## Environment Variables

Key variables set via Replit secrets/env:
- `SECRET_KEY` - Django secret key
- `ENCRYPTION_KEY` - AES-256 encryption key for sensitive data
- `JWT_SECRET_KEY` - JWT signing key
- `DJANGO_SETTINGS_MODULE` - Set to `haroo.settings.dev` for development
- `DEBUG` - True for development
- `ALLOWED_HOSTS` - Configured for Replit domains

## Key Dependencies

- `Django==4.2.7` - Web framework
- `djangorestframework==3.14.0` - REST API
- `djangorestframework-simplejwt==5.3.0` - JWT tokens
- `django-cors-headers==4.3.1` - CORS handling
- `celery==5.3.4` - Async task queue
- `fedapay` - Mobile payment gateway (Togo)
- `bcrypt==4.1.2` - Password hashing
- `pyotp==2.9.0` - Two-factor authentication
- `qrcode` - QR code generation for 2FA
