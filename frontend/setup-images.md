# Guide de Configuration des Images

## 🖼️ Images Nécessaires pour un Rendu Professionnel

### 1. Images de Hero (Page d'accueil)

**Télécharger depuis Unsplash:**

1. **Agriculture togolaise**
   - URL: https://unsplash.com/s/photos/african-agriculture
   - Recherche: "african agriculture", "togo farming", "west africa farm"
   - Taille recommandée: 1920x1080px
   - Sauvegarder comme: `frontend/public/images/hero-agriculture.jpg`

2. **Agriculteur au travail**
   - URL: https://unsplash.com/s/photos/african-farmer
   - Recherche: "african farmer", "farmer working"
   - Taille recommandée: 1920x1080px
   - Sauvegarder comme: `frontend/public/images/hero-farmer.jpg`

### 2. Photos d'Agronomes (Avatars)

**Sources recommandées:**
- **UI Faces**: https://uifaces.co/ (avatars gratuits)
- **This Person Does Not Exist**: https://thispersondoesnotexist.com/ (IA)
- **Pexels**: https://www.pexels.com/search/african%20professional/

**Instructions:**
1. Télécharger 10-15 photos professionnelles
2. Format: 400x400px (carré)
3. Nommer: `agronomist-1.jpg`, `agronomist-2.jpg`, etc.
4. Sauvegarder dans: `frontend/public/images/users/`

### 3. Images de Cultures

**Télécharger depuis Pixabay:**

1. **Maïs** - https://pixabay.com/images/search/corn%20field/
   - Sauvegarder comme: `frontend/public/images/cultures/mais.jpg`

2. **Riz** - https://pixabay.com/images/search/rice%20field/
   - Sauvegarder comme: `frontend/public/images/cultures/riz.jpg`

3. **Manioc** - https://pixabay.com/images/search/cassava/
   - Sauvegarder comme: `frontend/public/images/cultures/manioc.jpg`

4. **Tomate** - https://pixabay.com/images/search/tomato%20farm/
   - Sauvegarder comme: `frontend/public/images/cultures/tomate.jpg`

5. **Oignon** - https://pixabay.com/images/search/onion%20farm/
   - Sauvegarder comme: `frontend/public/images/cultures/oignon.jpg`

6. **Arachide** - https://pixabay.com/images/search/peanut%20farm/
   - Sauvegarder comme: `frontend/public/images/cultures/arachide.jpg`

### 4. Icônes et Illustrations

**Télécharger depuis:**
- **Flaticon**: https://www.flaticon.com/
- **Icons8**: https://icons8.com/

**Icônes nécessaires:**
- 📄 Document (document-icon.svg)
- 👨‍🌾 Agronome (agronomist-icon.svg)
- 🌾 Agriculture (agriculture-icon.svg)
- 💰 Paiement (payment-icon.svg)

## 📁 Structure des Dossiers

```
frontend/public/images/
├── hero/
│   ├── agriculture.jpg
│   ├── farmer.jpg
│   └── harvest.jpg
├── users/
│   ├── agronomist-1.jpg
│   ├── agronomist-2.jpg
│   └── ... (jusqu'à 15)
├── cultures/
│   ├── mais.jpg
│   ├── riz.jpg
│   ├── manioc.jpg
│   ├── tomate.jpg
│   ├── oignon.jpg
│   └── arachide.jpg
├── icons/
│   ├── document.svg
│   ├── agronomist.svg
│   └── agriculture.svg
└── placeholder/
    └── user-default.jpg
```

## 🎨 Recommandations de Style

### Pour les Photos de Hero:
- **Luminosité**: Lumière naturelle, ensoleillée
- **Composition**: Champs en premier plan, ciel bleu
- **Couleurs**: Tons verts et dorés dominants
- **Ambiance**: Positive, dynamique, professionnelle

### Pour les Avatars d'Agronomes:
- **Style**: Photos professionnelles, fond neutre
- **Expression**: Souriant, confiant, accessible
- **Vêtements**: Tenue professionnelle ou de terrain
- **Diversité**: Hommes et femmes, différents âges

### Pour les Images de Cultures:
- **Qualité**: Haute résolution, nettes
- **Angle**: Vue d'ensemble du champ
- **Saison**: Cultures matures, prêtes à récolter
- **Contexte**: Environnement africain si possible

## 🔧 Script d'Optimisation Automatique

Créer un fichier `optimize-images.js`:

```javascript
const sharp = require('sharp');
const fs = require('fs');
const path = require('path');

const directories = [
  { input: './raw/hero', output: './public/images/hero', width: 1920, height: 1080 },
  { input: './raw/users', output: './public/images/users', width: 400, height: 400 },
  { input: './raw/cultures', output: './public/images/cultures', width: 800, height: 600 }
];

directories.forEach(dir => {
  if (!fs.existsSync(dir.input)) return;
  
  fs.readdirSync(dir.input).forEach(file => {
    if (file.match(/\.(jpg|jpeg|png)$/i)) {
      sharp(path.join(dir.input, file))
        .resize(dir.width, dir.height, { fit: 'cover', position: 'center' })
        .jpeg({ quality: 85, progressive: true })
        .toFile(path.join(dir.output, file.replace(/\.(png|jpeg)$/i, '.jpg')))
        .then(() => console.log(`✓ Optimisé: ${file}`))
        .catch(err => console.error(`✗ Erreur: ${file}`, err));
    }
  });
});
```

**Utilisation:**
```bash
npm install sharp
node optimize-images.js
```

## 🌐 Alternative: Utiliser des API d'Images

### Unsplash API (Gratuit)

```typescript
// frontend/src/utils/unsplash.ts
const UNSPLASH_ACCESS_KEY = 'YOUR_ACCESS_KEY';

export const getRandomFarmerImage = async () => {
  const response = await fetch(
    `https://api.unsplash.com/photos/random?query=african-farmer&client_id=${UNSPLASH_ACCESS_KEY}`
  );
  const data = await response.json();
  return data.urls.regular;
};
```

### Utilisation dans le composant:

```typescript
const [heroImage, setHeroImage] = useState('');

useEffect(() => {
  getRandomFarmerImage().then(setHeroImage);
}, []);

<div style={{ backgroundImage: `url(${heroImage})` }}>
```

## 📝 Checklist de Configuration

- [ ] Créer les dossiers d'images
- [ ] Télécharger 3 images de hero
- [ ] Télécharger 10-15 avatars d'agronomes
- [ ] Télécharger 6 images de cultures
- [ ] Télécharger les icônes nécessaires
- [ ] Optimiser toutes les images
- [ ] Tester l'affichage sur le site
- [ ] Vérifier la performance (< 3s de chargement)

## 🎯 Images Prioritaires (Minimum Viable)

Si vous manquez de temps, commencez par:

1. **1 image de hero** (agriculture.jpg)
2. **5 avatars d'agronomes** (agronomist-1.jpg à 5.jpg)
3. **3 images de cultures** (mais.jpg, riz.jpg, manioc.jpg)
4. **1 placeholder par défaut** (user-default.jpg)

## 🔗 Liens Rapides

### Collections Unsplash Recommandées:
- Agriculture Africaine: https://unsplash.com/collections/4387360/african-agriculture
- Fermiers: https://unsplash.com/collections/1163637/farmers
- Cultures: https://unsplash.com/collections/1548919/crops

### Recherches Pexels:
- https://www.pexels.com/search/african%20agriculture/
- https://www.pexels.com/search/togo%20farming/
- https://www.pexels.com/search/west%20africa%20farm/

### Pixabay:
- https://pixabay.com/images/search/african%20farm/
- https://pixabay.com/images/search/agriculture%20africa/

## 💡 Conseils Pro

1. **Cohérence visuelle**: Utilisez des images avec une palette de couleurs similaire
2. **Authenticité**: Privilégiez les vraies photos aux illustrations
3. **Contexte local**: Cherchez spécifiquement "Togo", "West Africa", "African"
4. **Qualité**: Minimum 1200px de largeur pour les images principales
5. **Optimisation**: Toujours compresser avant d'uploader (max 200KB par image)

## 🚀 Résultat Attendu

Avec ces images, votre plateforme aura:
- ✅ Un aspect professionnel et crédible
- ✅ Une identité visuelle cohérente
- ✅ Une connexion émotionnelle avec les utilisateurs
- ✅ Une performance optimale (chargement rapide)
- ✅ Un design qui ne fait pas "IA" ou "template"

---

**Note**: Toutes les images doivent être libres de droits ou sous licence Creative Commons. Vérifiez toujours les conditions d'utilisation avant de télécharger.
