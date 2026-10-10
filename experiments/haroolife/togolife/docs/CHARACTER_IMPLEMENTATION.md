# Avatar original articulé — preuve d'implémentation

`src/character.js` produit un `THREE.SkinnedMesh` original avec 22 `Bone`, indices et poids de skinning GPU. Les volumes anatomiques, vêtements, chaussures et visage sont construits localement sans asset ni service externe. L'orientation avant est +Z ; le pivot est au sol. La hauteur initiale mesurée est 1,782 m.

API synchrone : `createCharacter({skin, shirt, trousers, hair, scale})` retourne `group`, `mesh`, `skeleton`, `joints`, `update(dt, speed)`, `animationState`, `dispose()`. La vitesse est exprimée en mètres par seconde ; la position, l'orientation et les collisions sont gérées par le contrôleur du jeu.

La locomotion transforme le squelette (hanches, genoux, chevilles, épaules, coudes, thorax), avec amortissement des transitions Idle/Walk/Run et fréquence du cycle dépendant de la vitesse. Les pieds ont un temps de récupération par flexion du genou. Ce n'est pas une animation de simples translations de formes.

## Vérification réellement exécutée

- `node --input-type=module --check < src/character.js` : réussi.
- Instanciation réelle du module avec Three.js dans Node, validation `isSkinnedMesh`, passage de 90 images pour chaque vitesse 0, 1,6, 4, 0 m/s, vérification des os finis, calcul des bounds et disposal : réussi.
- Résultat : 22 os, 4 597 sommets, 6 764 triangles, état final Idle.

La vérification visuelle en navigateur appartient au parcours de QA global ; elle n'est pas remplacée par ce test mathématique.

## Limites précises

Le personnage est stylisé avec des volumes organiques ellipsoïdaux. Les poids sont rigides par volume et les articulations se recouvrent ; ce n'est pas une peau sculptée avec poids continus. Il n'utilise pas glTF, mocap ou clips importés, ni IK garantissant des pieds exactement ancrés. Le rythme lié à la vitesse réduit le glissement sans l'éliminer. L'apparence se configure à la création. Les futurs modèles glTF pourront conserver la même API du contrôleur.

## Complément d'intégration — glTF réellement produit et chargé

Le 10 octobre, `scripts/export-avatar.mjs` a exporté le modèle original avec `GLTFExporter` Three.js r160 : `assets/avatar.gltf`, 517 962 octets, 22 os, trois clips Idle/Walk/Run. Les pistes ont été échantillonnées sur le rig original, pas obtenues par mocap. `src/avatar-loader.js` charge ce glTF pour le joueur avec GLTFLoader et AnimationMixer, crossfade de 180 ms et cadence liée à la vitesse. Le rig procédural reste une récupération en cas d'échec de chargement et le modèle des PNJ.

`tests/avatar.test.mjs` a réellement parsé le fichier glTF avec le loader officiel, vérifié les clips, le mouvement de l'os de hanche, les états Run puis Idle, personnalisation, valeurs finies et destruction. PASS. Aucun Blender utilisé ; aucune validation visuelle remplacée par cette vérification.
