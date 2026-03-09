"""
Tests pour le système de rate limiting avancé
"""
import pytest
import time
from django.test import RequestFactory
from django.contrib.auth import get_user_model
from django.core.cache import cache
from apps.core.rate_limiting import (
    SlidingWindowRateLimiter,
    RateLimitConfig,
    get_client_identifier,
    rate_limit,
    AdvancedRateLimitMiddleware,
    RateLimitService
)

User = get_user_model()


@pytest.fixture
def request_factory():
    """Factory pour créer des requêtes de test"""
    return RequestFactory()


@pytest.fixture
def test_user(db):
    """Créer un utilisateur de test"""
    return User.objects.create_user(
        email='test@example.com',
        password='TestPass123!',
        user_type='EXPLOITANT'
    )


@pytest.fixture(autouse=True)
def clear_cache():
    """Nettoyer le cache avant chaque test"""
    cache.clear()
    yield
    cache.clear()


class TestSlidingWindowRateLimiter:
    """Tests pour le rate limiter avec sliding window"""
    
    def test_allows_requests_within_limit(self):
        """Vérifie que les requêtes dans la limite sont autorisées"""
        limiter = SlidingWindowRateLimiter(
            max_requests=5,
            window_seconds=60,
            key_prefix="test"
        )
        
        # Faire 5 requêtes (limite)
        for i in range(5):
            is_allowed, info = limiter.is_allowed("test_user")
            assert is_allowed is True
            assert info['remaining'] == 4 - i
    
    def test_blocks_requests_over_limit(self):
        """Vérifie que les requêtes au-delà de la limite sont bloquées"""
        limiter = SlidingWindowRateLimiter(
            max_requests=3,
            window_seconds=60,
            key_prefix="test"
        )
        
        # Faire 3 requêtes (limite)
        for _ in range(3):
            is_allowed, _ = limiter.is_allowed("test_user")
            assert is_allowed is True
        
        # La 4ème requête doit être bloquée
        is_allowed, info = limiter.is_allowed("test_user")
        assert is_allowed is False
        assert info['remaining'] == 0
        assert info['retry_after'] > 0
    
    def test_sliding_window_behavior(self):
        """Vérifie le comportement de la fenêtre glissante"""
        limiter = SlidingWindowRateLimiter(
            max_requests=2,
            window_seconds=2,  # 2 secondes pour test rapide
            key_prefix="test"
        )
        
        # Faire 2 requêtes
        limiter.is_allowed("test_user")
        limiter.is_allowed("test_user")
        
        # La 3ème est bloquée
        is_allowed, _ = limiter.is_allowed("test_user")
        assert is_allowed is False
        
        # Attendre que la fenêtre glisse
        time.sleep(2.1)
        
        # Maintenant autorisé
        is_allowed, _ = limiter.is_allowed("test_user")
        assert is_allowed is True
    
    def test_different_identifiers_independent(self):
        """Vérifie que différents identifiants ont des limites indépendantes"""
        limiter = SlidingWindowRateLimiter(
            max_requests=2,
            window_seconds=60,
            key_prefix="test"
        )
        
        # User 1 fait 2 requêtes
        limiter.is_allowed("user1")
        limiter.is_allowed("user1")
        
        # User 1 est bloqué
        is_allowed, _ = limiter.is_allowed("user1")
        assert is_allowed is False
        
        # User 2 peut toujours faire des requêtes
        is_allowed, _ = limiter.is_allowed("user2")
        assert is_allowed is True


class TestGetClientIdentifier:
    """Tests pour la fonction get_client_identifier"""
    
    def test_returns_user_id_when_authenticated(self, request_factory, test_user):
        """Vérifie que l'ID utilisateur est retourné si authentifié"""
        request = request_factory.get('/')
        request.user = test_user
        
        identifier = get_client_identifier(request)
        assert identifier == f"user:{test_user.id}"
    
    def test_returns_ip_when_not_authenticated(self, request_factory):
        """Vérifie que l'IP est retournée si non authentifié"""
        request = request_factory.get('/')
        request.user = type('User', (), {'is_authenticated': False})()
        request.META['REMOTE_ADDR'] = '192.168.1.1'
        
        identifier = get_client_identifier(request)
        assert identifier == "ip:192.168.1.1"
    
    def test_handles_x_forwarded_for(self, request_factory):
        """Vérifie la gestion du header X-Forwarded-For"""
        request = request_factory.get('/')
        request.user = type('User', (), {'is_authenticated': False})()
        request.META['HTTP_X_FORWARDED_FOR'] = '10.0.0.1, 192.168.1.1'
        
        identifier = get_client_identifier(request)
        assert identifier == "ip:10.0.0.1"


class TestRateLimitDecorator:
    """Tests pour le décorateur rate_limit"""
    
    def test_allows_requests_within_limit(self, request_factory):
        """Vérifie que les requêtes dans la limite passent"""
        limiter = SlidingWindowRateLimiter(
            max_requests=3,
            window_seconds=60,
            key_prefix="test_decorator"
        )
        
        @rate_limit(limiter)
        def test_view(request):
            return type('Response', (), {'status_code': 200})()
        
        request = request_factory.get('/')
        request.user = type('User', (), {'is_authenticated': False})()
        request.META['REMOTE_ADDR'] = '192.168.1.1'
        
        # 3 requêtes doivent passer
        for _ in range(3):
            response = test_view(request)
            assert response.status_code == 200
    
    def test_blocks_requests_over_limit(self, request_factory):
        """Vérifie que les requêtes au-delà de la limite sont bloquées"""
        limiter = SlidingWindowRateLimiter(
            max_requests=2,
            window_seconds=60,
            key_prefix="test_decorator"
        )
        
        @rate_limit(limiter)
        def test_view(request):
            return type('Response', (), {'status_code': 200})()
        
        request = request_factory.get('/')
        request.user = type('User', (), {'is_authenticated': False})()
        request.META['REMOTE_ADDR'] = '192.168.1.2'
        
        # 2 requêtes passent
        test_view(request)
        test_view(request)
        
        # La 3ème est bloquée
        response = test_view(request)
        assert response.status_code == 429


class TestAdvancedRateLimitMiddleware:
    """Tests pour le middleware avancé"""
    
    def test_allows_exempt_paths(self, request_factory):
        """Vérifie que les chemins exemptés ne sont pas limités"""
        middleware = AdvancedRateLimitMiddleware(lambda r: type('Response', (), {'status_code': 200})())
        
        request = request_factory.get('/admin/')
        request.META['REMOTE_ADDR'] = '192.168.1.1'
        
        # Faire beaucoup de requêtes
        for _ in range(300):
            response = middleware(request)
            assert response.status_code == 200
    
    def test_blocks_suspicious_user_agents(self, request_factory):
        """Vérifie que les user agents suspects sont bloqués"""
        middleware = AdvancedRateLimitMiddleware(lambda r: type('Response', (), {'status_code': 200})())
        
        request = request_factory.get('/api/v1/users/')
        request.META['REMOTE_ADDR'] = '192.168.1.1'
        request.META['HTTP_USER_AGENT'] = 'sqlmap/1.0'
        
        response = middleware(request)
        assert response.status_code == 403
    
    def test_applies_global_rate_limit(self, request_factory):
        """Vérifie que le rate limiting global est appliqué"""
        middleware = AdvancedRateLimitMiddleware(lambda r: type('Response', (), {'status_code': 200})())
        
        request = request_factory.get('/api/v1/users/')
        request.META['REMOTE_ADDR'] = '192.168.1.3'
        request.META['HTTP_USER_AGENT'] = 'Mozilla/5.0'
        
        # Faire des requêtes jusqu'à la limite (200 par minute)
        for i in range(200):
            response = middleware(request)
            assert response.status_code == 200
        
        # La 201ème doit être bloquée
        response = middleware(request)
        assert response.status_code == 429


class TestRateLimitService:
    """Tests pour le service de compatibilité"""
    
    def test_check_rate_limit_compatibility(self):
        """Vérifie la compatibilité avec l'ancien système"""
        result = RateLimitService.check_rate_limit("test_ip", action="login")
        
        assert 'is_blocked' in result
        assert 'remaining_attempts' in result
        assert result['is_blocked'] is False
    
    def test_record_attempt_success_clears_limit(self):
        """Vérifie que record_attempt avec success=True réinitialise"""
        # Faire quelques tentatives échouées
        RateLimitService.check_rate_limit("test_ip2", action="login")
        RateLimitService.check_rate_limit("test_ip2", action="login")
        
        # Enregistrer un succès
        RateLimitService.record_attempt("test_ip2", action="login", success=True)
        
        # Vérifier que le compteur est réinitialisé
        result = RateLimitService.check_rate_limit("test_ip2", action="login")
        assert result['remaining_attempts'] == 5  # Limite par défaut pour login


class TestRateLimitConfig:
    """Tests pour la configuration des limites"""
    
    def test_auth_login_config(self):
        """Vérifie la configuration pour login"""
        limiter = RateLimitConfig.AUTH_LOGIN
        assert limiter.max_requests == 5
        assert limiter.window_seconds == 60
    
    def test_auth_register_config(self):
        """Vérifie la configuration pour register"""
        limiter = RateLimitConfig.AUTH_REGISTER
        assert limiter.max_requests == 3
        assert limiter.window_seconds == 300
    
    def test_payment_config(self):
        """Vérifie la configuration pour paiements"""
        limiter = RateLimitConfig.PAYMENT
        assert limiter.max_requests == 10
        assert limiter.window_seconds == 300


@pytest.mark.django_db
class TestRateLimitIntegration:
    """Tests d'intégration du rate limiting"""
    
    def test_login_endpoint_rate_limiting(self, client):
        """Vérifie que le rate limiting fonctionne sur l'endpoint login"""
        # Faire 5 tentatives de login (limite)
        for i in range(5):
            response = client.post('/api/v1/auth/login-email', {
                'email': 'test@example.com',
                'password': 'wrongpassword'
            })
            # Peut être 401 (mauvais credentials) ou 429 (rate limit)
            assert response.status_code in [401, 429]
        
        # La 6ème devrait être bloquée par rate limit
        response = client.post('/api/v1/auth/login-email', {
            'email': 'test@example.com',
            'password': 'wrongpassword'
        })
        # Devrait être 429 maintenant
        assert response.status_code == 429
