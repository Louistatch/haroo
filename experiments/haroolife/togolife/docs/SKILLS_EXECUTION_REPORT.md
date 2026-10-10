# Registre d'installation et d'exécution des skills

Audit réel du 9 octobre 2026. Les instructions open source sont installées dans `.claude/skills/` ; leur présence ne signifie pas qu'un générateur, Blender ou un test de gameplay a été exécuté. Les résultats de validation du jeu doivent être consignés par l'équipe QA après intégration.

## Sources, versions et sélection

| Origine | Commit figé vérifié par API commits | Licence vérifiée | Décision |
|---|---|---|---|
| majidmanzarpour/threejs-game-skills | 8286774b22a2566bf894dbc825825c16921866af | MIT, copyright Majid Manzarpour 2026 | Production skills retenus ; services payants exclus |
| alton47/threejs-skills | 7b8e25638cff83a6be4926d8f05001022cc80ac3 | MIT, copyright Allan Alton 2026 | Modules techniques retenus |
| majidmanzarpour/blender-game-skills | f0ef29385a03de139957e6f700b801cdc00b7e29 | MIT | Instructions installées ; Blender non exécuté |
| anthropics/skills | dbd4588f9e1033efb41dad4bef2f7947c8993d44 | Apache-2.0 dans chaque skill retenu | Frontend et navigateur retenus |
| JulienDelquignies/three-js-aaa-agent-skill | non accessible | non vérifiable | Métadonnées et tree : GitHub 404 ; recherche par nom sans résultat ; non installé |

Révisions ci-dessus confirmées séparément par l'API GitHub commits (per_page=1), après exploration tree HEAD. Dernières dates de commit vérifiées : pack principal 2026-09-28, alton47 2026-03-25, Blender 2026-09-24, anthropics 2026-10-09. Les fichiers ont été téléchargés par URLs raw figées à ce SHA. Les licences sont jointes à chaque dossier installé.

## Installation et sûreté

Installation manuelle des fichiers texte via connecteur GitHub et apply_patch dans le périmètre du jeu. Méthode équivalente à la copie de `skills/` documentée dans le README et le script d'installation du pack. Aucun script distant lancé via curl, aucune modification de la plateforme BAD/Bryq. Aucun package npm global installé.

`install.sh` a été inspecté : copie via rsync/cp, remplacement des dossiers homonymes par rm -rf et élagage optionnel. Pour éviter tout écrasement, il n'a pas été exécuté ; copie locale de fichiers inspectés. Scripts retenus : inspecteur canvas Node (Playwright/pngjs), vérificateur de preuves Python, gestionnaire de serveurs Python. Ce dernier lance les commandes explicitement fournies avec subprocess ; aucune commande externe n'a été fournie durant son invocation --help.

Tripo, Gemini et ElevenLabs : leurs SKILL.md ont été réellement consultés et écartés de l'installation/exécution, car la génération dépend de services propriétaires et de clés. Aucun probe de profils shell ni appel facturable. Blender : instructions consultées, pipeline non exécuté et aucune génération Blender annoncée.

## Skills individuels

### threejs-game-director

- Origine : https://github.com/majidmanzarpour/threejs-game-skills ; révision et licence dans le tableau ci-dessus.
- Rôle : orchestration, contrat de boucle, intégration et preuves.
- Installation : copie locale de `.claude/skills/threejs-game-director/SKILL.md`, licence et références présentes sélectionnées ; aucun installateur exécuté.
- Action effective : instructions téléchargées et consultées ; recommandations transmises au directeur pour application dans le jeu.
- Fichiers produits : dossier installé ; présent registre. check_evidence.py installé et --help exécuté PASS.
- Résultat : installation réussie. Application au code et tests du jeu à confirmer par rapports d'intégration ; ne pas interpréter cette ligne comme validation du gameplay.
- Limites : pas de dépendance automatique ajoutée, pas de service payant utilisé.

### threejs-gameplay-systems

- Origine : https://github.com/majidmanzarpour/threejs-game-skills ; révision et licence dans le tableau ci-dessus.
- Rôle : input, état, caméra, collisions et économie mesurable.
- Installation : copie locale de `.claude/skills/threejs-gameplay-systems/SKILL.md`, licence et références présentes sélectionnées ; aucun installateur exécuté.
- Action effective : instructions téléchargées et consultées ; recommandations transmises au directeur pour application dans le jeu.
- Fichiers produits : dossier installé ; présent registre. Aucun script de ce skill exécuté.
- Résultat : installation réussie. Application au code et tests du jeu à confirmer par rapports d'intégration ; ne pas interpréter cette ligne comme validation du gameplay.
- Limites : pas de dépendance automatique ajoutée, pas de service payant utilisé.

### threejs-aaa-graphics-builder

- Origine : https://github.com/majidmanzarpour/threejs-game-skills ; révision et licence dans le tableau ci-dessus.
- Rôle : formes détaillées, matériaux partagés et budgets.
- Installation : copie locale de `.claude/skills/threejs-aaa-graphics-builder/SKILL.md`, licence et références présentes sélectionnées ; aucun installateur exécuté.
- Action effective : instructions téléchargées et consultées ; recommandations transmises au directeur pour application dans le jeu.
- Fichiers produits : dossier installé ; présent registre. Aucun script de ce skill exécuté.
- Résultat : installation réussie. Application au code et tests du jeu à confirmer par rapports d'intégration ; ne pas interpréter cette ligne comme validation du gameplay.
- Limites : pas de dépendance automatique ajoutée, pas de service payant utilisé.

### threejs-qa-release

- Origine : https://github.com/majidmanzarpour/threejs-game-skills ; révision et licence dans le tableau ci-dessus.
- Rôle : tests navigateur et captures en jeu.
- Installation : copie locale de `.claude/skills/threejs-qa-release/SKILL.md`, licence et références présentes sélectionnées ; aucun installateur exécuté.
- Action effective : instructions téléchargées et consultées ; recommandations transmises au directeur pour application dans le jeu.
- Fichiers produits : dossier installé ; présent registre. Inspecteur canvas installé ; contrôle Node syntaxique PASS.
- Résultat : installation réussie. Application au code et tests du jeu à confirmer par rapports d'intégration ; ne pas interpréter cette ligne comme validation du gameplay.
- Limites : pas de dépendance automatique ajoutée, pas de service payant utilisé.

### threejs-game-ui-designer

- Origine : https://github.com/majidmanzarpour/threejs-game-skills ; révision et licence dans le tableau ci-dessus.
- Rôle : HUD, contrôles tactiles et zones sûres.
- Installation : copie locale de `.claude/skills/threejs-game-ui-designer/SKILL.md`, licence et références présentes sélectionnées ; aucun installateur exécuté.
- Action effective : instructions téléchargées et consultées ; recommandations transmises au directeur pour application dans le jeu.
- Fichiers produits : dossier installé ; présent registre. Aucun script de ce skill exécuté.
- Résultat : installation réussie. Application au code et tests du jeu à confirmer par rapports d'intégration ; ne pas interpréter cette ligne comme validation du gameplay.
- Limites : pas de dépendance automatique ajoutée, pas de service payant utilisé.

### threejs-debug-profiler

- Origine : https://github.com/majidmanzarpour/threejs-game-skills ; révision et licence dans le tableau ci-dessus.
- Rôle : diagnostics renderer et profiling.
- Installation : copie locale de `.claude/skills/threejs-debug-profiler/SKILL.md`, licence et références présentes sélectionnées ; aucun installateur exécuté.
- Action effective : instructions téléchargées et consultées ; recommandations transmises au directeur pour application dans le jeu.
- Fichiers produits : dossier installé ; présent registre. Aucun script de ce skill exécuté.
- Résultat : installation réussie. Application au code et tests du jeu à confirmer par rapports d'intégration ; ne pas interpréter cette ligne comme validation du gameplay.
- Limites : pas de dépendance automatique ajoutée, pas de service payant utilisé.

### threejs-camera

- Origine : https://github.com/alton47/threejs-skills ; révision et licence dans le tableau ci-dessus.
- Rôle : FOV, projection et suivi.
- Installation : copie locale de `.claude/skills/threejs-camera/SKILL.md`, licence et références présentes sélectionnées ; aucun installateur exécuté.
- Action effective : instructions téléchargées et consultées ; recommandations transmises au directeur pour application dans le jeu.
- Fichiers produits : dossier installé ; présent registre. Aucun script de ce skill exécuté.
- Résultat : installation réussie. Application au code et tests du jeu à confirmer par rapports d'intégration ; ne pas interpréter cette ligne comme validation du gameplay.
- Limites : pas de dépendance automatique ajoutée, pas de service payant utilisé.

### threejs-animation

- Origine : https://github.com/alton47/threejs-skills ; révision et licence dans le tableau ci-dessus.
- Rôle : AnimationMixer, clips et transitions.
- Installation : copie locale de `.claude/skills/threejs-animation/SKILL.md`, licence et références présentes sélectionnées ; aucun installateur exécuté.
- Action effective : instructions téléchargées et consultées ; recommandations transmises au directeur pour application dans le jeu.
- Fichiers produits : dossier installé ; présent registre. Aucun script de ce skill exécuté.
- Résultat : installation réussie. Application au code et tests du jeu à confirmer par rapports d'intégration ; ne pas interpréter cette ligne comme validation du gameplay.
- Limites : pas de dépendance automatique ajoutée, pas de service payant utilisé.

### threejs-lighting

- Origine : https://github.com/alton47/threejs-skills ; révision et licence dans le tableau ci-dessus.
- Rôle : éclairage et ombres.
- Installation : copie locale de `.claude/skills/threejs-lighting/SKILL.md`, licence et références présentes sélectionnées ; aucun installateur exécuté.
- Action effective : instructions téléchargées et consultées ; recommandations transmises au directeur pour application dans le jeu.
- Fichiers produits : dossier installé ; présent registre. Aucun script de ce skill exécuté.
- Résultat : installation réussie. Application au code et tests du jeu à confirmer par rapports d'intégration ; ne pas interpréter cette ligne comme validation du gameplay.
- Limites : pas de dépendance automatique ajoutée, pas de service payant utilisé.

### threejs-performance

- Origine : https://github.com/alton47/threejs-skills ; révision et licence dans le tableau ci-dessus.
- Rôle : instancing, culling et mémoire.
- Installation : copie locale de `.claude/skills/threejs-performance/SKILL.md`, licence et références présentes sélectionnées ; aucun installateur exécuté.
- Action effective : instructions téléchargées et consultées ; recommandations transmises au directeur pour application dans le jeu.
- Fichiers produits : dossier installé ; présent registre. Aucun script de ce skill exécuté.
- Résultat : installation réussie. Application au code et tests du jeu à confirmer par rapports d'intégration ; ne pas interpréter cette ligne comme validation du gameplay.
- Limites : pas de dépendance automatique ajoutée, pas de service payant utilisé.

### threejs-loaders

- Origine : https://github.com/alton47/threejs-skills ; révision et licence dans le tableau ci-dessus.
- Rôle : chargement glTF.
- Installation : copie locale de `.claude/skills/threejs-loaders/SKILL.md`, licence et références présentes sélectionnées ; aucun installateur exécuté.
- Action effective : instructions téléchargées et consultées ; recommandations transmises au directeur pour application dans le jeu.
- Fichiers produits : dossier installé ; présent registre. Aucun script de ce skill exécuté.
- Résultat : installation réussie. Application au code et tests du jeu à confirmer par rapports d'intégration ; ne pas interpréter cette ligne comme validation du gameplay.
- Limites : pas de dépendance automatique ajoutée, pas de service payant utilisé.

### threejs-materials

- Origine : https://github.com/alton47/threejs-skills ; révision et licence dans le tableau ci-dessus.
- Rôle : matériaux et textures.
- Installation : copie locale de `.claude/skills/threejs-materials/SKILL.md`, licence et références présentes sélectionnées ; aucun installateur exécuté.
- Action effective : instructions téléchargées et consultées ; recommandations transmises au directeur pour application dans le jeu.
- Fichiers produits : dossier installé ; présent registre. Aucun script de ce skill exécuté.
- Résultat : installation réussie. Application au code et tests du jeu à confirmer par rapports d'intégration ; ne pas interpréter cette ligne comme validation du gameplay.
- Limites : pas de dépendance automatique ajoutée, pas de service payant utilisé.

### threejs-physics

- Origine : https://github.com/alton47/threejs-skills ; révision et licence dans le tableau ci-dessus.
- Rôle : Rapier, proxies et pas fixe.
- Installation : copie locale de `.claude/skills/threejs-physics/SKILL.md`, licence et références présentes sélectionnées ; aucun installateur exécuté.
- Action effective : instructions téléchargées et consultées ; recommandations transmises au directeur pour application dans le jeu.
- Fichiers produits : dossier installé ; présent registre. Aucun script de ce skill exécuté.
- Résultat : installation réussie. Application au code et tests du jeu à confirmer par rapports d'intégration ; ne pas interpréter cette ligne comme validation du gameplay.
- Limites : pas de dépendance automatique ajoutée, pas de service payant utilisé.

### frontend-design

- Origine : https://github.com/anthropics/skills ; révision et licence dans le tableau ci-dessus.
- Rôle : identité visuelle et interface.
- Installation : copie locale de `.claude/skills/frontend-design/SKILL.md`, licence et références présentes sélectionnées ; aucun installateur exécuté.
- Action effective : instructions téléchargées et consultées ; recommandations transmises au directeur pour application dans le jeu.
- Fichiers produits : dossier installé ; présent registre. Aucun script de ce skill exécuté.
- Résultat : installation réussie. Application au code et tests du jeu à confirmer par rapports d'intégration ; ne pas interpréter cette ligne comme validation du gameplay.
- Limites : pas de dépendance automatique ajoutée, pas de service payant utilisé.

### webapp-testing

- Origine : https://github.com/anthropics/skills ; révision et licence dans le tableau ci-dessus.
- Rôle : reconnaissance et Playwright.
- Installation : copie locale de `.claude/skills/webapp-testing/SKILL.md`, licence et références présentes sélectionnées ; aucun installateur exécuté.
- Action effective : instructions téléchargées et consultées ; recommandations transmises au directeur pour application dans le jeu.
- Fichiers produits : dossier installé ; présent registre. with_server.py installé et --help exécuté PASS.
- Résultat : installation réussie. Application au code et tests du jeu à confirmer par rapports d'intégration ; ne pas interpréter cette ligne comme validation du gameplay.
- Limites : pas de dépendance automatique ajoutée, pas de service payant utilisé.

### blender-image-to-3d

- Origine : https://github.com/majidmanzarpour/blender-game-skills ; révision et licence dans le tableau ci-dessus.
- Rôle : pipeline modèles optimisés.
- Installation : copie locale de `.claude/skills/blender-image-to-3d/SKILL.md`, licence et références présentes sélectionnées ; aucun installateur exécuté.
- Action effective : instructions téléchargées et consultées ; recommandations transmises au directeur pour application dans le jeu.
- Fichiers produits : dossier installé ; présent registre. Aucun script de ce skill exécuté.
- Résultat : installation réussie. Application au code et tests du jeu à confirmer par rapports d'intégration ; ne pas interpréter cette ligne comme validation du gameplay.
- Limites : aucun Blender lancé, aucun modèle exporté par ce skill.

## Commandes réellement exécutées

Dans `/workspace/louis/togo-life-3d` :

```sh
python3 .claude/skills/webapp-testing/scripts/with_server.py --help
python3 .claude/skills/threejs-game-director/scripts/check_evidence.py --help
node --check .claude/skills/threejs-qa-release/scripts/inspect-threejs-canvas.mjs
```

Chaque commande : exit 0. Ces vérifications prouvent la présence/usage des aides et la syntaxe Node, pas la qualité visuelle ni les performances du jeu.

## Consignes appliquées à la préparation

- Le director a orienté la séparation des missions et le contrat de preuves ; recommandations envoyées au directeur : vraie boucle achat/transport/vente, caméra FOV 45–60°, capsule physique séparée du mesh, animation Idle/Walk/Run avec crossfade et test de mouvement réel.
- Graphics : formes avant effets, matériaux partagés, textures procédurales ; point de départ mobile 150 draw calls, 300k triangles, 40 textures, un soleil 1024 et DPR 1.5. Ce sont des budgets, pas des résultats mesurés.
- QA : desktop/mobile en jeu actif, mouvement non figé, erreur console/network et production preview. Scores visuels non déclarés sans captures inspectées ; les anchors binaires n'ont pas été importés et le score premium du pack n'est donc pas validé.
- Frontend : palette spécifique au lieu, interface courte, clavier/focus, mobile et reduced motion ; ne pas substituer une page marketing au jeu.

L'application concrète au code, les captures et le profiling doivent être complétés après les modifications finales, avec chemins et commandes réels. Aucune fonctionnalité commerciale, multijoueur ou couverture nationale n'est certifiée par l'installation d'un skill.


## Application réelle après intégration — 10 octobre

Le directeur a lu les cinq production SKILL.md (gameplay, graphics, UI, debug, QA), frontend-design et webapp-testing ; références physics-engine-selection, genre-design, game-feel, technical-art, authoring-recipes, shader-cookbook, visual-scorecard, ui-patterns, debug-playbook, release-checks, visual-test-harness, playtest-bot, evidence-manifest lues.

| Skills effectivement appliqués | Actions/fichiers produits | Vérification réelle / limite |
|---|---|---|
| game-director + gameplay-systems | `artifacts/game-progress.md`, `src/main.js`, `src/controller.js`, `src/simulation.js` ; boucle stock/transport/prix/demande et collisions à pas fixe | Tests économie/collisions ; navigateur bloqué |
| aaa-graphics-builder + materials + lighting + performance | `src/world.js`, rendu PBR/soleil/sky, textures locales, instancing, proxies caméra simples | Construction monde et positions vérifiées en Node ; aucun score premium validé |
| animation + loaders | `assets/avatar.gltf`, `scripts/export-avatar.mjs`, `src/avatar-loader.js` ; 22 os, Idle/Walk/Run, AnimationMixer/crossfade | Fichier glTF réellement exporté puis parsé/testé en Node ; motion capture en jeu non réalisée |
| game-ui-designer + frontend-design | `index.html`, `life.css`, HUD, dialogues, partage sans prénom, joystick pointer events | Imports/build validés ; responsive/touch non validés en navigateur |
| debug-profiler + qa-release + webapp-testing | `tests/browser.py`, diagnostics opt-in `?qa=1`, `artifacts/browser-results.json`, build/unit logs | Playwright réellement lancé : BLOCKED avant page à cause de restriction socket. Zéro capture et zéro test navigateur réussi |
| camera | Caméra amortie FOV 52°, anti-obstruction via proxies dans controller/main | Test segment-proxy réussi ; mouvement visuel non inspecté |

Physics : instructions consultées et choix explicite de collisions cinématiques locales ; Rapier non installé. Blender et générateurs 3D/image/audio : aucune exécution revendiquée. Les sons runtime sont des oscillateurs Web Audio originaux.

Build exécuté : `node scripts/build.mjs` (statique + monofichier). Tests : `node --test --test-isolation=none tests/*.test.mjs` : 14 tests réussis. Les scripts auxiliaires du director/QA ne remplacent pas le Playwright bloqué. Voir `artifacts/final-evidence.md` pour résultats et blocages exacts.

Exécution finale auxiliaire : director `check_evidence.py` sur le rapport : FAIL (inspection canvas absente), fichiers build/browser/avatar reconnus. QA `inspect-threejs-canvas.mjs` : tentative, échec de module Node Playwright manquant ; log conservé. La version Playwright Python est installée mais Chromium reste bloqué. Aucun npx/download non inspecté ni programme payant exécuté pour masquer ces limites.
