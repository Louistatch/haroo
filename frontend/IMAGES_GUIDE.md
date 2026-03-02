# 🖼️ Guide d'Utilisation des Images

## ✅ Images Téléchargées

Toutes les images réelles ont été téléchargées avec succès depuis Unsplash (libre de droits).

### 📊 Statistique
- **Total**: 27 images
- **Hero**: 4 images (1920x1080px)
- **Cultures**: 8 images (800x600px)
- **Agronomes**: 12 avatars (400x400px)
- **Placeholders**: 3 images par défaut

## 📁 Structure des Dossiers

```
public/images/
├── hero/                    # Images de bannière (1920x1080px)
│   ├── agriculture.jpg      # Agriculture africaine (377 KB)
│   ├── farmer.jpg           # Agriculteur au travail (579 KB)
│   ├── harvest.jpg          # Récolte (589 KB)
│   └── market.jpg           # Marché local (386 KB)
│
├── cultures/                # Images de cultures (800x600px)
│   ├── mais.jpg             # Maïs (168 KB)
│   ├── riz.jpg              # Riz (74 KB)
│   ├── tomate.jpg           # Tomates (26 KB)
│   ├── oignon.jpg           # Oignons (132 KB)
│   ├── arachide.jpg         # Arachides (96 KB)
│   ├── manioc.jpg           # Manioc (52 KB)
│   ├── soja.jpg             # Soja (106 KB)
│   └── coton.jpg            # Coton (50 KB)
│
├── users/                   # Avatars d'agronomes (400x400px)
│   ├── agronomist-1.jpg     # Agronome 1 (25 KB)
│   ├── agronomist-2.jpg     # Agronome 2 (25 KB)
│   ├── ...                  # ... (jusqu'à 12)
│   └── agronomist-12.jpg    # Agronome 12 (40 KB)
│
└── placeholder/             # Images par défaut
    ├── user-default.jpg     # Avatar par défaut (12 KB)
    ├── document-default.jpg # Document par défaut (178 KB)
    └── culture-default.jpg  # Culture par défaut (105 KB)
```

## 🎨 Utilisation dans React

### 1. Images de Hero (Landing Page)

```tsx
// Dans Landing.tsx
<div className="hero" style={{
  backgroundImage: 'url(/images/hero/agriculture.jpg)'
}}>
  <h1>Plateforme Agricole Intelligente du Togo</h1>
</div>

// Ou avec img tag
<img 
  src="/images/hero/farmer.jpg" 
  alt="Agriculteur togolais"
  className="hero-image"
/>
```

### 2. Avatars d'Agronomes (Agronomists.tsx)

```tsx
// Dans Agronomists.tsx
const agronomists = [
  {
    id: 1,
    name: "Dr. Kofi Mensah",
    photo: "/images/users/agronomist-1.jpg",
    specializations: ["Maïs", "Riz"]
  },
  {
    id: 2,
    name: "Mme. Ama Diallo",
    photo: "/images/users/agronomist-2.jpg",
    specializations: ["Tomate", "Oignon"]
  },
  // ...
];

// Affichage
<img 
  src={agronomist.photo} 
  alt={agronomist.name}
  className="agronomist-avatar"
  onError={(e) => {
    e.currentTarget.src = '/images/placeholder/user-default.jpg';
  }}
/>
```

### 3. Images de Cultures (Documents.tsx)

```tsx
// Dans Documents.tsx
const documents = [
  {
    id: 1,
    title: "Guide de Culture du Maïs",
    culture: "Maïs",
    image: "/images/cultures/mais.jpg"
  },
  {
    id: 2,
    title: "Techniques de Riziculture",
    culture: "Riz",
    image: "/images/cultures/riz.jpg"
  },
  // ...
];

// Affichage
<img 
  src={document.image} 
  alt={document.culture}
  className="document-thumbnail"
/>
```

### 4. Images avec Fallback

```tsx
// Composant réutilisable avec fallback
const SafeImage = ({ src, alt, fallback, className }) => {
  const [imgSrc, setImgSrc] = useState(src);
  
  return (
    <img 
      src={imgSrc}
      alt={alt}
      className={className}
      onError={() => setImgSrc(fallback || '/images/placeholder/user-default.jpg')}
    />
  );
};

// Utilisation
<SafeImage 
  src="/images/users/agronomist-1.jpg"
  alt="Agronome"
  fallback="/images/placeholder/user-default.jpg"
  className="avatar"
/>
```

## 🎯 Exemples d'Intégration

### Dashboard.tsx

```tsx
// Section Hero
<div className="dashboard-hero">
  <img 
    src="/images/hero/agriculture.jpg" 
    alt="Agriculture"
    className="hero-bg"
  />
  <div className="hero-content">
    <h1>Bienvenue sur votre tableau de bord</h1>
  </div>
</div>

// Statistiques avec icônes
<div className="stats-card">
  <img src="/images/cultures/mais.jpg" alt="Cultures" />
  <h3>Mes Cultures</h3>
  <p>5 cultures actives</p>
</div>
```

### Agronomists.tsx

```tsx
// Carte d'agronome
<div className="agronomist-card">
  <img 
    src={`/images/users/agronomist-${index + 1}.jpg`}
    alt={agronomist.name}
    className="agronomist-photo"
  />
  <h3>{agronomist.name}</h3>
  <div className="specializations">
    {agronomist.specializations.map(spec => (
      <span key={spec} className="badge">
        <img src={`/images/cultures/${spec.toLowerCase()}.jpg`} />
        {spec}
      </span>
    ))}
  </div>
</div>
```

### Documents.tsx

```tsx
// Catalogue de documents
<div className="document-grid">
  {documents.map(doc => (
    <div key={doc.id} className="document-card">
      <img 
        src={doc.image}
        alt={doc.title}
        className="document-image"
      />
      <h3>{doc.title}</h3>
      <p className="price">{doc.price} FCFA</p>
      <button>Acheter</button>
    </div>
  ))}
</div>
```

## 🚀 Optimisation des Images

Les images sont déjà optimisées, mais vous pouvez les optimiser davantage:

```bash
# Installer sharp (si pas déjà fait)
npm install sharp

# Optimiser toutes les images
node optimize-images.js
```

## 📱 Responsive Images

Utilisez srcset pour différentes tailles d'écran:

```tsx
<img 
  src="/images/hero/agriculture.jpg"
  srcSet="
    /images/hero/agriculture.jpg 1920w,
    /images/hero/agriculture-medium.jpg 1024w,
    /images/hero/agriculture-small.jpg 640w
  "
  sizes="(max-width: 640px) 640px, (max-width: 1024px) 1024px, 1920px"
  alt="Agriculture"
/>
```

## 🎨 CSS pour les Images

```css
/* Images de hero */
.hero-image {
  width: 100%;
  height: 500px;
  object-fit: cover;
  object-position: center;
}

/* Avatars d'agronomes */
.agronomist-avatar {
  width: 120px;
  height: 120px;
  border-radius: 50%;
  object-fit: cover;
  border: 3px solid #2e7d32;
}

/* Images de cultures */
.culture-image {
  width: 100%;
  height: 200px;
  object-fit: cover;
  border-radius: 8px;
}

/* Placeholder avec effet de chargement */
.image-loading {
  background: linear-gradient(90deg, #f0f0f0 25%, #e0e0e0 50%, #f0f0f0 75%);
  background-size: 200% 100%;
  animation: loading 1.5s infinite;
}

@keyframes loading {
  0% { background-position: 200% 0; }
  100% { background-position: -200% 0; }
}
```

## ✨ Bonnes Pratiques

1. **Toujours utiliser un fallback**
   ```tsx
   onError={(e) => e.currentTarget.src = '/images/placeholder/user-default.jpg'}
   ```

2. **Ajouter des alt text descriptifs**
   ```tsx
   alt="Dr. Kofi Mensah, agronome spécialisé en maïs et riz"
   ```

3. **Lazy loading pour les performances**
   ```tsx
   loading="lazy"
   ```

4. **Utiliser object-fit pour maintenir les proportions**
   ```css
   object-fit: cover;
   object-position: center;
   ```

5. **Précharger les images critiques**
   ```html
   <link rel="preload" as="image" href="/images/hero/agriculture.jpg">
   ```

## 📄 License

Toutes les images proviennent de **Unsplash** et sont sous **Unsplash License**:
- ✅ Utilisation commerciale autorisée
- ✅ Modification autorisée
- ✅ Pas d'attribution requise (mais appréciée)
- ✅ Libre de droits

Source: https://unsplash.com/license

## 🔄 Mise à Jour des Images

Pour télécharger de nouvelles images:

```bash
# Télécharger de nouvelles images
python download_images_simple.py

# Ou télécharger des images spécifiques
python download_real_images.py
```

## 📞 Support

Si vous avez besoin d'images supplémentaires:
1. Visitez https://unsplash.com
2. Recherchez "african agriculture", "togo farming", etc.
3. Téléchargez et placez dans le dossier approprié
4. Optimisez avec `node optimize-images.js`

---

**Dernière mise à jour**: Mars 2026
**Total d'images**: 27 images réelles
**Taille totale**: ~3.5 MB
