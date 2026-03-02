# Task 15.2: Workflow de Validation des Exploitations - Résumé

## Objectif
Créer le workflow de validation administrative des exploitations agricoles permettant aux administrateurs de vérifier ou rejeter les demandes de vérification.

## Exigences Couvertes
- **10.4**: Validation de la cohérence entre superficie déclarée et documents fournis
- **10.5**: Attribution du statut Exploitant_Vérifié et déblocage des fonctionnalités premium
- **10.6**: Gestion des notifications de validation/rejet avec motif détaillé

## Implémentation

### 1. Service de Vérification (`apps/users/services.py`)

Ajout de la classe `FarmVerificationService` avec les méthodes suivantes:

#### `verify_farm(exploitant_profile, admin_user, approved, motif_rejet)`
- Valide ou rejette une demande de vérification d'exploitation
- Vérifie que l'utilisateur est administrateur
- Vérifie que le profil est en attente de vérification
- Si approuvé:
  - Change le statut à `VERIFIE`
  - Enregistre la date de vérification
  - Débloque les fonctionnalités premium
  - Envoie une notification de succès
- Si rejeté:
  - Change le statut à `REJETE`
  - Enregistre le motif de rejet
  - Envoie une notification avec le motif

#### `get_pending_verifications()`
- Récupère la liste des exploitations en attente de vérification
- Retourne les informations complètes (utilisateur, localisation, documents)

#### `_send_verification_notification(exploitant_profile, approved, motif_rejet)`
- Envoie des notifications SMS et email
- Messages personnalisés selon validation ou rejet
- Limite SMS à 160 caractères

### 2. Endpoints API (`apps/users/views.py`)

#### `POST /api/v1/farms/{id}/verify` (Admin uniquement)
**Paramètres:**
```json
{
  "approved": true/false,
  "motif_rejet": "Raison du rejet" (requis si approved=false)
}
```

**Réponse (succès):**
```json
{
  "message": "Exploitation vérifiée avec succès...",
  "exploitant": {
    "id": 1,
    "username": "exploitant1",
    "statut_verification": "VERIFIE",
    "date_verification": "2026-03-01T10:30:00Z",
    "superficie_totale": "15.50",
    "premium_features_unlocked": true,
    "first_name": "Jean",
    "last_name": "Dupont",
    "canton_principal": {...},
    "cultures_actuelles": ["Maïs", "Manioc"]
  }
}
```

**Réponse (rejet):**
```json
{
  "message": "Demande rejetée",
  "exploitant": {
    "id": 1,
    "username": "exploitant1",
    "statut_verification": "REJETE",
    "motif_rejet": "Documents justificatifs insuffisants...",
    "date_verification": "2026-03-01T10:30:00Z"
  }
}
```

#### `GET /api/v1/farms/pending` (Admin uniquement)
Récupère la liste des exploitations en attente de vérification.

**Réponse:**
```json
{
  "count": 2,
  "profiles": [
    {
      "id": 1,
      "username": "exploitant1",
      "first_name": "Jean",
      "last_name": "Dupont",
      "superficie_totale": "15.50",
      "canton_principal": {
        "id": 1,
        "nom": "Lomé 1er",
        "prefecture": {...},
        "region": {...}
      },
      "cultures_actuelles": ["Maïs", "Manioc"],
      "date_demande": "2026-02-15T08:00:00Z",
      "nombre_documents": 3
    }
  ]
}
```

#### `GET /api/v1/farms/{id}/details` (Admin uniquement)
Récupère les détails complets d'une exploitation avec documents.

**Réponse:**
```json
{
  "id": 1,
  "username": "exploitant1",
  "first_name": "Jean",
  "last_name": "Dupont",
  "email": "jean@example.com",
  "phone_number": "+22890000001",
  "profile": {
    "superficie_totale": "15.50",
    "canton_principal": {...},
    "coordonnees_gps": {"lat": 6.1319, "lon": 1.2228},
    "cultures_actuelles": ["Maïs", "Manioc"],
    "statut_verification": "EN_ATTENTE",
    "statut_verification_display": "En Attente de Vérification"
  },
  "documents": [
    {
      "id": 1,
      "type": "Titre Foncier",
      "type_code": "TITRE_FONCIER",
      "nom_fichier": "titre_foncier.pdf",
      "url": "/media/farms/verification/titre_foncier.pdf",
      "uploaded_at": "2026-02-15T08:00:00Z"
    }
  ],
  "nombre_documents": 3
}
```

### 3. Routes URL (`apps/users/urls.py`)

Ajout des routes suivantes:
```python
path('farms/pending', views.get_pending_farms, name='get-pending-farms'),
path('farms/<int:farm_id>/details', views.get_farm_details, name='get-farm-details'),
path('farms/<int:farm_id>/verify', views.verify_farm, name='verify-farm'),
```

### 4. Tests (`apps/users/test_farm_verification_workflow.py`)

#### Tests du Workflow (13 tests, tous passent ✅)

**Tests d'API:**
1. ✅ `test_verify_farm_success` - Validation réussie d'une exploitation
2. ✅ `test_reject_farm_with_reason` - Rejet avec motif
3. ✅ `test_reject_without_reason_fails` - Rejet sans motif échoue
4. ✅ `test_non_admin_cannot_verify` - Seuls les admins peuvent vérifier
5. ✅ `test_cannot_verify_already_verified_farm` - Pas de double vérification
6. ✅ `test_get_pending_farms` - Liste des exploitations en attente
7. ✅ `test_get_farm_details` - Détails complets d'une exploitation
8. ✅ `test_premium_features_unlocked_after_verification` - Déblocage des fonctionnalités premium
9. ✅ `test_premium_features_locked_when_not_verified` - Fonctionnalités bloquées si non vérifié

**Tests du Service:**
10. ✅ `test_service_verify_farm_success` - Service valide correctement
11. ✅ `test_service_reject_farm_with_reason` - Service rejette correctement
12. ✅ `test_service_requires_admin` - Service vérifie les permissions
13. ✅ `test_service_get_pending_verifications` - Service récupère les profils en attente

## Fonctionnalités Premium Débloquées

Après vérification, l'exploitant a accès à:
1. ✅ Dashboard avancé avec statistiques détaillées
2. ✅ Recrutement d'agronomes validés
3. ✅ Recrutement d'ouvriers saisonniers
4. ✅ Création de préventes agricoles
5. ✅ Analyses de marché et prévisions de prix
6. ✅ Optimisation logistique (itinéraires, coûts de transport)
7. ✅ Recommandations de cultures adaptées
8. ✅ Irrigation intelligente (besoins en eau, zones irrigables)

## Workflow Complet

```
1. Exploitant soumet demande de vérification
   └─> Statut: EN_ATTENTE
   
2. Admin consulte la liste des demandes en attente
   └─> GET /api/v1/farms/pending
   
3. Admin consulte les détails et documents
   └─> GET /api/v1/farms/{id}/details
   
4. Admin prend une décision:
   
   a) VALIDATION:
      └─> POST /api/v1/farms/{id}/verify {"approved": true}
      └─> Statut: VERIFIE
      └─> Fonctionnalités premium débloquées
      └─> Notification SMS/Email envoyée
      
   b) REJET:
      └─> POST /api/v1/farms/{id}/verify {"approved": false, "motif_rejet": "..."}
      └─> Statut: REJETE
      └─> Notification avec motif envoyée
```

## Sécurité

- ✅ Authentification requise pour tous les endpoints
- ✅ Vérification des permissions admin (is_staff ou is_superuser)
- ✅ Validation des paramètres (approved requis, motif_rejet si rejet)
- ✅ Protection contre la double vérification
- ✅ Transactions atomiques pour garantir la cohérence des données

## Notifications

### SMS (160 caractères max)
- **Validation**: "Votre exploitation a ete verifiee. Acces aux fonctionnalites premium active."
- **Rejet**: "Demande exploitation rejetee. Motif: [motif tronqué si nécessaire]..."

### Email (complet)
- **Validation**: Message détaillé avec liste des fonctionnalités débloquées
- **Rejet**: Message avec motif complet du rejet

## Intégration avec le Système

Le workflow s'intègre avec:
- ✅ Système d'authentification et permissions
- ✅ Modèles ExploitantProfile et FarmVerificationDocument
- ✅ Service de notifications (SMS/Email)
- ✅ Système de gestion des sessions
- ✅ Cache Redis pour optimisation

## Prochaines Étapes

Cette tâche complète le workflow de vérification des exploitations. Les tâches suivantes dans la roadmap sont:
- **15.3**: Créer l'endpoint des fonctionnalités premium (déjà implémenté dans `farm_premium_features`)
- **16.1-16.4**: Système de notation et avis (Phase V1)
- **20.1**: Dashboard exploitant vérifié (Phase V2)

## Statut Final

✅ **Tâche 15.2 complétée avec succès**
- Service de vérification implémenté
- 3 endpoints API créés
- 13 tests unitaires et d'intégration passent
- Documentation complète
- Exigences 10.4, 10.5, 10.6 satisfaites
