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
- **Authentication**: Neon Auth (Better Auth) for sign-in/sign-up (email + Google OAuth) → JWT exchange with Django backend via `POST /api/v1/auth/neon-exchange`; Django still issues its own access/refresh JWTs for all API calls
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
      missions.ts         # Mission CRUD API calls
      twoFactor.ts        # 2FA setup/enable/disable/status API calls
    pages/
      Landing.tsx         # Public landing page
      Login.tsx           # Email login + Google OAuth (green split-screen, Neon Auth)
      Register.tsx        # Account registration (2-step wizard: user type + email/password)
      Home.tsx            # Post-login hub: real purchase count, user stats, quick actions by type
      Dashboard.tsx       # Redirects to /home (alias)
      Documents.tsx       # Browse/purchase technical documents
      Agronomists.tsx     # Agronomist directory
      PurchaseHistory.tsx # Purchase history: card grid, filters, download/regenerate (inline styles)
      Profile.tsx         # User profile: edit PATCH /users/me, change password modal
      Missions.tsx        # Mission management: role-based (EXPLOITANT/AGRONOME), create/accept/complete
      Security.tsx        # 2FA management: TOTP setup wizard, QR code, backup codes, disable flow
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
- `framer-motion` — Smooth animations and parallax effects

## Design System

- **Theme**: `frontend/src/styles/theme.css` — Full CSS custom properties system (colors, spacing, typography, shadows, radii, z-index)
- **Font**: Inter (Google Fonts) — loaded via `@import` in theme.css
- **Dark mode**: `prefers-color-scheme` auto + manual toggle stored in `localStorage` as `haroo-theme`; applied via `data-theme` attribute on `document.documentElement`
- **Header**: Glassmorphism scroll-aware header (`Header.tsx`); transparent only on landing page (`/`), solid on all other pages; active nav indicator, dark mode toggle, mobile menu with AnimatePresence
- **Landing**: Premium Stripe/Notion-style page (`Landing.tsx`) — animated hero with parallax + word-switcher, animated counters, staggered service/feature cards, testimonials, strong CTAs
- **Animations**: `AnimatedSection.tsx` provides `AnimatedSection`, `StaggerContainer`, `StaggerItem` components for scroll-triggered Framer Motion animations
- **Legacy compatibility**: Theme exports aliases (`--card`, `--spacing-*`, `--font-size-*`, etc.) to keep older pages working

## Dev Setup Notes

- CORS: `CORS_ALLOW_ALL_ORIGINS = True` in dev.py
- Cache: `DummyCache` in dev.py (disabled to avoid stale responses after seeding)
- Database: **Neon PostgreSQL** (PostgreSQL 17.8) — host `ep-muddy-salad-aljfiixs-pooler.c-3.eu-central-1.aws.neon.tech`, db `neondb`; credentials via secrets `DB_PASSWORD`, env vars `DB_HOST/DB_NAME/DB_USER/DB_PORT/DB_SSL`
- Seed data: Run `python manage.py seed_data` to populate 5 regions, 11+ prefectures, 40+ cantons, 2 document templates, 12 technical documents + 3 demo accounts
- Demo accounts: `+22890000001/Demo123!` (exploitant), `+22890000002/Demo123!` (agronome), `+22890000003/Admin123!` (admin)
- Admin: Django admin at `/admin/` (create superuser with `python manage.py createsuperuser`)
- Phone format: `+228XXXXXXXX` (Togolese numbers only)
- Auth: JWT tokens stored in `localStorage` (access_token, refresh_token)
- Token refresh: Automatic via axios interceptor in `src/api/auth.ts`
- Backend binding: Must use `0.0.0.0:8000` (not `127.0.0.1:8000`) for Replit workflow port detection to work
- Design rule: All authenticated pages (Home, Profile, PurchaseHistory, Documents, Agronomists) use **inline styles + Framer Motion** only — zero external CSS file dependencies
- Bug fixed: `changePassword()` in auth.ts now sends `new_password_confirm` (was `confirm_password`) matching ChangePasswordSerializer
- `Dashboard` route redirects to `/home` to eliminate duplication
