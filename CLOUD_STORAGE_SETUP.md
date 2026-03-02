# Configuration du Stockage Cloud - Plateforme Haroo

Ce document explique comment configurer le stockage cloud pour la plateforme Haroo avec AWS S3 ou Cloudinary.

## Vue d'Ensemble

La plateforme supporte deux backends de stockage cloud:
- **AWS S3**: Service de stockage d'Amazon Web Services
- **Cloudinary**: Service de stockage et gestion de médias

**Exigences implémentées:**
- 31.1: Upload de fichiers aux formats PDF, JPEG, PNG, Excel, Word
- 31.2: Limitation de taille à 10 Mo par fichier
- 31.3: Stockage sur service cloud sécurisé (S3 ou Cloudinary)
- 31.4: Génération d'URLs signées avec expiration configurable
- 31.5: Scan antivirus des fichiers uploadés
- 31.6: Rejet et notification en cas de virus détecté

## Option 1: Configuration AWS S3

### Prérequis

1. Compte AWS actif
2. Bucket S3 créé
3. Clés d'accès IAM avec permissions appropriées

### Étapes de Configuration

#### 1. Créer un Bucket S3

```bash
# Via AWS CLI
aws s3 mb s3://haroo-storage --region eu-west-1
```

Ou via la console AWS:
- Aller sur S3 → Créer un bucket
- Nom: `haroo-storage` (ou votre choix)
- Région: `eu-west-1` (ou votre choix)
- Bloquer l'accès public: **Activé** (sécurité)

#### 2. Configurer les Permissions IAM

Créer une politique IAM avec les permissions suivantes:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "s3:PutObject",
        "s3:GetObject",
        "s3:DeleteObject",
        "s3:ListBucket"
      ],
      "Resource": [
        "arn:aws:s3:::haroo-storage",
        "arn:aws:s3:::haroo-storage/*"
      ]
    }
  ]
}
```

#### 3. Configurer les Variables d'Environnement

Dans votre fichier `.env`:

```env
# Activer S3
USE_S3=True
USE_CLOUDINARY=False

# Credentials AWS
AWS_ACCESS_KEY_ID=AKIAIOSFODNN7EXAMPLE
AWS_SECRET_ACCESS_KEY=wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY
AWS_STORAGE_BUCKET_NAME=haroo-storage
AWS_S3_REGION_NAME=eu-west-1
```

#### 4. Configurer CORS (si nécessaire)

Si vous accédez aux fichiers depuis le frontend:

```json
[
  {
    "AllowedHeaders": ["*"],
    "AllowedMethods": ["GET", "PUT", "POST", "DELETE"],
    "AllowedOrigins": ["https://votre-domaine.com"],
    "ExposeHeaders": ["ETag"],
    "MaxAgeSeconds": 3000
  }
]
```

### Coûts AWS S3

- Stockage: ~0.023 USD/Go/mois (région eu-west-1)
- Requêtes GET: 0.0004 USD/1000 requêtes
- Requêtes PUT: 0.005 USD/1000 requêtes
- Transfert sortant: Gratuit jusqu'à 100 Go/mois

**Estimation pour 1000 utilisateurs:**
- Stockage: 50 Go → ~1.15 USD/mois
- Requêtes: ~10,000/mois → ~0.05 USD/mois
- **Total: ~1.20 USD/mois**

## Option 2: Configuration Cloudinary

### Prérequis

1. Compte Cloudinary (gratuit jusqu'à 25 Go)
2. Credentials API

### Étapes de Configuration

#### 1. Créer un Compte Cloudinary

- Aller sur [cloudinary.com](https://cloudinary.com)
- S'inscrire (plan gratuit disponible)
- Noter les credentials du dashboard

#### 2. Configurer les Variables d'Environnement

Dans votre fichier `.env`:

```env
# Activer Cloudinary
USE_S3=False
USE_CLOUDINARY=True

# Credentials Cloudinary
CLOUDINARY_CLOUD_NAME=votre-cloud-name
CLOUDINARY_API_KEY=123456789012345
CLOUDINARY_API_SECRET=abcdefghijklmnopqrstuvwxyz123456
```

#### 3. Configurer les Dossiers

Cloudinary organise automatiquement les fichiers par dossiers:
- `/profiles/` - Photos de profil
- `/documents/` - Documents techniques
- `/verification/` - Documents de vérification

### Coûts Cloudinary

**Plan Gratuit:**
- 25 Go de stockage
- 25 Go de bande passante/mois
- 25,000 transformations/mois

**Plan Payant (si dépassement):**
- Stockage: 0.18 USD/Go/mois
- Bande passante: 0.08 USD/Go
- Transformations: 1.50 USD/1000

**Estimation pour 1000 utilisateurs:**
- Plan gratuit suffisant pour démarrer
- Si dépassement: ~5-10 USD/mois

## Configuration du Scan Antivirus

### Option 1: ClamAV (Recommandé)

#### Installation sur Ubuntu/Debian

```bash
sudo apt-get update
sudo apt-get install clamav clamav-daemon

# Mettre à jour les définitions de virus
sudo freshclam

# Démarrer le service
sudo systemctl start clamav-daemon
sudo systemctl enable clamav-daemon
```

#### Installation sur Windows

1. Télécharger ClamAV depuis [clamav.net](https://www.clamav.net/downloads)
2. Installer et ajouter au PATH
3. Mettre à jour les définitions: `freshclam`

#### Vérification

```bash
clamscan --version
# Devrait afficher: ClamAV 1.x.x
```

### Option 2: Scan Basique (Fallback)

Si ClamAV n'est pas disponible, le système utilise automatiquement un scan basique par signatures. Ce scan détecte:
- Fichiers de test EICAR
- Signatures d'exécutables Windows
- Extensions dangereuses

**Note:** Le scan basique est moins robuste que ClamAV. Installation de ClamAV recommandée en production.

## Génération d'URLs Signées

### Utilisation dans le Code

```python
from apps.core.storage import SecureCloudStorage

# Générer une URL signée valide 48h (défaut)
signed_url = SecureCloudStorage.generate_signed_url('documents/file.pdf')

# Générer une URL signée valide 24h
signed_url = SecureCloudStorage.generate_signed_url(
    'documents/file.pdf',
    expiration_hours=24
)

# Récupérer l'URL d'un fichier (signée ou publique)
url = SecureCloudStorage.get_file_url('documents/file.pdf', signed=True)
```

### Sécurité des URLs Signées

- **Expiration par défaut:** 48 heures (Exigence 31.4)
- **Expiration configurable:** De 1 heure à 7 jours
- **Accès unique:** Chaque URL est unique et ne peut être réutilisée après expiration
- **Pas de cache:** Les URLs signées ne doivent pas être mises en cache

## Validation des Fichiers

### Formats Autorisés

**Images:**
- JPEG (.jpg, .jpeg)
- PNG (.png)

**Documents:**
- PDF (.pdf)
- Excel (.xlsx, .xls)
- Word (.docx, .doc)

### Limites de Taille

- **Images de profil:** 5 Mo maximum
- **Documents:** 10 Mo maximum (Exigence 31.2)

### Processus de Validation

1. **Vérification de l'extension** (Exigence 31.1)
2. **Vérification de la taille** (Exigence 31.2)
3. **Validation du type MIME** (Exigence 31.5)
4. **Scan antivirus** (Exigences 31.5, 31.6)
5. **Validation du contenu** (pour les images)

Si un fichier échoue à une étape, il est rejeté avec un message d'erreur explicite.

## Tests

### Exécuter les Tests

```bash
# Tous les tests de stockage
python manage.py test apps.core.tests.test_storage

# Tous les tests de sécurité
python manage.py test apps.core.tests.test_file_security

# Tests spécifiques
python manage.py test apps.core.tests.test_storage.SecureCloudStorageTest
python manage.py test apps.core.tests.test_file_security.AntivirusServiceTest
```

### Tests avec Fichier EICAR

Le fichier de test EICAR est un standard pour tester les antivirus:

```python
# Créer un fichier de test EICAR
eicar_content = b'X5O!P%@AP[4\\PZX54(P^)7CC)7}$EICAR-STANDARD-ANTIVIRUS-TEST-FILE!$H+H*'

# Ce fichier devrait être détecté comme malveillant
```

## Migration depuis Stockage Local

Si vous avez déjà des fichiers en local:

```bash
# Script de migration vers S3
python manage.py migrate_to_s3

# Script de migration vers Cloudinary
python manage.py migrate_to_cloudinary
```

## Monitoring et Logs

### Logs de Sécurité

Les événements suivants sont loggés:
- Fichiers rejetés pour virus
- Échecs de validation MIME
- Erreurs de génération d'URLs signées
- Suppressions de fichiers

### Vérifier les Logs

```bash
# Logs de sécurité des fichiers
grep "malveillant" logs/haroo.log

# Logs de stockage
grep "storage" logs/haroo.log
```

## Dépannage

### Erreur: "ClamAV non disponible"

**Solution:** Installer ClamAV ou accepter le scan basique (moins robuste)

### Erreur: "Type MIME non autorisé"

**Solution:** Vérifier que le fichier est dans un format autorisé et que le type MIME est correct

### Erreur: "Fichier trop volumineux"

**Solution:** Réduire la taille du fichier ou augmenter la limite dans les settings (non recommandé)

### Erreur: "AWS credentials not found"

**Solution:** Vérifier que les variables d'environnement AWS sont correctement configurées

### Erreur: "Cloudinary configuration error"

**Solution:** Vérifier les credentials Cloudinary dans le fichier .env

## Sécurité en Production

### Checklist de Sécurité

- [ ] Activer HTTPS/TLS pour toutes les communications
- [ ] Configurer les permissions IAM minimales pour S3
- [ ] Activer le chiffrement au repos sur S3
- [ ] Installer et maintenir ClamAV à jour
- [ ] Configurer les alertes pour fichiers malveillants
- [ ] Limiter l'accès aux buckets S3 (pas d'accès public)
- [ ] Utiliser des URLs signées pour tous les téléchargements
- [ ] Configurer la rotation des clés API
- [ ] Activer les logs d'accès S3/Cloudinary
- [ ] Mettre en place une politique de rétention des fichiers

## Support

Pour toute question ou problème:
- Documentation Django Storages: https://django-storages.readthedocs.io/
- Documentation AWS S3: https://docs.aws.amazon.com/s3/
- Documentation Cloudinary: https://cloudinary.com/documentation
- Documentation ClamAV: https://docs.clamav.net/
