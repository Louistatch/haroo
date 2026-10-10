# Revue indépendante de l’intégration

Revue du 10 octobre 2026 : `src/main.js`, `world.js`, `character.js`, `controller.js`, `npcs.js`, `simulation.js`. Lecture du code et exécution réelle de `npm test` et de scénarios Node. Aucun navigateur exécuté dans cette revue : qualité visuelle, cadence réelle, touch et rendu GPU restent **non validés**.

## Résultat vérifié

- `npm test` : 2 fichiers passent, zéro échec. Ce chiffre compte des fichiers Node, pas une couverture complète du gameplay.
- Scénario métier : ouverture à 9 000 F, achat de 12 unités à 350 F, dépôt, puis 120 secondes à pas de 1/60 s. Résultat : 10 ventes, 7 300 F disponibles, 2 unités restantes. Les achats et ventes modifient effectivement stock et argent.
- Le contrôleur utilise des sous-pas spatiaux et des AABB pour les bâtiments. Le mouvement affiché à l’animation dépend de la distance réellement parcourue, ce qui évite de marcher sur place contre un mur.
- Les objets statiques répétés sont instanciés. Les géométries, matériaux, textures et squelettes possèdent des méthodes de destruction ; aucun rechargement de monde répété n’est actuellement proposé dans l’interface.

## Défauts et limites prioritaires

### P1 — Validation navigateur manquante

Les tests Node ne prouvent ni le bon rendu du skinning ni le fonctionnement des dialogues, de la caméra et des captures tactiles. Le raycast caméra est réalisé sur tout le monde détaillé à chaque image ; son coût, y compris les instances, n’est pas mesuré. Ne pas annoncer de FPS ou de niveau graphique validé avant cette validation.

### P2 — La reprise perd l’apparence et la position

`Simulation.snapshot()` contient l’économie et le nom, mais aucun shirt/skin ni position. `start(true)` restaure cette économie et conserve l’avatar par défaut au spawn. Un joueur personnalisé revient donc avec une autre tenue et au point de départ. Conserver une configuration d’avatar et un point de reprise validé est requis pour une sauvegarde complète.

### P2 — Les besoins et missions restent peu contraignants

À nourriture zéro, `tick(60)` conserve une énergie de 89,4 à partir de 90 ; prendre un contrat reste possible. La faim est actuellement un indicateur sans conséquence distincte. Deux cycles contract/deliver immédiats sont acceptés par le domaine et donnent 17 400 F depuis 15 000 F. L’interface impose l’approche des lieux, mais aucun quota, temps de trajet minimum ni stock de commandes ne limite les livraisons répétées. Ce n’est pas une panne de transaction, mais cela réduit la profondeur économique.

### P2 — Routines PNJ et collisions incomplètes

`npcs.js` change les libellés buy/work/waitTaxi/home aux points du parcours. Ces états déclenchent uniquement une pause ; l’heure influence un libellé home après 18 h sans modifier la destination. Les habitants ne consomment ni stock ni ressources, et traversent les autres personnages. Les véhicules ne figurent pas dans les colliders, ni les bancs et poteaux. Les collisions avec façades sont opérationnelles dans le code ; la collision de toute la scène ne l’est pas.

### P3 — Contrôle visuel requis pour le personnage

L’avatar est bien un `SkinnedMesh` original avec squelette et états Idle/Walk/Run. Chaque volume anatomique est rigidement attaché à un seul os ; aucune animation glTF, IK de pied, transition par clips ou capture de mouvement n’est chargée. La cadence suit la vitesse, mais cette formule n’établit pas un verrouillage du pied au sol. Les proportions, articulations et éventuels interstices doivent être jugés en captures réelles.

### P3 — Améliorations UI

Les dialogues suspendent toute la simulation, y compris ventes et PNJ. C’est cohérent pour une pause solo mais doit être expliqué au joueur. Les feedbacks sonores sont des oscillateurs brefs ; pas d’ambiance sonore. La carte liste des destinations, sans transport ou seconde ville jouable. La carte de partage reste une création 2D à partir des statistiques, pas une capture du jeu.

## Décision de revue

Aucun défaut critique démontré justifiant une modification urgente du code par cette revue. La version peut être proposée comme tranche jouable solo en développement, avec ces limites explicites. Elle ne peut pas être qualifiée de simulateur commercial complet, de locomotion professionnelle validée ou de produit mobile performant sur la seule base des tests présents. Priorité suivante : navigateur réel, captures puis correction des problèmes observés, avant revendication de qualité graphique.

## Corrections par le directeur après revue (10 octobre)

Apparence/position validées et sauvegardées, quota quotidien de livraison, ralentissement faim/énergie et épuisement si affamé ajoutés. Les horaires PNJ déterminent désormais les destinations via un graphe de trottoirs ; les états restent des activités simplifiées, sans animation de travail détaillée ou consommation économique individuelle. Raycast caméra détaillé remplacé par segments/proxies. Colliders d'étals, bancs, arbres et taxis ajoutés ; PNJ et poteaux restent sans collision physique complète. Chevauchement marché/atelier corrigé via test de lieux accessibles. Avatar joueur exporté en glTF original avec clips et loader/mixer réels ; Node vérifie son chargement. Cette note décrit les corrections du directeur, sans nouvelle endorsement de l'agent de revue. Le blocage navigateur subsiste.
