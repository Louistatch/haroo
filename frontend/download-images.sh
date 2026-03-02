#!/bin/bash

# Script pour télécharger des images de placeholder
# Usage: bash download-images.sh

echo "🖼️  Configuration des images pour la Plateforme Agricole Togo"
echo "============================================================"

# Créer les dossiers nécessaires
echo "📁 Création des dossiers..."
mkdir -p public/images/hero
mkdir -p public/images/users
mkdir -p public/images/cultures
mkdir -p public/images/icons
mkdir -p public/images/placeholder

echo "✅ Dossiers créés!"

# Instructions pour télécharger les images
echo ""
echo "📸 Téléchargez les images suivantes:"
echo ""
echo "1️⃣  IMAGES DE HERO (1920x1080px)"
echo "   → Unsplash: https://unsplash.com/s/photos/african-agriculture"
echo "   → Sauvegarder dans: public/images/hero/"
echo "   → Noms: agriculture.jpg, farmer.jpg, harvest.jpg"
echo ""
echo "2️⃣  AVATARS D'AGRONOMES (400x400px)"
echo "   → UI Faces: https://uifaces.co/"
echo "   → This Person: https://thispersondoesnotexist.com/"
echo "   → Sauvegarder dans: public/images/users/"
echo "   → Noms: agronomist-1.jpg à agronomist-10.jpg"
echo ""
echo "3️⃣  IMAGES DE CULTURES (800x600px)"
echo "   → Pixabay: https://pixabay.com/images/search/crops/"
echo "   → Sauvegarder dans: public/images/cultures/"
echo "   → Noms: mais.jpg, riz.jpg, manioc.jpg, tomate.jpg, oignon.jpg, arachide.jpg"
echo ""
echo "4️⃣  PLACEHOLDER PAR DÉFAUT"
echo "   → Télécharger: https://via.placeholder.com/400x400/2e7d32/ffffff?text=User"
echo "   → Sauvegarder comme: public/images/placeholder/user-default.jpg"
echo ""

# Créer un fichier placeholder simple
echo "🎨 Création d'un placeholder temporaire..."
cat > public/images/placeholder/README.md << 'EOF'
# Images Placeholder

Ce dossier contient les images par défaut utilisées quand les vraies images ne sont pas disponibles.

## Images nécessaires:
- user-default.jpg (400x400px) - Avatar par défaut
- document-default.jpg (800x600px) - Document par défaut
- culture-default.jpg (800x600px) - Culture par défaut

## Télécharger des placeholders:
- https://via.placeholder.com/400x400
- https://placehold.co/400x400
- https://dummyimage.com/400x400
EOF

echo "✅ Placeholder README créé!"

# Créer un fichier d'index des images
cat > public/images/INDEX.md << 'EOF'
# Index des Images

## Structure des Dossiers

```
images/
├── hero/                    # Images de bannière (1920x1080px)
│   ├── agriculture.jpg
│   ├── farmer.jpg
│   └── harvest.jpg
├── users/                   # Avatars d'utilisateurs (400x400px)
│   ├── agronomist-1.jpg
│   ├── agronomist-2.jpg
│   └── ... (jusqu'à 15)
├── cultures/                # Images de cultures (800x600px)
│   ├── mais.jpg
│   ├── riz.jpg
│   ├── manioc.jpg
│   ├── tomate.jpg
│   ├── oignon.jpg
│   └── arachide.jpg
├── icons/                   # Icônes SVG
│   ├── document.svg
│   ├── agronomist.svg
│   └── agriculture.svg
└── placeholder/             # Images par défaut
    ├── user-default.jpg
    ├── document-default.jpg
    └── culture-default.jpg
```

## Sources Recommandées

### Images Gratuites et Libres de Droits:
1. **Unsplash** - https://unsplash.com
   - Recherche: "african agriculture", "togo farming"
   
2. **Pexels** - https://pexels.com
   - Recherche: "african farmer", "west africa farm"
   
3. **Pixabay** - https://pixabay.com
   - Recherche: "agriculture", "crops"

### Avatars:
1. **UI Faces** - https://uifaces.co
2. **This Person Does Not Exist** - https://thispersondoesnotexist.com
3. **Generated Photos** - https://generated.photos

### Icônes:
1. **Flaticon** - https://flaticon.com
2. **Icons8** - https://icons8.com
3. **Font Awesome** - https://fontawesome.com

## Optimisation

Après avoir téléchargé les images, optimisez-les:

```bash
npm install sharp
node optimize-images.js
```

## Checklist

- [ ] 3 images de hero téléchargées
- [ ] 10 avatars d'agronomes téléchargés
- [ ] 6 images de cultures téléchargées
- [ ] 3 placeholders créés
- [ ] Images optimisées (< 200KB chacune)
- [ ] Testées dans le navigateur

## Notes

- Toutes les images doivent être libres de droits
- Format recommandé: JPEG pour les photos, SVG pour les icônes
- Qualité: 85% pour un bon compromis taille/qualité
- Nommage: kebab-case (ex: agronomist-1.jpg)
EOF

echo "✅ Index des images créé!"

echo ""
echo "🎉 Configuration terminée!"
echo ""
echo "📝 Prochaines étapes:"
echo "   1. Téléchargez les images depuis les liens ci-dessus"
echo "   2. Placez-les dans les dossiers appropriés"
echo "   3. Optimisez-les avec: npm install sharp && node optimize-images.js"
echo "   4. Testez le site: npm run dev"
echo ""
echo "📚 Consultez public/images/INDEX.md pour plus de détails"
echo ""
