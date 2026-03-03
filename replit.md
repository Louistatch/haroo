# Haroo - Plateforme Agricole Intelligente du Togo

## Project Overview

Haroo is a full-stack agricultural platform for Togo. It consists of:
- **Backend**: Django 4.2.7 REST API (port 8000, internal only)
- **Frontend**: React + TypeScript + Vite (port 5000, public webview)

## Architecture

- **Backend Framework**: Django 4.2.7 with Django REST Framework
- **Frontend Framework**: React 18 + TypeScript + Vite 7
- **Language**: Python 3.12 (backend), TypeScript (frontend)
- **Database**: SQLite (dev) / PostgreSQL with PostGIS (prod)
- **Cache**: Disabled/DummyCache (dev) / Redis (prod)
- **Task Queue**: Celery with Redis broker
- **Authentication**: Custom JWT tokens (access + refresh), phone-based (+228 Togo)
- **Storage**: Local (dev) / AWS S3 or Cloudinary (prod)
- **Payments**: Fedapay mobile payment gateway

## Workflows

- **Backend**: `DJANGO_SETTINGS_MODULE=haroo.settings.dev python3 manage.py runserver 0.0.0.0:8000 --noreload` (must bind 0.0.0.0 for Replit port detection; --noreload for faster startup)
- **Frontend**: `cd frontend && npx vite --port 5000 --host 0.0.0.0`

## Frontend → Backend Integration

Vite dev server proxies all `/api/*` requests to `http://127.0.0.1:8000`.
All API calls in the frontend use relative paths `/api/v1/...` — no hardcoded URLs.

## Project Structure

```
haroo/                    # Django project config
  settings/
    base.py               # Shared settings
    dev.py                # Development settings (SQLite, in-memory cache)
    prod.py               # Production settings
  urls.py                 # Root URL config
  celery.py               # Celery config
  wsgi.py                 # WSGI entry point

apps/                     # Django applications
  core/                   # Core utilities
  users/                  # Auth, user profiles, agronomists
  locations/              # Geographic data
  documents/              # Technical document management
  payments/               # Fedapay payment processing
  missions/               # Mission/task management
  institutional/          # Institutional management
  compliance/             # Regulatory compliance
  ratings/                # User rating system

frontend/                 # React + TypeScript frontend
  src/
    api/
      auth.ts             # Axios client + all auth/user API calls
      payments.ts         # Payment API calls
      purchases.ts        # Purchase history API calls
    pages/
      Landing.tsx         # Public landing page
      Login.tsx           # Phone number login
      Register.tsx        # Account registration
      Dashboard.tsx       # Authenticated user dashboard
      Documents.tsx       # Browse/purchase technical documents
      Agronomists.tsx     # Agronomist directory
      PurchaseHistory.tsx # Purchase history + download
      Profile.tsx         # User profile management
      PaymentSuccess.tsx  # Payment callback page
    components/
      Header.tsx          # Navigation header
      ProtectedRoute.tsx  # Auth guard for routes
      PurchaseModal.tsx   # Document purchase confirmation
      Toast.tsx           # Notification toasts
    styles/               # Component-specific CSS files
  vite.config.ts          # Vite config: port 5000, proxy /api → backend
```

## API Endpoints (all prefixed with /api/v1/)

- `auth/register`, `auth/login`, `auth/verify-sms` — Registration/login
- `auth/refresh-token`, `auth/logout`, `auth/logout-all` — Token management
- `auth/2fa/*` — Two-factor authentication (TOTP)
- `users/me` — Profile management (GET, PATCH)
- `agronomists/` — Public agronomist directory
- `agronomists/register` — Agronomist registration
- `documents/` — Technical document catalog
- `documents/{id}/purchase` — Purchase a document
- `purchases/history` — Purchase history
- `payments/callback` — Fedapay payment callback

## Environment Variables

- `SECRET_KEY` — Django secret key
- `ENCRYPTION_KEY` — AES-256 encryption key for sensitive data
- `JWT_SECRET_KEY` — JWT signing key
- `DJANGO_SETTINGS_MODULE` — Set to `haroo.settings.dev` for development
- `DEBUG` — True for development
- `ALLOWED_HOSTS` — Configured for Replit domains

## Key Dependencies

### Backend
- `Django==4.2.7`, `djangorestframework==3.14.0`
- `djangorestframework-simplejwt==5.3.0` — JWT tokens
- `django-cors-headers==4.3.1` — CORS handling
- `celery==5.3.4` — Async tasks
- `fedapay` — Mobile payment (Togo)
- `pyotp==2.9.0` — 2FA TOTP
- `bcrypt==4.1.2` — Password hashing

### Frontend
- `react@18`, `react-router-dom@6`, `axios`, `typescript`, `vite@7`

## Dev Setup Notes

- CORS: `CORS_ALLOW_ALL_ORIGINS = True` in dev.py
- Cache: `DummyCache` in dev.py (disabled to avoid stale responses after seeding)
- Database: SQLite at `db.sqlite3`
- Seed data: Run `python manage.py seed_data` to populate 5 regions, 11+ prefectures, 40+ cantons, 2 document templates, 12 technical documents
- Admin: Django admin at `/admin/` (create superuser with `python manage.py createsuperuser`)
- Phone format: `+228XXXXXXXX` (Togolese numbers only)
- Auth: JWT tokens stored in `localStorage` (access_token, refresh_token)
- Token refresh: Automatic via axios interceptor in `src/api/auth.ts`
- Backend binding: Must use `0.0.0.0:8000` (not `127.0.0.1:8000`) for Replit workflow port detection to work
