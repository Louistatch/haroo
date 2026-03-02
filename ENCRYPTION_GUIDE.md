# Guide de Chiffrement des Données Sensibles

## Vue d'Ensemble

Ce document décrit l'implémentation du chiffrement des données sensibles pour la Plateforme Agricole Intelligente du Togo, conformément aux exigences de sécurité 33.1, 33.2 et 33.3.

## Exigences de Sécurité

### Exigence 33.1: Chiffrement TLS 1.3
**Statut**: ✅ Configuré

Toutes les communications sont chiffrées avec HTTPS/TLS 1.3:
- Configuration Django pour forcer HTTPS en production
- Headers de sécurité HSTS configurés (1 an)
- Redirection automatique HTTP → HTTPS
- Cookies sécurisés (Secure, HttpOnly, SameSite)

**Configuration serveur requise** (Nginx/Apache):
```nginx
# Nginx - Configuration TLS 1.3
ssl_protocols TLSv1.3;
ssl_prefer_server_ciphers on;
ssl_ciphers 'TLS_AES_256_GCM_SHA384:TLS_CHACHA20_POLY1305_SHA256:TLS_AES_128_GCM_SHA256';
```

### Exigence 33.2: Hachage bcrypt pour mots de passe
**Statut**: ✅ Configuré

Les mots de passe sont hachés avec bcrypt (salt unique automatique):
- Algorithme: BCryptSHA256PasswordHasher
- Salt unique généré automatiquement pour chaque mot de passe
- Coût: 12 rounds (par défaut bcrypt)
- Fallback: PBKDF2 pour compatibilité

**Configuration**: `haroo/settings/base.py`
```python
PASSWORD_HASHERS = [
    'django.contrib.auth.hashers.BCryptSHA256PasswordHasher',
    'django.contrib.auth.hashers.PBKDF2PasswordHasher',
]
```

### Exigence 33.3: Chiffrement AES-256 pour documents d'identité
**Statut**: ✅ Implémenté

Les documents d'identité et données sensibles sont chiffrés au repos avec AES-256-GCM:
- Algorithme: AES-256-GCM (Galois/Counter Mode)
- Chiffrement authentifié (AEAD)
- Nonce unique de 12 bytes pour chaque opération
- Protection contre les modifications

## Architecture de Chiffrement

### 1. Service de Chiffrement (`apps/core/encryption.py`)

Le service `EncryptionService` fournit le chiffrement/déchiffrement AES-256-GCM:

```python
from apps.core.encryption import get_encryption_service

# Obtenir le service
encryption_service = get_encryption_service()

# Chiffrer des données
encrypted = encryption_service.encrypt("Données sensibles")

# Déchiffrer des données
decrypted = encryption_service.decrypt(encrypted)
```

**Caractéristiques**:
- Dérivation de clé avec PBKDF2 (100,000 itérations)
- Nonce aléatoire unique pour chaque chiffrement
- Encodage base64 pour stockage en base de données
- Gestion d'erreurs robuste

### 2. Champs Django Chiffrés (`apps/core/fields.py`)

Trois types de champs chiffrés sont disponibles:

#### EncryptedTextField
Pour les textes longs (descriptions, notes, etc.):
```python
from apps.core.fields import EncryptedTextField

class MyModel(models.Model):
    notes_sensibles = EncryptedTextField()
```

#### EncryptedCharField
Pour les chaînes courtes (numéros, identifiants, etc.):
```python
from apps.core.fields import EncryptedCharField

class MyModel(models.Model):
    numero_identite = EncryptedCharField(max_length=50)
```

#### EncryptedFileField
Pour les fichiers sensibles (documents d'identité, etc.):
```python
from apps.core.fields import EncryptedFileField

class MyModel(models.Model):
    document_identite = EncryptedFileField(upload_to='documents/identite/')
```

**Note**: Les champs chiffrés ne peuvent pas être utilisés pour les recherches ou les index.

## Configuration

### 1. Générer une Clé de Chiffrement

**IMPORTANT**: Générez une clé unique et sécurisée pour chaque environnement:

```bash
python -c 'import secrets; print(secrets.token_urlsafe(32))'
```

### 2. Configurer les Variables d'Environnement

Ajoutez la clé dans `.env`:
```env
ENCRYPTION_KEY=votre-cle-generee-ici
```

**⚠️ ATTENTION**:
- Ne JAMAIS commiter la clé dans Git
- Utiliser des clés différentes pour dev/staging/prod
- Stocker la clé de production dans un gestionnaire de secrets (AWS Secrets Manager, HashiCorp Vault, etc.)
- Sauvegarder la clé de manière sécurisée (perte = données irrécupérables)

### 3. Installer les Dépendances

```bash
pip install -r requirements/base.txt
```

## Utilisation

### Exemple 1: Chiffrer des Données de Profil

```python
from django.db import models
from apps.core.fields import EncryptedCharField, EncryptedTextField

class ExploitantProfile(models.Model):
    # Données publiques (non chiffrées)
    nom = models.CharField(max_length=100)
    
    # Données sensibles (chiffrées)
    numero_identite = EncryptedCharField(max_length=50)
    adresse_complete = EncryptedTextField()
    coordonnees_bancaires = EncryptedTextField(blank=True, null=True)
```

### Exemple 2: Chiffrer des Documents

```python
from django.db import models
from apps.core.fields import EncryptedFileField

class DocumentVerification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    
    # Document chiffré
    piece_identite = EncryptedFileField(
        upload_to='verifications/identite/',
        help_text="Carte d'identité ou passeport (chiffré)"
    )
    
    # Métadonnées (non chiffrées)
    type_document = models.CharField(max_length=50)
    date_upload = models.DateTimeField(auto_now_add=True)
```

### Exemple 3: Chiffrement Manuel

```python
from apps.core.encryption import get_encryption_service

def process_sensitive_data(data: str) -> str:
    """Traite et chiffre des données sensibles"""
    encryption_service = get_encryption_service()
    
    # Traiter les données
    processed = data.strip().upper()
    
    # Chiffrer avant stockage
    encrypted = encryption_service.encrypt(processed)
    
    return encrypted
```

## Migration des Données Existantes

Si vous avez des données non chiffrées existantes, créez une migration de données:

```python
# migrations/0XXX_encrypt_sensitive_data.py
from django.db import migrations
from apps.core.encryption import get_encryption_service

def encrypt_existing_data(apps, schema_editor):
    """Chiffre les données sensibles existantes"""
    MyModel = apps.get_model('myapp', 'MyModel')
    encryption_service = get_encryption_service()
    
    for obj in MyModel.objects.all():
        if obj.sensitive_field and not is_encrypted(obj.sensitive_field):
            obj.sensitive_field = encryption_service.encrypt(obj.sensitive_field)
            obj.save(update_fields=['sensitive_field'])

def is_encrypted(value):
    """Vérifie si une valeur est déjà chiffrée"""
    try:
        import base64
        decoded = base64.b64decode(value.encode('utf-8'))
        return len(decoded) > 12
    except:
        return False

class Migration(migrations.Migration):
    dependencies = [
        ('myapp', '0XXX_previous_migration'),
    ]
    
    operations = [
        migrations.RunPython(encrypt_existing_data),
    ]
```

## Sécurité et Bonnes Pratiques

### ✅ À FAIRE

1. **Gestion des Clés**:
   - Utiliser un gestionnaire de secrets en production
   - Rotation régulière des clés (avec re-chiffrement)
   - Sauvegardes sécurisées des clés

2. **Chiffrement Sélectif**:
   - Chiffrer uniquement les données sensibles
   - Données publiques non chiffrées (performance)
   - Documenter quelles données sont chiffrées

3. **Monitoring**:
   - Logger les échecs de déchiffrement
   - Alertes sur les tentatives suspectes
   - Audit des accès aux données sensibles

4. **Tests**:
   - Tester le chiffrement/déchiffrement
   - Tester la rotation des clés
   - Tester la récupération après perte de clé

### ❌ À ÉVITER

1. **Ne JAMAIS**:
   - Commiter les clés dans Git
   - Utiliser la même clé pour tous les environnements
   - Stocker les clés en clair dans le code
   - Perdre la clé de production (données irrécupérables)

2. **Limitations**:
   - Pas de recherche sur champs chiffrés
   - Pas d'index sur champs chiffrés
   - Performance légèrement réduite (chiffrement/déchiffrement)

## Tests

### Test du Service de Chiffrement

```python
from apps.core.encryption import get_encryption_service

def test_encryption_decryption():
    service = get_encryption_service()
    
    # Test chiffrement/déchiffrement
    plaintext = "Données sensibles"
    encrypted = service.encrypt(plaintext)
    decrypted = service.decrypt(encrypted)
    
    assert decrypted == plaintext
    assert encrypted != plaintext
```

### Test des Champs Chiffrés

```python
from django.test import TestCase
from myapp.models import MyModel

class EncryptedFieldTest(TestCase):
    def test_encrypted_field_storage(self):
        # Créer un objet avec données sensibles
        obj = MyModel.objects.create(
            sensitive_field="Données sensibles"
        )
        
        # Vérifier que les données sont chiffrées en base
        from django.db import connection
        with connection.cursor() as cursor:
            cursor.execute(
                "SELECT sensitive_field FROM myapp_mymodel WHERE id = %s",
                [obj.id]
            )
            raw_value = cursor.fetchone()[0]
            assert raw_value != "Données sensibles"
        
        # Vérifier que les données sont déchiffrées à la lecture
        obj.refresh_from_db()
        assert obj.sensitive_field == "Données sensibles"
```

## Conformité Réglementaire

Cette implémentation respecte:
- ✅ Exigence 33.1: HTTPS/TLS 1.3 pour toutes les communications
- ✅ Exigence 33.2: Hachage bcrypt avec salt unique pour les mots de passe
- ✅ Exigence 33.3: Chiffrement AES-256 pour les documents d'identité au repos

## Support et Maintenance

### Rotation des Clés

Pour changer la clé de chiffrement:

1. Générer une nouvelle clé
2. Déchiffrer toutes les données avec l'ancienne clé
3. Re-chiffrer avec la nouvelle clé
4. Mettre à jour ENCRYPTION_KEY
5. Redémarrer l'application

### Récupération après Perte de Clé

**⚠️ IMPORTANT**: Si la clé de chiffrement est perdue, les données chiffrées sont **IRRÉCUPÉRABLES**.

Mesures préventives:
- Sauvegardes sécurisées de la clé
- Clé stockée dans plusieurs emplacements sécurisés
- Procédure de récupération documentée
- Tests réguliers de récupération

## Ressources

- [Cryptography Documentation](https://cryptography.io/)
- [Django Password Hashers](https://docs.djangoproject.com/en/4.2/topics/auth/passwords/)
- [NIST Encryption Guidelines](https://csrc.nist.gov/publications/detail/sp/800-175b/rev-1/final)
- [OWASP Cryptographic Storage Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Cryptographic_Storage_Cheat_Sheet.html)
