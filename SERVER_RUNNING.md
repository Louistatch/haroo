# 🚀 Plateforme Agricole du Togo - Serveur en Cours d'Exécution

## ✅ Statut du Serveur

Le serveur Django est **ACTIF** et fonctionne sur:

**URL**: http://127.0.0.1:8000/

## 📋 Endpoints Disponibles

### Authentification
- `POST /api/v1/auth/register/` - Inscription
- `POST /api/v1/auth/login/` - Connexion
- `POST /api/v1/auth/logout/` - Déconnexion
- `POST /api/v1/auth/token/refresh/` - Rafraîchir le token

### Découpage Administratif
- `GET /api/v1/regions/` - Liste des régions
- `GET /api/v1/regions/{id}/prefectures/` - Préfectures d'une région
- `GET /api/v1/prefectures/{id}/cantons/` - Cantons d'une préfecture
- `GET /api/v1/cantons/search/` - Recherche de cantons

### Profils Utilisateurs
- `GET /api/v1/users/me/` - Mon profil
- `PATCH /api/v1/users/me/` - Mettre à jour mon profil

### Agronomes (NOUVEAU)
- `POST /api/v1/agronomists/register/` - Inscription agronome
- `POST /api/v1/agronomists/{id}/validate/` - Valider un agronome (admin)
- `GET /api/v1/agronomists/` - Annuaire des agronomes
- `GET /api/v1/agronomists/{id}/` - Détails d'un agronome

### Missions (NOUVEAU - Tâches 14.1 & 14.2)
- `POST /api/v1/missions/` - Créer une mission
- `GET /api/v1/missions/` - Liste de mes missions
- `GET /api/v1/missions/{id}/` - Détails d'une mission
- `POST /api/v1/missions/{id}/accept/` - Accepter une mission (agronome)
- `POST /api/v1/missions/{id}/complete/` - Terminer une mission (exploitant)

### Documents Techniques
- `GET /api/v1/documents/` - Catalogue de documents
- `GET /api/v1/documents/{id}/` - Détails d'un document
- `POST /api/v1/documents/{id}/purchase/` - Acheter un document
- `GET /api/v1/documents/{id}/download/` - Télécharger un document
- `GET /api/v1/purchases/history/` - Historique des achats

### Paiements
- `POST /api/v1/payments/initiate/` - Initier un paiement
- `POST /api/v1/payments/webhooks/fedapay/` - Webhook Fedapay
- `GET /api/v1/transactions/history/` - Historique des transactions

### Dashboard Institutionnel
- `GET /api/v1/institutional/dashboard/` - Statistiques sectorielles
- `POST /api/v1/institutional/reports/export/` - Exporter un rapport

### Conformité
- `GET /api/v1/compliance/cgu/` - CGU
- `POST /api/v1/compliance/accept-cgu/` - Accepter les CGU
- `POST /api/v1/compliance/delete-account/` - Supprimer mon compte
- `GET /api/v1/compliance/export-data/` - Exporter mes données

### Admin Django
- `http://127.0.0.1:8000/admin/` - Interface d'administration

## 🔑 Comptes de Test

### Exploitant Vérifié
- **Username**: exploitant_demo
- **Password**: Demo123!
- **Type**: EXPLOITANT
- **Statut**: Vérifié (peut créer des missions)

### Agronome Validé
- **Username**: agronome_demo
- **Password**: Demo123!
- **Type**: AGRONOME
- **Statut**: Validé (peut accepter des missions)

### Administrateur
- **Username**: admin_demo
- **Password**: Admin123!
- **Type**: ADMIN
- **Accès**: Interface admin + validation agronomes

## 📊 Données Chargées

- ✅ 5 Régions du Togo
- ✅ 38 Préfectures
- ✅ 323 Cantons avec coordonnées GPS
- ✅ 3 utilisateurs de test
- ✅ Système de missions opérationnel
- ✅ Système d'escrow pour paiements

## 🆕 Nouvelles Fonctionnalités (Session Actuelle)

### Tâche 14.1 - Système de Missions ✅
- Modèle Mission avec 6 statuts (DEMANDE, ACCEPTEE, REFUSEE, EN_COURS, TERMINEE, ANNULEE)
- Création de missions par exploitants vérifiés
- Acceptation par agronomes validés
- Complétion avec libération de paiement
- 14 tests unitaires

### Tâche 14.2 - Paiement des Missions avec Escrow ✅
- Service EscrowService pour rétention des paiements
- Blocage du paiement jusqu'à fin de mission
- Libération automatique avec déduction de 10% de commission
- Intégration complète avec Fedapay
- 10 tests unitaires

## 🧪 Tester les Nouvelles Fonctionnalités

### Flux Complet de Mission

1. **Connexion Exploitant**:
```bash
curl -X POST http://127.0.0.1:8000/api/v1/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"username": "exploitant_demo", "password": "Demo123!"}'
```

2. **Créer une Mission**:
```bash
curl -X POST http://127.0.0.1:8000/api/v1/missions/ \
  -H "Authorization: Bearer <token_exploitant>" \
  -H "Content-Type: application/json" \
  -d '{
    "agronome": <id_agronome>,
    "description": "Conseil pour culture de maïs",
    "budget_propose": "50000.00",
    "date_debut": "2026-03-15",
    "date_fin": "2026-03-30"
  }'
```

3. **Connexion Agronome**:
```bash
curl -X POST http://127.0.0.1:8000/api/v1/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"username": "agronome_demo", "password": "Demo123!"}'
```

4. **Accepter la Mission**:
```bash
curl -X POST http://127.0.0.1:8000/api/v1/missions/<mission_id>/accept/ \
  -H "Authorization: Bearer <token_agronome>"
```

5. **Payer la Mission** (Exploitant):
- Utiliser l'endpoint de paiement Fedapay
- Le paiement sera bloqué en escrow

6. **Terminer la Mission** (Exploitant):
```bash
curl -X POST http://127.0.0.1:8000/api/v1/missions/<mission_id>/complete/ \
  -H "Authorization: Bearer <token_exploitant>"
```
- Libère le paiement
- Transfère 45,000 FCFA à l'agronome (50,000 - 10% commission)

## 📈 Progression du Projet

**Tâches Complétées**: 7/76 (9.2%)
- ✅ 11.1 - Checkpoint MVP
- ✅ 12.1 - Inscription agronomes
- ✅ 12.2 - Validation administrative
- ✅ 13.1 - Annuaire agronomes
- ✅ 13.2 - Détails agronome
- ✅ 14.1 - Système de missions
- ✅ 14.2 - Paiement missions avec escrow

**Tâches en File d'Attente**: 69 tâches (V1, V2, V3)

## 🛠️ Commandes Utiles

### Arrêter le Serveur
Le serveur tourne en arrière-plan. Pour l'arrêter, utilisez Ctrl+C dans le terminal ou fermez la fenêtre.

### Voir les Logs
Les logs s'affichent dans le terminal où le serveur a été démarré.

### Accéder à l'Admin
1. Aller sur http://127.0.0.1:8000/admin/
2. Se connecter avec admin_demo / Admin123!

### Exécuter les Tests
```bash
python manage.py test
```

## 📝 Notes

- Le serveur utilise SQLite en développement
- Redis est optionnel (cache désactivé si non disponible)
- Fedapay est en mode sandbox
- Toutes les migrations sont appliquées
- Les données de test sont chargées

## 🎯 Prochaines Étapes

Pour continuer l'implémentation, dites simplement "continue" et je reprendrai l'exécution des 69 tâches restantes.

---

**Serveur démarré le**: 1er Mars 2026, 18:56
**Port**: 8000
**Environnement**: Développement
