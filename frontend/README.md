# 🌾 Frontend - Plateforme Agricole Intelligente du Togo

Interface utilisateur moderne et responsive pour la plateforme agricole du Togo.

## 🚀 Démarrage Rapide

```bash
# Installation des dépendances
npm install

# Lancement en mode développement
npm run dev

# Build pour la production
npm run build

# Prévisualisation du build
npm run preview
```

## 📁 Structure du Projet

```
frontend/
├── public/
│   └── images/              # Images statiques
│       ├── hero/           # Images de bannière
│       ├── users/          # Avatars d'utilisateurs
│       ├── cultures/       # Images de cultures
│       └── placeholder/    # Images par défaut
├── src/
│   ├── api/                # Clients API
│   ├── components/         # Composants réutilisables
│   │   ├── Header.tsx
│   │   ├── Loading.tsx
│   │   └── ...
│   ├── hooks/              # Custom React hooks
│   ├── pages/              # Pages de l'application
│   │   ├── Landing.tsx     # Page d'accueil
│   │   ├── Dashboard.tsx   # Tableau de bord
│   │   ├── Documents.tsx   # Catalogue de documents
│   │   ├── Agronomists.tsx # Annuaire des agronomes
│   │   ├── Login.tsx       # Connexion
│   │   ├── Register.tsx    # Inscription
│   │   └── Profile.tsx     # Profil utilisateur
│   ├── styles/             # Fichiers CSS
│   │   ├── theme.css       # Thème global
│   │   ├── responsive.css  # Styles responsive
│   │   ├── forms.css       # Styles des formulaires
│   │   ├── dashboard.css   # Dashboard
│   │   ├── documents.css   # Documents
│   │   └── agronomists.css # Agronomes
│   ├── utils/              # Fonctions utilitaires
│   ├── App.tsx             # Composant principal
│   └── main.tsx            # Point d'entrée
├── optimize-images.js      # Script d'optimisation
├── download-images.sh      # Script de téléchargement
└── package.json
```

## 🎨 Pages Disponibles

### 1. Landing Page (`/`)
Page d'accueil avec présentation de la plateforme
- Hero section
- Présentation des services
- Call-to-action

### 2. Dashboard (`/dashboard`)
Tableau de bord utilisateur (authentifié)
- Statistiques en temps réel
- Aperçu du profil
- Actions rapides
- Activité récente

### 3. Documents (`/documents`)
Catalogue de documents techniques
- Filtres avancés (culture, région)
- Système d'achat intégré
- Design en grille responsive

### 4. Agronomes (`/agronomists`)
Annuaire des agronomes validés
- Système de notation (étoiles)
- Filtres par région et spécialisation
- Modal de détails avec contact

### 5. Profil (`/me`)
Gestion du profil personnel (authentifié)
- Informations personnelles
- Historique d'activité
- Paramètres

### 6. Connexion / Inscription (`/login`, `/register`)
Authentification utilisateur
- Formulaires de connexion et inscription
- Validation en temps réel
- Gestion des erreurs

## 🎨 Design System

### Couleurs Principales

```css
--primary-green: #2e7d32;    /* Agriculture */
--light-green: #66bb6a;
--primary-orange: #ff6f00;   /* Agronomes */
--light-orange: #ffa726;
--primary-blue: #1976d2;     /* Informations */
--primary-purple: #7b1fa2;   /* Premium */
```

### Typographie

- **Police principale**: System fonts (optimisé pour chaque OS)
- **Tailles**: 0.85rem à 2.5rem
- **Poids**: 400 (normal), 500 (medium), 600 (semi-bold), 700 (bold)

### Breakpoints Responsive

```css
/* Mobile */
@media (max-width: 768px) { }

/* Tablet */
@media (min-width: 769px) and (max-width: 1024px) { }

/* Desktop */
@media (min-width: 1025px) { }
```

## 🖼️ Configuration des Images

### Étape 1: Télécharger les Images

```bash
# Exécuter le script de configuration
bash download-images.sh
```

### Étape 2: Ajouter vos Images

Placez vos images dans:
- `public/images/raw/hero/` - Images de bannière (1920x1080px)
- `public/images/raw/users/` - Avatars (400x400px)
- `public/images/raw/cultures/` - Images de cultures (800x600px)

### Étape 3: Optimiser les Images

```bash
# Installer sharp
npm install sharp

# Optimiser toutes les images
node optimize-images.js
```

### Sources d'Images Recommandées

- **Unsplash**: https://unsplash.com/s/photos/african-agriculture
- **Pexels**: https://www.pexels.com/search/african%20farmer/
- **Pixabay**: https://pixabay.com/images/search/agriculture/
- **UI Faces**: https://uifaces.co/ (avatars)

## 🔧 Configuration

### Variables d'Environnement

Créez un fichier `.env` à la racine du frontend:

```env
VITE_API_URL=http://localhost:8000/api/v1
VITE_APP_NAME=Plateforme Agricole Togo
```

### Configuration de l'API

Dans `src/api/client.ts`:

```typescript
const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1';
```

## 🧪 Tests

```bash
# Lancer les tests (à implémenter)
npm test

# Tests avec coverage
npm run test:coverage
```

## 📦 Build et Déploiement

### Build de Production

```bash
npm run build
```

Les fichiers optimisés seront dans le dossier `dist/`.

### Déploiement

#### Netlify
```bash
# Installer Netlify CLI
npm install -g netlify-cli

# Déployer
netlify deploy --prod
```

#### Vercel
```bash
# Installer Vercel CLI
npm install -g vercel

# Déployer
vercel --prod
```

#### Serveur Classique
```bash
# Build
npm run build

# Copier le dossier dist/ sur votre serveur
scp -r dist/* user@server:/var/www/html/
```

## 🔐 Authentification

### Stockage des Tokens

Les tokens JWT sont stockés dans `localStorage`:
- `access_token` - Token d'accès
- `refresh_token` - Token de rafraîchissement

### Protection des Routes

Les routes protégées utilisent le composant `ProtectedRoute`:

```typescript
<Route 
  path="/dashboard" 
  element={
    <ProtectedRoute>
      <Dashboard />
    </ProtectedRoute>
  } 
/>
```

## 🌐 Internationalisation (À venir)

Support prévu pour:
- 🇫🇷 Français (par défaut)
- 🇹🇬 Ewe
- 🇹🇬 Kabyè

## 📱 Progressive Web App (À venir)

Fonctionnalités PWA prévues:
- Installation sur l'écran d'accueil
- Mode hors ligne
- Notifications push
- Synchronisation en arrière-plan

## 🐛 Débogage

### Problèmes Courants

#### 1. CORS Error
**Symptôme**: Erreur CORS dans la console

**Solution**: Ajouter dans Django `settings.py`:
```python
CORS_ALLOWED_ORIGINS = [
    "http://localhost:5173",
]
```

#### 2. Images ne s'affichent pas
**Symptôme**: Images cassées

**Solution**: 
- Vérifier que les images sont dans `public/images/`
- Utiliser le chemin `/images/...` (pas `./images/...`)

#### 3. API ne répond pas
**Symptôme**: Erreur de connexion

**Solution**:
- Vérifier que Django tourne sur port 8000
- Vérifier l'URL de l'API dans `.env`

### Outils de Débogage

```bash
# Analyser le bundle
npm run build -- --analyze

# Vérifier les performances
npm run lighthouse
```

## 📊 Performance

### Objectifs de Performance

- ⚡ First Contentful Paint: < 1.5s
- ⚡ Time to Interactive: < 3s
- ⚡ Lighthouse Score: > 90

### Optimisations Appliquées

- ✅ Code splitting automatique (Vite)
- ✅ Lazy loading des routes
- ✅ Compression des images
- ✅ Minification CSS/JS
- ✅ Tree shaking

## 🤝 Contribution

### Guidelines

1. Créer une branche pour chaque feature
2. Suivre les conventions de nommage
3. Tester sur mobile et desktop
4. Documenter les changements

### Conventions de Code

```typescript
// Composants: PascalCase
export default function MyComponent() { }

// Fonctions: camelCase
function handleClick() { }

// Constantes: UPPER_SNAKE_CASE
const API_BASE_URL = '...';

// CSS Classes: kebab-case
.my-component { }
```

## 📚 Documentation Complète

- `FRONTEND_COMPLETE_GUIDE.md` - Guide complet du frontend
- `FRONTEND_SUMMARY.md` - Résumé et checklist
- `setup-images.md` - Guide de configuration des images

## 🆘 Support

Pour toute question:
1. Consulter la documentation
2. Vérifier les logs du navigateur (F12)
3. Tester avec Postman pour isoler les problèmes API

## 📄 Licence

Ce projet est sous licence MIT.

---

**Développé avec ❤️ pour la Plateforme Agricole du Togo**

**Version**: 1.0.0  
**Dernière mise à jour**: Mars 2026
