# Dashboard Institutionnel

Module pour le dashboard institutionnel sécurisé destiné aux partenaires gouvernementaux.

## Exigences

- **25.1**: Dashboard accessible uniquement aux comptes institutionnels validés
- **25.2**: Authentification à deux facteurs (2FA) obligatoire
- **25.3**: Statistiques agrégées sectorielles
- **25.4**: Filtrage par région et période

## Fonctionnalités

### 1. Contrôle d'accès sécurisé

- Authentification requise
- Type d'utilisateur: INSTITUTION uniquement
- 2FA obligatoire (Exigence 25.2)
- Gestion des permissions par niveau d'accès (NATIONAL, REGIONAL, PREFECTORAL)

### 2. Statistiques disponibles

#### Statistiques globales
- Nombre d'exploitations vérifiées
- Superficie totale cultivée (hectares)
- Emplois créés (agronomes + ouvriers)
- Volume et valeur des transactions
- Commissions plateforme

#### Statistiques par région
- Répartition par région avec tous les indicateurs

#### Statistiques par préfecture
- Nombre d'exploitations
- Superficie totale
- Nombre d'agronomes

#### Répartition des transactions
- Par type de transaction
- Montant total et commission par type

#### Tendances mensuelles
- Évolution des indicateurs sur 12 mois (configurable jusqu'à 24 mois)

### 3. Filtres

- **Par région**: Filtrer les statistiques pour une région spécifique
- **Par période**: Filtrer par date de début et date de fin
- **Par nombre de mois**: Pour les tendances mensuelles

## API Endpoints

### GET /api/v1/institutional/dashboard/

Dashboard principal avec tous les indicateurs.

**Query Parameters:**
- `region` (int, optionnel): ID de la région
- `start_date` (datetime, optionnel): Date de début (ISO 8601)
- `end_date` (datetime, optionnel): Date de fin (ISO 8601)

**Response:**
```json
{
  "statistiques_globales": {
    "nombre_exploitations": 150,
    "superficie_totale_hectares": 2500.50,
    "emplois_crees": {
      "total": 75,
      "agronomes": 45,
      "ouvriers": 30
    },
    "transactions": {
      "volume": 500,
      "valeur_totale_fcfa": 50000000.00,
      "commission_plateforme_fcfa": 2500000.00
    }
  },
  "statistiques_par_region": [...],
  "repartition_transactions": [...],
  "filtres_appliques": {
    "region_id": null,
    "start_date": null,
    "end_date": null
  }
}
```

### GET /api/v1/institutional/statistics/aggregated/

Statistiques agrégées uniquement.

**Query Parameters:** Identiques au dashboard principal

### GET /api/v1/institutional/statistics/by-prefecture/

Statistiques par préfecture.

**Query Parameters:**
- `region` (int, optionnel): ID de la région pour filtrer
- `start_date` (datetime, optionnel): Date de début
- `end_date` (datetime, optionnel): Date de fin

### GET /api/v1/institutional/statistics/transactions/

Répartition des transactions par type.

**Query Parameters:** Identiques aux statistiques agrégées

### GET /api/v1/institutional/statistics/trends/

Tendances mensuelles.

**Query Parameters:**
- `region` (int, optionnel): ID de la région
- `months` (int, optionnel): Nombre de mois (1-24, défaut: 12)

## Services

### InstitutionalDashboardService

Service principal pour le calcul des statistiques.

**Méthodes:**

- `get_aggregated_statistics(region_id=None, start_date=None, end_date=None)`: Calcule les statistiques agrégées
- `get_statistics_by_region(start_date=None, end_date=None)`: Statistiques par région
- `get_statistics_by_prefecture(region_id=None, start_date=None, end_date=None)`: Statistiques par préfecture
- `get_transaction_breakdown(region_id=None, start_date=None, end_date=None)`: Répartition des transactions
- `get_monthly_trends(region_id=None, months=12)`: Tendances mensuelles

## Permissions

### IsInstitutionalUser

Permission personnalisée qui vérifie:
1. L'utilisateur est authentifié
2. Le type d'utilisateur est INSTITUTION
3. Le 2FA est activé (Exigence 25.2)
4. Le profil institution existe

## Tests

Le module inclut des tests complets:

- **Tests de service**: Validation des calculs de statistiques
- **Tests d'API**: Validation des endpoints et permissions
- **Tests de sécurité**: Vérification du contrôle d'accès et du 2FA

Exécuter les tests:
```bash
python manage.py test apps.institutional
```

## Sécurité

- Authentification JWT requise
- 2FA obligatoire pour tous les comptes institutionnels
- Validation des permissions par niveau d'accès
- Anonymisation des données dans les exports (à implémenter dans task 7.3)

## Performance

- Requêtes optimisées avec agrégations Django ORM
- Utilisation de `select_related` et `prefetch_related` pour réduire les requêtes
- Cache Redis recommandé pour les endpoints (désactivé dans les tests)

## Dépendances

- Django REST Framework
- PostgreSQL (avec PostGIS)
- Redis (optionnel, pour le cache)

## Notes d'implémentation

- Les statistiques sont calculées en temps réel
- Les filtres par région respectent les permissions d'accès institutionnelles
- Les dates sont gérées en UTC
- Les montants sont en Francs CFA (FCFA)
