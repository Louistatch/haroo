# Guide d'Installation - Haroo

## Prérequis Installés

✅ Python 3.11
✅ Django 4.2.7
✅ Toutes les dépendances de base (voir requirements/base.txt)

## Structure Créée

Le projet Django Haroo a été initialisé avec succès avec la structure suivante:

```
haroo/
├── apps/                          # Applications Django
│   ├── core/                      # Fonctionnalités communes
│   ├── users/                     # Gestion utilisateurs (modèle User personnalisé)
│   ├── locations/                 # Découpage administratif (Région, Préfecture, Canton)
│   ├── documents/                 # Marketplace documents techniques
│   └── payments/                  # Intégration Fedapay
│
├── haroo/                         # Configuration Django
│   ├── settings/                  # Settings modulaires
│   │   ├── base.py               # Configuration de base
│   │   ├── dev.py                # Développement
│   │   ├── staging.py            # Staging
│   │   └── prod.py               # Production
│   ├── celery.py                 # Configuration Celery
│   └── urls.py                   # URLs principales
│
├── requirements/                  # Dépendances
│   ├── base.txt                  # Dépendances communes
│   ├── dev.txt                   # Développement
│   └── prod.txt                  # Production
│
├── .env                          # Variables d'environnement (dev)
├── .env.example                  # Template variables
├── .gitignore                    # Fichiers à ignorer
├── manage.py                     # Script Django
├── README.md                     # Documentation principale
└── ARCHITECTURE.md               # Documentation architecture
```

## Prochaines Étapes

### 1. Installer PostgreSQL (Optionnel pour dev)

Le projet est configuré pour utiliser PostgreSQL. Pour le développement, vous pouvez:

**Option A: Utiliser PostgreSQL**
```bash
# Installer PostgreSQL 14+
# Créer la base de données
createdb haroo_db
createuser haroo_user -P
```

**Option B: Utiliser SQLite (plus simple pour dev)**
Modifier `haroo/settings/dev.py`:
```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / 'db.sqlite3',
    }
}
```

### 2. Installer Redis (Optionnel pour dev)

Redis est utilisé pour le cache et Celery. Pour le développement:

**Option A: Installer Redis**
- Windows: https://github.com/microsoftarchive/redis/releases
- Linux: `sudo apt-get install redis-server`
- Mac: `brew install redis`

**Option B: Désactiver Redis temporairement**
Modifier `haroo/settings/dev.py`:
```python
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.dummy.DummyCache',
    }
}
```

### 3. Exécuter les Migrations

```bash
py manage.py makemigrations
py manage.py migrate
```

### 4. Créer un Superutilisateur

```bash
py manage.py createsuperuser
```

### 5. Lancer le Serveur

```bash
py manage.py runserver
```

Accéder à:
- Application: http://localhost:8000
- Admin: http://localhost:8000/admin

## Configuration PostGIS (Production)

Pour activer PostGIS en production:

1. Installer GDAL:
   - Windows: https://www.gisinternals.com/
   - Linux: `sudo apt-get install gdal-bin libgdal-dev`
   - Mac: `brew install gdal`

2. Activer l'extension PostgreSQL:
```sql
CREATE EXTENSION postgis;
```

3. Le modèle Canton utilisera automatiquement PointField

## Services Externes à Configurer

### Fedapay (Paiement Mobile)
1. Créer un compte sur https://fedapay.com
2. Obtenir les clés API (sandbox pour dev)
3. Configurer dans `.env`:
```
FEDAPAY_API_KEY=your_api_key
FEDAPAY_SECRET_KEY=your_secret_key
FEDAPAY_ENVIRONMENT=sandbox
```

### SMS Gateway
Configurer un service SMS (ex: Twilio, Nexmo) pour la vérification des numéros:
```
SMS_GATEWAY_API_KEY=your_api_key
SMS_GATEWAY_SENDER_ID=HAROO
```

### Stockage Cloud (Production)
Pour AWS S3:
```
USE_S3=True
AWS_ACCESS_KEY_ID=your_access_key
AWS_SECRET_ACCESS_KEY=your_secret_key
AWS_STORAGE_BUCKET_NAME=haroo-storage
```

## Tests

Exécuter les tests (une fois configurés):
```bash
pytest
```

## Commandes Utiles

```bash
# Vérifier la configuration
py manage.py check

# Créer une nouvelle migration
py manage.py makemigrations

# Appliquer les migrations
py manage.py migrate

# Créer un superutilisateur
py manage.py createsuperuser

# Collecter les fichiers statiques
py manage.py collectstatic

# Lancer le shell Django
py manage.py shell

# Lancer Celery worker
celery -A haroo worker -l info

# Lancer Celery beat
celery -A haroo beat -l info
```

## Dépannage

### Erreur GDAL
Si vous voyez une erreur GDAL, c'est normal en dev. Le projet est configuré pour fonctionner sans PostGIS en développement.

### Erreur Redis
Si Redis n'est pas installé, vous pouvez utiliser le cache dummy (voir étape 2).

### Erreur PostgreSQL
Vous pouvez utiliser SQLite en développement (voir étape 1).

## Support

Pour toute question:
- Documentation: README.md et ARCHITECTURE.md
- Spécifications: .kiro/specs/plateforme-agricole-togo/
