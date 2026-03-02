# Structure du Projet Haroo

## 🌾 Nom du Projet

**Haroo** - Plateforme Agricole Intelligente du Togo

## 📋 Clarification Importante

Il s'agit d'un **seul projet** avec plusieurs fonctionnalités:

- ✅ **Nom du projet**: Haroo
- ✅ **Tagline**: Plateforme Agricole Intelligente du Togo
- ✅ **Domaine**: haroo.tg
- ✅ **Email**: noreply@haroo.tg

### ⚠️ Confusion à éviter

Les deux specs dans `.kiro/specs/` ne sont PAS deux projets différents:

1. **plateforme-agricole-togo/** - Spec principale du projet complet
2. **marketplace-documents-finalisation/** - Spec pour une fonctionnalité spécifique

Le "marketplace-documents-finalisation" est simplement une **fonctionnalité** du projet Haroo, pas un projet séparé.

---

## 🏗️ Architecture du Projet

### Backend Django (haroo/)

```
haroo/
├── apps/                          # Applications Django
│   ├── core/                      # Fonctionnalités communes
│   ├── users/                     # Gestion utilisateurs
│   ├── locations/                 # Découpage administratif Togo
│   ├── documents/                 # 📄 Marketplace documents techniques
│   ├── payments/                  # 💳 Intégration Fedapay
│   ├── missions/                  # 🤝 Missions agronomes
│   ├── institutional/             # 🏛️ Dashboards institutionnels
│   ├── compliance/                # ⚖️ Conformité RGPD
│   └── ratings/                   # ⭐ Système de notation
├── haroo/                         # Configuration Django
│   ├── settings/                  # Settings modulaires
│   │   ├── base.py               # Configuration de base
│   │   ├── dev.py                # Développement
│   │   ├── staging.py            # Staging
│   │   └── prod.py               # Production
│   ├── urls.py                   # URLs principales
│   ├── wsgi.py                   # WSGI application
│   └── celery.py                 # Configuration Celery
├── templates/                     # Templates Django
│   └── emails/                   # 📧 Templates d'emails
│       ├── base_email.html       # Template de base
│       ├── purchase_confirmation.html/txt
│       ├── expiration_reminder.html/txt
│       └── link_regenerated.html/txt
└── manage.py                      # Script de gestion Django
```

### Frontend React (frontend/)

```
frontend/
├── src/
│   ├── pages/                     # Pages React
│   │   ├── Landing.tsx           # Page d'accueil
│   │   ├── Home.tsx              # Dashboard utilisateur
│   │   ├── Documents.tsx         # 📄 Marketplace documents
│   │   ├── PurchaseHistory.tsx   # 📋 Historique achats
│   │   ├── PaymentSuccess.tsx    # ✅ Confirmation paiement
│   │   ├── Agronomists.tsx       # 👨‍🌾 Annuaire agronomes
│   │   └── Dashboard.tsx         # 📊 Tableau de bord
│   ├── components/               # Composants réutilisables
│   ├── api/                      # Appels API
│   ├── hooks/                    # Hooks personnalisés
│   ├── styles/                   # Fichiers CSS
│   └── utils/                    # Utilitaires
└── package.json
```

---

## 🎯 Fonctionnalités du Projet Haroo

### 1. 📄 Marketplace de Documents Techniques (apps/documents)
**Status**: En cours de finalisation (Phase 2.2)

- Vente de comptes d'exploitation
- Vente d'itinéraires techniques
- Génération dynamique de documents
- Paiement via Fedapay
- Téléchargement sécurisé avec tokens
- Système d'emails automatiques

**Pages Frontend**:
- `/documents` - Liste des documents
- `/purchases` - Historique d'achats
- `/payment/success` - Confirmation paiement

### 2. 👨‍🌾 Recrutement d'Agronomes (apps/missions)
**Status**: Implémenté

- Annuaire d'agronomes validés
- Système de notation et avis
- Profils détaillés avec spécialisations
- Vérification des diplômes

**Pages Frontend**:
- `/agronomists` - Annuaire agronomes

### 3. 💳 Système de Paiement (apps/payments)
**Status**: Implémenté

- Intégration Fedapay (Mobile Money)
- Système d'escrow
- Gestion des commissions
- Webhooks pour confirmations

### 4. 👤 Gestion Utilisateurs (apps/users)
**Status**: Implémenté

- Types de profils: Exploitant, Agronome, Ouvrier, Institutionnel
- Authentification JWT
- Vérification SMS
- 2FA pour comptes institutionnels
- Vérification de ferme avec GPS

### 5. 📍 Découpage Administratif (apps/locations)
**Status**: Implémenté

- Régions, Préfectures, Cantons du Togo
- Support PostGIS pour coordonnées
- API de recherche géographique

### 6. ⚖️ Conformité RGPD (apps/compliance)
**Status**: Implémenté

- Politiques de rétention des données
- Anonymisation automatique
- Gestion des consentements
- Export de données utilisateur

### 7. ⭐ Système de Notation (apps/ratings)
**Status**: Implémenté

- Notation des agronomes
- Calcul de réputation
- Avis et commentaires
- Modération

### 8. 🏛️ Dashboards Institutionnels (apps/institutional)
**Status**: Implémenté

- Accès pour partenaires gouvernementaux
- Statistiques sectorielles
- Rapports personnalisés

---

## 🎨 Branding Unifié

### Nom et Identité
- **Nom**: Haroo
- **Tagline**: Plateforme Agricole Intelligente du Togo
- **Logo**: 🌾 (emoji blé)
- **Couleurs**:
  - Vert principal: `#2e7d32`
  - Vert secondaire: `#4caf50`
  - Vert clair: `#e8f5e9`

### Domaines et Emails
- **Domaine**: haroo.tg
- **Email système**: noreply@haroo.tg
- **Email support**: support@haroo.tg
- **Email admin**: admin@haroo.tg

### Réseaux Sociaux (à configurer)
- Facebook: facebook.com/haroo.tg
- Twitter: @haroo_tg
- Instagram: @haroo.tg

---

## 📦 Technologies Utilisées

### Backend
- Django 4.2.7
- Django REST Framework
- PostgreSQL + PostGIS
- Redis (cache + Celery)
- Celery (tâches asynchrones)
- Premailer (optimisation emails)

### Frontend
- React 18
- TypeScript
- Vite
- CSS modules

### Services Externes
- Fedapay (paiement mobile)
- AWS S3 / Cloudinary (stockage)
- Twilio (SMS)
- Sentry (monitoring)

---

## 🚀 Environnements

### Développement
- Backend: `http://localhost:8000`
- Frontend: `http://localhost:5173`
- Database: PostgreSQL local
- Email: MailHog (localhost:8025)

### Staging
- Backend: `https://staging-api.haroo.tg`
- Frontend: `https://staging.haroo.tg`
- Database: PostgreSQL staging
- Email: Mailtrap

### Production
- Backend: `https://api.haroo.tg`
- Frontend: `https://haroo.tg`
- Database: PostgreSQL production
- Email: SMTP production

---

## 📝 État d'Avancement

### ✅ Complété
- Infrastructure de base
- Authentification et utilisateurs
- Découpage administratif
- Système de paiement Fedapay
- Marketplace documents (frontend)
- Recrutement agronomes
- Système de notation
- Conformité RGPD
- Dashboards institutionnels

### 🔄 En Cours
- **Phase 2.2**: Email templates (99% complété)
  - ✅ Templates créés
  - ✅ Premailer intégré
  - ⏳ Tests sur clients email (Gmail, Outlook, Apple Mail)

### 📋 À Venir
- Phase 2.3: Configuration Celery
- Phase 2.4: Intégration EmailService dans views
- Phase 2.5: Tests d'intégration emails
- Phase 3: Améliorations admin Django
- Phase 4: Enhancements API

---

## 📚 Documentation

### Documents Principaux
- `README.md` - Vue d'ensemble du projet
- `ARCHITECTURE.md` - Architecture technique
- `PROJET_HAROO_STRUCTURE.md` - Ce document
- `EMAIL_SERVICE_SUMMARY.md` - Documentation EmailService
- `EMAIL_TESTING_GUIDE.md` - Guide de test des emails

### Specs
- `.kiro/specs/plateforme-agricole-togo/` - Spec principale
- `.kiro/specs/marketplace-documents-finalisation/` - Spec marketplace

### Guides
- `DEMARRAGE_RAPIDE.md` - Guide de démarrage
- `QUICK_START.md` - Quick start guide
- `MARKETPLACE_README.md` - Guide marketplace

---

## 🎯 Vision du Projet

Haroo vise à devenir la plateforme de référence pour l'agriculture moderne au Togo, en offrant:

1. **Accès à l'information** - Documents techniques de qualité
2. **Mise en relation** - Agronomes et exploitants
3. **Facilitation des transactions** - Paiement mobile intégré
4. **Intelligence de marché** - Données et prévisions
5. **Support institutionnel** - Outils pour partenaires gouvernementaux

---

## 📞 Contact

- **Email**: support@haroo.tg
- **Téléphone**: +228 XX XX XX XX
- **Adresse**: Lomé, Togo

---

**Dernière mise à jour**: 2024
**Version**: 1.0.0 (MVP)
