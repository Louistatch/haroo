# Commande de Peuplement des Données Administratives du Togo

## Description

Cette commande Django peuple la base de données avec le découpage administratif complet du Togo:
- **5 Régions**: Maritime, Plateaux, Centrale, Kara, Savanes
- **38 Préfectures**: Réparties dans les 5 régions
- **323+ Cantons**: Avec coordonnées GPS (latitude, longitude)

## Utilisation

### Peuplement initial
```bash
python manage.py populate_administrative_data
```

### Suppression et re-peuplement
```bash
python manage.py populate_administrative_data --clear
```

## Caractéristiques

### Idempotence
La commande peut être exécutée plusieurs fois sans créer de doublons. Elle utilise `get_or_create` pour éviter les duplications.

### Gestion des coordonnées GPS
- **Avec PostGIS**: Les coordonnées sont stockées comme `PointField` géographique
- **Sans PostGIS**: Les coordonnées sont stockées en JSON `{"lat": float, "lon": float}`

### Validation hiérarchique
La commande valide automatiquement que:
- Chaque Préfecture appartient à une Région valide
- Chaque Canton appartient à une Préfecture valide

### Statistiques
À la fin de l'exécution, la commande affiche:
- Nombre total de régions, préfectures et cantons créés
- Répartition par région (nombre de préfectures et cantons)
- Résultat de la validation hiérarchique

## Structure des données

### Régions (5)
- Maritime (MAR)
- Plateaux (PLA)
- Centrale (CEN)
- Kara (KAR)
- Savanes (SAV)

### Préfectures (38)
Chaque préfecture est associée à une région et possède un code unique.

### Cantons (323+)
Chaque canton possède:
- Un nom unique dans sa préfecture
- Un code unique
- Une référence à sa préfecture
- Des coordonnées GPS du centre (latitude, longitude)

## Exemples de données

### Région Maritime
- Préfectures: Golfe, Lacs, Vo, Yoto, Zio, Avé, Bas-Mono, Moyen-Mono
- Cantons: Lomé 1er, Lomé 2ème, Agoè-Nyivé 1, Aného, Vogan, Tabligbo, Tsévié, etc.

### Région Plateaux
- Préfectures: Agou, Amou, Danyi, Est-Mono, Haho, Kloto, Kpélé, Ogou, Wawa
- Cantons: Kpalimé, Atakpamé, Notsé, etc.

## Tests

Des tests unitaires sont disponibles dans `apps/locations/tests/test_populate_command.py`:

```bash
python manage.py test apps.locations.tests.test_populate_command
```

Les tests vérifient:
- La création des régions, préfectures et cantons
- La cohérence hiérarchique
- La présence de coordonnées GPS
- L'idempotence de la commande
- Le fonctionnement de l'option `--clear`

## Notes techniques

### Performance
- La commande utilise des transactions pour garantir l'intégrité des données
- Les créations sont groupées pour optimiser les performances
- Un compteur affiche la progression tous les 50 cantons créés

### Gestion des erreurs
- Les erreurs sont capturées et affichées clairement
- En cas d'erreur, la transaction est annulée (rollback)
- Les préfectures/cantons avec des références invalides sont signalés

### Compatibilité
- Compatible avec ou sans PostGIS
- Fonctionne avec SQLite, PostgreSQL, MySQL
- Encodage UTF-8 pour les caractères spéciaux (é, è, ô, etc.)
