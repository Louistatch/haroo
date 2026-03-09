# Haroo - Plateforme Agricole Intelligente du Togo

![CI Status](https://github.com/your-username/haroo/workflows/CI%20-%20Tests%20et%20Qualité/badge.svg)
![CD Status](https://github.com/your-username/haroo/workflows/CD%20-%20Déploiement%20Production/badge.svg)
[![codecov](https://codecov.io/gh/your-username/haroo/branch/main/graph/badge.svg)](https://codecov.io/gh/your-username/haroo)
![Python](https://img.shields.io/badge/python-3.11-blue.svg)
![Django](https://img.shields.io/badge/django-4.2.7-green.svg)
![React](https://img.shields.io/badge/react-18-blue.svg)
![License](https://img.shields.io/badge/license-MIT-blue.svg)

## Description

Haroo est une plateforme numérique complète destinée à moderniser le secteur agricole togolais. Elle intègre plusieurs services:

- 🌾 **Marketplace de documents techniques** - Vente de comptes d'exploitation et itinéraires techniques
- 👨‍🌾 **Recrutement d'agronomes** - Mise en relation avec des professionnels validés
- 🤝 **Emploi saisonnier** - Gestion de contrats d'ouvriers agricoles
- 📊 **Prévente agricole** - Engagement de vente de production future
- 📈 **Intelligence de marché** - Prévisions de prix et analyse de demande
- 🚚 **Optimisation logistique** - Calcul d'itinéraires et coûts de transport
- 💧 **Irrigation intelligente** - Cartographie des zones irrigables
- 🏛️ **Dashboards institutionnels** - Suivi sectoriel pour partenaires gouvernementaux

## Stack Technique

- **Backend**: Django 4.2.7 + Django REST Framework
- **Base de données**: PostgreSQL + PostGIS
- **Cache**: Redis
- **Tâches asynchrones**: Celery
- **Paiement**: Fedapay (paiement mobile togolais)
- **Stockage**: AWS S3 / Cloudinary

## Installation

### Prérequis

- Python 3.11+
- PostgreSQL 14+ avec extension PostGIS
- Redis 7+

### Configuration

1. Cloner le repository

```bash
git clone <repository-url>
cd haroo
```

2. Créer un environnement virtuel

```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
```

3. Installer les dépendances

```bash
pip install -r requirements/dev.txt
```

4. Configurer les variables d'environnement

```bash
cp .env.example .env
# Éditer .env avec vos configurations
```

5. Créer la base de données PostgreSQL

```sql
CREATE DATABASE haroo_db;
CREATE USER haroo_user WITH PASSWORD 'your_password';
ALTER ROLE haroo_user SET client_encoding TO 'utf8';
ALTER ROLE haroo_user SET default_transaction_isolation TO 'read committed';
ALTER ROLE haroo_user SET timezone TO 'Africa/Lome';
GRANT ALL PRIVILEGES ON DATABASE haroo_db TO haroo_user;

-- Activer PostGIS
\c haroo_db
CREATE EXTENSION postgis;
```

6. Exécuter les migrations

```bash
python manage.py migrate
```

7. Créer un superutilisateur

```bash
python manage.py createsuperuser
```

8. Lancer le serveur de développement

```bash
python manage.py runserver
```

## Structure du Projet

```
haroo/
├── apps/                      # Applications Django
│   ├── core/                  # Fonctionnalités communes
│   ├── users/                 # Gestion utilisateurs
│   ├── locations/             # Découpage administratif
│   ├── documents/             # Marketplace documents
│   └── payments/              # Intégration Fedapay
├── haroo/                     # Configuration Django
│   ├── settings/              # Settings modulaires
│   │   ├── base.py           # Configuration de base
│   │   ├── dev.py            # Configuration développement
│   │   ├── staging.py        # Configuration staging
│   │   └── prod.py           # Configuration production
│   ├── urls.py               # URLs principales
│   └── wsgi.py               # WSGI application
├── requirements/              # Dépendances
│   ├── base.txt              # Dépendances communes
│   ├── dev.txt               # Dépendances développement
│   └── prod.txt              # Dépendances production
├── .env.example              # Template variables d'environnement
├── .gitignore                # Fichiers à ignorer
├── manage.py                 # Script de gestion Django
└── README.md                 # Documentation
```

## Configuration des Environnements

### Développement

```bash
export DJANGO_SETTINGS_MODULE=haroo.settings.dev
python manage.py runserver
```

### Staging

```bash
export DJANGO_SETTINGS_MODULE=haroo.settings.staging
gunicorn haroo.wsgi:application
```

### Production

```bash
export DJANGO_SETTINGS_MODULE=haroo.settings.prod
gunicorn haroo.wsgi:application --bind 0.0.0.0:8000
```

## Services Externes

### Fedapay (Paiement Mobile)

Configurer les clés API dans `.env`:
```
FEDAPAY_API_KEY=your_api_key
FEDAPAY_SECRET_KEY=your_secret_key
FEDAPAY_ENVIRONMENT=sandbox  # ou 'live' en production
```

### Redis (Cache et Sessions)

```
REDIS_URL=redis://localhost:6379/0
REDIS_CACHE_URL=redis://localhost:6379/1
```

### Celery (Tâches Asynchrones)

Lancer le worker Celery:
```bash
celery -A haroo worker -l info
```

Lancer Celery Beat (tâches planifiées):
```bash
celery -A haroo beat -l info
```

## Tests

Exécuter les tests:
```bash
pytest
```

Avec couverture:
```bash
pytest --cov=apps --cov-report=html
```

## Déploiement

### Checklist Production

- [ ] Configurer `SECRET_KEY` unique et sécurisée
- [ ] Définir `DEBUG=False`
- [ ] Configurer `ALLOWED_HOSTS`
- [ ] Activer HTTPS/TLS
- [ ] Configurer le stockage cloud (S3/Cloudinary)
- [ ] Configurer Sentry pour le monitoring
- [ ] Configurer les backups de base de données
- [ ] Tester l'intégration Fedapay en mode live
- [ ] Configurer les certificats SSL
- [ ] Activer le 2FA pour les comptes administrateurs

## Licence

Propriétaire - Tous droits réservés

## Contact

Pour toute question ou support, contactez: support@haroo.tg


## 🐳 Déploiement avec Docker

### Prérequis

- Docker 20.10+
- Docker Compose 2.0+

### Démarrage Rapide

```bash
# Cloner le repository
git clone <repository-url>
cd haroo

# Copier les variables d'environnement
cp .env.docker .env

# Build et démarrer les services
make build
make up

# Voir les logs
make logs

# Accéder à l'application
# Frontend: http://localhost:5000
# Backend: http://localhost:8000
# Admin: http://localhost:8000/admin
```

### Commandes Makefile

```bash
make help              # Afficher toutes les commandes
make build             # Build les images Docker
make up                # Démarrer tous les services
make down              # Arrêter tous les services
make logs              # Afficher les logs
make shell             # Shell dans le backend
make migrate           # Exécuter les migrations
make test              # Exécuter les tests
make lint              # Vérifier la qualité du code
make format            # Formater le code
make backup-db         # Backup de la base de données
```

### Services Docker

- **db**: PostgreSQL 14 + PostGIS
- **redis**: Redis 7 (cache + Celery)
- **backend**: Django + Gunicorn
- **frontend**: React + Nginx
- **celery_worker**: Worker Celery
- **celery_beat**: Scheduler Celery

## 🚀 CI/CD Pipeline

### Workflows GitHub Actions

Le projet utilise GitHub Actions pour l'intégration et le déploiement continus:

#### CI - Tests et Qualité (`.github/workflows/ci.yml`)

Déclenché sur:
- Push vers `main` ou `develop`
- Pull Requests vers `main` ou `develop`

Jobs:
- **backend-tests**: Tests Django avec PostgreSQL + Redis
- **frontend-tests**: Lint, tests et build React
- **security-scan**: Scan de vulnérabilités avec Trivy
- **code-quality**: Vérification avec flake8, black, isort

#### CD - Déploiement Production (`.github/workflows/cd.yml`)

Déclenché sur:
- Merge dans `main`
- Push de tags `v*`

Jobs:
- **build-and-push**: Build et push des images Docker vers GitHub Container Registry
- **deploy**: Déploiement SSH automatique sur serveur de production

#### Release (`.github/workflows/release.yml`)

Déclenché sur:
- Push de tags `v*` (ex: `v1.0.0`)

Crée automatiquement une release GitHub avec changelog.

### Configuration des Secrets

Pour configurer le pipeline CI/CD, voir [GITHUB_SECRETS_SETUP.md](./GITHUB_SECRETS_SETUP.md)

Secrets requis:
- `PROD_HOST`: IP/domaine du serveur
- `PROD_USER`: Utilisateur SSH
- `PROD_SSH_KEY`: Clé privée SSH
- `PROD_PORT`: Port SSH (22)
- `SLACK_WEBHOOK_URL`: Webhook Slack (optionnel)

## 🧪 Tests

### Exécuter les tests

```bash
# Avec Docker
make test

# Avec couverture
make test-cov

# Sans Docker
pytest
pytest --cov=apps --cov-report=html
```

### Qualité du code

```bash
# Vérifier la qualité
make lint

# Formater le code
make format

# Manuellement
flake8 apps/ haroo/
black apps/ haroo/
isort apps/ haroo/
```

## 🚀 Déploiement Production

Pour un guide complet de déploiement, voir [DEPLOYMENT.md](./DEPLOYMENT.md).

```bash
# Déploiement
./scripts/deploy-production.sh deploy

# Rollback
./scripts/deploy-production.sh rollback

# Backup manuel
./scripts/backup-cron.sh

# Installer backup automatique (cron quotidien 02:00)
./scripts/backup-cron.sh setup-cron

# Restaurer un backup
./scripts/backup-cron.sh restore /opt/haroo/backups/haroo_db_XXXXXXXX.sql.gz

# Health check
./scripts/deploy-production.sh health
```

## 📚 Documentation

- [DEPLOYMENT.md](./DEPLOYMENT.md) - Guide de déploiement production complet
- [PRODUCTION_ROADMAP.md](./PRODUCTION_ROADMAP.md) - Roadmap complète avec code
- [IMPLEMENTATION_STATUS.md](./IMPLEMENTATION_STATUS.md) - Statut d'implémentation
- [TASK-1_COMPLETED.md](./TASK-1_COMPLETED.md) - Sécurité JWT avec cookies
- [TASK-3_COMPLETED.md](./TASK-3_COMPLETED.md) - Pipeline CI/CD
- [GITHUB_SECRETS_SETUP.md](./GITHUB_SECRETS_SETUP.md) - Configuration secrets GitHub
- [MIGRATION_JWT_COOKIES.md](./MIGRATION_JWT_COOKIES.md) - Guide migration JWT

## 🔒 Sécurité

### Fonctionnalités de Sécurité

- ✅ JWT dans cookies HttpOnly (protection XSS)
- ✅ CSRF protection activée
- ✅ Rate limiting multi-niveaux
- ✅ Scan de sécurité automatique (Trivy)
- ✅ HTTPS en production
- ✅ Secrets dans variables d'environnement
- ✅ Validation des entrées utilisateur
- ✅ Protection SQL injection (ORM)

### Rapporter une Vulnérabilité

Si vous découvrez une vulnérabilité de sécurité, veuillez envoyer un email à security@haroo.tg au lieu de créer une issue publique.

## 🤝 Contribution

Les contributions sont les bienvenues! Veuillez suivre ces étapes:

1. Fork le projet
2. Créer une branche feature (`git checkout -b feature/AmazingFeature`)
3. Commit vos changements (`git commit -m 'Add some AmazingFeature'`)
4. Push vers la branche (`git push origin feature/AmazingFeature`)
5. Ouvrir une Pull Request

### Standards de Code

- Suivre PEP 8 pour Python
- Utiliser black pour le formatage
- Utiliser isort pour les imports
- Écrire des tests pour les nouvelles fonctionnalités
- Documenter les fonctions et classes

## 📄 License

Ce projet est sous licence MIT. Voir le fichier [LICENSE](LICENSE) pour plus de détails.

## 👥 Équipe

- **Product Owner**: [Nom]
- **Tech Lead**: [Nom]
- **Backend Developers**: [Noms]
- **Frontend Developers**: [Noms]
- **DevOps**: [Nom]

## 📞 Contact

- **Email**: contact@haroo.tg
- **Website**: https://haroo.tg
- **Support**: support@haroo.tg

## 🙏 Remerciements

- Ministère de l'Agriculture du Togo
- Fedapay pour l'intégration des paiements mobiles
- Communauté open source Django et React

---

**Fait avec ❤️ au Togo 🇹🇬**
