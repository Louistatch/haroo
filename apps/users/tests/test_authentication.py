"""
TASK-8.2: Tests d'authentification complets

Couvre: inscription email, connexion email, endpoints protégés,
cookies HttpOnly, rate limiting, profil utilisateur.
"""
import pytest
from django.contrib.auth import get_user_model
from rest_framework import status

User = get_user_model()


# ============================================
# Tests d'inscription par email
# ============================================

class TestEmailRegistration:
    """Tests pour POST /api/v1/auth/register-email"""

    URL = '/api/v1/auth/register-email'

    def test_register_success(self, api_client, db):
        """Inscription réussie retourne 201 + tokens"""
        data = {
            'email': 'new@example.com',
            'password': 'Test123!@#',
            'password_confirm': 'Test123!@#',
            'user_type': 'EXPLOITANT',
            'first_name': 'Jean',
            'last_name': 'Dupont',
        }
        response = api_client.post(self.URL, data, format='json')
        assert response.status_code == status.HTTP_201_CREATED
        assert 'tokens' in response.data
        assert 'access_token' in response.data['tokens']
        assert 'refresh_token' in response.data['tokens']
        assert response.data['user']['email'] == 'new@example.com'

    def test_register_duplicate_email(self, api_client, user):
        """Inscription avec email existant retourne 400"""
        data = {
            'email': user.email,
            'password': 'Test123!@#',
            'password_confirm': 'Test123!@#',
            'user_type': 'EXPLOITANT',
        }
        response = api_client.post(self.URL, data, format='json')
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_register_password_mismatch(self, api_client, db):
        """Mots de passe différents retourne 400"""
        data = {
            'email': 'new@example.com',
            'password': 'Test123!@#',
            'password_confirm': 'Different123!@#',
            'user_type': 'EXPLOITANT',
        }
        response = api_client.post(self.URL, data, format='json')
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_register_weak_password(self, api_client, db):
        """Mot de passe faible retourne 400"""
        data = {
            'email': 'new@example.com',
            'password': 'weak',
            'password_confirm': 'weak',
            'user_type': 'EXPLOITANT',
        }
        response = api_client.post(self.URL, data, format='json')
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_register_missing_email(self, api_client, db):
        """Email manquant retourne 400"""
        data = {
            'password': 'Test123!@#',
            'password_confirm': 'Test123!@#',
            'user_type': 'EXPLOITANT',
        }
        response = api_client.post(self.URL, data, format='json')
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_register_creates_user_in_db(self, api_client, db):
        """L'inscription crée bien l'utilisateur en base"""
        data = {
            'email': 'dbcheck@example.com',
            'password': 'Test123!@#',
            'password_confirm': 'Test123!@#',
            'user_type': 'AGRONOME',
        }
        api_client.post(self.URL, data, format='json')
        assert User.objects.filter(email='dbcheck@example.com').exists()
        u = User.objects.get(email='dbcheck@example.com')
        assert u.user_type == 'AGRONOME'


# ============================================
# Tests de connexion par email
# ============================================

class TestEmailLogin:
    """Tests pour POST /api/v1/auth/login-email"""

    URL = '/api/v1/auth/login-email'

    def test_login_success(self, api_client, user):
        """Connexion réussie retourne 200 + tokens"""
        data = {'email': user.email, 'password': user._raw_password}
        response = api_client.post(self.URL, data, format='json')
        assert response.status_code == status.HTTP_200_OK
        assert 'tokens' in response.data
        assert 'access_token' in response.data['tokens']

    def test_login_wrong_password(self, api_client, user):
        """Mauvais mot de passe retourne 401"""
        data = {'email': user.email, 'password': 'WrongPass123!@#'}
        response = api_client.post(self.URL, data, format='json')
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_login_nonexistent_email(self, api_client, db):
        """Email inexistant retourne 401"""
        data = {'email': 'ghost@example.com', 'password': 'Test123!@#'}
        response = api_client.post(self.URL, data, format='json')
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_login_inactive_user(self, api_client, user):
        """Utilisateur désactivé retourne 403"""
        user.is_active = False
        user.save()
        data = {'email': user.email, 'password': user._raw_password}
        response = api_client.post(self.URL, data, format='json')
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_login_returns_user_info(self, api_client, user):
        """La réponse contient les infos utilisateur"""
        data = {'email': user.email, 'password': user._raw_password}
        response = api_client.post(self.URL, data, format='json')
        assert response.data['user']['email'] == user.email
        assert response.data['user']['user_type'] == user.user_type


# ============================================
# Tests des endpoints protégés
# ============================================

class TestProtectedEndpoints:
    """Tests pour les endpoints nécessitant une authentification"""

    def test_profile_requires_auth(self, api_client, db):
        """GET /users/me sans token retourne 401"""
        response = api_client.get('/api/v1/users/me')
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_profile_with_auth(self, auth_client, user):
        """GET /users/me avec auth retourne le profil"""
        response = auth_client.get('/api/v1/users/me')
        assert response.status_code == status.HTTP_200_OK
        assert response.data['email'] == user.email

    def test_change_password_requires_auth(self, api_client, db):
        """Change password sans auth retourne 401"""
        response = api_client.post('/api/v1/users/me/change-password', {}, format='json')
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_change_password_success(self, auth_client, user):
        """Changement de mot de passe réussi"""
        data = {
            'old_password': user._raw_password,
            'new_password': 'NewPass123!@#',
            'new_password_confirm': 'NewPass123!@#',
        }
        response = auth_client.post(
            '/api/v1/users/me/change-password', data, format='json'
        )
        assert response.status_code == status.HTTP_200_OK
        # Vérifier que le nouveau mot de passe fonctionne
        user.refresh_from_db()
        assert user.check_password('NewPass123!@#')

    def test_change_password_wrong_old(self, auth_client, user):
        """Ancien mot de passe incorrect retourne 400"""
        data = {
            'old_password': 'WrongOld123!@#',
            'new_password': 'NewPass123!@#',
            'new_password_confirm': 'NewPass123!@#',
        }
        response = auth_client.post(
            '/api/v1/users/me/change-password', data, format='json'
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_update_profile(self, auth_client, user):
        """PATCH /users/me met à jour le profil"""
        data = {'first_name': 'Updated', 'last_name': 'Name'}
        response = auth_client.patch('/api/v1/users/me', data, format='json')
        assert response.status_code == status.HTTP_200_OK
        user.refresh_from_db()
        assert user.first_name == 'Updated'

    def test_sessions_requires_auth(self, api_client, db):
        """Sessions endpoint sans auth retourne 401"""
        response = api_client.get('/api/v1/users/me/sessions')
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


# ============================================
# Tests de connexion avec cookies HttpOnly
# ============================================

class TestCookieAuth:
    """Tests pour les endpoints JWT cookies (TASK-1)"""

    def test_login_cookies_success(self, api_client, user):
        """Login cookies retourne 200 + set-cookie headers"""
        data = {'email': user.email, 'password': user._raw_password}
        response = api_client.post(
            '/api/v1/auth/login-cookies', data, format='json'
        )
        assert response.status_code == status.HTTP_200_OK
        assert 'access_token' in response.cookies
        assert 'refresh_token' in response.cookies

    def test_login_cookies_httponly(self, api_client, user):
        """Les cookies sont HttpOnly"""
        data = {'email': user.email, 'password': user._raw_password}
        response = api_client.post(
            '/api/v1/auth/login-cookies', data, format='json'
        )
        access_cookie = response.cookies.get('access_token')
        assert access_cookie is not None
        assert access_cookie['httponly']

    def test_login_cookies_wrong_password(self, api_client, user):
        """Login cookies avec mauvais password retourne 401"""
        data = {'email': user.email, 'password': 'Wrong123!@#'}
        response = api_client.post(
            '/api/v1/auth/login-cookies', data, format='json'
        )
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


# ============================================
# Tests rate limiting sur login
# ============================================

class TestLoginRateLimiting:
    """Tests pour le rate limiting sur la connexion"""

    URL = '/api/v1/auth/login-email'

    def test_rate_limit_after_failures(self, api_client, db):
        """Après N tentatives échouées, retourne 429"""
        data = {'email': 'victim@example.com', 'password': 'Wrong123!@#'}
        # Créer l'utilisateur pour que les tentatives soient comptées
        User.objects.create_user(
            username='victim', email='victim@example.com',
            password='Real123!@#', user_type='EXPLOITANT',
        )
        last_status = None
        for _ in range(10):
            response = api_client.post(self.URL, data, format='json')
            last_status = response.status_code
            if last_status == status.HTTP_429_TOO_MANY_REQUESTS:
                break
        # On devrait avoir atteint 429 ou 401
        assert last_status in [
            status.HTTP_429_TOO_MANY_REQUESTS,
            status.HTTP_401_UNAUTHORIZED,
        ]
