---
name: Production Ready - Haroo
description: Transformer Haroo en application production-ready avec sécurité, performance et DevOps
version: 1.0.0
status: draft
---

# Production Ready - Haroo

## Contexte

Haroo est une plateforme agricole intelligente du Togo développée avec Django 4.2.7 (backend) et React 18 + Vite 7 (frontend). Le projet fonctionne en développement mais nécessite des améliorations critiques pour être prêt pour la production.

## Objectifs

Transformer Haroo en application production-ready en implémentant:
- Sécurité renforcée (JWT sécurisés, rate limiting, HTTPS)
- Infrastructure moderne (Docker, CI/CD)
- Performance optimisée (cache, requêtes optimisées)
- Monitoring et observabilité (Sentry, logs structurés)
- Tests automatisés et qualité du code

## Architecture Actuelle

**Backend:**
- Django 4.2.7 + Django REST Framework
- PostgreSQL + PostGIS (SQLite en dev)
- Redis (4 bases: cache, sessions, Celery broker/backend)
- Celery pour tâches asynchrones
- JWT custom pour authentification
- Rate limiting custom

**Frontend:**
- React 18 + TypeScript
- Vite 7
- Tailwind CSS v4
- Axios pour API calls
- Tokens JWT stockés dans localStorage ⚠️

**Problèmes identifiés:**
- ❌ Tokens JWT en localStorage (vulnérable XSS)
- ❌ Pas de Docker/containerisation
- ❌ Pas de CI/CD
- ❌ Pas de documentation API
- ❌ Rate limiting basique
- ❌ Requêtes N+1 non optimisées
- ❌ Pas de monitoring production
- ❌ Pas de tests automatisés

## Références

- #[[file:README.md]] - Documentation projet
- #[[file:ARCHITECTURE.md]] - Architecture détaillée
- #[[file:PRODUCTION_ROADMAP.md]] - Roadmap complète avec code
- #[[file:haroo/settings/base.py]] - Configuration Django
- #[[file:frontend/src/api/auth.ts]] - Authentification actuelle

---

# Requirements

## REQ-1: Sécurité JWT avec Cookies HttpOnly
**Priority:** CRITICAL  
**Category:** Security

### Description
Remplacer le stockage des tokens JWT dans localStorage par des cookies HttpOnly pour protéger contre les attaques XSS.

### Acceptance Criteria
- [ ] Tokens JWT stockés dans cookies HttpOnly
- [ ] Cookies configurés avec Secure, SameSite=Lax
- [ ] Backend supporte authentification par cookie
- [ ] Frontend n'accède plus à localStorage pour les tokens
- [ ] Rafraîchissement automatique des tokens
- [ ] Déconnexion propre avec suppression des cookies
- [ ] Compatible avec l'authentification existante (migration progressive)

### Technical Notes
- Modifier `apps/users/authentication.py` pour supporter cookies
- Créer nouveaux endpoints: `/auth/login-cookies`, `/auth/refresh-cookies`, `/auth/logout-cookies`
- Créer `frontend/src/api/authSecure.ts` avec `withCredentials: true`
- Configurer CORS pour accepter les credentials

### References
- OWASP A03:2021 (Injection)
- #[[file:PRODUCTION_ROADMAP.md]] Section "TÂCHE 1"

---

## REQ-2: Containerisation avec Docker
**Priority:** CRITICAL  
**Category:** DevOps

### Description
Containeriser l'application complète avec Docker et Docker Compose pour un déploiement reproductible.

### Acceptance Criteria
- [ ] Dockerfile pour Django backend
- [ ] Dockerfile pour React frontend avec Nginx
- [ ] docker-compose.yml avec tous les services (db, redis, backend, frontend, celery)
- [ ] Script d'entrée Docker avec migrations automatiques
- [ ] Configuration Nginx pour proxy et SPA routing
- [ ] Healthchecks pour tous les services
- [ ] Volumes persistants pour données
- [ ] Makefile pour simplifier les commandes
- [ ] Documentation de déploiement Docker

### Technical Notes
- Utiliser `postgis/postgis:14-3.3` pour PostgreSQL
- Utiliser `redis:7-alpine` pour Redis
- Multi-stage build pour frontend (builder + nginx)
- Variables d'environnement via `.env.docker`

### References
- #[[file:PRODUCTION_ROADMAP.md]] Section "TÂCHE 2"

---

## REQ-3: Pipeline CI/CD
**Priority:** CRITICAL  
**Category:** DevOps

### Description
Mettre en place un pipeline CI/CD complet avec GitHub Actions pour automatiser tests, build et déploiement.

### Acceptance Criteria
- [ ] Workflow CI pour tests automatiques (backend + frontend)
- [ ] Workflow CD pour déploiement production
- [ ] Analyse de sécurité avec Trivy
- [ ] Vérification qualité du code (flake8, black, isort)
- [ ] Build et push automatique des images Docker
- [ ] Déploiement automatique sur merge dans main
- [ ] Notifications Slack sur succès/échec
- [ ] Workflow de release avec changelog automatique
- [ ] Secrets GitHub configurés

### Technical Notes
- Tests backend avec pytest + PostgreSQL service
- Tests frontend avec npm (lint + build)
- Images Docker poussées vers GitHub Container Registry
- Déploiement SSH vers serveur de production

### References
- #[[file:PRODUCTION_ROADMAP.md]] Section "TÂCHE 3"

---

## REQ-4: Documentation API OpenAPI
**Priority:** IMPORTANT  
**Category:** Documentation

### Description
Générer une documentation API interactive avec Swagger/OpenAPI pour faciliter l'intégration.

### Acceptance Criteria
- [ ] drf-spectacular installé et configuré
- [ ] Schéma OpenAPI 3.0 généré automatiquement
- [ ] Interface Swagger UI accessible à `/api/docs/`
- [ ] Interface ReDoc accessible à `/api/redoc/`
- [ ] Tous les endpoints documentés avec exemples
- [ ] Modèles de requête/réponse documentés
- [ ] Tags pour grouper les endpoints par domaine

### Technical Notes
- Utiliser `@extend_schema` pour documenter les endpoints
- Configurer `SPECTACULAR_SETTINGS` dans settings
- Ajouter exemples de requêtes/réponses

### References
- #[[file:PRODUCTION_ROADMAP.md]] Section "TÂCHE 4"

---

## REQ-5: Rate Limiting Robuste
**Priority:** IMPORTANT  
**Category:** Security

### Description
Implémenter un rate limiting robuste au niveau application et infrastructure pour protéger contre les abus.

### Acceptance Criteria
- [ ] django-ratelimit installé et configuré
- [ ] Rate limiting par endpoint (différencié)
- [ ] Rate limiting Nginx configuré
- [ ] Middleware de rate limiting avancé (sliding window)
- [ ] Messages d'erreur clairs avec retry_after
- [ ] Blocage des user agents suspects
- [ ] Monitoring des tentatives de rate limit

### Technical Notes
- Endpoints auth: 5 requêtes/minute
- Endpoints API: 10 requêtes/seconde
- Utiliser Redis pour le comptage
- Configurer `limit_req_zone` dans Nginx

### References
- #[[file:PRODUCTION_ROADMAP.md]] Section "TÂCHE 5"

---

## REQ-6: Optimisation Performances
**Priority:** IMPORTANT  
**Category:** Performance

### Description
Optimiser les performances de l'application avec cache, requêtes optimisées et pagination efficace.

### Acceptance Criteria
- [ ] Requêtes N+1 éliminées (select_related, prefetch_related)
- [ ] Cache Redis pour données statiques
- [ ] Pagination cursor pour grandes listes
- [ ] Index de base de données optimaux
- [ ] Compression automatique des images
- [ ] Temps de réponse API < 200ms (p95)
- [ ] Invalidation de cache automatique

### Technical Notes
- Utiliser `select_related` pour relations ForeignKey
- Utiliser `prefetch_related` pour relations ManyToMany
- Cache TTL: 24h pour locations, 5min pour données dynamiques
- Pagination cursor avec `CursorPagination`

### References
- #[[file:PRODUCTION_ROADMAP.md]] Section "TÂCHE 6"

---

## REQ-7: Monitoring et Logs
**Priority:** IMPORTANT  
**Category:** Observability

### Description
Mettre en place un système de monitoring et de logs structurés pour faciliter le debugging en production.

### Acceptance Criteria
- [ ] Sentry configuré pour monitoring des erreurs
- [ ] Logs structurés en JSON
- [ ] Rotation automatique des logs
- [ ] Middleware de logging des requêtes
- [ ] Health check endpoint
- [ ] Alertes automatiques (email + Slack)
- [ ] Dashboard Sentry configuré
- [ ] Filtrage des données sensibles

### Technical Notes
- Utiliser `pythonjsonlogger` pour logs JSON
- Logger: requêtes, erreurs, sécurité
- Health check: vérifier DB, Redis, Celery
- Sentry: filtrer passwords, tokens, secrets

### References
- #[[file:PRODUCTION_ROADMAP.md]] Section "TÂCHE 7"

---

## REQ-8: Tests Automatisés
**Priority:** IMPROVEMENT  
**Category:** Quality

### Description
Ajouter une suite de tests automatisés pour garantir la qualité du code et éviter les régressions.

### Acceptance Criteria
- [x] pytest configuré pour backend
- [ ] Couverture de code > 70%
- [x] Tests unitaires pour authentification
- [x] Tests d'intégration pour endpoints critiques
- [x] Vitest configuré pour frontend
- [x] Tests des composants React
- [x] Tests automatiques dans CI/CD

### Technical Notes
- pytest avec fixtures pour données de test
- Tests avec base de données de test
- Mocking des appels API externes
- Tests frontend avec @testing-library/react

### References
- #[[file:PRODUCTION_ROADMAP.md]] Section "TÂCHE 8"

---

## REQ-9: Optimisation UX/UI
**Priority:** IMPROVEMENT  
**Category:** Frontend

### Description
Améliorer l'expérience utilisateur avec gestion d'état moderne, lazy loading et PWA.

### Acceptance Criteria
- [ ] React Query installé et configuré
- [ ] Hooks personnalisés pour API calls
- [ ] Lazy loading des composants
- [ ] PWA configurée (manifest + service worker)
- [ ] Mode offline basique
- [ ] Score Lighthouse > 90
- [ ] Cache automatique des requêtes API

### Technical Notes
- React Query pour cache et synchronisation
- Lazy loading avec `React.lazy()` et `Suspense`
- PWA avec `vite-plugin-pwa`
- Service worker pour cache des assets

### References
- #[[file:PRODUCTION_ROADMAP.md]] Section "TÂCHE 9"

---

## REQ-10: Déploiement Production
**Priority:** IMPROVEMENT  
**Category:** DevOps

### Description
Préparer le déploiement en production avec scripts, SSL, backups et stratégie de rollback.

### Acceptance Criteria
- [x] Script de déploiement automatisé
- [x] SSL/TLS configuré avec Let's Encrypt
- [x] Backups automatiques quotidiens
- [x] Stratégie de rollback documentée
- [x] Monitoring de la santé de l'application
- [x] Documentation de déploiement complète
- [x] Crontab configurée pour backups

### Technical Notes
- Script bash pour déploiement avec backup pré-déploiement
- Nginx avec SSL/TLS 1.3
- Backup PostgreSQL + fichiers media
- Retention: 7 jours
- Upload backups vers S3 (optionnel)

### References
- #[[file:PRODUCTION_ROADMAP.md]] Section "TÂCHE 10"

---

# Design

## Architecture Cible

### Vue d'ensemble

```
┌─────────────────────────────────────────────────────────────┐
│                         Internet                             │
└────────────────────────┬────────────────────────────────────┘
                         │
                    ┌────▼────┐
                    │  Nginx  │ (SSL/TLS, Rate Limiting)
                    │  Proxy  │
                    └────┬────┘
                         │
        ┌────────────────┼────────────────┐
        │                │                │
   ┌────▼────┐     ┌────▼────┐     ┌────▼────┐
   │ Frontend│     │ Backend │     │  Admin  │
   │  React  │     │ Django  │     │  Panel  │
   │  (SPA)  │     │   API   │     │         │
   └─────────┘     └────┬────┘     └─────────┘
                        │
        ┌───────────────┼───────────────┐
        │               │               │
   ┌────▼────┐    ┌────▼────┐    ┌────▼────┐
   │PostgreSQL│    │  Redis  │    │ Celery  │
   │ PostGIS  │    │  Cache  │    │ Workers │
   └──────────┘    └─────────┘    └─────────┘
```

### Composants

**1. Frontend (React + Nginx)**
- Application React buildée en production
- Servie par Nginx avec compression gzip
- Routing SPA avec fallback vers index.html
- Proxy vers backend pour `/api/` et `/admin/`
- PWA avec service worker pour cache offline

**2. Backend (Django + Gunicorn)**
- API REST avec Django REST Framework
- Authentification JWT via cookies HttpOnly
- Rate limiting multi-niveaux
- Cache Redis pour performances
- Logs structurés en JSON

**3. Base de données (PostgreSQL + PostGIS)**
- PostgreSQL 14 avec extension PostGIS
- Index optimisés pour requêtes fréquentes
- Backups automatiques quotidiens
- Réplication (future)

**4. Cache & Sessions (Redis)**
- DB 0: Sessions utilisateurs
- DB 1: Cache applicatif
- DB 2: Broker Celery
- DB 3: Backend Celery

**5. Tâches asynchrones (Celery)**
- Worker pour tâches longues
- Beat pour tâches planifiées
- Monitoring avec Flower (optionnel)

**6. Monitoring (Sentry + Logs)**
- Sentry pour erreurs et performance
- Logs structurés avec rotation
- Health check endpoint
- Alertes automatiques

### Flux d'authentification sécurisé

```
┌─────────┐                ┌─────────┐                ┌─────────┐
│ Browser │                │  Nginx  │                │ Django  │
└────┬────┘                └────┬────┘                └────┬────┘
     │                          │                          │
     │ POST /auth/login-cookies │                          │
     ├─────────────────────────>│                          │
     │                          │ Forward request          │
     │                          ├─────────────────────────>│
     │                          │                          │
     │                          │                          │ Verify credentials
     │                          │                          │ Generate JWT tokens
     │                          │                          │
     │                          │ Set-Cookie: access_token │
     │                          │ Set-Cookie: refresh_token│
     │<─────────────────────────┤<─────────────────────────┤
     │                          │                          │
     │ GET /api/users/me        │                          │
     │ Cookie: access_token     │                          │
     ├─────────────────────────>│                          │
     │                          │ Forward with cookie      │
     │                          ├─────────────────────────>│
     │                          │                          │
     │                          │                          │ Verify JWT from cookie
     │                          │                          │ Return user data
     │                          │                          │
     │<─────────────────────────┤<─────────────────────────┤
     │                          │                          │
```

### Stratégie de cache

**Niveaux de cache:**

1. **Browser Cache** (Frontend)
   - Assets statiques: 1 an
   - API responses: géré par React Query (5 min)

2. **Nginx Cache** (Reverse Proxy)
   - Fichiers statiques: 1 jour
   - Pas de cache pour API

3. **Redis Cache** (Application)
   - Données statiques (locations): 24h
   - Données dynamiques (users): 5min
   - Invalidation automatique sur modification

4. **Database Query Cache** (PostgreSQL)
   - Requêtes fréquentes avec index
   - Matérialized views pour agrégations

### Stratégie de déploiement

**Environnements:**

1. **Development** (Local)
   - SQLite ou PostgreSQL local
   - DEBUG=True
   - Hot reload activé

2. **Staging** (Serveur de test)
   - PostgreSQL + Redis
   - DEBUG=False
   - Données de test
   - Tests automatiques

3. **Production** (Serveur principal)
   - PostgreSQL + Redis + Celery
   - DEBUG=False
   - SSL/TLS obligatoire
   - Monitoring actif
   - Backups automatiques

**Processus de déploiement:**

```
1. Developer push code → GitHub
2. GitHub Actions CI:
   - Run tests (backend + frontend)
   - Check code quality (linting)
   - Security scan (Trivy)
3. If tests pass:
   - Build Docker images
   - Push to Container Registry
4. If branch = main:
   - Backup database
   - Deploy to production
   - Run migrations
   - Health check
   - Notify team (Slack)
5. If deployment fails:
   - Rollback to previous version
   - Alert team
```

### Sécurité

**Couches de sécurité:**

1. **Infrastructure**
   - Firewall (ports 80, 443 uniquement)
   - SSL/TLS 1.3
   - DDoS protection (Cloudflare optionnel)

2. **Application**
   - JWT dans cookies HttpOnly
   - CSRF protection
   - Rate limiting multi-niveaux
   - Input validation
   - SQL injection protection (ORM)

3. **Données**
   - Passwords hashed (bcrypt)
   - Données sensibles chiffrées (AES-256)
   - Backups chiffrés
   - Logs sans PII

4. **Monitoring**
   - Sentry pour erreurs
   - Logs de sécurité séparés
   - Alertes sur activités suspectes

---

# Implementation Tasks

## Phase 1: Sécurité Critique (Semaine 1)

### TASK-1.1: Créer endpoints JWT avec cookies (Backend)
**Estimate:** 2h  
**Dependencies:** None  
**Files:**
- `apps/users/views.py`
- `apps/users/authentication.py`
- `haroo/urls.py`

**Steps:**
1. Créer `login_with_cookies()` dans `apps/users/views.py`
2. Créer `refresh_token_with_cookies()` dans `apps/users/views.py`
3. Créer `logout_with_cookies()` dans `apps/users/views.py`
4. Modifier `JWTAuthentication.authenticate()` pour supporter cookies
5. Ajouter routes dans `haroo/urls.py`
6. Tester avec curl/Postman

**Acceptance:**
- [ ] Endpoint `/api/v1/auth/login-cookies` retourne cookies HttpOnly
- [ ] Endpoint `/api/v1/auth/refresh-cookies` rafraîchit le token
- [ ] Endpoint `/api/v1/auth/logout-cookies` supprime les cookies
- [ ] Authentification fonctionne avec cookie ou header

**Reference:** #[[file:PRODUCTION_ROADMAP.md]] TÂCHE 1 - Backend

---

### TASK-1.2: Créer service d'authentification sécurisé (Frontend)
**Estimate:** 2h  
**Dependencies:** TASK-1.1  
**Files:**
- `frontend/src/api/authSecure.ts`
- `frontend/src/components/Login.tsx`

**Steps:**
1. Créer `frontend/src/api/authSecure.ts` avec `withCredentials: true`
2. Implémenter `login()`, `logout()`, `isLoggedIn()`
3. Ajouter intercepteur pour refresh automatique
4. Mettre à jour composant Login pour utiliser nouveau service
5. Tester le flux complet

**Acceptance:**
- [ ] Tokens ne sont plus dans localStorage
- [ ] Cookies envoyés automatiquement avec requêtes
- [ ] Refresh automatique fonctionne
- [ ] Déconnexion supprime les cookies

**Reference:** #[[file:PRODUCTION_ROADMAP.md]] TÂCHE 1 - Frontend

---

## Phase 2: Infrastructure Docker (Semaine 1)

### TASK-2.1: Créer Dockerfile Backend
**Estimate:** 2h  
**Dependencies:** None  
**Files:**
- `Dockerfile`
- `docker-entrypoint.sh`
- `.dockerignore`

**Steps:**
1. Créer `Dockerfile` avec Python 3.11
2. Installer dépendances système (PostgreSQL, GDAL)
3. Créer `docker-entrypoint.sh` avec migrations
4. Configurer `.dockerignore`
5. Tester build: `docker build -t haroo-backend .`

**Acceptance:**
- [ ] Image Docker se build sans erreur
- [ ] Migrations s'exécutent automatiquement
- [ ] Application démarre sur port 8000
- [ ] Healthcheck fonctionne

**Reference:** #[[file:PRODUCTION_ROADMAP.md]] TÂCHE 2 - Dockerfile Backend

---

### TASK-2.2: Créer Dockerfile Frontend
**Estimate:** 1h  
**Dependencies:** None  
**Files:**
- `frontend/Dockerfile`
- `frontend/nginx.conf`

**Steps:**
1. Créer `frontend/Dockerfile` multi-stage (builder + nginx)
2. Créer `frontend/nginx.conf` avec proxy vers backend
3. Configurer SPA routing
4. Tester build: `docker build -t haroo-frontend ./frontend`

**Acceptance:**
- [ ] Image Docker se build sans erreur
- [ ] Frontend accessible sur port 80
- [ ] Proxy vers backend fonctionne
- [ ] SPA routing fonctionne

**Reference:** #[[file:PRODUCTION_ROADMAP.md]] TÂCHE 2 - Dockerfile Frontend

---

### TASK-2.3: Créer docker-compose.yml
**Estimate:** 3h  
**Dependencies:** TASK-2.1, TASK-2.2  
**Files:**
- `docker-compose.yml`
- `.env.docker`
- `Makefile`

**Steps:**
1. Créer `docker-compose.yml` avec tous les services
2. Configurer services: db, redis, backend, frontend, celery_worker, celery_beat
3. Créer `.env.docker` avec variables d'environnement
4. Créer `Makefile` pour simplifier commandes
5. Tester: `make build && make up`

**Acceptance:**
- [ ] Tous les services démarrent correctement
- [ ] Healthchecks passent
- [ ] Frontend accessible sur http://localhost:5000
- [ ] Backend accessible sur http://localhost:8000
- [ ] Volumes persistants fonctionnent

**Reference:** #[[file:PRODUCTION_ROADMAP.md]] TÂCHE 2 - docker-compose

-----

## Phase 3: CI/CD Pipeline (Semaine 2)

### TASK-3.1: Créer workflow CI pour tests
**Estimate:** 4h  
**Dependencies:** TASK-2.3  
**Files:**
- `.github/workflows/ci.yml`
- `pytest.ini`

**Steps:**
1. Créer `.github/workflows/ci.yml`
2. Configurer job `backend-tests` avec PostgreSQL service
3. Configurer job `frontend-tests` avec Node.js
4. Configurer job `security-scan` avec Trivy
5. Configurer job `code-quality` avec flake8, black, isort
6. Tester en créant une PR

**Acceptance:**
- [ ] Tests backend s'exécutent automatiquement
- [ ] Tests frontend s'exécutent automatiquement
- [ ] Scan de sécurité fonctionne
- [ ] Vérification qualité du code fonctionne
- [ ] Badge de statut dans README

**Reference:** #[[file:PRODUCTION_ROADMAP.md]] TÂCHE 3 - CI

---

### TASK-3.2: Créer workflow CD pour déploiement
**Estimate:** 4h  
**Dependencies:** TASK-3.1  
**Files:**
- `.github/workflows/cd.yml`
- `.github/workflows/release.yml`

**Steps:**
1. Créer `.github/workflows/cd.yml`
2. Configurer build et push des images Docker
3. Configurer déploiement SSH vers serveur
4. Créer `.github/workflows/release.yml` pour releases
5. Configurer secrets GitHub
6. Tester déploiement sur serveur de staging

**Acceptance:**
- [ ] Images Docker buildées et poussées automatiquement
- [ ] Déploiement automatique sur merge dans main
- [ ] Notifications Slack fonctionnent
- [ ] Releases créées automatiquement sur tag

**Reference:** #[[file:PRODUCTION_ROADMAP.md]] TÂCHE 3 - CD

---

## Phase 4: Documentation et Rate Limiting (Semaine 2)

### TASK-4.1: Configurer Swagger/OpenAPI
**Estimate:** 2h  
**Dependencies:** None  
**Files:**
- `haroo/settings/base.py`
- `haroo/urls.py`
- `requirements-no-gdal.txt`

**Steps:**
1. Installer `drf-spectacular`
2. Configurer dans `settings/base.py`
3. Ajouter routes dans `urls.py`
4. Tester: accéder à `/api/docs/`

**Acceptance:**
- [ ] Swagger UI accessible à `/api/docs/`
- [ ] ReDoc accessible à `/api/redoc/`
- [ ] Schéma OpenAPI généré automatiquement
- [ ] Tous les endpoints listés

**Reference:** #[[file:PRODUCTION_ROADMAP.md]] TÂCHE 4

---

### TASK-4.2: Documenter endpoints existants
**Estimate:** 2h  
**Dependencies:** TASK-4.1  
**Files:**
- `apps/users/views.py`
- `apps/*/views.py`

**Steps:**
1. Ajouter `@extend_schema` sur endpoints auth
2. Ajouter exemples de requêtes/réponses
3. Ajouter tags pour grouper endpoints
4. Documenter modèles de données
5. Vérifier dans Swagger UI

**Acceptance:**
- [ ] Tous les endpoints ont description
- [ ] Exemples de requêtes/réponses présents
- [ ] Tags configurés (Authentification, Users, etc.)
- [ ] Modèles documentés

**Reference:** #[[file:PRODUCTION_ROADMAP.md]] TÂCHE 4

---

### TASK-5.1: Implémenter rate limiting Django
**Estimate:** 3h  
**Dependencies:** None  
**Files:**
- `apps/users/views.py`
- `apps/core/middleware.py`
- `requirements-no-gdal.txt`

**Steps:**
1. Installer `django-ratelimit`
2. Ajouter `@ratelimit` sur endpoints sensibles
3. Créer `AdvancedRateLimitMiddleware` dans `apps/core/middleware.py`
4. Configurer dans `settings/base.py`
5. Tester avec script de charge

**Acceptance:**
- [ ] Rate limiting actif sur endpoints auth
- [ ] Messages d'erreur clairs avec retry_after
- [ ] Middleware de rate limiting fonctionne
- [ ] Compteurs Redis fonctionnent

**Reference:** #[[file:PRODUCTION_ROADMAP.md]] TÂCHE 5

---

### TASK-5.2: Configurer rate limiting Nginx
**Estimate:** 3h  
**Dependencies:** TASK-2.2  
**Files:**
- `frontend/nginx.conf`
- `nginx/nginx-ssl.conf`

**Steps:**
1. Ajouter `limit_req_zone` dans nginx.conf
2. Configurer rate limiting par endpoint
3. Bloquer user agents suspects
4. Tester avec script de charge
5. Documenter configuration

**Acceptance:**
- [ ] Rate limiting Nginx actif
- [ ] Endpoints auth limités à 5 req/min
- [ ] Endpoints API limités à 10 req/s
- [ ] User agents suspects bloqués

**Reference:** #[[file:PRODUCTION_ROADMAP.md]] TÂCHE 5

---

## Phase 5: Performance et Monitoring (Semaine 3)

### TASK-6.1: Optimiser requêtes database
**Estimate:** 4h  
**Dependencies:** None  
**Files:**
- `apps/users/views.py`
- `apps/*/models.py`

**Steps:**
1. Identifier requêtes N+1 avec Django Debug Toolbar
2. Ajouter `select_related()` pour ForeignKey
3. Ajouter `prefetch_related()` pour ManyToMany
4. Ajouter index dans modèles
5. Créer migration pour index
6. Tester performances avec `django-silk`

**Acceptance:**
- [ ] Requêtes N+1 éliminées
- [ ] Index créés sur champs fréquents
- [ ] Temps de réponse réduit de 50%+
- [ ] Nombre de requêtes réduit

**Reference:** #[[file:PRODUCTION_ROADMAP.md]] TÂCHE 6

---

### TASK-6.2: Implémenter cache Redis
**Estimate:** 2h  
**Dependencies:** None  
**Files:**
- `apps/locations/views.py`
- `apps/core/cache.py`

**Steps:**
1. Créer fonctions de cache dans `apps/core/cache.py`
2. Ajouter `@cache_page` sur endpoints statiques
3. Implémenter invalidation de cache
4. Configurer TTL par type de données
5. Tester cache avec Redis CLI

**Acceptance:**
- [ ] Cache actif pour données statiques
- [ ] TTL configurés (24h locations, 5min users)
- [ ] Invalidation automatique fonctionne
- [ ] Hit rate > 80% pour données statiques

**Reference:** #[[file:PRODUCTION_ROADMAP.md]] TÂCHE 6

---

### TASK-6.3: Implémenter pagination cursor
**Estimate:** 2h  
**Dependencies:** None  
**Files:**
- `apps/core/pagination.py`
- `apps/users/views.py`

**Steps:**
1. Créer `StandardCursorPagination` dans `apps/core/pagination.py`
2. Remplacer `PageNumberPagination` par `CursorPagination`
3. Tester sur grandes listes (>1000 items)
4. Documenter dans Swagger

**Acceptance:**
- [ ] Pagination cursor active sur grandes listes
- [ ] Performance améliorée vs pagination classique
- [ ] Documentation Swagger mise à jour

**Reference:** #[[file:PRODUCTION_ROADMAP.md]] TÂCHE 6

---

### TASK-7.1: Configurer Sentry
**Estimate:** 2h  
**Dependencies:** None  
**Files:**
- `haroo/settings/prod.py`
- `requirements-no-gdal.txt`

**Steps:**
1. Créer compte Sentry
2. Installer `sentry-sdk`
3. Configurer dans `settings/prod.py`
4. Implémenter `filter_sensitive_data()`
5. Tester en déclenchant une erreur

**Acceptance:**
- [ ] Sentry configuré en production
- [ ] Erreurs capturées automatiquement
- [ ] Données sensibles filtrées
- [ ] Alertes email configurées

**Reference:** #[[file:PRODUCTION_ROADMAP.md]] TÂCHE 7

---

### TASK-7.2: Implémenter logs structurés
**Estimate:** 2h  
**Dependencies:** None  
**Files:**
- `haroo/settings/base.py`
- `apps/core/middleware.py`

**Steps:**
1. Installer `python-json-logger`
2. Configurer logging JSON dans settings
3. Créer `RequestLoggingMiddleware`
4. Configurer rotation des logs
5. Tester logs avec tail -f

**Acceptance:**
- [ ] Logs en format JSON
- [ ] Rotation automatique (10MB, 10 fichiers)
- [ ] Logs séparés (app, errors, security)
- [ ] Métadonnées complètes (user_id, ip, duration)

**Reference:** #[[file:PRODUCTION_ROADMAP.md]] TÂCHE 7

---

### TASK-7.3: Créer health check endpoint
**Estimate:** 2h  
**Dependencies:** None  
**Files:**
- `apps/core/views.py`
- `haroo/urls.py`

**Steps:**
1. Créer `health_check()` dans `apps/core/views.py`
2. Vérifier DB, Redis, Celery
3. Ajouter route `/api/v1/health/`
4. Tester avec curl
5. Configurer monitoring externe (UptimeRobot)

**Acceptance:**
- [ ] Endpoint `/api/v1/health/` retourne statut
- [ ] Vérifie DB, Redis, Celery
- [ ] Retourne 200 si healthy, 503 si unhealthy
- [ ] Monitoring externe configuré

**Reference:** #[[file:PRODUCTION_ROADMAP.md]] TÂCHE 7

---

## Phase 6: Tests et Qualité (Semaine 4)

### TASK-8.1: Configurer pytest Backend ✅
**Estimate:** 2h  
**Dependencies:** None  
**Files:**
- `pytest.ini`
- `conftest.py`
- `requirements-no-gdal.txt`

**Steps:**
1. Installer pytest, pytest-django, pytest-cov
2. Créer `pytest.ini`
3. Créer `conftest.py` avec fixtures
4. Configurer base de données de test
5. Tester: `pytest`

**Acceptance:**
- [x] pytest configuré
- [x] Fixtures de base créées (api_client, user_data)
- [x] Base de données de test fonctionne
- [x] Couverture de code activée

**Reference:** #[[file:PRODUCTION_ROADMAP.md]] TÂCHE 8

---

### TASK-8.2: Créer tests authentification ✅
**Estimate:** 4h  
**Dependencies:** TASK-8.1  
**Files:**
- `apps/users/tests/test_authentication.py`
- `apps/users/tests/test_jwt.py`

**Steps:**
1. Créer `apps/users/tests/test_authentication.py`
2. Tester inscription (succès, email dupliqué)
3. Tester connexion (succès, mauvais password)
4. Tester endpoints protégés
5. Tester refresh token
6. Viser couverture > 80% pour apps/users

**Acceptance:**
- [x] Tests d'inscription fonctionnent
- [x] Tests de connexion fonctionnent
- [x] Tests d'endpoints protégés fonctionnent
- [x] Couverture > 80% pour apps/users

**Reference:** #[[file:PRODUCTION_ROADMAP.md]] TÂCHE 8

---

### TASK-8.3: Configurer Vitest Frontend ✅
**Estimate:** 2h  
**Dependencies:** None  
**Files:**
- `frontend/vitest.config.ts`
- `frontend/src/test/setup.ts`
- `frontend/package.json`

**Steps:**
1. Installer vitest, @testing-library/react
2. Créer `vitest.config.ts`
3. Créer `src/test/setup.ts`
4. Ajouter script test dans package.json
5. Tester: `npm run test`

**Acceptance:**
- [x] Vitest configuré
- [x] Testing Library configuré
- [x] Tests s'exécutent
- [x] Couverture de code activée

**Reference:** #[[file:PRODUCTION_ROADMAP.md]] TÂCHE 8

---

### TASK-8.4: Créer tests composants React ✅
**Estimate:** 4h  
**Dependencies:** TASK-8.3  
**Files:**
- `frontend/src/components/__tests__/Login.test.tsx`
- `frontend/src/components/__tests__/Dashboard.test.tsx`

**Steps:**
1. Créer tests pour composant Login
2. Tester rendu, erreurs, succès
3. Mocker appels API
4. Créer tests pour autres composants critiques
5. Viser couverture > 70%

**Acceptance:**
- [x] Tests Login fonctionnent
- [x] Tests Dashboard fonctionnent
- [x] Mocking API fonctionne
- [x] Couverture > 70%

**Reference:** #[[file:PRODUCTION_ROADMAP.md]] TÂCHE 8

---

## Phase 7: UX/UI et Déploiement (Semaine 4)

### TASK-9.1: Implémenter React Query ✅
**Estimate:** 4h  
**Dependencies:** None  
**Files:**
- `frontend/src/main.tsx`
- `frontend/src/hooks/useAuth.ts`
- `frontend/package.json`

**Steps:**
1. Installer `@tanstack/react-query`
2. Configurer QueryClient dans main.tsx
3. Créer hooks personnalisés (useUser, useLogin, useLogout)
4. Remplacer appels API directs par hooks
5. Tester cache et synchronisation

**Acceptance:**
- [x] React Query configuré
- [x] Hooks personnalisés créés
- [x] Cache automatique fonctionne
- [x] Synchronisation entre onglets fonctionne

**Reference:** #[[file:PRODUCTION_ROADMAP.md]] TÂCHE 9

---

### TASK-9.2: Implémenter lazy loading et PWA ✅
**Estimate:** 3h  
**Dependencies:** None  
**Files:**
- `frontend/src/App.tsx`
- `frontend/vite.config.ts`
- `frontend/package.json`

**Steps:**
1. Implémenter lazy loading avec React.lazy()
2. Installer `vite-plugin-pwa`
3. Configurer manifest.json
4. Configurer service worker
5. Tester installation PWA

**Acceptance:**
- [x] Lazy loading actif sur routes
- [x] PWA installable
- [x] Service worker fonctionne
- [x] Mode offline basique fonctionne

**Reference:** #[[file:PRODUCTION_ROADMAP.md]] TÂCHE 9

---

### TASK-9.3: Optimiser performances frontend ✅
**Estimate:** 3h  
**Dependencies:** TASK-9.1, TASK-9.2  
**Files:**
- `frontend/vite.config.ts`
- `frontend/src/components/*`

**Steps:**
1. Analyser bundle avec `vite-plugin-visualizer`
2. Optimiser imports (tree shaking)
3. Compresser images
4. Configurer code splitting
5. Tester avec Lighthouse

**Acceptance:**
- [x] Score Lighthouse > 90
- [x] Bundle size réduit
- [x] First Contentful Paint < 1.5s
- [x] Time to Interactive < 3s

**Reference:** #[[file:PRODUCTION_ROADMAP.md]] TÂCHE 9

---

### TASK-10.1: Créer scripts de déploiement
**Estimate:** 3h  
**Dependencies:** TASK-2.3  
**Files:**
- `scripts/deploy-production.sh`
- `scripts/backup-cron.sh`

**Steps:**
1. Créer `scripts/deploy-production.sh`
2. Implémenter backup pré-déploiement
3. Implémenter déploiement avec health check
4. Implémenter rollback
5. Créer `scripts/backup-cron.sh`
6. Tester sur serveur de staging

**Acceptance:**
- [x] Script de déploiement fonctionne
- [x] Backup automatique avant déploiement
- [x] Health check après déploiement
- [x] Rollback fonctionne
- [x] Script de backup fonctionne

**Reference:** #[[file:PRODUCTION_ROADMAP.md]] TÂCHE 10

---

### TASK-10.2: Configurer SSL/TLS
**Estimate:** 2h  
**Dependencies:** None  
**Files:**
- `nginx/nginx-ssl.conf`

**Steps:**
1. Installer certbot sur serveur
2. Générer certificats Let's Encrypt
3. Créer `nginx/nginx-ssl.conf`
4. Configurer redirection HTTP → HTTPS
5. Configurer HSTS
6. Tester avec SSL Labs

**Acceptance:**
- [x] Certificats SSL installés
- [x] HTTPS actif
- [x] Redirection HTTP → HTTPS fonctionne
- [x] Score SSL Labs: A+
- [x] HSTS configuré

**Reference:** #[[file:PRODUCTION_ROADMAP.md]] TÂCHE 10

---

### TASK-10.3: Configurer backups automatiques
**Estimate:** 2h  
**Dependencies:** TASK-10.1  
**Files:**
- `scripts/backup-cron.sh`
- Crontab serveur

**Steps:**
1. Configurer crontab pour backups quotidiens
2. Tester backup PostgreSQL
3. Tester backup fichiers media
4. Configurer retention (7 jours)
5. Optionnel: Upload vers S3
6. Tester restauration

**Acceptance:**
- [x] Backups quotidiens automatiques
- [x] Backup DB + media
- [x] Retention 7 jours
- [x] Restauration testée et fonctionnelle

**Reference:** #[[file:PRODUCTION_ROADMAP.md]] TÂCHE 10

---

### TASK-10.4: Documentation finale
**Estimate:** 1h  
**Dependencies:** All previous tasks  
**Files:**
- `DEPLOYMENT.md`
- `README.md`

**Steps:**
1. Créer `DEPLOYMENT.md` avec guide complet
2. Documenter procédures de déploiement
3. Documenter procédures de rollback
4. Documenter procédures de backup/restore
5. Mettre à jour README.md

**Acceptance:**
- [x] Guide de déploiement complet
- [x] Procédures documentées
- [x] README à jour
- [x] Checklist de production complète

**Reference:** #[[file:PRODUCTION_ROADMAP.md]] TÂCHE 10

---

# Testing Strategy

## Test Coverage Goals

- **Backend:** > 70% code coverage
- **Frontend:** > 70% code coverage
- **Critical paths:** 100% coverage (auth, payments)

## Test Types

### Unit Tests (Backend)
- Models: validation, methods, properties
- Serializers: validation, transformation
- Services: business logic
- Utilities: helper functions

### Integration Tests (Backend)
- API endpoints: request/response
- Authentication flow: login, logout, refresh
- Database operations: CRUD, transactions
- Cache operations: set, get, invalidate

### Component Tests (Frontend)
- UI components: rendering, interactions
- Forms: validation, submission
- Routing: navigation, guards
- State management: React Query hooks

### E2E Tests (Optional)
- User flows: registration → login → dashboard
- Critical paths: payment flow, document purchase
- Cross-browser testing

## Test Data Strategy

### Fixtures (Backend)
```python
@pytest.fixture
def user_data():
    return {
        'email': 'test@example.com',
        'password': 'TestPass123!',
        'first_name': 'Test',
        'last_name': 'User',
        'user_type': 'EXPLOITANT'
    }

@pytest.fixture
def authenticated_user(api_client, user_data):
    user = User.objects.create_user(**user_data)
    api_client.force_authenticate(user=user)
    return user
```

### Mocking (Frontend)
```typescript
vi.mock('../api/authSecure', () => ({
  login: vi.fn(),
  logout: vi.fn(),
  me: vi.fn(),
}));
```

## CI/CD Integration

Tests run automatically on:
- Every push to feature branches
- Every pull request
- Before deployment to production

Deployment blocked if:
- Any test fails
- Code coverage drops below threshold
- Security vulnerabilities found

---

# Deployment Strategy

## Environments

### Development (Local)
- **Purpose:** Development and debugging
- **Database:** SQLite or PostgreSQL local
- **Debug:** Enabled
- **Hot reload:** Enabled
- **Access:** localhost only

### Staging (Test Server)
- **Purpose:** Pre-production testing
- **Database:** PostgreSQL (separate from prod)
- **Debug:** Disabled
- **Data:** Test data, refreshed weekly
- **Access:** Internal team only
- **URL:** staging.haroo.tg

### Production (Live Server)
- **Purpose:** Live application
- **Database:** PostgreSQL with replication
- **Debug:** Disabled
- **Data:** Real user data
- **Access:** Public
- **URL:** haroo.tg

## Deployment Process

### Manual Deployment (Initial)
```bash
# 1. Backup database
./scripts/deploy-production.sh backup

# 2. Deploy application
./scripts/deploy-production.sh deploy

# 3. If issues, rollback
./scripts/deploy-production.sh rollback
```

### Automated Deployment (CI/CD)
1. Developer merges PR to main
2. GitHub Actions CI runs tests
3. If tests pass, build Docker images
4. Push images to registry
5. SSH to production server
6. Backup database
7. Pull new images
8. Run migrations
9. Restart services
10. Health check
11. Notify team (Slack)

## Rollback Strategy

### Automatic Rollback
- Health check fails after deployment
- Error rate > 5% in first 5 minutes
- Response time > 2s (p95)

### Manual Rollback
```bash
# Rollback to previous version
./scripts/deploy-production.sh rollback

# Or rollback to specific version
git checkout v1.2.3
docker-compose down
docker-compose up -d
```

## Zero-Downtime Deployment

### Strategy: Blue-Green Deployment
1. Deploy new version (green) alongside current (blue)
2. Run health checks on green
3. Switch traffic from blue to green
4. Keep blue running for quick rollback
5. After 24h, shut down blue

### Implementation (Future)
- Use Docker Swarm or Kubernetes
- Load balancer (Nginx or HAProxy)
- Database migrations backward compatible

---

# Monitoring and Alerting

## Metrics to Monitor

### Application Metrics
- **Response time:** p50, p95, p99
- **Error rate:** 4xx, 5xx errors
- **Request rate:** requests per second
- **Active users:** concurrent users

### Infrastructure Metrics
- **CPU usage:** per container
- **Memory usage:** per container
- **Disk usage:** database, media files
- **Network:** bandwidth, latency

### Business Metrics
- **User registrations:** per day
- **Active users:** DAU, MAU
- **Transactions:** successful, failed
- **Revenue:** per day, per month

## Alerting Rules

### Critical Alerts (Immediate)
- Application down (health check fails)
- Error rate > 5%
- Database connection lost
- Disk usage > 90%

### Warning Alerts (15 min delay)
- Response time > 1s (p95)
- Error rate > 1%
- CPU usage > 80%
- Memory usage > 80%

### Info Alerts (Daily digest)
- New user registrations
- Failed login attempts
- Slow queries (> 1s)

## Alert Channels
- **Email:** Critical alerts to dev team
- **Slack:** All alerts to #alerts channel
- **SMS:** Critical alerts to on-call engineer (future)
- **PagerDuty:** 24/7 on-call rotation (future)

---

# Security Checklist

## Pre-Production

- [ ] All secrets in environment variables (not in code)
- [ ] DEBUG=False in production
- [ ] SECRET_KEY unique and secure (> 50 chars)
- [ ] ALLOWED_HOSTS configured
- [ ] CORS_ALLOWED_ORIGINS configured
- [ ] SSL/TLS certificates installed
- [ ] HTTPS redirect enabled
- [ ] HSTS enabled
- [ ] Security headers configured (X-Frame-Options, CSP, etc.)
- [ ] Rate limiting active
- [ ] JWT in HttpOnly cookies
- [ ] CSRF protection enabled
- [ ] SQL injection protection (ORM only)
- [ ] XSS protection (template escaping)
- [ ] File upload validation
- [ ] Password hashing (bcrypt)
- [ ] 2FA enabled for admin accounts
- [ ] Sentry configured (no PII in logs)
- [ ] Backups encrypted
- [ ] Database access restricted (firewall)
- [ ] SSH key-based authentication only
- [ ] Fail2ban configured
- [ ] Security updates automated

## Post-Production

- [ ] Security audit performed
- [ ] Penetration testing completed
- [ ] OWASP Top 10 vulnerabilities checked
- [ ] Dependency vulnerabilities scanned (Snyk, Dependabot)
- [ ] SSL Labs score: A+
- [ ] Security headers score: A+ (securityheaders.com)
- [ ] GDPR compliance reviewed
- [ ] Privacy policy published
- [ ] Terms of service published
- [ ] Incident response plan documented

---

# Performance Optimization Checklist

## Backend

- [ ] Database queries optimized (no N+1)
- [ ] Database indexes created
- [ ] Redis cache configured
- [ ] Cache invalidation strategy implemented
- [ ] Pagination implemented (cursor for large lists)
- [ ] API response time < 200ms (p95)
- [ ] Gunicorn workers configured (2-4 per CPU core)
- [ ] Connection pooling configured
- [ ] Slow query logging enabled
- [ ] Database query timeout configured

## Frontend

- [ ] Code splitting implemented
- [ ] Lazy loading for routes
- [ ] Images optimized (WebP, compression)
- [ ] Assets minified and compressed (gzip/brotli)
- [ ] CDN configured for static files
- [ ] Browser caching configured
- [ ] Service worker for offline support
- [ ] Lighthouse score > 90
- [ ] First Contentful Paint < 1.5s
- [ ] Time to Interactive < 3s
- [ ] Bundle size < 500KB (gzipped)

## Infrastructure

- [ ] HTTP/2 enabled
- [ ] Nginx caching configured
- [ ] Load balancing configured (future)
- [ ] Auto-scaling configured (future)
- [ ] CDN configured (Cloudflare, CloudFront)
- [ ] Database replication configured (future)
- [ ] Redis clustering configured (future)

---

# Maintenance Plan

## Daily Tasks (Automated)
- Database backups
- Log rotation
- Security updates check
- Health checks
- Performance monitoring

## Weekly Tasks
- Review error logs
- Review slow queries
- Check disk usage
- Review security alerts
- Update dependencies (minor versions)

## Monthly Tasks
- Full security audit
- Performance review
- Cost optimization review
- Backup restoration test
- Update dependencies (major versions)
- Team retrospective

## Quarterly Tasks
- Disaster recovery drill
- Penetration testing
- Architecture review
- Capacity planning
- Documentation update

---

# Success Criteria

## Technical Metrics

- [ ] **Uptime:** > 99.9% (< 43 minutes downtime/month)
- [ ] **Response time:** < 200ms (p95)
- [ ] **Error rate:** < 0.1%
- [ ] **Test coverage:** > 70%
- [ ] **Security score:** A+ (SSL Labs, Security Headers)
- [ ] **Performance score:** > 90 (Lighthouse)
- [ ] **Build time:** < 5 minutes
- [ ] **Deployment time:** < 10 minutes

## Business Metrics

- [ ] **User satisfaction:** > 4.5/5
- [ ] **Page load time:** < 2s
- [ ] **Conversion rate:** Baseline established
- [ ] **Support tickets:** < 5% of active users
- [ ] **Churn rate:** < 5% monthly

## Team Metrics

- [ ] **Deployment frequency:** > 1 per week
- [ ] **Lead time:** < 1 day (commit to production)
- [ ] **MTTR:** < 1 hour (mean time to recovery)
- [ ] **Change failure rate:** < 15%

---

# Timeline

## Week 1: Critical Security & Infrastructure
- Days 1-2: JWT cookies (TASK-1.1, TASK-1.2)
- Days 3-5: Docker setup (TASK-2.1, TASK-2.2, TASK-2.3)

## Week 2: CI/CD & Documentation
- Days 1-2: CI workflow (TASK-3.1)
- Days 3-4: CD workflow (TASK-3.2)
- Day 5: API documentation (TASK-4.1, TASK-4.2)

## Week 3: Performance & Monitoring
- Days 1-2: Rate limiting (TASK-5.1, TASK-5.2)
- Days 3-4: Performance optimization (TASK-6.1, TASK-6.2, TASK-6.3)
- Day 5: Monitoring setup (TASK-7.1, TASK-7.2, TASK-7.3)

## Week 4: Testing & Deployment
- Days 1-2: Backend tests (TASK-8.1, TASK-8.2)
- Days 3-4: Frontend tests & optimization (TASK-8.3, TASK-8.4, TASK-9.1, TASK-9.2, TASK-9.3)
- Day 5: Production deployment (TASK-10.1, TASK-10.2, TASK-10.3, TASK-10.4)

**Total Duration:** 4 weeks (~72 hours)

---

# Risk Management

## Identified Risks

### High Risk
1. **Data loss during migration**
   - Mitigation: Multiple backups, test restoration
   - Contingency: Rollback to previous version

2. **Downtime during deployment**
   - Mitigation: Blue-green deployment, health checks
   - Contingency: Quick rollback procedure

3. **Security vulnerability**
   - Mitigation: Security scanning, penetration testing
   - Contingency: Incident response plan

### Medium Risk
1. **Performance degradation**
   - Mitigation: Load testing, monitoring
   - Contingency: Scale resources, optimize queries

2. **Third-party service failure (Fedapay, SMS)**
   - Mitigation: Retry logic, fallback options
   - Contingency: Manual processing, user notification

3. **Team knowledge gaps**
   - Mitigation: Documentation, training
   - Contingency: External consultant

### Low Risk
1. **Browser compatibility issues**
   - Mitigation: Cross-browser testing
   - Contingency: Polyfills, graceful degradation

2. **Dependency conflicts**
   - Mitigation: Lock files, version pinning
   - Contingency: Rollback, alternative packages

---

# Glossary

- **CI/CD:** Continuous Integration / Continuous Deployment
- **JWT:** JSON Web Token
- **XSS:** Cross-Site Scripting
- **CSRF:** Cross-Site Request Forgery
- **CORS:** Cross-Origin Resource Sharing
- **HSTS:** HTTP Strict Transport Security
- **TTL:** Time To Live (cache duration)
- **p95:** 95th percentile (performance metric)
- **MTTR:** Mean Time To Recovery
- **DAU/MAU:** Daily/Monthly Active Users
- **ORM:** Object-Relational Mapping
- **CDN:** Content Delivery Network
- **PWA:** Progressive Web App
- **SPA:** Single Page Application

---

# Appendix

## Useful Commands

### Docker
```bash
# Build images
make build

# Start services
make up

# View logs
make logs

# Stop services
make down

# Shell into backend
make shell

# Run migrations
make migrate

# Run tests
make test
```

### Django
```bash
# Create superuser
docker-compose exec backend python manage.py createsuperuser

# Run migrations
docker-compose exec backend python manage.py migrate

# Collect static files
docker-compose exec backend python manage.py collectstatic

# Django shell
docker-compose exec backend python manage.py shell
```

### Database
```bash
# Backup database
docker-compose exec db pg_dump -U haroo_user haroo_db > backup.sql

# Restore database
docker-compose exec -T db psql -U haroo_user haroo_db < backup.sql

# Connect to database
docker-compose exec db psql -U haroo_user haroo_db
```

### Redis
```bash
# Connect to Redis
docker-compose exec redis redis-cli

# Check cache keys
docker-compose exec redis redis-cli KEYS "*"

# Flush cache
docker-compose exec redis redis-cli FLUSHALL
```

## External Resources

- [Django Best Practices](https://docs.djangoproject.com/en/4.2/topics/security/)
- [React Best Practices](https://react.dev/learn)
- [Docker Best Practices](https://docs.docker.com/develop/dev-best-practices/)
- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [12 Factor App](https://12factor.net/)
- [Sentry Documentation](https://docs.sentry.io/)
- [GitHub Actions Documentation](https://docs.github.com/en/actions)

