# Haroo - Plateforme Agricole Intelligente du Togo

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
