# 🔧 Corrections Frontend - Connexion API

## Problème Identifié

Le frontend ne pouvait pas se connecter au backend à cause de plusieurs incompatibilités:

### 1. URL de Base Incorrecte
- **Avant**: `http://localhost:8000/api`
- **Après**: `http://localhost:8000/api/v1`

### 2. Slashes Finaux
- **Backend**: URLs sans slash final (`/auth/login`)
- **Frontend**: Envoyait avec slash final (`/auth/login/`)
- **Correction**: Supprimé les slashes finaux dans le frontend

### 3. Nom du Champ Téléphone
- **Backend attend**: `phone_number`
- **Frontend envoyait**: `phone`
- **Correction**: Changé en `phone_number`

### 4. Structure des Tokens
- **Backend retourne**: 
  ```json
  {
    "tokens": {
      "access_token": "...",
      "refresh_token": "..."
    }
  }
  ```
- **Frontend attendait**: 
  ```json
  {
    "access": "...",
    "refresh": "..."
  }
  ```
- **Correction**: Adapté pour lire `tokens.access_token` et `tokens.refresh_token`

## Fichiers Modifiés

### `frontend/.env`
```env
VITE_API_BASE_URL=http://localhost:8000/api/v1
```

### `frontend/src/api/auth.ts`
- Changé BASE_URL par défaut
- Supprimé slashes finaux des endpoints
- Changé `phone` en `phone_number` dans la requête login
- Adapté la lecture des tokens: `res.data.tokens.access_token`
- Corrigé le refresh token pour envoyer `refresh_token` au lieu de `refresh`

## Test de Connexion

Vous pouvez maintenant vous connecter avec:

| Numéro de téléphone | Mot de passe | Rôle |
|---------------------|--------------|------|
| +22890000001 | Demo123! | Exploitant (Farmer) |
| +22890000002 | Demo123! | Agronome (Agronomist) |
| +22890000003 | Admin123! | Administrateur |

## Endpoints Fonctionnels

✅ POST `/api/v1/auth/login` - Connexion
✅ POST `/api/v1/auth/register` - Inscription
✅ POST `/api/v1/auth/refresh-token` - Rafraîchir le token
✅ GET `/api/v1/users/me` - Profil utilisateur

## Prochaines Étapes

1. Rafraîchir la page frontend (http://localhost:3000)
2. Essayer de se connecter avec un des comptes de test
3. Vérifier que le profil s'affiche correctement après connexion

## Notes Techniques

- Le backend utilise JWT pour l'authentification
- Les tokens sont stockés dans localStorage
- Le refresh automatique est géré par un intercepteur axios
- La session est créée dans Redis lors de la connexion
