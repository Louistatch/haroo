# TOGO LIFE — preuves de session

## Résultat exact

Tranche solo codée et construite, **non validée dans un navigateur**. Branche `feat/togo-life-montagne-aimant`, base exacte `4a4c4a248093734f7eb028894aa07064a627b76c`. Le clone shell échouait sur le proxy ; les sources ont été récupérées par connecteur GitHub. Blobs et arbres historiques ont été reconstruits avec empreintes identiques pour un checkout shallow local ; les commits distants restent enfants de la base existante. BAD/Bryq est préservé.

## Commandes réussies

- `node scripts/export-avatar.mjs` : glTF original 517 962 octets, 22 os, Idle/Walk/Run.
- `node --test --test-isolation=none tests/*.test.mjs` : 14 PASS, zéro FAIL. Économie, sauvegarde, limites de contrats, collisions, caméra-proxies, glTF/mixer et routines horaires.
- `node scripts/build.mjs` : imports locaux vérifiés, distribution statique et `TOGO_LIFE_MONTAGNE.html` générées.
- Syntaxe ES de l'intégration validée avec Node.

Preuves enregistrées : [tests](unit-tests.txt), [build](build.json), [log build](build-log.txt), [tentative Playwright](browser-results.json), [avatar](../assets/avatar.gltf).

## Navigateur : blocage réel

`python tests/browser.py` a réellement tenté Chromium et écrit `artifacts/browser-results.json` : BLOCKED, 0 contrôles exécutés, 0 capture. Premier défaut : `setsockopt: Operation not permitted` dans crashpad. Avec crashpad désactivé pour le test : `shutdown: Operation not permitted` dans sandbox_host_linux. Les demandes d'exception ont été interrompues ; aucune autorisation additionnelle n'est supposée. Aucun contournement de politique réseau ou de secrets.

Le script contient les contrôles par vrais inputs PC, parcours marché/comptoir, transaction, pause, sauvegarde, joystick/cancel mobile, captures et vidéo. Ils restent à exécuter sur un environnement autorisant Chromium. Les fichiers de capture sont volontairement absents. La carte de partage 2D n'est pas une capture de gameplay.

## Mesures disponibles et indisponibles

Mesures réelles de taille dans `build.json` et log. Avatar 517 962 octets ; distribution ES environ 1,53 Mo avant monofichier ; monofichier environ 1,85 Mo. Ces tailles ne sont pas des temps de téléchargement mesurés. FPS desktop/Android, frame time GPU, draw calls en jeu, mémoire/fuites, temps de chargement et caméra/mobile : **non mesurés**. SwiftShader prévu pour les contrôles fonctionnels ne serait pas une preuve de performance matérielle Android.

Budgets configurés, pas mesures : DPR ≤1,5, ombre soleil 1024, zéro post-pass, physique cinématique 1/60, huit PNJ, textures locales et instances. Diagnostics accessibles uniquement avec `?qa=1`.

## Couverture et limites

Livré dans le code : quartier Lomé artistique, avatar personnalisable glTF, mouvement course/marche/freinage, caméra, collisions bâtiments/étals/taxis, PNJ à horaires, trafic sur rails, commerce et besoins, logement accessible, sauvegarde, partage privé, mode prototype de secours.

Non livré : validation esthétique professionnelle, contact pieds IK, physique Rapier, villes réelles OSM, quarantaine de quartiers, deuxième région distincte, véhicules possédés, foule sociale avancée, animations de travail, multijoueur, événements réseau, paiement, compte ou lancement commercial.

Références vérifiées : `docs/LAGOS_LIFE_RESEARCH.md`, `docs/TECHNICAL_REFERENCES.md`. Skills installés/appliqués et limites : `docs/SKILLS_EXECUTION_REPORT.md`. Revue : `docs/INDEPENDENT_REVIEW.md`. Critique non flatteuse : `docs/LAGOS_LIFE_EVALUATION.md`.

## Scripts de skills réellement exécutés sur le résultat

`check_evidence.py . --report artifacts/final-evidence.md` : FAIL attendu car aucun JSON d'inspection canvas existe ; confirme les fichiers de preuve présents et refuse une couverture visuelle non produite. `inspect-threejs-canvas.mjs --url ...` : tentative réelle, échec de dépendance Node Playwright (version Python installée seulement). Voir `artifacts/canvas-inspector-attempt.txt`. Ces échecs sont conservés, aucune ligne remplacée par une réussite fictive.
