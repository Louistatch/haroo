# Références techniques additionnelles — sélection raisonnée
Recherche GitHub API + arbres racine réalisée le 9 octobre 2026. Métadonnées exactes dans github-evidence.json. Aucun de ces dépôts n'est prétendu installé ou exécuté dans ce rapport. Présence de tests ≠ tests exécutés. Licence de code ≠ licence de ses assets.

| Ressource | Licence/API et maintenance | Évaluation / décision |
|---|---|---|
| [Yuka](https://github.com/Mugen87/yuka) | MIT, push 2026-10-04, src/test/examples | Bonne séparation IA/rendu ; FSM, steering et navigation. Source à étudier ; petite FSM propre suffit au premier quartier, évite dépendance inutile. Tests présents, non exécutés. |
| [Recast Navigation](https://github.com/recastnavigation/recastnavigation) | Zlib, push 2026-02-27, Tests/DetourCrowd | Mature pour navmesh/foule, code natif + outils. À intégrer via WASM quand la complexité des intérieurs le justifie ; ne pas installer tout un pipeline C++ pour quelques routes. |
| [recast-navigation-js](https://github.com/isaac-mason/recast-navigation-js) | Découvert par recherche web ; licence non encore auditée | Port WASM avec foule. Candidat ultérieur, aucune installation autorisée sur cette seule découverte. |
| [vectiler](https://github.com/karimnaaji/vectiler) | MIT, push 2024-05-20, tests/3rdparty | OSM/tuiles vers modèles urbains. CLI C++, dépendances tierces à auditer. Maintenance moins récente, pas adapté au démarrage client sans préparation hors ligne. |
| [Procedural Cities](https://github.com/lanmower/Procedural-Cities) | README annonce MIT, non auditée via LICENSE | Algorithmes routes/parcelles intéressants ; génération générique ne restitue pas Lomé. Référence seulement. |
| [threex.proceduralcity](https://github.com/jeromeetienne/threex.proceduralcity) | MIT annoncé, Bower/ancienne API | Écarté comme base visuelle et technique : extrusions rudimentaires et stack vieillissante. |
| [Three.js](https://github.com/mrdoob/three.js) | MIT, push 2026-10-09 | Choix moteur ; AnimationMixer, GLTFLoader, instancing, LOD et matériaux PBR sans framework additionnel. |
| [glTF Transform](https://github.com/donmccurdy/glTF-Transform) | MIT, push 2026-10-06, packages/benchmarks | Optimisation offline des assets, compression/inspection. Auditer dépendances et droits des modèles avant exécution. |
| [gltfjsx](https://github.com/pmndrs/gltfjsx) | MIT, push 2024-11-04 | Génère JSX, impose un besoin React absent : non retenu. |
| [CharacterStudio](https://github.com/M3-org/CharacterStudio) | README annonce MIT, assets non auditables sur cette recherche | Avatar VRM configurable, dépendances React/crypto possibles. Non retenu pour ne pas importer stack et licences de personnages inconnues. |
| [SUMO](https://github.com/eclipse-sumo/sumo) | EPL-2.0, push 2026-10-09, tests/unittest | Simulation trafic robuste mais lourde, adaptée à génération/validation hors ligne ; trajectoires locales et priorité simple préférées pour slice. |
| [Colyseus](https://github.com/colyseus/colyseus) | MIT, push 2026-10-09, packages/jest.config.js | Serveur Node autoritaire, rooms et synchro. Préparer commands/simulation séparés ; pas intégré ni annoncé multijoueur sans tests de charge. |
| [Playwright](https://github.com/microsoft/playwright) | Apache-2.0, push 2026-10-09, tests/examples | Retenu pour validation navigateur : contrôles, transactions, persistence, captures et instrumentation FPS. |
| [MapLibre GL JS](https://github.com/maplibre/maplibre-gl-js) | API NOASSERTION, push 2026-10-09 | Licence détaillée à vérifier ; carte 2D possible plus tard. Inutile comme second moteur du quartier Three.js. |

Les appels initialement essayés vers recast-navigation/recastnavigation et Cabbibo/Traffic ont retourné 404. Le premier a été corrigé en recastnavigation/recastnavigation ; le second n'est pas retenu. Aucun score étoilé n'a été utilisé pour choisir.

## Contrat de données géographiques
OSM impose attribution et obligations ODbL sur les bases dérivées. Séparer données cartographiques de meshes artistiques. Ne jamais annoncer un relevé OSM réel lorsqu'aucun extrait n'a été chargé. geoBoundaries et Open Admin Data restent des sources à auditer avant incorporation. Le quartier initial peut être une interprétation stylisée explicitement identifiée. Un annuaire de préfectures n'est pas quarante villes jouables.

## Architecture retenue en principe
Three.js + modules TypeScript, géométrie réutilisable, renderer dissocié des règles économiques ; routines PNJ sans API générative ; contrôles tactiles à pointer events ; sauvegarde versionnée. Routes déterministes simples pour la slice, navmesh plus tard. Simulations et commandes isolées préparent un serveur autoritaire futur sans le prétendre opérationnel. Bibliothèques inspectées sont des références, pas une liste de skills exécutés.

