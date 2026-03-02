# Guide Complet du Frontend - Plateforme Agricole Togo

## 📋 Pages Créées

### 1. **Page d'Accueil (Landing)** ✅
- **Route**: `/`
- **Fichier**: `frontend/src/pages/Landing.tsx`
- **Description**: Page d'accueil avec présentation de la plateforme
- **Fonctionnalités**: Hero section, features, CTA

### 2. **Tableau de Bord (Dashboard)** ✅
- **Route**: `/dashboard`
- **Fichier**: `frontend/src/pages/Dashboard.tsx`
- **Description**: Vue d'ensemble de l'activité utilisateur
- **Fonctionnalités**:
  - Statistiques rapides (missions, documents, dépenses)
  - Informations du profil
  - Actions rapides
  - Activité récente

### 3. **Documents Techniques** ✅
- **Route**: `/documents`
- **Fichier**: `frontend/src/pages/Documents.tsx`
- **Description**: Catalogue de documents agricoles
- **Fonctionnalités**:
  - Filtres par culture, région, recherche
  - Grille de documents avec prix
  - Achat via Fedapay
  - Design responsive

### 4. **Annuaire des Agronomes** ✅
- **Route**: `/agronomists`
- **Fichier**: `frontend/src/pages/Agronomists.tsx`
- **Description**: Liste des agronomes validés
- **Fonctionnalités**:
  - Filtres par région, spécialisation
  - Système de notation (étoiles)
  - Modal de détails avec contact
  - Badge de validation

### 5. **Profil Utilisateur** ✅
- **Route**: `/me`
- **Fichier**: `frontend/src/pages/Profile.tsx`
- **Description**: Gestion du profil personnel

### 6. **Connexion / Inscription** ✅
- **Routes**: `/login`, `/register`
- **Fichiers**: `frontend/src/pages/Login.tsx`, `Register.tsx`

## 🎨 Styles CSS Créés

1. **documents.css** - Style pour la page documents
2. **agronomists.css** - Style pour l'annuaire des agronomes
3. **dashboard.css** - Style pour le tableau de bord
4. **theme.css** - Thème global (déjà existant)
5. **responsive.css** - Styles responsive (déjà existant)
6. **forms.css** - Styles des formulaires (déjà existant)

## 🖼️ Guide pour Ajouter des Images Réelles

### Étape 1: Créer le dossier d'images

```bash
mkdir -p frontend/public/images
mkdir -p frontend/public/images/users
mkdir -p frontend/public/images/documents
mkdir -p frontend/public/images/hero
```

### Étape 2: Images recommandées

#### Images de Hero (Page d'accueil)
- **hero-agriculture.jpg** (1920x1080px) - Champ agricole togolais
- **hero-farmer.jpg** (1920x1080px) - Agriculteur au travail
- **hero-harvest.jpg** (1920x1080px) - Récolte

#### Images d'utilisateurs (Agronomes)
- **agronomist-1.jpg** à **agronomist-10.jpg** (400x400px)
- Photos professionnelles d'agronomes africains
- Format carré pour les avatars

#### Images de documents
- **document-icon.svg** - Icône de document
- **pdf-icon.svg** - Icône PDF
- **excel-icon.svg** - Icône Excel

#### Images de cultures
- **maize.jpg** - Maïs
- **rice.jpg** - Riz
- **cassava.jpg** - Manioc
- **tomato.jpg** - Tomate
- **onion.jpg** - Oignon

### Étape 3: Sources d'images gratuites

**Sites recommandés** (images libres de droits):
1. **Unsplash** (https://unsplash.com)
   - Recherche: "african farmer", "agriculture togo", "harvest"
   
2. **Pexels** (https://pexels.com)
   - Recherche: "african agriculture", "farming africa"
   
3. **Pixabay** (https://pixabay.com)
   - Recherche: "agriculture", "farmer", "crops"

4. **Wikimedia Commons** (https://commons.wikimedia.org)
   - Recherche: "Togo agriculture"

### Étape 4: Optimisation des images

```bash
# Installer sharp pour l'optimisation
npm install sharp

# Script d'optimisation (créer optimize-images.js)
const sharp = require('sharp');
const fs = require('fs');
const path = require('path');

const inputDir = './frontend/public/images/raw';
const outputDir = './frontend/public/images';

fs.readdirSync(inputDir).forEach(file => {
  sharp(path.join(inputDir, file))
    .resize(800, 800, { fit: 'cover' })
    .jpeg({ quality: 85 })
    .toFile(path.join(outputDir, file));
});
```

### Étape 5: Utiliser les images dans le code

#### Dans Agronomists.tsx:
```typescript
// Remplacer l'avatar emoji par une vraie image
<div className="avatar">
  <img 
    src={`/images/users/agronomist-${agro.id % 10 + 1}.jpg`}
    alt={`${agro.user.first_name} ${agro.user.last_name}`}
    style={{ width: '100%', height: '100%', objectFit: 'cover', borderRadius: '50%' }}
  />
</div>
```

#### Dans Documents.tsx:
```typescript
// Ajouter une image de culture
<div className="document-image">
  <img 
    src={`/images/cultures/${doc.culture.toLowerCase()}.jpg`}
    alt={doc.culture}
    style={{ width: '100%', height: '200px', objectFit: 'cover', borderRadius: '8px' }}
  />
</div>
```

#### Dans Landing.tsx:
```typescript
// Hero avec image de fond
<div 
  className="hero"
  style={{
    backgroundImage: 'url(/images/hero/agriculture.jpg)',
    backgroundSize: 'cover',
    backgroundPosition: 'center'
  }}
>
```

## 🚀 Lancer le Frontend

```bash
cd frontend
npm install
npm run dev
```

Le frontend sera accessible sur: http://localhost:5173

## 📱 Design Responsive

Toutes les pages sont optimisées pour:
- **Mobile**: 320px - 768px
- **Tablet**: 769px - 1024px
- **Desktop**: 1025px+

### Points de rupture CSS:
```css
/* Mobile */
@media (max-width: 768px) { }

/* Tablet */
@media (min-width: 769px) and (max-width: 1024px) { }

/* Desktop */
@media (min-width: 1025px) { }
```

## 🎨 Palette de Couleurs

### Couleurs Principales:
- **Vert Principal**: `#2e7d32` (Agriculture)
- **Vert Clair**: `#66bb6a`
- **Orange**: `#ff6f00` (Agronomes)
- **Orange Clair**: `#ffa726`
- **Bleu**: `#1976d2` (Informations)
- **Violet**: `#7b1fa2` (Premium)

### Couleurs Secondaires:
- **Gris Clair**: `#f5f5f5`
- **Gris Moyen**: `#666`
- **Gris Foncé**: `#333`
- **Blanc**: `#ffffff`

## 🔧 Composants Réutilisables

### Loading Spinner:
```typescript
<div className="loading-container">
  <div className="spinner"></div>
  <p>Chargement...</p>
</div>
```

### Card Template:
```typescript
<div className="card">
  <div className="card-header">
    <h3>Titre</h3>
  </div>
  <div className="card-body">
    Contenu
  </div>
  <div className="card-footer">
    Actions
  </div>
</div>
```

### Button Styles:
```css
.btn-primary { /* Vert */ }
.btn-secondary { /* Gris */ }
.btn-danger { /* Rouge */ }
.btn-success { /* Vert clair */ }
```

## 📊 Intégration API

### Configuration Axios:
```typescript
// frontend/src/api/client.ts
import axios from 'axios';

const API_BASE_URL = 'http://localhost:8000/api/v1';

export const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Intercepteur pour ajouter le token
apiClient.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});
```

## 🔐 Authentification

### Vérifier l'authentification:
```typescript
const isAuthenticated = () => {
  return Boolean(localStorage.getItem('access_token'));
};
```

### Déconnexion:
```typescript
const handleLogout = () => {
  localStorage.removeItem('access_token');
  localStorage.removeItem('refresh_token');
  navigate('/login');
};
```

## 📝 TODO - Améliorations Futures

### Pages à Ajouter:
- [ ] Page Missions (liste et détails)
- [ ] Page Préventes Agricoles
- [ ] Page Ouvriers Saisonniers
- [ ] Page Historique des Achats
- [ ] Page Notifications
- [ ] Page Paramètres

### Fonctionnalités à Ajouter:
- [ ] Système de notifications en temps réel (WebSocket)
- [ ] Chat en direct avec les agronomes
- [ ] Carte interactive pour la localisation
- [ ] Graphiques de statistiques (Chart.js)
- [ ] Export PDF des documents
- [ ] Mode sombre
- [ ] Multilingue (Français, Ewe, Kabyè)

### Optimisations:
- [ ] Lazy loading des images
- [ ] Code splitting
- [ ] Service Worker pour PWA
- [ ] Compression des assets
- [ ] CDN pour les images

## 🐛 Débogage

### Problèmes courants:

1. **CORS Error**:
```python
# Dans Django settings.py
CORS_ALLOWED_ORIGINS = [
    "http://localhost:5173",
]
```

2. **Images ne s'affichent pas**:
- Vérifier le chemin: `/images/...` (pas `./images/...`)
- Vérifier que les images sont dans `frontend/public/images/`

3. **API ne répond pas**:
- Vérifier que le backend Django tourne sur port 8000
- Vérifier les tokens d'authentification

## 📚 Documentation Technique

### Structure des Dossiers:
```
frontend/
├── public/
│   └── images/          # Images statiques
├── src/
│   ├── api/            # Clients API
│   ├── components/     # Composants réutilisables
│   ├── hooks/          # Custom hooks
│   ├── pages/          # Pages de l'application
│   ├── styles/         # Fichiers CSS
│   ├── utils/          # Fonctions utilitaires
│   ├── App.tsx         # Composant principal
│   └── main.tsx        # Point d'entrée
└── package.json
```

### Technologies Utilisées:
- **React 18** - Framework UI
- **TypeScript** - Typage statique
- **React Router 6** - Routing
- **Axios** - Requêtes HTTP
- **Vite** - Build tool
- **CSS3** - Styling

## 🎯 Checklist de Déploiement

- [ ] Optimiser les images
- [ ] Minifier le CSS/JS
- [ ] Configurer les variables d'environnement
- [ ] Tester sur différents navigateurs
- [ ] Tester sur mobile réel
- [ ] Vérifier l'accessibilité (WCAG)
- [ ] Configurer le CDN
- [ ] Activer HTTPS
- [ ] Configurer le cache
- [ ] Ajouter Google Analytics

## 📞 Support

Pour toute question ou problème:
1. Vérifier cette documentation
2. Consulter les logs du navigateur (F12)
3. Vérifier les logs du backend Django
4. Tester avec Postman pour isoler les problèmes API

---

**Dernière mise à jour**: Mars 2026
**Version**: 1.0.0
**Statut**: ✅ MVP Complet
