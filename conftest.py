"""
Fixtures globales pour pytest - Haroo

Fournit: api_client, user_factory, user_data, auth_headers, etc.
"""
import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient

User = get_user_model()


# ============================================
# Fixtures de base
# ============================================

@pytest.fixture
def api_client():
    """Client API REST Framework non authentifié"""
    return APIClient()


@pytest.fixture
def user_data():
    """Données de base pour créer un utilisateur"""
    return {
        'username': 'testuser',
        'email': 'testuser@example.com',
        'password': 'Test123!@#',
        'user_type': 'EXPLOITANT',
        'first_name': 'Test',
        'last_name': 'User',
    }


@pytest.fixture
def user_data_agronome():
    """Données pour un utilisateur agronome"""
    return {
        'username': 'agronome1',
        'email': 'agronome@example.com',
        'password': 'Test123!@#',
        'user_type': 'AGRONOME',
        'first_name': 'Agro',
        'last_name': 'Nome',
    }


# ============================================
# Fixtures utilisateurs
# ============================================

@pytest.fixture
def user(db, user_data):
    """Crée un utilisateur exploitant actif"""
    u = User.objects.create_user(
        username=user_data['username'],
        email=user_data['email'],
        password=user_data['password'],
        user_type=user_data['user_type'],
        first_name=user_data['first_name'],
        last_name=user_data['last_name'],
        phone_verified=True,
    )
    u._raw_password = user_data['password']
    return u


@pytest.fixture
def admin_user(db):
    """Crée un utilisateur administrateur"""
    u = User.objects.create_superuser(
        username='admin',
        email='admin@example.com',
        password='Admin123!@#',
        user_type='ADMIN',
    )
    u._raw_password = 'Admin123!@#'
    return u


# ============================================
# Fixtures authentification
# ============================================

@pytest.fixture
def auth_client(api_client, user):
    """Client API authentifié avec un utilisateur standard"""
    api_client.force_authenticate(user=user)
    return api_client


@pytest.fixture
def admin_client(api_client, admin_user):
    """Client API authentifié avec un administrateur"""
    api_client.force_authenticate(user=admin_user)
    return api_client


@pytest.fixture
def jwt_tokens(user):
    """Génère des tokens JWT pour un utilisateur"""
    from apps.users.services import JWTAuthService
    return JWTAuthService.generate_tokens(user)


@pytest.fixture
def auth_headers(jwt_tokens):
    """Headers d'authentification Bearer"""
    return {'HTTP_AUTHORIZATION': f"Bearer {jwt_tokens['access_token']}"}


# ============================================
# Fixtures utilitaires
# ============================================

@pytest.fixture(autouse=True)
def clear_cache():
    """Vide le cache avant chaque test"""
    from django.core.cache import cache
    cache.clear()
    yield
    cache.clear()
