"""
Tests pour l'authentification et la gestion des utilisateurs
"""
from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.core.cache import cache
from rest_framework import status
import json

from .services import (
    SMSVerificationService,
    JWTAuthService,
    RateLimitService,
    PasswordValidationService
)

User = get_user_model()


class PasswordValidationTests(TestCase):
    """Tests pour la validation des mots de passe"""
    
    def test_valid_password(self):
        """Test avec un mot de passe valide"""
        result = PasswordValidationService.validate_password('Test123!@#')
        self.assertTrue(result['is_valid'])
        self.assertEqual(len(result['errors']), 0)
    
    def test_password_too_short(self):
        """Test avec un mot de passe trop court"""
        result = PasswordValidationService.validate_password('Test1!')
        self.assertFalse(result['is_valid'])
        self.assertIn('8 caractères', result['errors'][0])
    
    def test_password_no_uppercase(self):
        """Test sans majuscule"""
        result = PasswordValidationService.validate_password('test123!@#')
        self.assertFalse(result['is_valid'])
        self.assertTrue(any('majuscule' in err for err in result['errors']))
    
    def test_password_no_digit(self):
        """Test sans chiffre"""
        result = PasswordValidationService.validate_password('TestTest!@#')
        self.assertFalse(result['is_valid'])
        self.assertTrue(any('chiffre' in err for err in result['errors']))
    
    def test_password_no_special_char(self):
        """Test sans caractère spécial"""
        result = PasswordValidationService.validate_password('TestTest123')
        self.assertFalse(result['is_valid'])
        self.assertTrue(any('spécial' in err for err in result['errors']))


class SMSVerificationTests(TestCase):
    """Tests pour le service de vérification SMS"""
    
    def setUp(self):
        cache.clear()
    
    def test_generate_code(self):
        """Test de génération de code"""
        code = SMSVerificationService.generate_code()
        self.assertEqual(len(code), 6)
        self.assertTrue(code.isdigit())
    
    def test_send_verification_code(self):
        """Test d'envoi de code de vérification"""
        result = SMSVerificationService.send_verification_code('+22890123456')
        self.assertEqual(result['status'], 'success')
    
    def test_verify_valid_code(self):
        """Test de vérification avec un code valide"""
        phone = '+22890123456'
        
        # Envoyer le code
        send_result = SMSVerificationService.send_verification_code(phone)
        code = send_result.get('code')  # En mode dev
        
        if code:
            # Vérifier le code
            verify_result = SMSVerificationService.verify_code(phone, code)
            self.assertEqual(verify_result['status'], 'success')
    
    def test_verify_invalid_code(self):
        """Test de vérification avec un code invalide"""
        phone = '+22890123456'
        
        # Envoyer le code
        SMSVerificationService.send_verification_code(phone)
        
        # Vérifier avec un mauvais code
        verify_result = SMSVerificationService.verify_code(phone, '000000')
        self.assertEqual(verify_result['status'], 'error')
    
    def test_verify_expired_code(self):
        """Test de vérification avec un code expiré"""
        phone = '+22890123456'
        
        # Vérifier sans avoir envoyé de code
        verify_result = SMSVerificationService.verify_code(phone, '123456')
        self.assertEqual(verify_result['status'], 'error')
        self.assertIn('expiré', verify_result['message'].lower())
    
    def test_max_attempts(self):
        """Test du nombre maximum de tentatives"""
        phone = '+22890123456'
        
        # Envoyer le code
        SMSVerificationService.send_verification_code(phone)
        
        # Faire 3 tentatives échouées
        for _ in range(3):
            SMSVerificationService.verify_code(phone, '000000')
        
        # La 4ème tentative devrait échouer avec un message spécifique
        result = SMSVerificationService.verify_code(phone, '000000')
        self.assertEqual(result['status'], 'error')
        self.assertIn('maximum', result['message'].lower())


class JWTAuthTests(TestCase):
    """Tests pour le service d'authentification JWT"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            phone_number='+22890123456',
            password='Test123!@#',
            user_type='EXPLOITANT'
        )
    
    def test_generate_tokens(self):
        """Test de génération de tokens"""
        tokens = JWTAuthService.generate_tokens(self.user)
        
        self.assertIn('access_token', tokens)
        self.assertIn('refresh_token', tokens)
        self.assertIn('expires_in', tokens)
    
    def test_verify_valid_access_token(self):
        """Test de vérification d'un token d'accès valide"""
        tokens = JWTAuthService.generate_tokens(self.user)
        
        payload = JWTAuthService.verify_token(
            tokens['access_token'],
            token_type='access'
        )
        
        self.assertIsNotNone(payload)
        self.assertEqual(payload['user_id'], self.user.id)
        self.assertEqual(payload['user_type'], self.user.user_type)
    
    def test_verify_invalid_token(self):
        """Test de vérification d'un token invalide"""
        payload = JWTAuthService.verify_token('invalid_token')
        self.assertIsNone(payload)
    
    def test_refresh_access_token(self):
        """Test de rafraîchissement du token d'accès"""
        tokens = JWTAuthService.generate_tokens(self.user)
        
        result = JWTAuthService.refresh_access_token(tokens['refresh_token'])
        
        self.assertIsNotNone(result)
        self.assertIn('access_token', result)
        self.assertIn('expires_in', result)
    
    def test_expired_access_token_rejected(self):
        """Test que les tokens d'accès expirés sont rejetés"""
        # Créer un token avec une durée de vie très courte (1 seconde)
        from datetime import datetime, timedelta
        import jwt
        from django.conf import settings
        
        now = datetime.utcnow()
        payload = {
            'user_id': self.user.id,
            'username': self.user.username,
            'user_type': self.user.user_type,
            'exp': now - timedelta(seconds=1),  # Token expiré il y a 1 seconde
            'iat': now - timedelta(seconds=2),
            'type': 'access'
        }
        
        expired_token = jwt.encode(payload, settings.JWT_SECRET_KEY, algorithm='HS256')
        
        # Vérifier que le token expiré est rejeté
        result = JWTAuthService.verify_token(expired_token, token_type='access')
        self.assertIsNone(result)
    
    def test_expired_refresh_token_rejected(self):
        """Test que les tokens de rafraîchissement expirés sont rejetés"""
        # Créer un refresh token avec une durée de vie très courte
        from datetime import datetime, timedelta
        import jwt
        from django.conf import settings
        
        now = datetime.utcnow()
        payload = {
            'user_id': self.user.id,
            'username': self.user.username,
            'user_type': self.user.user_type,
            'exp': now - timedelta(seconds=1),  # Token expiré il y a 1 seconde
            'iat': now - timedelta(seconds=2),
            'type': 'refresh'
        }
        
        expired_refresh_token = jwt.encode(payload, settings.JWT_SECRET_KEY, algorithm='HS256')
        
        # Vérifier que le refresh token expiré ne peut pas générer un nouveau access token
        result = JWTAuthService.refresh_access_token(expired_refresh_token)
        self.assertIsNone(result)
    
    def test_access_token_cannot_be_used_as_refresh_token(self):
        """Test qu'un token d'accès ne peut pas être utilisé comme refresh token"""
        tokens = JWTAuthService.generate_tokens(self.user)
        
        # Essayer d'utiliser l'access token comme refresh token
        result = JWTAuthService.refresh_access_token(tokens['access_token'])
        
        # Cela devrait échouer car le type de token ne correspond pas
        self.assertIsNone(result)
    
    def test_refresh_token_cannot_be_used_as_access_token(self):
        """Test qu'un refresh token ne peut pas être utilisé comme access token"""
        tokens = JWTAuthService.generate_tokens(self.user)
        
        # Essayer de vérifier le refresh token comme access token
        result = JWTAuthService.verify_token(tokens['refresh_token'], token_type='access')
        
        # Cela devrait échouer car le type de token ne correspond pas
        self.assertIsNone(result)


class RateLimitTests(TestCase):
    """Tests pour le service de rate limiting"""
    
    def setUp(self):
        cache.clear()
    
    def test_check_rate_limit_initial(self):
        """Test du rate limit initial"""
        result = RateLimitService.check_rate_limit('192.168.1.1')
        
        self.assertFalse(result['is_blocked'])
        self.assertEqual(result['remaining_attempts'], RateLimitService.MAX_ATTEMPTS)
    
    def test_record_failed_attempts(self):
        """Test d'enregistrement de tentatives échouées"""
        ip = '192.168.1.1'
        
        # Enregistrer 3 tentatives échouées
        for _ in range(3):
            RateLimitService.record_attempt(ip, success=False)
        
        result = RateLimitService.check_rate_limit(ip)
        self.assertEqual(result['remaining_attempts'], 2)
    
    def test_block_after_max_attempts(self):
        """Test du blocage après le nombre maximum de tentatives"""
        ip = '192.168.1.1'
        
        # Enregistrer 5 tentatives échouées
        for _ in range(5):
            RateLimitService.record_attempt(ip, success=False)
        
        result = RateLimitService.check_rate_limit(ip)
        self.assertTrue(result['is_blocked'])
        self.assertEqual(result['remaining_attempts'], 0)
    
    def test_reset_on_success(self):
        """Test de réinitialisation après succès"""
        ip = '192.168.1.1'
        
        # Enregistrer 3 tentatives échouées
        for _ in range(3):
            RateLimitService.record_attempt(ip, success=False)
        
        # Enregistrer une tentative réussie
        RateLimitService.record_attempt(ip, success=True)
        
        # Vérifier que le compteur est réinitialisé
        result = RateLimitService.check_rate_limit(ip)
        self.assertEqual(result['remaining_attempts'], RateLimitService.MAX_ATTEMPTS)


class AuthenticationAPITests(TestCase):
    """Tests pour les endpoints d'authentification"""
    
    def setUp(self):
        self.client = Client()
        cache.clear()
    
    def test_register_success(self):
        """Test d'inscription réussie"""
        data = {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'phone_number': '+22890123456',
            'password': 'Test123!@#',
            'password_confirm': 'Test123!@#',
            'user_type': 'EXPLOITANT',
            'first_name': 'Test',
            'last_name': 'User'
        }
        
        response = self.client.post(
            '/api/v1/auth/register',
            data=json.dumps(data),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('user', response.json())
        self.assertIn('message', response.json())
    
    def test_register_duplicate_phone(self):
        """Test d'inscription avec un numéro déjà utilisé"""
        # Créer un utilisateur
        User.objects.create_user(
            username='existing',
            email='existing@example.com',
            phone_number='+22890123456',
            password='Test123!@#',
            user_type='EXPLOITANT'
        )
        
        # Essayer de créer un autre utilisateur avec le même numéro
        data = {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'phone_number': '+22890123456',
            'password': 'Test123!@#',
            'password_confirm': 'Test123!@#',
            'user_type': 'EXPLOITANT'
        }
        
        response = self.client.post(
            '/api/v1/auth/register',
            data=json.dumps(data),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_register_invalid_password(self):
        """Test d'inscription avec un mot de passe invalide"""
        data = {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'phone_number': '+22890123456',
            'password': 'weak',
            'password_confirm': 'weak',
            'user_type': 'EXPLOITANT'
        }
        
        response = self.client.post(
            '/api/v1/auth/register',
            data=json.dumps(data),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
    
    def test_login_success(self):
        """Test de connexion réussie"""
        # Créer un utilisateur
        user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            phone_number='+22890123456',
            password='Test123!@#',
            user_type='EXPLOITANT'
        )
        user.phone_verified = True
        user.save()
        
        # Se connecter
        data = {
            'phone_number': '+22890123456',
            'password': 'Test123!@#'
        }
        
        response = self.client.post(
            '/api/v1/auth/login',
            data=json.dumps(data),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('tokens', response.json())
        self.assertIn('user', response.json())
    
    def test_login_invalid_credentials(self):
        """Test de connexion avec des identifiants invalides"""
        data = {
            'phone_number': '+22890123456',
            'password': 'WrongPassword123!@#'
        }
        
        response = self.client.post(
            '/api/v1/auth/login',
            data=json.dumps(data),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_login_rate_limiting(self):
        """Test du rate limiting sur la connexion"""
        data = {
            'phone_number': '+22890123456',
            'password': 'WrongPassword123!@#'
        }
        
        # Faire 5 tentatives échouées
        for _ in range(5):
            self.client.post(
                '/api/v1/auth/login',
                data=json.dumps(data),
                content_type='application/json'
            )
        
        # La 6ème tentative devrait être bloquée
        response = self.client.post(
            '/api/v1/auth/login',
            data=json.dumps(data),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, status.HTTP_429_TOO_MANY_REQUESTS)
