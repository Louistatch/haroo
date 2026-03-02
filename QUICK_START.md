# 🚀 Guide de Démarrage Rapide - Plateforme Agricole Togo

## Prérequis

- Python 3.10+
- Node.js 18+
- PostgreSQL 14+
- Redis 7+

## Installation Rapide

### 1. Backend Django

```bash
# Créer l'environnement virtuel
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
.venv\Scripts\activate     # Windows

# Installer les dépendances
pip install -r requirements.txt

# Configurer les variables d'environnement
cp .env.example .env
# Éditer .env avec vos configurations

# Appliquer les migrations
python manage.py migrate

# Charger les données administratives du Togo
python manage.py populate_administrative_data

# Créer un superutilisateur
python manage.py createsuperuser

# Lancer le serveur
python manage.py runserver
```

Le backend sera accessible sur **http://127.0.0.1:8000**

### 2. Frontend React

```bash
# Aller dans le dossier frontend
cd frontend

# Installer les dépendances
npm install

# Lancer le serveur de développement
npm run dev
```

Le frontend sera accessible sur **http://localhost:3000**

## Accès Rapide

### URLs Principales
- **Frontend**: http://localhost:3000
- **Backend API**: http://127.0.0.1:8000/api/v1/
- **Admin Django**: http://127.0.0.1:8000/admin/

### Comptes de Test

| Utilisateur | Téléphone | Mot de passe | Rôle |
|-------------|-----------|--------------|------|
| exploitant_demo | +22890000001 | Demo123! | Exploitant |
| agronome_demo | +22890000002 | Demo123! | Agronome |
| admin_demo | +22890000003 | Admin123! | Admin |

## Endpoints API Principaux

### Authentification
```bash
# Connexion
POST /api/v1/auth/login
{
  "phone_number": "+22890000001",
  "password": "Demo123!"
}

# Inscription
POST /api/v1/auth/register
{
  "phone_number": "+228...",
  "password": "...",
  "first_name": "...",
  "last_name": "...",
  "user_type": "EXPLOITANT"
}
```

### Découpage Administratif
```bash
GET /api/v1/regions
GET /api/v1/regions/{id}/prefectures
GET /api/v1/prefectures/{id}/cantons
GET /api/v1/cantons/search?q=Lomé
```

### Agronomes
```bash
# Annuaire public
GET /api/v1/users/agronomists?region=1&specialisation=maraichage

# Détails publics
GET /api/v1/users/agronomists/{id}

# Inscription agronome
POST /api/v1/users/agronomists/register

# Validation (admin)
POST /api/v1/users/agronomists/{id}/validate
```

### Missions
```bash
# Créer une mission
POST /api/v1/missions
{
  "title": "Conseil en maraîchage",
  "description": "...",
  "budget": 50000,
  "agronome_id": 2
}

# Accepter une mission
POST /api/v1/missions/{id}/accept

# Compléter une mission
POST /api/v1/missions/{id}/complete
```

## Tests

```bash
# Lancer tous les tests
python manage.py test

# Tests d'une app spécifique
python manage.py test apps.users
python manage.py test apps.missions

# Avec couverture
coverage run --source='.' manage.py test
coverage report
```

## Commandes Utiles

### Django
```bash
# Créer une migration
python manage.py makemigrations

# Appliquer les migrations
python manage.py migrate

# Shell Django
python manage.py shell

# Collecter les fichiers statiques
python manage.py collectstatic
```

### Frontend
```bash
# Build de production
npm run build

# Preview du build
npm run preview

# Linter
npm run lint
```

## Structure du Projet

```
.
├── apps/                    # Applications Django
│   ├── users/              # Gestion utilisateurs
│   ├── locations/          # Découpage administratif
│   ├── documents/          # Documents techniques
│   ├── payments/           # Paiements Fedapay
│   ├── missions/           # Système de missions
│   ├── compliance/         # Conformité RGPD
│   └── institutional/      # Dashboard institutionnel
├── frontend/               # Application React
│   ├── src/
│   │   ├── components/    # Composants réutilisables
│   │   ├── pages/         # Pages de l'application
│   │   ├── hooks/         # Hooks personnalisés
│   │   ├── styles/        # Styles CSS
│   │   └── utils/         # Utilitaires
│   └── public/            # Assets statiques
├── haroo/                 # Configuration Django
│   └── settings/          # Settings par environnement
└── .kiro/                 # Spécifications et tâches
    └── specs/
```

## Dépannage

### Backend ne démarre pas
```bash
# Vérifier PostgreSQL
psql -U postgres -c "SELECT version();"

# Vérifier Redis
redis-cli ping

# Réinitialiser la base de données
python manage.py flush
python manage.py migrate
```

### Frontend ne compile pas
```bash
# Nettoyer node_modules
rm -rf node_modules package-lock.json
npm install

# Vérifier la version de Node
node --version  # Doit être 18+
```

### Erreur de connexion API
- Vérifier que le backend tourne sur le port 8000
- Vérifier le fichier `frontend/.env`
- Vérifier les CORS dans `haroo/settings/dev.py`

## Variables d'Environnement

### Backend (.env)
```env
DEBUG=True
SECRET_KEY=your-secret-key
DATABASE_URL=postgresql://user:pass@localhost:5432/haroo
REDIS_URL=redis://localhost:6379/0
FEDAPAY_API_KEY=your-fedapay-key
CLOUDINARY_URL=cloudinary://...
```

### Frontend (.env)
```env
VITE_API_BASE_URL=http://localhost:8000/api/v1
```

## Support

Pour toute question ou problème:
1. Consulter la documentation dans `/docs`
2. Vérifier les issues GitHub
3. Contacter l'équipe de développement

---

**Bon développement! 🌾**
