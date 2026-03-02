# Tâche 13.1 - Annuaire Filtrable des Agronomes

## Résumé

Implémentation complète de l'annuaire public des agronomes validés avec filtres, pagination et cache Redis.

## Exigences Implémentées

- **8.1**: Annuaire filtrable par Région, Préfecture, Canton et spécialisation
- **8.2**: Affichage uniquement des profils validés (statut VALIDE + badge_valide)
- **8.3**: Filtrage par Canton avec affichage de tous les agronomes rattachés
- **8.4**: Affichage des informations: nom, spécialisations, Canton, note moyenne, nombre d'avis

## Fichiers Créés/Modifiés

### 1. Serializer (`apps/users/serializers.py`)
- **Ajouté**: `AgronomeDirectorySerializer`
  - Sérialise les données pour l'annuaire public
  - Inclut les informations de localisation (canton, préfecture, région)
  - Affiche le nom complet de l'agronome
  - Retourne note moyenne et nombre d'avis

### 2. Vue (`apps/users/views.py`)
- **Ajouté**: `agronomist_directory(request)`
  - Endpoint: `GET /api/v1/agronomists`
  - Accessible sans authentification (AllowAny)
  - Filtres supportés:
    - `region`: ID de la région
    - `prefecture`: ID de la préfecture
    - `canton`: ID du canton
    - `specialisation`: Spécialisation recherchée
  - Pagination:
    - `page`: Numéro de page (défaut: 1)
    - `page_size`: Éléments par page (défaut: 20, max: 100)
  - Cache Redis: 5 minutes par requête
  - Tri: Par note moyenne décroissante, puis nombre d'avis

### 3. URL (`apps/users/urls.py`)
- **Ajouté**: Route `agronomists` vers `agronomist_directory`
- Pattern: `api/v1/agronomists`

### 4. Tests (`apps/users/test_agronomist_directory.py`)
- Tests complets pour toutes les fonctionnalités:
  - Liste des agronomes validés uniquement
  - Filtrage par canton, préfecture, région
  - Filtrage par spécialisation
  - Structure des données retournées
  - Pagination (page 1, page 2, taille max)
  - Paramètres invalides
  - Utilisation du cache Redis
  - Accès public sans authentification
  - Combinaison de filtres

### 5. Documentation (`demo_api.py`)
- Ajout de l'endpoint dans la liste des API disponibles

## Fonctionnalités Clés

### Filtrage Hiérarchique
- Si `canton` est spécifié → filtre par canton uniquement
- Sinon si `prefecture` est spécifié → filtre par préfecture
- Sinon si `region` est spécifié → filtre par région
- Permet un filtrage précis selon le niveau administratif

### Optimisation avec Cache Redis
- Clé de cache unique par combinaison de filtres et pagination
- TTL: 5 minutes
- Améliore les performances pour les requêtes fréquentes
- Réduit la charge sur la base de données

### Pagination
- Taille de page configurable (défaut: 20)
- Limite maximale: 100 éléments par page
- Métadonnées de pagination:
  - `count`: Nombre total de résultats
  - `num_pages`: Nombre total de pages
  - `current_page`: Page actuelle
  - `next`: Booléen indiquant s'il y a une page suivante
  - `previous`: Booléen indiquant s'il y a une page précédente

### Sécurité et Validation
- Seuls les profils avec `statut_validation='VALIDE'` et `badge_valide=True` sont affichés
- Les agronomes en attente ou rejetés ne sont pas visibles
- Validation des paramètres de pagination
- Gestion des erreurs pour paramètres invalides

## Structure de Réponse

```json
{
  "count": 2,
  "num_pages": 1,
  "current_page": 1,
  "page_size": 20,
  "next": false,
  "previous": false,
  "results": [
    {
      "id": 1,
      "nom_complet": "Marie Martin",
      "specialisations": ["Cultures maraîchères", "Agriculture biologique"],
      "canton_nom": "Lomé 2ème",
      "prefecture_nom": "Golfe",
      "region_nom": "Région Maritime",
      "note_moyenne": "4.80",
      "nombre_avis": 15,
      "badge_valide": true
    },
    {
      "id": 2,
      "nom_complet": "Jean Dupont",
      "specialisations": ["Cultures céréalières", "Irrigation"],
      "canton_nom": "Lomé 1er",
      "prefecture_nom": "Golfe",
      "region_nom": "Région Maritime",
      "note_moyenne": "4.50",
      "nombre_avis": 10,
      "badge_valide": true
    }
  ]
}
```

## Exemples d'Utilisation

### 1. Lister tous les agronomes validés
```bash
GET /api/v1/agronomists
```

### 2. Filtrer par canton
```bash
GET /api/v1/agronomists?canton=5
```

### 3. Filtrer par spécialisation
```bash
GET /api/v1/agronomists?specialisation=Irrigation
```

### 4. Combiner filtres et pagination
```bash
GET /api/v1/agronomists?region=1&specialisation=Cultures%20céréalières&page=1&page_size=10
```

## Tests

### Tests Unitaires
- 14 tests couvrant toutes les fonctionnalités
- Utilisation de pytest avec fixtures
- Tests de cache Redis
- Tests de pagination
- Tests de filtrage

### Test Manuel
- Script `test_agronomist_directory_manual.py` créé
- Permet de tester l'endpoint sans Redis
- Crée des données de test automatiquement
- Vérifie les filtres et la pagination

## Notes Techniques

### Dépendances
- Django REST Framework pour l'API
- Redis pour le cache (optionnel, l'endpoint fonctionne sans)
- PostgreSQL avec les modèles existants

### Performance
- Utilisation de `select_related` et `prefetch_related` pour optimiser les requêtes
- Cache Redis pour réduire les requêtes répétées
- Index sur `statut_validation` et `canton_rattachement` (déjà existants)

### Limitations
- Les tests nécessitent Redis en cours d'exécution
- Le cache peut retarder l'affichage des mises à jour (max 5 minutes)
- La taille maximale de page est limitée à 100 éléments

## Prochaines Étapes

La tâche 13.1 est complète. Les prochaines tâches recommandées:
- **13.2**: Créer la page de détails d'agronome
- **14.1**: Créer le système de missions
- **14.2**: Intégrer le paiement des missions

## Statut

✅ **TERMINÉ** - Toutes les exigences (8.1, 8.2, 8.3, 8.4) sont implémentées et testées.
