# HarooLife — base TogoLife

## Objectif

Transformer le mécanisme de regroupement agricole de Haroo en jeu interactif : former des équipes d'ouvriers et regrouper les besoins des exploitants. Nom du futur produit : **HarooLife**.

## Copie de référence — 10 octobre 2026

- Source : https://github.com/Louistatch/louis
- Révision : `f4fbdb43d6dd1c243f6386b0713ec9340c02141b`
- Dossier source : `togo-life-3d/` (le dossier parallèle `togo-life-3d-preview/` n'est pas copié).
- Destination : `experiments/haroolife/togolife/`.
- Copie intégrale, fichiers et licences conservés, sans historique Git imbriqué.
- Le README, les rapports et les résultats de tests contenus dans `togolife/` proviennent du projet source ; ils ne constituent pas une nouvelle validation de HarooLife.

Cet emplacement isole le prototype du frontend React et du backend Django de Haroo. Aucun raccordement aux routes, comptes, bases de données, paiements ou déploiements existants n'est effectué. Aucune dépendance n'a été installée pour cette copie.

## Base technique

TogoLife propose une simulation 3D avec Three.js fourni localement, avatar, déplacements, interactions, missions et économie virtuelle. Voir [le README original](togolife/README.md), [les instructions du projet](togolife/AGENTS.md) et [la licence](togolife/LICENSE).

Commandes indiquées par le projet source, à exécuter ultérieurement depuis ce dossier :

```sh
cd togolife
npm run build
python3 -m http.server 8000
```

Le serveur sert alors le résultat dans `/dist/`. Ces commandes n'ont pas été exécutées lors de la copie.

## Direction fonctionnelle à développer

1. Ouvrier : créer ou rejoindre une équipe, voir sa progression vers 8 membres et réaliser des missions agricoles.
2. Exploitant : rejoindre un regroupement et suivre la superficie cumulée vers le seuil actuel de 10 hectares.
3. Montrer les cantons, compétences, disponibilités et délais de constitution des groupes dans un parcours interactif.
4. Relier ensuite les actions utiles aux services Haroo, après validation des règles et des permissions côté serveur.

Les règles actuelles (8 ouvriers, 10 hectares, délai de 2 jours) viennent de `apps/jobs/models.py` et `apps/jobs/views.py`. Leur adaptation ludique reste à concevoir. Le code existant présente des incohérences de statuts entre création, participation et recherche des équipes ; les résoudre avant de connecter le jeu aux opérations réelles.

La monnaie et la progression du prototype sont virtuelles. Toute future interaction avec contrats, rémunérations ou données personnelles doit être explicitement conçue ; le prototype actuel ne réalise aucune de ces opérations.

## Vérification de cette livraison

Chaque fichier copié a été comparé à sa source par SHA-256. Aucun changement fonctionnel, build, test navigateur ou déploiement n'est inclus : cette étape prépare uniquement la base de travail et sa provenance.
