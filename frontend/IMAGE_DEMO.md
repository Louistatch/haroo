# 🎨 Démonstration d'Utilisation des Images

## 📸 Images Disponibles

### Hero Images (1920x1080px)
```
/images/hero/agriculture.jpg  - Agriculture africaine
/images/hero/farmer.jpg       - Agriculteur au travail
/images/hero/harvest.jpg      - Récolte
/images/hero/market.jpg       - Marché local
```

### Avatars Agronomes (400x400px)
```
/images/users/agronomist-1.jpg  à  /images/users/agronomist-12.jpg
```

### Cultures (800x600px)
```
/images/cultures/mais.jpg
/images/cultures/riz.jpg
/images/cultures/tomate.jpg
/images/cultures/oignon.jpg
/images/cultures/arachide.jpg
/images/cultures/manioc.jpg
/images/cultures/soja.jpg
/images/cultures/coton.jpg
```

## 🔧 Intégration dans les Pages

### 1. Landing.tsx - Page d'Accueil

Remplacez la section hero actuelle par:

```tsx
<section className="hero" style={{
  backgroundImage: 'url(/images/hero/agriculture.jpg)',
  backgroundSize: 'cover',
  backgroundPosition: 'center',
  height: '600px',
  position: 'relative'
}}>
  <div style={{
    position: 'absolute',
    top: 0,
    left: 0,
    right: 0,
    bottom: 0,
    backgroundColor: 'rgba(0, 0, 0, 0.4)',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center'
  }}>
    <div style={{ textAlign: 'center', color: 'white', padding: '2rem' }}>
      <h1 style={{ fontSize: '3rem', marginBottom: '1rem' }}>
        Plateforme Agricole Intelligente du Togo
      </h1>
      <p style={{ fontSize: '1.5rem', marginBottom: '2rem' }}>
        Connectez-vous avec des agronomes, accédez à des documents techniques
      </p>
      <button className="cta-button">Commencer</button>
    </div>
  </div>
</section>

{/* Section Features avec images */}
<section className="features" style={{ padding: '4rem 2rem' }}>
  <div className="feature-grid" style={{ 
    display: 'grid', 
    gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))',
    gap: '2rem',
    maxWidth: '1200px',
    margin: '0 auto'
  }}>
    <div className="feature-card">
      <img 
        src="/images/hero/farmer.jpg" 
        alt="Agronomes"
        style={{ width: '100%', height: '200px', objectFit: 'cover', borderRadius: '8px' }}
      />
      <h3>Trouvez des Agronomes</h3>
      <p>Connectez-vous avec des experts agricoles certifiés</p>
    </div>
    
    <div className="feature-card">
      <img 
        src="/images/cultures/mais.jpg" 
        alt="Documents"
        style={{ width: '100%', height: '200px', objectFit: 'cover', borderRadius: '8px' }}
      />
      <h3>Documents Techniques</h3>
      <p>Accédez à des guides de culture personnalisés</p>
    </div>
    
    <div className="feature-card">
      <img 
        src="/images/hero/market.jpg" 
        alt="Marché"
        style={{ width: '100%', height: '200px', objectFit: 'cover', borderRadius: '8px' }}
      />
      <h3>Accès au Marché</h3>
      <p>Vendez vos produits directement aux acheteurs</p>
    </div>
  </div>
</section>
```

### 2. Dashboard.tsx - Tableau de Bord

Ajoutez des images aux cartes de statistiques:

```tsx
<div className="dashboard-stats">
  <div className="stat-card">
    <div className="stat-icon">
      <img 
        src="/images/cultures/mais.jpg" 
        alt="Cultures"
        style={{ width: '60px', height: '60px', borderRadius: '50%', objectFit: 'cover' }}
      />
    </div>
    <div className="stat-info">
      <h3>Mes Cultures</h3>
      <p className="stat-value">5</p>
      <p className="stat-label">cultures actives</p>
    </div>
  </div>

  <div className="stat-card">
    <div className="stat-icon">
      <img 
        src="/images/users/agronomist-1.jpg" 
        alt="Agronomes"
        style={{ width: '60px', height: '60px', borderRadius: '50%', objectFit: 'cover' }}
      />
    </div>
    <div className="stat-info">
      <h3>Agronomes</h3>
      <p className="stat-value">3</p>
      <p className="stat-label">consultations</p>
    </div>
  </div>

  <div className="stat-card">
    <div className="stat-icon">
      <img 
        src="/images/hero/harvest.jpg" 
        alt="Récoltes"
        style={{ width: '60px', height: '60px', borderRadius: '50%', objectFit: 'cover' }}
      />
    </div>
    <div className="stat-info">
      <h3>Récoltes</h3>
      <p className="stat-value">2</p>
      <p className="stat-label">prévues ce mois</p>
    </div>
  </div>
</div>
```

### 3. Agronomists.tsx - Annuaire des Agronomes

Utilisez les vraies photos d'agronomes:

```tsx
const mockAgronomists = [
  {
    id: 1,
    name: "Dr. Kofi Mensah",
    photo: "/images/users/agronomist-1.jpg",
    specializations: ["Maïs", "Riz"],
    location: "Lomé, Maritime",
    rating: 4.8,
    reviews: 24,
    verified: true
  },
  {
    id: 2,
    name: "Mme. Ama Diallo",
    photo: "/images/users/agronomist-2.jpg",
    specializations: ["Tomate", "Oignon"],
    location: "Kara, Kara",
    rating: 4.9,
    reviews: 31,
    verified: true
  },
  {
    id: 3,
    name: "M. Kwame Asante",
    photo: "/images/users/agronomist-3.jpg",
    specializations: ["Manioc", "Arachide"],
    location: "Sokodé, Centrale",
    rating: 4.7,
    reviews: 18,
    verified: true
  },
  {
    id: 4,
    name: "Dr. Fatou Ndiaye",
    photo: "/images/users/agronomist-4.jpg",
    specializations: ["Riz", "Soja"],
    location: "Dapaong, Savanes",
    rating: 4.9,
    reviews: 42,
    verified: true
  },
  {
    id: 5,
    name: "M. Ibrahim Touré",
    photo: "/images/users/agronomist-5.jpg",
    specializations: ["Coton", "Maïs"],
    location: "Atakpamé, Plateaux",
    rating: 4.6,
    reviews: 15,
    verified: true
  },
  {
    id: 6,
    name: "Mme. Aïcha Keita",
    photo: "/images/users/agronomist-6.jpg",
    specializations: ["Tomate", "Oignon"],
    location: "Lomé, Maritime",
    rating: 4.8,
    reviews: 28,
    verified: true
  }
];

// Dans le rendu
<div className="agronomist-card">
  <img 
    src={agronomist.photo}
    alt={agronomist.name}
    className="agronomist-photo"
    onError={(e) => {
      e.currentTarget.src = '/images/placeholder/user-default.jpg';
    }}
  />
  <div className="agronomist-info">
    <h3>{agronomist.name}</h3>
    {agronomist.verified && (
      <span className="badge-verified">✓ Vérifié</span>
    )}
    <div className="rating">
      {'⭐'.repeat(Math.floor(agronomist.rating))} {agronomist.rating} ({agronomist.reviews} avis)
    </div>
    <p className="location">📍 {agronomist.location}</p>
    <div className="specializations">
      {agronomist.specializations.map(spec => (
        <span key={spec} className="badge">{spec}</span>
      ))}
    </div>
  </div>
</div>
```

### 4. Documents.tsx - Catalogue de Documents

Associez chaque document à une image de culture:

```tsx
const mockDocuments = [
  {
    id: 1,
    title: "Guide Complet de Culture du Maïs",
    description: "Techniques modernes de culture du maïs adaptées au climat togolais",
    culture: "Maïs",
    image: "/images/cultures/mais.jpg",
    price: 5000,
    region: "Toutes régions",
    type: "Guide de culture"
  },
  {
    id: 2,
    title: "Techniques de Riziculture Intensive",
    description: "Méthodes pour augmenter le rendement du riz",
    culture: "Riz",
    image: "/images/cultures/riz.jpg",
    price: 4500,
    region: "Maritime, Plateaux",
    type: "Guide de culture"
  },
  {
    id: 3,
    title: "Production de Tomates en Saison Sèche",
    description: "Irrigation et gestion des tomates hors saison",
    culture: "Tomate",
    image: "/images/cultures/tomate.jpg",
    price: 3500,
    region: "Toutes régions",
    type: "Guide de culture"
  },
  {
    id: 4,
    title: "Culture de l'Oignon: De la Plantation à la Récolte",
    description: "Guide complet pour la culture de l'oignon",
    culture: "Oignon",
    image: "/images/cultures/oignon.jpg",
    price: 3000,
    region: "Savanes, Kara",
    type: "Guide de culture"
  },
  {
    id: 5,
    title: "Arachide: Techniques de Production Améliorées",
    description: "Maximisez votre rendement d'arachide",
    culture: "Arachide",
    image: "/images/cultures/arachide.jpg",
    price: 4000,
    region: "Centrale, Kara",
    type: "Guide de culture"
  },
  {
    id: 6,
    title: "Manioc: Culture et Transformation",
    description: "De la plantation à la transformation du manioc",
    culture: "Manioc",
    image: "/images/cultures/manioc.jpg",
    price: 3500,
    region: "Toutes régions",
    type: "Guide de culture"
  }
];

// Dans le rendu
<div className="document-card">
  <img 
    src={document.image}
    alt={document.culture}
    className="document-image"
  />
  <div className="document-content">
    <span className="document-type">{document.type}</span>
    <h3>{document.title}</h3>
    <p className="document-description">{document.description}</p>
    <div className="document-meta">
      <span className="culture-badge">{document.culture}</span>
      <span className="region">📍 {document.region}</span>
    </div>
    <div className="document-footer">
      <span className="price">{document.price.toLocaleString('fr-FR')} FCFA</span>
      <button className="btn-buy">Acheter</button>
    </div>
  </div>
</div>
```

## 🎨 CSS Recommandé

Ajoutez ces styles pour optimiser l'affichage des images:

```css
/* Images générales */
img {
  max-width: 100%;
  height: auto;
  display: block;
}

/* Hero images */
.hero {
  position: relative;
  overflow: hidden;
}

.hero::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: linear-gradient(to bottom, rgba(0,0,0,0.3), rgba(0,0,0,0.6));
  z-index: 1;
}

.hero > * {
  position: relative;
  z-index: 2;
}

/* Avatars circulaires */
.agronomist-photo {
  width: 120px;
  height: 120px;
  border-radius: 50%;
  object-fit: cover;
  border: 4px solid #2e7d32;
  box-shadow: 0 4px 8px rgba(0,0,0,0.1);
}

/* Images de documents */
.document-image {
  width: 100%;
  height: 200px;
  object-fit: cover;
  border-radius: 8px 8px 0 0;
}

/* Effet hover sur les images */
.document-card:hover .document-image {
  transform: scale(1.05);
  transition: transform 0.3s ease;
}

/* Placeholder avec animation */
.image-loading {
  background: linear-gradient(90deg, #f0f0f0 25%, #e0e0e0 50%, #f0f0f0 75%);
  background-size: 200% 100%;
  animation: loading 1.5s infinite;
}

@keyframes loading {
  0% { background-position: 200% 0; }
  100% { background-position: -200% 0; }
}

/* Responsive */
@media (max-width: 768px) {
  .hero {
    height: 400px;
  }
  
  .agronomist-photo {
    width: 80px;
    height: 80px;
  }
  
  .document-image {
    height: 150px;
  }
}
```

## ✅ Checklist d'Intégration

- [ ] Remplacer les emojis par des vraies images dans Landing.tsx
- [ ] Ajouter les photos d'agronomes dans Agronomists.tsx
- [ ] Associer les images de cultures aux documents dans Documents.tsx
- [ ] Ajouter des images au Dashboard.tsx
- [ ] Implémenter les fallbacks pour toutes les images
- [ ] Ajouter le lazy loading: `loading="lazy"`
- [ ] Optimiser les images avec `node optimize-images.js`
- [ ] Tester sur mobile et desktop
- [ ] Vérifier les performances avec Lighthouse

## 🚀 Prochaines Étapes

1. **Intégrer les images dans les composants**
2. **Tester l'affichage sur différents écrans**
3. **Optimiser les performances**
4. **Ajouter plus d'images si nécessaire**

---

**Note**: Toutes les images sont sous licence Unsplash (libre d'utilisation commerciale)
