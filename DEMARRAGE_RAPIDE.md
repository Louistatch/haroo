# 🚀 Démarrage Rapide - Plateforme Agricole Togo

## Problème: "Erreur - Impossible de charger les documents"

Ce guide vous aide à résoudre ce problème courant.

## ✅ Vérifications Préalables

### 1. Vérifier que le serveur backend est démarré

```bash
# Dans le terminal, vérifiez si le serveur Django tourne
# Vous devriez voir quelque chose comme:
# "Starting development server at http://127.0.0.1:8000/"

# Si le serveur n'est pas démarré, lancez:
python manage.py runserver
```

### 2. Vérifier que le frontend est démarré

```bash
# Dans un autre terminal, allez dans le dossier frontend
cd frontend

# Démarrez le serveur de développement
npm run dev

# Vous devriez voir:
# "Local: http://localhost:5173/"
```

### 3. Tester l'API manuellement

```bash
# Exécutez le script de test
python test_documents_api.py
```

## 🔧 Solutions aux Problèmes Courants

### Problème 1: Serveur backend non démarré

**Symptôme:** `ERR_NETWORK` ou "Impossible de contacter le serveur"

**Solution:**
```bash
python manage.py runserver
```

### Problème 2: Base de données vide

**Symptôme:** "Aucun document trouvé"

**Solution:** Créer des documents de test
```bash
python manage.py shell
```

Puis dans le shell Python:
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
doc = DocumentTechnique.objects.create(
    template=template,
    titre="Compte d'exploitation - Maïs (Maritime)",
    description="Guide complet pour la culture du maïs dans la région Maritime",
    prix=5000,
    culture="Maïs",
    region=region,
    prefecture=prefecture,
    canton=canton,
    actif=True
)

print(f"✅ Document créé: {doc.titre}")
```

### Problème 3: CORS (Cross-Origin)

**Symptôme:** Erreur CORS dans la console du navigateur

**Solution:** Vérifier `settings.py`
```python
# Dans config/settings.py
CORS_ALLOWED_ORIGINS = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
]

CORS_ALLOW_CREDENTIALS = True
```

### Problème 4: Port déjà utilisé

**Symptôme:** "Address already in use"

**Solution:**
```bash
# Trouver le processus qui utilise le port 8000
# Windows:
netstat -ano | findstr :8000

# Linux/Mac:
lsof -i :8000

# Tuer le processus ou utiliser un autre port
python manage.py runserver 8001
```

## 🧪 Test Complet

### 1. Backend
```bash
# Terminal 1
python manage.py runserver

# Devrait afficher:
# Starting development server at http://127.0.0.1:8000/
```

### 2. Frontend
```bash
# Terminal 2
cd frontend
npm run dev

# Devrait afficher:
# Local: http://localhost:5173/
```

### 3. Test API
```bash
# Terminal 3
python test_documents_api.py

# Devrait afficher:
# ✅ Succès!
# Nombre de documents: X
```

### 4. Test dans le navigateur

1. Ouvrez http://localhost:5173
2. Connectez-vous
3. Cliquez sur "Documents Techniques"
4. Vous devriez voir la liste des documents

## 📝 Logs Utiles

### Voir les logs du backend
```bash
# Les logs s'affichent dans le terminal où vous avez lancé runserver
# Recherchez les erreurs en rouge
```

### Voir les logs du frontend
```bash
# Ouvrez la console du navigateur (F12)
# Onglet "Console" pour voir les erreurs JavaScript
# Onglet "Network" pour voir les requêtes HTTP
```

## 🆘 Besoin d'Aide?

Si le problème persiste:

1. Vérifiez les logs dans les deux terminaux
2. Ouvrez la console du navigateur (F12)
3. Exécutez `python test_documents_api.py`
4. Notez les messages d'erreur exacts

## 📚 Commandes Utiles

```bash
# Migrations
python manage.py makemigrations
python manage.py migrate

# Créer un superuser
python manage.py createsuperuser

# Accéder à l'admin Django
# http://localhost:8000/admin

# Shell Django
python manage.py shell

# Tests
python manage.py test apps.documents
```

## ✨ Tout Fonctionne?

Si vous voyez la page des documents avec la liste, félicitations! 🎉

Vous pouvez maintenant:
- Parcourir les documents
- Filtrer par culture et région
- Acheter des documents (nécessite une connexion)
- Télécharger vos achats
