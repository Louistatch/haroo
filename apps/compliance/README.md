# Module de Conformité Réglementaire

Ce module implémente les exigences de conformité réglementaire togolaise pour la plateforme.

## Exigences Implémentées

### Exigence 45.1 - Protection des données personnelles
- Respect de la loi togolaise sur la protection des données
- Chiffrement des données sensibles
- Contrôle d'accès strict

### Exigence 45.2 - CGU et Politique de Confidentialité
- **Endpoints:**
  - `GET /api/v1/compliance/cgu/` - Affiche les CGU en français
  - `GET /api/v1/compliance/privacy-policy/` - Affiche la politique de confidentialité

### Exigence 45.3 - Acceptation explicite des CGU
- **Endpoints:**
  - `POST /api/v1/compliance/cgu-acceptances/accept/` - Enregistre l'acceptation des CGU
  - `GET /api/v1/compliance/cgu-acceptances/current_status/` - Vérifie le statut d'acceptation
  - `GET /api/v1/compliance/cgu-acceptances/` - Historique des acceptations

- **Données enregistrées:**
  - Version des CGU acceptée
  - Date et heure d'acceptation
  - Adresse IP
  - User agent du navigateur

### Exigence 45.4 - Suppression de compte et données
- **Endpoints:**
  - `POST /api/v1/compliance/account-deletion/request_deletion/` - Demande de suppression
  - `GET /api/v1/compliance/account-deletion/` - Liste des demandes
  - `POST /api/v1/compliance/account-deletion/{id}/process/` - Traiter une demande (admin)

- **Processus:**
  1. L'utilisateur demande la suppression
  2. Export automatique des données personnelles
  3. Anonymisation des données (pas de suppression complète)
  4. Conservation des données de transaction (10 ans)

### Exigence 45.5 - Reçus électroniques
- **Endpoints:**
  - `GET /api/v1/compliance/receipts/` - Liste des reçus
  - `GET /api/v1/compliance/receipts/{id}/` - Détails d'un reçu
  - `GET /api/v1/compliance/receipts/{id}/download_pdf/` - Télécharger le PDF

- **Génération automatique:**
  - Reçu créé automatiquement pour chaque transaction réussie
  - Format PDF conforme à la réglementation togolaise
  - Numérotation unique: REC-YYYY-NNNNN
  - Inclut TVA (18%)

### Exigence 45.6 - Rétention des données
- **Politiques configurées:**
  - Transactions: 10 ans (conformité fiscale)
  - Données utilisateur: 5 ans après suppression
  - Logs système: 90 jours
  - Documents: 5 ans

- **Endpoints:**
  - `GET /api/v1/compliance/retention-policies/` - Liste des politiques

### Exigence 33.6 - Export des données personnelles
- **Endpoint:**
  - `POST /api/v1/compliance/data-export/` - Exporte toutes les données au format JSON

- **Données exportées:**
  - Informations de profil
  - Historique des transactions
  - Acceptations CGU
  - Données spécifiques au type d'utilisateur

## Utilisation

### Accepter les CGU lors de l'inscription

```python
POST /api/v1/compliance/cgu-acceptances/accept/
{
    "accepted": true
}
```

### Demander la suppression de compte

```python
POST /api/v1/compliance/account-deletion/request_deletion/
{
    "confirm": true,
    "reason": "Je n'utilise plus la plateforme"
}
```

### Exporter ses données personnelles

```python
POST /api/v1/compliance/data-export/
{
    "format": "json"
}
```

### Télécharger un reçu

```python
GET /api/v1/compliance/receipts/{id}/download_pdf/
```

## Administration

### Initialiser les politiques de rétention

```bash
python manage.py init_retention_policies
```

### Traiter une demande de suppression (admin)

```python
POST /api/v1/compliance/account-deletion/{id}/process/
```

## Modèles

### CGUAcceptance
Enregistre chaque acceptation des CGU avec horodatage et traçabilité.

### ElectronicReceipt
Reçus électroniques conformes pour toutes les transactions.

### DataRetentionPolicy
Politiques de rétention configurables par type de données.

### AccountDeletionRequest
Demandes de suppression de compte avec export automatique des données.

## Services

### CGUService
- Gestion des versions CGU
- Enregistrement des acceptations
- Vérification du statut

### ReceiptService
- Génération de numéros uniques
- Création de reçus PDF
- Calcul automatique de la TVA

### DataExportService
- Export complet des données utilisateur
- Format JSON structuré
- Respect de la vie privée

### AccountDeletionService
- Traitement des demandes de suppression
- Anonymisation des données
- Conservation des données légales

### DataRetentionService
- Gestion des politiques de rétention
- Vérification des périodes de conservation
- Configuration par type de données

## Sécurité

- Authentification requise pour tous les endpoints (sauf CGU/Privacy Policy)
- Permissions admin pour le traitement des suppressions
- Traçabilité complète des actions
- Anonymisation au lieu de suppression complète
- Conservation des données légales obligatoires

## Tests

Les tests unitaires couvrent:
- Acceptation des CGU
- Génération de reçus
- Export des données
- Suppression de compte
- Politiques de rétention

## Conformité

Ce module assure la conformité avec:
- Loi togolaise sur la protection des données personnelles
- Obligations fiscales (conservation 10 ans)
- Droit à l'oubli (avec exceptions légales)
- Transparence et traçabilité
