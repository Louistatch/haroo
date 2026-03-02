# Module d'Authentification JWT - Haroo

Ce module implémente un système d'authentification complet basé sur JWT avec vérification SMS pour la plateforme Haroo.

## Fonctionnalités

### 1. Inscription (Registration)
- Validation du numéro de téléphone togolais (+228XXXXXXXX)
- Validation du mot de passe (min 8 caractères, 1 majuscule, 1 chiffre, 1 caractère spécial)
- Envoi automatique d'un code de vérification SMS
- Support de plusieurs types d'utilisateurs (EXPLOITANT, AGRONOME, OUVRIER, ACHETEUR, INSTITUTION, ADMIN)

### 2. Vérification SMS
- Code à 6 chiffres
- Expiration après 10 minutes
- Maximum 3 tentatives de vérification
- Possibilité de renvoyer le code

### 3. Connexion (Login)
- Authentification par numéro de téléphone et mot de passe
- Génération de tokens JWT (access + refresh)
- Rate limiting: blocage après 5 tentatives échouées pendant 30 minutes

### 4. Gestion des Tokens JWT
- Access token: valide 1 heure
- Refresh token: valide 24 heures
- Endpoint de rafraîchissement du token d'accès

### 5. Sécurité
- Hachage des mots de passe avec bcrypt
- Rate limiting par IP et par utilisateur
- Protection CSRF
- En-têtes de sécurité HTTP
- Validation stricte des entrées

## Endpoints API

### POST /api/v1/auth/register
Inscription d'un nouvel utilisateur.

**Request Body:**
```json
{
  "username": "john_doe",
  "email": "john@example.com",
  "phone_number": "+22890123456",
  "password": "SecurePass123!",
  "password_confirm": "SecurePass123!",
  "user_type": "EXPLOITANT",
  "first_name": "John",
  "last_name": "Doe"
}
```

**Response (201):**
```json
{
  "message": "Inscription réussie. Un code de vérification a été envoyé par SMS.",
  "user": {
    "id": 1,
    "username": "john_doe",
    "email": "john@example.com",
    "phone_number": "+22890123456",
    "phone_verified": false,
    "user_type": "EXPLOITANT"
  },
  "sms_sent": true
}
```

### POST /api/v1/auth/verify-sms
Vérification du code SMS.

**Request Body:**
```json
{
  "phone_number": "+22890123456",
  "code": "123456"
}
```

**Response (200):**
```json
{
  "message": "Téléphone vérifié avec succès",
  "user": { ... },
  "tokens": {
    "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
    "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
    "expires_in": 3600
  }
}
```

### POST /api/v1/auth/login
Connexion d'un utilisateur.

**Request Body:**
```json
{
  "phone_number": "+22890123456",
  "password": "SecurePass123!"
}
```

**Response (200):**
```json
{
  "message": "Connexion réussie",
  "user": { ... },
  "tokens": {
    "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
    "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
    "expires_in": 3600
  }
}
```

### POST /api/v1/auth/refresh-token
Rafraîchissement du token d'accès.

**Request Body:**
```json
{
  "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

**Response (200):**
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "expires_in": 3600
}
```

### POST /api/v1/auth/resend-sms
Renvoie un code de vérification SMS.

**Request Body:**
```json
{
  "phone_number": "+22890123456"
}
```

### GET /api/v1/users/me
Récupère les informations de l'utilisateur connecté.

**Headers:**
```
Authorization: Bearer <access_token>
```

**Response (200):**
```json
{
  "id": 1,
  "username": "john_doe",
  "email": "john@example.com",
  "phone_number": "+22890123456",
  "phone_verified": true,
  "user_type": "EXPLOITANT",
  "first_name": "John",
  "last_name": "Doe"
}
```

### PATCH /api/v1/users/me/update
Met à jour le profil de l'utilisateur connecté.

**Headers:**
```
Authorization: Bearer <access_token>
```

**Request Body:**
```json
{
  "first_name": "Jean",
  "last_name": "Dupont"
}
```

### POST /api/v1/users/me/change-password
Change le mot de passe de l'utilisateur connecté.

**Headers:**
```
Authorization: Bearer <access_token>
```

**Request Body:**
```json
{
  "old_password": "OldPass123!",
  "new_password": "NewPass123!",
  "new_password_confirm": "NewPass123!"
}
```

## Utilisation des Tokens JWT

Pour accéder aux endpoints protégés, incluez le token d'accès dans l'en-tête Authorization:

```
Authorization: Bearer <access_token>
```

Exemple avec curl:
```bash
curl -H "Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGc..." \
     http://localhost:8000/api/v1/users/me
```

## Configuration

Les paramètres suivants peuvent être configurés dans les variables d'environnement:

```env
# JWT
JWT_SECRET_KEY=your-secret-key
JWT_ACCESS_TOKEN_LIFETIME=3600  # 1 heure
JWT_REFRESH_TOKEN_LIFETIME=86400  # 24 heures

# SMS Gateway
SMS_GATEWAY_API_KEY=your-api-key
SMS_GATEWAY_SENDER_ID=HAROO

# Redis (pour le cache et rate limiting)
REDIS_URL=redis://localhost:6379/0
REDIS_CACHE_URL=redis://localhost:6379/1
```

## Tests

Pour exécuter les tests:

```bash
python manage.py test apps.users
```

Tests disponibles:
- Validation des mots de passe
- Vérification SMS
- Génération et vérification des tokens JWT
- Rate limiting
- Endpoints d'authentification

## Sécurité

### Politique de Mot de Passe
- Minimum 8 caractères
- Au moins une majuscule
- Au moins un chiffre
- Au moins un caractère spécial

### Rate Limiting
- **Inscription**: Blocage après 5 tentatives échouées
- **Connexion**: Blocage après 5 tentatives échouées pendant 30 minutes
- **Vérification SMS**: Maximum 3 tentatives par code

### Protection
- Hachage bcrypt pour les mots de passe
- Tokens JWT signés avec HS256
- Protection CSRF
- En-têtes de sécurité HTTP (X-Frame-Options, X-Content-Type-Options, etc.)
- Validation stricte des entrées

## Mode Développement

En mode développement (sans SMS_GATEWAY_API_KEY configuré), les codes SMS sont affichés dans la console:

```
[DEV MODE] SMS Code for +22890123456: 123456
```

## Dépendances

- Django 4.2+
- djangorestframework
- PyJWT
- bcrypt
- django-redis
- requests (pour le gateway SMS)

## Architecture

```
apps/users/
├── models.py           # Modèle User personnalisé
├── serializers.py      # Serializers pour l'API
├── views.py            # Endpoints d'authentification
├── services.py         # Services métier (SMS, JWT, Rate Limiting)
├── authentication.py   # Backend d'authentification JWT
├── validators.py       # Validateurs personnalisés
├── middleware.py       # Middleware de sécurité
├── urls.py             # Configuration des URLs
└── tests.py            # Tests unitaires
```

## Prochaines Étapes

- [ ] Authentification à deux facteurs (2FA) pour les comptes institutionnels
- [ ] Gestion des sessions multi-appareils
- [ ] Logs d'audit pour les actions sensibles
- [ ] Support de l'authentification sociale (optionnel)
