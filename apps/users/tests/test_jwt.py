"""
TASK-8.2: Tests JWT (tokens, refresh, expiration)

Couvre: génération tokens, vérification, refresh, expiration,
type mismatch, token invalide.
"""
import pytest
from datetime import datetime, timedelta
from django.conf import settings
from django.contrib.auth import get_user_model

User = get_user_model()


class TestJWTTokenGeneration:
    """Tests pour la génération de tokens JWT"""

    def test_generate_tokens_returns_access_and_refresh(self, user, jwt_tokens):
        """generate_tokens retourne access_token et refresh_token"""
        assert 'access_token' in jwt_tokens
        assert 'refresh_token' in jwt_tokens
        assert 'expires_in' in jwt_tokens

    def test_tokens_are_different(self, jwt_tokens):
        """access_token et refresh_token sont différents"""
        assert jwt_tokens['access_token'] != jwt_tokens['refresh_token']

    def test_access_token_contains_user_info(self, user, jwt_tokens):
        """Le payload du access_token contient les infos utilisateur"""
        from apps.users.services import JWTAuthService
        payload = JWTAuthService.verify_token(
            jwt_tokens['access_token'], token_type='access'
        )
        assert payload is not None
        assert payload['user_id'] == user.id
        assert payload['user_type'] == user.user_type


class TestJWTTokenVerification:
    """Tests pour la vérification de tokens"""

    def test_verify_valid_access_token(self, user, jwt_tokens):
        """Token d'accès valide est accepté"""
        from apps.users.services import JWTAuthService
        payload = JWTAuthService.verify_token(
            jwt_tokens['access_token'], token_type='access'
        )
        assert payload is not None
        assert payload['user_id'] == user.id

    def test_verify_invalid_token(self):
        """Token invalide retourne None"""
        from apps.users.services import JWTAuthService
        payload = JWTAuthService.verify_token('invalid.token.here')
        assert payload is None

    def test_verify_empty_token(self):
        """Token vide retourne None"""
        from apps.users.services import JWTAuthService
        payload = JWTAuthService.verify_token('')
        assert payload is None

    def test_access_token_rejected_as_refresh(self, jwt_tokens):
        """access_token ne peut pas être utilisé comme refresh_token"""
        from apps.users.services import JWTAuthService
        result = JWTAuthService.refresh_access_token(jwt_tokens['access_token'])
        assert result is None

    def test_refresh_token_rejected_as_access(self, jwt_tokens):
        """refresh_token ne peut pas être utilisé comme access_token"""
        from apps.users.services import JWTAuthService
        payload = JWTAuthService.verify_token(
            jwt_tokens['refresh_token'], token_type='access'
        )
        assert payload is None


class TestJWTTokenRefresh:
    """Tests pour le rafraîchissement de tokens"""

    def test_refresh_returns_new_access_token(self, jwt_tokens):
        """Refresh retourne un nouveau access_token"""
        from apps.users.services import JWTAuthService
        result = JWTAuthService.refresh_access_token(jwt_tokens['refresh_token'])
        assert result is not None
        assert 'access_token' in result
        assert 'expires_in' in result

    def test_refresh_endpoint_success(self, api_client, jwt_tokens):
        """POST /auth/refresh-token retourne un nouveau token"""
        data = {'refresh_token': jwt_tokens['refresh_token']}
        response = api_client.post(
            '/api/v1/auth/refresh-token', data, format='json'
        )
        assert response.status_code == 200
        assert 'access_token' in response.data

    def test_refresh_endpoint_invalid_token(self, api_client, db):
        """POST /auth/refresh-token avec token invalide retourne 401"""
        data = {'refresh_token': 'invalid_token'}
        response = api_client.post(
            '/api/v1/auth/refresh-token', data, format='json'
        )
        assert response.status_code == 401


class TestJWTTokenExpiration:
    """Tests pour l'expiration des tokens"""

    def test_expired_access_token_rejected(self, user):
        """Token d'accès expiré est rejeté"""
        import jwt as pyjwt
        from apps.users.services import JWTAuthService

        now = datetime.utcnow()
        payload = {
            'user_id': user.id,
            'username': user.username,
            'user_type': user.user_type,
            'exp': now - timedelta(seconds=10),
            'iat': now - timedelta(seconds=20),
            'type': 'access',
        }
        expired_token = pyjwt.encode(
            payload, settings.JWT_SECRET_KEY, algorithm='HS256'
        )
        result = JWTAuthService.verify_token(expired_token, token_type='access')
        assert result is None

    def test_expired_refresh_token_rejected(self, user):
        """Refresh token expiré ne peut pas générer un nouveau access token"""
        import jwt as pyjwt
        from apps.users.services import JWTAuthService

        now = datetime.utcnow()
        payload = {
            'user_id': user.id,
            'username': user.username,
            'user_type': user.user_type,
            'exp': now - timedelta(seconds=10),
            'iat': now - timedelta(seconds=20),
            'type': 'refresh',
        }
        expired_token = pyjwt.encode(
            payload, settings.JWT_SECRET_KEY, algorithm='HS256'
        )
        result = JWTAuthService.refresh_access_token(expired_token)
        assert result is None


class TestJWTAuthEndpoint:
    """Tests d'intégration pour l'authentification JWT via API"""

    def test_bearer_token_grants_access(self, api_client, jwt_tokens):
        """Un Bearer token valide donne accès aux endpoints protégés"""
        api_client.credentials(
            HTTP_AUTHORIZATION=f"Bearer {jwt_tokens['access_token']}"
        )
        response = api_client.get('/api/v1/users/me')
        assert response.status_code == 200

    def test_no_token_denied(self, api_client, db):
        """Sans token, l'accès est refusé"""
        response = api_client.get('/api/v1/users/me')
        assert response.status_code == 401

    def test_invalid_bearer_denied(self, api_client, db):
        """Bearer token invalide est refusé"""
        api_client.credentials(HTTP_AUTHORIZATION='Bearer invalid_token')
        response = api_client.get('/api/v1/users/me')
        assert response.status_code == 401
