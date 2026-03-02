# Architecture du Projet Haroo

## Vue d'Ensemble

Haroo utilise une architecture Django modulaire avec des applications séparées pour chaque domaine fonctionnel.

## Structure des Applications

### apps/core
**Fonctionnalités communes**
- Modèles de base (TimeStampedModel)
- Utilitaires partagés
- Mixins réutilisables

### apps/users
**Gestion des utilisateurs**
- Modèle User personnalisé avec types de profils
- Authentification JWT
- Vérification SMS
- Profils spécifiques (Exploitant, Agronome, Ouvrier, etc.)

### apps/locations
**Découpage administratif du Togo**
- Modèles: Region, Prefecture, Canton
- Support PostGIS pour coordonnées géographiques
- API de recherche et filtrage

### apps/documents
**Marketplace de documents techniques**
- Templates dynamiques avec variables
- Génération de documents personnalisés
- Gestion des achats et téléchargements

### apps/payments
**Intégration Fedapay**
- Gestion des transactions
- Webhooks Fedapay
- Système d'escrow
- Calcul des commissions

## Configuration Modulaire

### haroo/settings/
- **base.py**: Configuration commune à tous les environnements
- **dev.py**: Configuration de développement
- **staging.py**: Configuration de staging
- **prod.py**: Configuration de production

## Services Externes

### PostgreSQL + PostGIS
- Base de données principale
- Extension PostGIS pour données géographiques
- En dev: PostgreSQL standard (sans PostGIS)

### Redis
- Cache (DB 1)
- Sessions (DB 0)
- Broker Celery (DB 2)
- Backend Celery (DB 3)

### Celery
- Tâches asynchrones
- Envoi d'emails
- Génération de documents
- Notifications

### Fedapay
- Paiement mobile togolais
- Sandbox en dev/staging
- Live en production

## Sécurité

### Authentification
- JWT tokens (access + refresh)
- Vérification SMS obligatoire
- 2FA pour comptes institutionnels

### Protection des Données
- HTTPS/TLS 1.3 en production
- Chiffrement AES-256 pour données sensibles
- Hachage bcrypt pour mots de passe
- CORS configuré par environnement

### Validation
- Django Forms pour validation backend
- Sanitization des uploads
- Scan antivirus pour fichiers
- Rate limiting sur API

## Performance

### Cache
- Redis pour cache applicatif
- Cache des requêtes fréquentes (découpage administratif)
- TTL configurables par type de données

### Optimisation Base de Données
- Index sur champs fréquemment recherchés
- select_related et prefetch_related
- Pagination (50 éléments par page)

### Stockage
- Fichiers statiques: CDN en production
- Media: S3/Cloudinary en production
- Système de fichiers local en dev

## Monitoring

### Logs
- Niveau DEBUG en dev
- Niveau INFO en staging
- Niveau WARNING en production
- Rotation automatique des logs

### Sentry (Production)
- Monitoring des erreurs
- Alertes en temps réel
- Traces de performance

## Déploiement

### Environnements
1. **Développement**: Local avec SQLite/PostgreSQL
2. **Staging**: Serveur de test avec données de test
3. **Production**: Serveur de production avec données réelles

### CI/CD
- Tests automatiques avant déploiement
- Migrations automatiques
- Collecte des fichiers statiques
- Redémarrage des services

## Évolution Future

### Phase MVP (Actuelle)
- ✅ Infrastructure de base
- ✅ Authentification
- ✅ Découpage administratif
- ✅ Marketplace documents
- ✅ Paiements Fedapay

### Phase V1 (Prochaine)
- Recrutement agronomes
- Système de notation
- Messagerie interne
- Dashboard administrateur

### Phase V2
- Emploi saisonnier
- Prévente agricole
- Intelligence de marché
- Abonnements premium

### Phase V3
- Optimisation logistique
- Irrigation intelligente
- Recommandations de cultures
- Dashboards institutionnels
