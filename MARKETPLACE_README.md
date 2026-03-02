# 📚 Marketplace de Documents Techniques

## Vue d'Ensemble

Le marketplace de documents techniques permet aux utilisateurs d'acheter et de télécharger des comptes d'exploitation et des itinéraires techniques adaptés à leur région et culture.

## 🚀 Démarrage Rapide

### Option 1: Scripts Automatiques

**Linux/Mac:**
```bash
chmod +x start_dev.sh
./start_dev.sh
```

**Windows:**
```bash
start_dev.bat
```

### Option 2: Démarrage Manuel

**Terminal 1 - Backend:**
```bash
python manage.py runserver
```

**Terminal 2 - Frontend:**
```bash
cd frontend
npm run dev
```

## 📖 Documentation

- **[DEMARRAGE_RAPIDE.md](DEMARRAGE_RAPIDE.md)** - Guide de dépannage
- **[MARKETPLACE_DOCUMENTS_SUMMARY.md](MARKETPLACE_DOCUMENTS_SUMMARY.md)** - Résumé complet
- **[frontend/MANUAL_TESTING_GUIDE.md](frontend/MANUAL_TESTING_GUIDE.md)** - Tests manuels

## 🎯 Fonctionnalités Principales

### 1. Catalogue de Documents
- Filtrage par culture, région, recherche
- Affichage des prix en FCFA
- Badge "Acheté" sur documents possédés
- Skeleton loaders pendant chargement

### 2. Processus d'Achat
- Modal de confirmation avec détails
- Paiement sécurisé via Fedapay
- Page de succès avec animation
- Téléchargement immédiat

### 3. Historique des Achats
- Liste complète des achats
- Filtres avancés (date, culture, statut)
- Pagination (20 par page)
- Régénération de liens expirés
- Téléchargement direct

### 4. Notifications
- Toast pour toutes les actions
- Messages contextuels
- Auto-dismiss configurable
- 4 types: success, error, warning, info

## 🔗 Routes

| Route | Description | Protection |
|-------|-------------|------------|
| `/documents` | Catalogue de documents | Public |
| `/purchases` | Historique des achats | Authentifié |
| `/payment/success` | Confirmation de paiement | Public |

## 🎨 Composants

### Pages
- `Documents.tsx` - Catalogue avec filtres
- `PurchaseHistory.tsx` - Historique des achats
- `PaymentSuccess.tsx` - Confirmation de paiement

### Composants Réutilisables
- `Toast.tsx` - Notifications
- `PurchaseModal.tsx` - Confirmation d'achat

### Hooks
- `useToast()` - Gestion des notifications
- `useDebounce()` - Optimisation des filtres

### API
- `purchases.ts` - Gestion des achats
- `payments.ts` - Vérification des paiements

## 🧪 Tests

### Lancer les Tests
```bash
# Tests unitaires
cd frontend
npm test

# Test API backend
python test_documents_api.py
```

### Tests Manuels
Consultez `frontend/MANUAL_TESTING_GUIDE.md` pour les scénarios de test complets.

## 🐛 Dépannage

### Problème: "Erreur - Impossible de charger les documents"

**Solutions:**
1. Vérifiez que le backend est démarré: `python manage.py runserver`
2. Testez l'API: `python test_documents_api.py`
3. Vérifiez la console du navigateur (F12)
4. Consultez `DEMARRAGE_RAPIDE.md`

### Problème: Aucun document affiché

**Solution:** Créez des documents de test
```bash
python manage.py shell
```

Puis:
```python
from apps.documents.models import DocumentTechnique, DocumentTemplate
from apps.locations.models import Region, Prefecture, Canton

# Créer une région
region = Region.objects.create(nom="Maritime")
prefecture = Prefecture.objects.create(nom="Golfe", region=region)
canton = Canton.objects.create(nom="Lomé", prefecture=prefecture)

# Créer un template
template = DocumentTemplate.objects.create(
    titre="Template Maïs",
    type_document="COMPTE_EXPLOITATION",
    format_fichier="EXCEL",
    fichier_template="templates/mais.xlsx"
)

# Créer un document
DocumentTechnique.objects.create(
    template=template,
    titre="Compte d'exploitation - Maïs (Maritime)",
    description="Guide complet pour la culture du maïs",
    prix=5000,
    culture="Maïs",
    region=region,
    prefecture=prefecture,
    canton=canton,
    actif=True
)
```

### Problème: Toast ne s'affiche pas

**Solution:** Vérifiez que le composant Toast est importé dans la page:
```tsx
import { useToast } from '../hooks/useToast';
import Toast from '../components/Toast';

// Dans le composant
const { toasts, removeToast, success, error } = useToast();

// Dans le JSX
<div className="toast-container">
  {toasts.map(toast => (
    <Toast key={toast.id} {...toast} onClose={removeToast} />
  ))}
</div>
```

## 📊 Métriques

### Performance
- Temps de chargement: < 2s
- Pagination: 20 documents/page
- Debounce filtres: 300ms
- Expiration liens: 48h

### Sécurité
- Authentification JWT
- Liens signés
- Validation serveur
- Protection CSRF

## 🔐 Configuration

### Backend (settings.py)
```python
CORS_ALLOWED_ORIGINS = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
]

# Fedapay
FEDAPAY_API_KEY = os.getenv('FEDAPAY_API_KEY')
FEDAPAY_ENVIRONMENT = 'sandbox'  # ou 'live'
```

### Frontend (.env)
```bash
VITE_API_BASE_URL=http://localhost:8000/api/v1
```

## 📝 Conventions de Code

### TypeScript
- Interfaces pour tous les types
- Props typées pour composants
- Gestion d'erreurs avec try/catch
- JSDoc pour fonctions complexes

### CSS
- BEM pour noms de classes
- Variables CSS dans theme.css
- Mobile-first responsive
- Animations avec @keyframes

### Git
- Commits descriptifs
- Branches par fonctionnalité
- Pull requests avec review

## 🚀 Déploiement

### Prérequis
- Python 3.8+
- Node.js 16+
- PostgreSQL (production)
- Redis (cache)

### Étapes
1. Configurer variables d'environnement
2. Migrer la base de données
3. Collecter les fichiers statiques
4. Démarrer les services
5. Configurer Nginx/Apache
6. Activer HTTPS

## 📞 Support

Pour toute question ou problème:
1. Consultez la documentation
2. Vérifiez les issues GitHub
3. Contactez l'équipe de développement

## 📄 Licence

Propriétaire - Plateforme Agricole Togo

---

**Version:** 1.0.0  
**Dernière mise à jour:** 2024  
**Équipe:** Plateforme Agricole Togo
