"""
Tests pour la gestion des sessions

Exigences: 40.1, 40.2, 40.3, 40.4, 40.5
"""
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.core.cache import cache
from rest_framework.test import APIClient
from rest_framework import status

from .session_service import SessionManagementService
from .services import JWTAuthService

User = get_user_model()


class SessionManagementServiceTest(TestCase):
    """Tests pour le service de gestion des sessions"""
    
    def setUp(self):
        """Configuration initiale pour les tests"""
        # Nettoyer le cache avant chaque test
        cache.clear()
        
        # Créer un utilisateur de test
        self.user = User.objects.create_user(
            username='testuser',
            phone_number='+22890123456',
            password='TestPass123!',
            user_type='EXPLOITANT',
            phone_verified=True
        )
        
        # Générer un token JWT
        tokens = JWTAuthService.generate_tokens(self.user)
        self.access_token = tokens['access_token']
    
    def tearDown(self):
        """Nettoyage après chaque test"""
        cache.clear()
    
    def test_create_session(self):
        """
        Test: Création d'une session
        Exigences: 40.1
        """
        session_data = SessionManagementService.create_session(
            user_id=self.user.id,
            token=self.access_token,
            ip_address='192.168.1.1',
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/91.0'
        )
        
        # Vérifier que la session a été créée
        self.assertIsNotNone(session_data)
        self.assertEqual(session_data['user_id'], self.user.id)
        self.assertEqual(session_data['ip_address'], '192.168.1.1')
        self.assertIn('device', session_data)
        self.assertIn('browser', session_data)
        self.assertIn('os', session_data)
        self.assertIn('created_at', session_data)
        self.assertIn('last_activity', session_data)
    
    def test_session_ttl_24_hours(self):
        """
        Test: La session a un TTL de 24 heures
        Exigences: 40.1
        """
        SessionManagementService.create_session(
            user_id=self.user.id,
            token=self.access_token,
            ip_address='192.168.1.1'
        )
        
        # Vérifier que la session existe
        is_valid = SessionManagementService.is_session_valid(self.user.id, self.access_token)
        self.assertTrue(is_valid)
        
        # Vérifier que le TTL est bien de 24 heures (86400 secondes)
        token_hash = SessionManagementService._hash_token(self.access_token)
        session_key = SessionManagementService._get_session_key(self.user.id, token_hash)
        ttl = cache.ttl(session_key)
        
        # Le TTL devrait être proche de 86400 (avec une marge de quelques secondes)
        self.assertGreater(ttl, 86390)
        self.assertLessEqual(ttl, 86400)
    
    def test_update_session_activity(self):
        """
        Test: Mise à jour de l'activité de la session
        Exigences: 40.1
        """
        # Créer une session
        session_data = SessionManagementService.create_session(
            user_id=self.user.id,
            token=self.access_token,
            ip_address='192.168.1.1'
        )
        
        initial_activity = session_data['last_activity']
        
        # Attendre un peu et mettre à jour
        import time
        time.sleep(0.1)
        
        success = SessionManagementService.update_session_activity(
            user_id=self.user.id,
            token=self.access_token
        )
        
        self.assertTrue(success)
        
        # Récupérer la session mise à jour
        updated_session = SessionManagementService.get_session_info(
            user_id=self.user.id,
            token=self.access_token
        )
        
        # Vérifier que last_activity a été mis à jour
        self.assertNotEqual(updated_session['last_activity'], initial_activity)
    
    def test_invalidate_session(self):
        """
        Test: Invalidation d'une session (déconnexion)
        Exigences: 40.2
        """
        # Créer une session
        SessionManagementService.create_session(
            user_id=self.user.id,
            token=self.access_token,
            ip_address='192.168.1.1'
        )
        
        # Vérifier que la session existe
        is_valid = SessionManagementService.is_session_valid(self.user.id, self.access_token)
        self.assertTrue(is_valid)
        
        # Invalider la session
        success = SessionManagementService.invalidate_session(
            user_id=self.user.id,
            token=self.access_token
        )
        
        self.assertTrue(success)
        
        # Vérifier que la session n'existe plus
        is_valid = SessionManagementService.is_session_valid(self.user.id, self.access_token)
        self.assertFalse(is_valid)
    
    def test_invalidate_all_sessions(self):
        """
        Test: Invalidation de toutes les sessions (déconnexion multi-appareils)
        Exigences: 40.3
        """
        # Créer plusieurs sessions (simuler plusieurs appareils)
        tokens = []
        for i in range(3):
            token_data = JWTAuthService.generate_tokens(self.user)
            token = token_data['access_token']
            tokens.append(token)
            
            SessionManagementService.create_session(
                user_id=self.user.id,
                token=token,
                ip_address=f'192.168.1.{i+1}'
            )
        
        # Vérifier que toutes les sessions existent
        for token in tokens:
            is_valid = SessionManagementService.is_session_valid(self.user.id, token)
            self.assertTrue(is_valid)
        
        # Invalider toutes les sessions
        count = SessionManagementService.invalidate_all_sessions(self.user.id)
        
        self.assertEqual(count, 3)
        
        # Vérifier qu'aucune session n'existe plus
        for token in tokens:
            is_valid = SessionManagementService.is_session_valid(self.user.id, token)
            self.assertFalse(is_valid)
    
    def test_get_active_sessions(self):
        """
        Test: Récupération des sessions actives
        Exigences: 40.4, 40.5
        """
        # Créer plusieurs sessions avec différents appareils
        devices = [
            {
                'token': JWTAuthService.generate_tokens(self.user)['access_token'],
                'ip': '192.168.1.1',
                'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/91.0'
            },
            {
                'token': JWTAuthService.generate_tokens(self.user)['access_token'],
                'ip': '192.168.1.2',
                'user_agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 14_6 like Mac OS X) Safari/604.1'
            },
            {
                'token': JWTAuthService.generate_tokens(self.user)['access_token'],
                'ip': '192.168.1.3',
                'user_agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) Safari/605.1.15'
            }
        ]
        
        for device in devices:
            SessionManagementService.create_session(
                user_id=self.user.id,
                token=device['token'],
                ip_address=device['ip'],
                user_agent=device['user_agent']
            )
        
        # Récupérer les sessions actives
        active_sessions = SessionManagementService.get_active_sessions(self.user.id)
        
        # Vérifier le nombre de sessions
        self.assertEqual(len(active_sessions), 3)
        
        # Vérifier que chaque session contient les informations requises
        for session in active_sessions:
            self.assertIn('device', session)
            self.assertIn('browser', session)
            self.assertIn('os', session)
            self.assertIn('ip_address', session)
            self.assertIn('location', session)
            self.assertIn('created_at', session)
            self.assertIn('last_activity', session)
            self.assertIn('session_id', session)
            
            # Vérifier que le token_hash complet n'est pas exposé
            self.assertNotIn('token_hash', session)
    
    def test_parse_user_agent_desktop(self):
        """Test: Parsing du user agent pour un desktop"""
        user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        
        device_info = SessionManagementService._parse_user_agent(user_agent)
        
        self.assertEqual(device_info['device'], 'Desktop')
        self.assertEqual(device_info['browser'], 'Chrome')
        self.assertEqual(device_info['os'], 'Windows')
    
    def test_parse_user_agent_mobile(self):
        """Test: Parsing du user agent pour un mobile"""
        user_agent = 'Mozilla/5.0 (iPhone; CPU iPhone OS 14_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.1 Mobile/15E148 Safari/604.1'
        
        device_info = SessionManagementService._parse_user_agent(user_agent)
        
        self.assertEqual(device_info['device'], 'Mobile')
        self.assertEqual(device_info['browser'], 'Safari')
        self.assertEqual(device_info['os'], 'iOS')


class SessionAPITest(TestCase):
    """Tests pour les endpoints API de gestion des sessions"""
    
    def setUp(self):
        """Configuration initiale pour les tests"""
        cache.clear()
        
        self.client = APIClient()
        
        # Créer un utilisateur de test
        self.user = User.objects.create_user(
            username='testuser',
            phone_number='+22890123456',
            password='TestPass123!',
            user_type='EXPLOITANT',
            phone_verified=True
        )
        
        # Générer un token JWT
        tokens = JWTAuthService.generate_tokens(self.user)
        self.access_token = tokens['access_token']
        
        # Créer une session
        SessionManagementService.create_session(
            user_id=self.user.id,
            token=self.access_token,
            ip_address='192.168.1.1',
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/91.0'
        )
    
    def tearDown(self):
        """Nettoyage après chaque test"""
        cache.clear()
    
    def test_logout_endpoint(self):
        """
        Test: Endpoint de déconnexion
        Exigences: 40.2
        """
        # Authentifier le client
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.access_token}')
        
        # Appeler l'endpoint de déconnexion
        response = self.client.post('/api/v1/auth/logout')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('message', response.data)
        
        # Vérifier que la session a été invalidée
        is_valid = SessionManagementService.is_session_valid(self.user.id, self.access_token)
        self.assertFalse(is_valid)
    
    def test_logout_all_devices_endpoint(self):
        """
        Test: Endpoint de déconnexion de tous les appareils
        Exigences: 40.3
        """
        # Créer plusieurs sessions
        for i in range(2):
            token_data = JWTAuthService.generate_tokens(self.user)
            SessionManagementService.create_session(
                user_id=self.user.id,
                token=token_data['access_token'],
                ip_address=f'192.168.1.{i+2}'
            )
        
        # Authentifier le client
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.access_token}')
        
        # Appeler l'endpoint de déconnexion de tous les appareils
        response = self.client.post('/api/v1/auth/logout-all')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('sessions_invalidated', response.data)
        self.assertEqual(response.data['sessions_invalidated'], 3)
        
        # Vérifier qu'aucune session n'existe plus
        active_sessions = SessionManagementService.get_active_sessions(self.user.id)
        self.assertEqual(len(active_sessions), 0)
    
    def test_active_sessions_endpoint(self):
        """
        Test: Endpoint de récupération des sessions actives
        Exigences: 40.4, 40.5
        """
        # Créer une session supplémentaire
        token_data = JWTAuthService.generate_tokens(self.user)
        SessionManagementService.create_session(
            user_id=self.user.id,
            token=token_data['access_token'],
            ip_address='192.168.1.2',
            user_agent='Mozilla/5.0 (iPhone; CPU iPhone OS 14_6 like Mac OS X) Safari/604.1'
        )
        
        # Authentifier le client
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.access_token}')
        
        # Appeler l'endpoint des sessions actives
        response = self.client.get('/api/v1/users/me/sessions')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('sessions', response.data)
        self.assertIn('total', response.data)
        self.assertEqual(response.data['total'], 2)
        
        # Vérifier les informations de chaque session
        for session in response.data['sessions']:
            self.assertIn('device', session)
            self.assertIn('browser', session)
            self.assertIn('os', session)
            self.assertIn('ip_address', session)
            self.assertIn('location', session)
            self.assertIn('created_at', session)
            self.assertIn('last_activity', session)
    
    def test_logout_without_token(self):
        """Test: Déconnexion sans token"""
        response = self.client.post('/api/v1/auth/logout')
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_active_sessions_without_authentication(self):
        """Test: Récupération des sessions sans authentification"""
        response = self.client.get('/api/v1/users/me/sessions')
        
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
