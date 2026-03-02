"""
Tests pour le système d'authentification à deux facteurs (2FA)

Exigences: 25.2
"""
import pytest
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from apps.users.services import TwoFactorAuthService
import pyotp

User = get_user_model()


@pytest.fixture
def api_client():
    """Client API pour les tests"""
    return APIClient()


@pytest.fixture
def test_user(db):
    """Utilisateur de test"""
    user = User.objects.create_user(
        username='testuser',
        email='test@example.com',
        phone_number='+22812345678',
        password='TestPass123!',
        user_type='EXPLOITANT'
    )
    user.phone_verified = True
    user.save()
    return user


@pytest.fixture
def institutional_user(db):
    """Utilisateur institutionnel de test"""
    user = User.objects.create_user(
        username='institution',
        email='institution@example.com',
        phone_number='+22887654321',
        password='InstPass123!',
        user_type='INSTITUTION'
    )
    user.phone_verified = True
    user.save()
    return user


@pytest.fixture
def authenticated_client(api_client, test_user):
    """Client authentifié"""
    from apps.users.services import JWTAuthService
    tokens = JWTAuthService.generate_tokens(test_user)
    api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {tokens["access_token"]}')
    return api_client


@pytest.fixture
def authenticated_institutional_client(api_client, institutional_user):
    """Client institutionnel authentifié"""
    from apps.users.services import JWTAuthService
    tokens = JWTAuthService.generate_tokens(institutional_user)
    api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {tokens["access_token"]}')
    return api_client


class TestTwoFactorAuthService:
    """Tests pour le service TwoFactorAuthService"""
    
    def test_generate_secret(self):
        """Test de génération de secret TOTP"""
        secret = TwoFactorAuthService.generate_secret()
        
        assert secret is not None
        assert len(secret) == 32  # Base32 secret
        assert secret.isalnum()
        assert secret.isupper()
    
    def test_generate_qr_code(self, test_user):
        """Test de génération de QR code"""
        secret = TwoFactorAuthService.generate_secret()
        qr_code = TwoFactorAuthService.generate_qr_code(test_user, secret)
        
        assert qr_code is not None
        assert qr_code.startswith('data:image/png;base64,')
    
    def test_verify_token_valid(self):
        """Test de vérification d'un token valide"""
        secret = TwoFactorAuthService.generate_secret()
        totp = pyotp.TOTP(secret)
        token = totp.now()
        
        assert TwoFactorAuthService.verify_token(secret, token) is True
    
    def test_verify_token_invalid(self):
        """Test de vérification d'un token invalide"""
        secret = TwoFactorAuthService.generate_secret()
        
        assert TwoFactorAuthService.verify_token(secret, '000000') is False
    
    def test_verify_token_empty(self):
        """Test de vérification avec token vide"""
        secret = TwoFactorAuthService.generate_secret()
        
        assert TwoFactorAuthService.verify_token(secret, '') is False
        assert TwoFactorAuthService.verify_token('', '123456') is False
    
    def test_require_2fa_for_institution(self, institutional_user, test_user):
        """Test de vérification si le 2FA est obligatoire"""
        assert TwoFactorAuthService.require_2fa_for_institution(institutional_user) is True
        assert TwoFactorAuthService.require_2fa_for_institution(test_user) is False
    
    def test_setup_2fa(self, test_user):
        """Test de configuration du 2FA"""
        result = TwoFactorAuthService.setup_2fa(test_user)
        
        assert result['status'] == 'success'
        assert 'secret' in result
        assert 'qr_code' in result
        assert 'message' in result
        
        # Vérifier que le secret est sauvegardé
        test_user.refresh_from_db()
        assert test_user.two_factor_secret is not None
        assert test_user.two_factor_enabled is False  # Pas encore activé
    
    def test_enable_2fa_success(self, test_user):
        """Test d'activation du 2FA avec token valide"""
        # Configurer le 2FA
        result = TwoFactorAuthService.setup_2fa(test_user)
        secret = result['secret']
        
        # Générer un token valide
        totp = pyotp.TOTP(secret)
        token = totp.now()
        
        # Activer le 2FA
        result = TwoFactorAuthService.enable_2fa(test_user, token)
        
        assert result['status'] == 'success'
        assert 'backup_codes' in result
        assert len(result['backup_codes']) == 10
        
        # Vérifier que le 2FA est activé
        test_user.refresh_from_db()
        assert test_user.two_factor_enabled is True
    
    def test_enable_2fa_invalid_token(self, test_user):
        """Test d'activation du 2FA avec token invalide"""
        # Configurer le 2FA
        TwoFactorAuthService.setup_2fa(test_user)
        
        # Essayer d'activer avec un token invalide
        result = TwoFactorAuthService.enable_2fa(test_user, '000000')
        
        assert result['status'] == 'error'
        
        # Vérifier que le 2FA n'est pas activé
        test_user.refresh_from_db()
        assert test_user.two_factor_enabled is False
    
    def test_disable_2fa_success(self, test_user):
        """Test de désactivation du 2FA"""
        # Configurer et activer le 2FA
        result = TwoFactorAuthService.setup_2fa(test_user)
        secret = result['secret']
        totp = pyotp.TOTP(secret)
        token = totp.now()
        TwoFactorAuthService.enable_2fa(test_user, token)
        
        # Désactiver le 2FA
        result = TwoFactorAuthService.disable_2fa(test_user, 'TestPass123!')
        
        assert result['status'] == 'success'
        
        # Vérifier que le 2FA est désactivé
        test_user.refresh_from_db()
        assert test_user.two_factor_enabled is False
        assert test_user.two_factor_secret is None
    
    def test_disable_2fa_wrong_password(self, test_user):
        """Test de désactivation du 2FA avec mauvais mot de passe"""
        # Configurer et activer le 2FA
        result = TwoFactorAuthService.setup_2fa(test_user)
        secret = result['secret']
        totp = pyotp.TOTP(secret)
        token = totp.now()
        TwoFactorAuthService.enable_2fa(test_user, token)
        
        # Essayer de désactiver avec un mauvais mot de passe
        result = TwoFactorAuthService.disable_2fa(test_user, 'WrongPassword')
        
        assert result['status'] == 'error'
        
        # Vérifier que le 2FA est toujours activé
        test_user.refresh_from_db()
        assert test_user.two_factor_enabled is True


class TestTwoFactorAuthEndpoints:
    """Tests pour les endpoints d'authentification 2FA"""
    
    def test_setup_2fa_authenticated(self, authenticated_client, test_user):
        """Test de configuration du 2FA pour un utilisateur authentifié"""
        url = reverse('users:2fa-setup')
        response = authenticated_client.post(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert 'secret' in response.data
        assert 'qr_code' in response.data
        assert 'instructions' in response.data
        
        # Vérifier que le secret est sauvegardé
        test_user.refresh_from_db()
        assert test_user.two_factor_secret is not None
    
    def test_setup_2fa_unauthenticated(self, api_client):
        """Test de configuration du 2FA sans authentification"""
        url = reverse('users:2fa-setup')
        response = api_client.post(url)
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    def test_setup_2fa_already_enabled(self, authenticated_client, test_user):
        """Test de configuration du 2FA quand déjà activé"""
        # Activer le 2FA
        result = TwoFactorAuthService.setup_2fa(test_user)
        secret = result['secret']
        totp = pyotp.TOTP(secret)
        token = totp.now()
        TwoFactorAuthService.enable_2fa(test_user, token)
        
        # Essayer de reconfigurer
        url = reverse('users:2fa-setup')
        response = authenticated_client.post(url)
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
    
    def test_enable_2fa_success(self, authenticated_client, test_user):
        """Test d'activation du 2FA via l'API"""
        # Configurer le 2FA
        setup_url = reverse('users:2fa-setup')
        setup_response = authenticated_client.post(setup_url)
        secret = setup_response.data['secret']
        
        # Générer un token valide
        totp = pyotp.TOTP(secret)
        token = totp.now()
        
        # Activer le 2FA
        enable_url = reverse('users:2fa-enable')
        response = authenticated_client.post(enable_url, {'token': token})
        
        assert response.status_code == status.HTTP_200_OK
        assert 'backup_codes' in response.data
        assert len(response.data['backup_codes']) == 10
        
        # Vérifier que le 2FA est activé
        test_user.refresh_from_db()
        assert test_user.two_factor_enabled is True
    
    def test_enable_2fa_invalid_token(self, authenticated_client, test_user):
        """Test d'activation du 2FA avec token invalide"""
        # Configurer le 2FA
        setup_url = reverse('users:2fa-setup')
        authenticated_client.post(setup_url)
        
        # Essayer d'activer avec un token invalide
        enable_url = reverse('users:2fa-enable')
        response = authenticated_client.post(enable_url, {'token': '000000'})
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
    
    def test_disable_2fa_success(self, authenticated_client, test_user):
        """Test de désactivation du 2FA via l'API"""
        # Configurer et activer le 2FA
        result = TwoFactorAuthService.setup_2fa(test_user)
        secret = result['secret']
        totp = pyotp.TOTP(secret)
        token = totp.now()
        TwoFactorAuthService.enable_2fa(test_user, token)
        
        # Désactiver le 2FA
        url = reverse('users:2fa-disable')
        response = authenticated_client.post(url, {'password': 'TestPass123!'})
        
        assert response.status_code == status.HTTP_200_OK
        
        # Vérifier que le 2FA est désactivé
        test_user.refresh_from_db()
        assert test_user.two_factor_enabled is False
    
    def test_verify_2fa_success(self, api_client, test_user):
        """Test de vérification du token 2FA lors de la connexion"""
        # Configurer et activer le 2FA
        result = TwoFactorAuthService.setup_2fa(test_user)
        secret = result['secret']
        totp = pyotp.TOTP(secret)
        token = totp.now()
        TwoFactorAuthService.enable_2fa(test_user, token)
        
        # Générer un nouveau token pour la connexion
        new_token = totp.now()
        
        # Vérifier le token 2FA
        url = reverse('users:2fa-verify')
        response = api_client.post(url, {
            'phone_number': test_user.phone_number,
            'token': new_token
        })
        
        assert response.status_code == status.HTTP_200_OK
        assert 'tokens' in response.data
        assert 'access_token' in response.data['tokens']
        assert 'refresh_token' in response.data['tokens']
    
    def test_verify_2fa_invalid_token(self, api_client, test_user):
        """Test de vérification avec token 2FA invalide"""
        # Configurer et activer le 2FA
        result = TwoFactorAuthService.setup_2fa(test_user)
        secret = result['secret']
        totp = pyotp.TOTP(secret)
        token = totp.now()
        TwoFactorAuthService.enable_2fa(test_user, token)
        
        # Essayer avec un token invalide
        url = reverse('users:2fa-verify')
        response = api_client.post(url, {
            'phone_number': test_user.phone_number,
            'token': '000000'
        })
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    def test_check_2fa_status_institutional(self, authenticated_institutional_client, institutional_user):
        """Test de vérification du statut 2FA pour un compte institutionnel"""
        url = reverse('users:2fa-status')
        response = authenticated_institutional_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['user_type'] == 'INSTITUTION'
        assert response.data['two_factor_required'] is True
        assert response.data['two_factor_enabled'] is False
    
    def test_check_2fa_status_non_institutional(self, authenticated_client, test_user):
        """Test de vérification du statut 2FA pour un compte non-institutionnel"""
        url = reverse('users:2fa-status')
        response = authenticated_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['user_type'] == 'EXPLOITANT'
        assert response.data['two_factor_required'] is False
        assert response.data['two_factor_enabled'] is False
    
    def test_login_with_2fa_required(self, api_client, test_user):
        """Test de connexion avec 2FA activé"""
        # Configurer et activer le 2FA
        result = TwoFactorAuthService.setup_2fa(test_user)
        secret = result['secret']
        totp = pyotp.TOTP(secret)
        token = totp.now()
        TwoFactorAuthService.enable_2fa(test_user, token)
        
        # Essayer de se connecter
        login_url = reverse('users:login')
        response = api_client.post(login_url, {
            'phone_number': test_user.phone_number,
            'password': 'TestPass123!'
        })
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['requires_2fa'] is True
        assert 'tokens' not in response.data  # Pas de tokens sans 2FA
    
    def test_institutional_login_without_2fa_setup(self, api_client, institutional_user):
        """Test de connexion institutionnelle sans 2FA configuré"""
        login_url = reverse('users:login')
        response = api_client.post(login_url, {
            'phone_number': institutional_user.phone_number,
            'password': 'InstPass123!'
        })
        
        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert response.data['requires_2fa_setup'] is True