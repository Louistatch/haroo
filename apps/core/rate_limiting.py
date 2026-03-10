"""
Rate Limiting avancé avec sliding window et décorateurs

Implémente un système de rate limiting robuste avec:
- Sliding window pour comptage précis
- Décorateurs pour faciliter l'utilisation
- Support de différents niveaux (IP, user, endpoint)
- Messages d'erreur clairs avec retry_after
"""
from functools import wraps
from typing import Optional, Dict, Any, Callable
from datetime import datetime, timedelta
from django.core.cache import cache
from django.http import JsonResponse
from rest_framework import status
import time


class SlidingWindowRateLimiter:
    """
    Rate limiter avec sliding window pour un comptage précis
    
    Contrairement au fixed window, le sliding window compte les requêtes
    dans une fenêtre glissante, évitant les pics en début de période.
    """
    
    def __init__(self, max_requests: int, window_seconds: int, key_prefix: str = "rate_limit"):
        """
        Args:
            max_requests: Nombre maximum de requêtes autorisées
            window_seconds: Durée de la fenêtre en secondes
            key_prefix: Préfixe pour les clés Redis
        """
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.key_prefix = key_prefix
    
    def _get_cache_key(self, identifier: str) -> str:
        """Génère la clé de cache pour un identifiant"""
        return f"{self.key_prefix}:{identifier}"
    
    def is_allowed(self, identifier: str) -> tuple[bool, Dict[str, Any]]:
        """
        Vérifie si une requête est autorisée
        
        Args:
            identifier: Identifiant unique (IP, user_id, etc.)
            
        Returns:
            Tuple (is_allowed, info_dict)
            info_dict contient: remaining, reset_at, retry_after
        """
        cache_key = self._get_cache_key(identifier)
        now = time.time()
        window_start = now - self.window_seconds
        
        # Récupérer les timestamps des requêtes
        requests = cache.get(cache_key, [])
        
        # Filtrer les requêtes dans la fenêtre
        requests = [req_time for req_time in requests if req_time > window_start]
        
        # Vérifier la limite
        is_allowed = len(requests) < self.max_requests
        
        if is_allowed:
            # Ajouter la requête actuelle
            requests.append(now)
            cache.set(cache_key, requests, timeout=self.window_seconds + 10)
        
        # Calculer les informations
        remaining = max(0, self.max_requests - len(requests))
        oldest_request = min(requests) if requests else now
        reset_at = oldest_request + self.window_seconds
        retry_after = max(0, int(reset_at - now)) if not is_allowed else 0
        
        info = {
            'remaining': remaining,
            'limit': self.max_requests,
            'reset_at': datetime.fromtimestamp(reset_at).isoformat(),
            'retry_after': retry_after,
            'window_seconds': self.window_seconds
        }
        
        return is_allowed, info


class RateLimitConfig:
    """Configuration des limites de rate limiting par endpoint"""
    
    # Endpoints d'authentification (très sensibles)
    AUTH_LOGIN = SlidingWindowRateLimiter(
        max_requests=5,
        window_seconds=60,  # 5 requêtes par minute
        key_prefix="rate_limit:auth:login"
    )
    
    AUTH_REGISTER = SlidingWindowRateLimiter(
        max_requests=3,
        window_seconds=300,  # 3 requêtes par 5 minutes
        key_prefix="rate_limit:auth:register"
    )
    
    AUTH_VERIFY = SlidingWindowRateLimiter(
        max_requests=10,
        window_seconds=60,  # 10 requêtes par minute
        key_prefix="rate_limit:auth:verify"
    )
    
    # Endpoints API généraux
    API_READ = SlidingWindowRateLimiter(
        max_requests=100,
        window_seconds=60,  # 100 requêtes par minute
        key_prefix="rate_limit:api:read"
    )
    
    API_WRITE = SlidingWindowRateLimiter(
        max_requests=30,
        window_seconds=60,  # 30 requêtes par minute
        key_prefix="rate_limit:api:write"
    )
    
    # Endpoints de paiement (très sensibles)
    PAYMENT = SlidingWindowRateLimiter(
        max_requests=10,
        window_seconds=300,  # 10 requêtes par 5 minutes
        key_prefix="rate_limit:payment"
    )


def get_client_identifier(request) -> str:
    """
    Récupère l'identifiant du client (IP ou user_id)
    
    Priorité:
    1. User ID si authentifié
    2. IP address
    """
    if hasattr(request, 'user') and request.user.is_authenticated:
        return f"user:{request.user.id}"
    
    # Récupérer l'IP
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0].strip()
    else:
        ip = request.META.get('REMOTE_ADDR', 'unknown')
    
    return f"ip:{ip}"


def rate_limit(limiter: SlidingWindowRateLimiter):
    """
    Décorateur pour appliquer le rate limiting à une vue
    
    Usage:
        @rate_limit(RateLimitConfig.AUTH_LOGIN)
        @api_view(['POST'])
        def login_view(request):
            ...
    """
    def decorator(view_func: Callable) -> Callable:
        @wraps(view_func)
        def wrapped_view(request, *args, **kwargs):
            identifier = get_client_identifier(request)
            is_allowed, info = limiter.is_allowed(identifier)
            
            if not is_allowed:
                return JsonResponse({
                    'error': 'Trop de requêtes',
                    'message': f'Limite de {info["limit"]} requêtes par {info["window_seconds"]} secondes atteinte.',
                    'retry_after': info['retry_after'],
                    'reset_at': info['reset_at']
                }, status=status.HTTP_429_TOO_MANY_REQUESTS)
            
            # Ajouter les headers de rate limiting
            response = view_func(request, *args, **kwargs)
            
            if hasattr(response, '__setitem__'):
                response['X-RateLimit-Limit'] = str(info['limit'])
                response['X-RateLimit-Remaining'] = str(info['remaining'])
                response['X-RateLimit-Reset'] = info['reset_at']
            
            return response
        
        return wrapped_view
    return decorator


class AdvancedRateLimitMiddleware:
    """
    Middleware de rate limiting avancé avec détection d'abus
    
    Fonctionnalités:
    - Rate limiting global par IP
    - Détection de patterns suspects
    - Blocage automatique des user agents malveillants
    - Logging des tentatives d'abus
    """
    
    # User agents suspects à bloquer
    BLOCKED_USER_AGENTS = [
        'bot', 'crawler', 'spider', 'scraper',
        'curl', 'wget', 'python-requests',
        'masscan', 'nmap', 'nikto', 'sqlmap'
    ]
    
    # Endpoints exemptés du rate limiting global
    EXEMPT_PATHS = [
        '/admin/',
        '/static/',
        '/media/',
        '/api/v1/health/',
        '/api/v1/ping/',
    ]
    
    def __init__(self, get_response):
        self.get_response = get_response
        self.global_limiter = SlidingWindowRateLimiter(
            max_requests=200,
            window_seconds=60,  # 200 requêtes par minute par IP
            key_prefix="rate_limit:global"
        )
    
    def __call__(self, request):
        # Vérifier si l'endpoint est exempté
        if self.is_exempt_path(request.path):
            return self.get_response(request)
        
        # Bloquer les user agents suspects
        if self.is_blocked_user_agent(request):
            return JsonResponse({
                'error': 'Accès refusé',
                'message': 'Votre user agent est bloqué.'
            }, status=status.HTTP_403_FORBIDDEN)
        
        # Appliquer le rate limiting global
        identifier = get_client_identifier(request)
        is_allowed, info = self.global_limiter.is_allowed(identifier)
        
        if not is_allowed:
            # Logger la tentative d'abus
            self.log_rate_limit_exceeded(request, identifier, info)
            
            return JsonResponse({
                'error': 'Trop de requêtes',
                'message': 'Limite globale de requêtes atteinte.',
                'retry_after': info['retry_after'],
                'reset_at': info['reset_at']
            }, status=status.HTTP_429_TOO_MANY_REQUESTS)
        
        response = self.get_response(request)
        
        # Ajouter les headers de rate limiting
        if hasattr(response, '__setitem__'):
            response['X-RateLimit-Limit'] = str(info['limit'])
            response['X-RateLimit-Remaining'] = str(info['remaining'])
            response['X-RateLimit-Reset'] = info['reset_at']
        
        return response
    
    def is_exempt_path(self, path: str) -> bool:
        """Vérifie si le chemin est exempté"""
        return any(path.startswith(exempt) for exempt in self.EXEMPT_PATHS)
    
    def is_blocked_user_agent(self, request) -> bool:
        """Vérifie si le user agent est bloqué"""
        user_agent = request.META.get('HTTP_USER_AGENT', '').lower()
        return any(blocked in user_agent for blocked in self.BLOCKED_USER_AGENTS)
    
    def log_rate_limit_exceeded(self, request, identifier: str, info: Dict[str, Any]):
        """Log les tentatives d'abus"""
        import logging
        logger = logging.getLogger('security')
        
        logger.warning(
            f"Rate limit exceeded: {identifier} | "
            f"Path: {request.path} | "
            f"Method: {request.method} | "
            f"User-Agent: {request.META.get('HTTP_USER_AGENT', 'unknown')} | "
            f"Retry after: {info['retry_after']}s"
        )


# Helpers pour compatibilité avec l'ancien système
class RateLimitService:
    """
    Service de compatibilité avec l'ancien système de rate limiting
    
    Maintient l'API existante tout en utilisant le nouveau système
    """
    
    @staticmethod
    def check_rate_limit(identifier: str, action: str = 'login') -> Dict[str, Any]:
        """
        Vérifie le rate limit (compatibilité)
        
        Args:
            identifier: IP ou identifiant utilisateur
            action: Type d'action ('login', 'register', etc.)
            
        Returns:
            Dict avec is_blocked, remaining_attempts, blocked_until
        """
        # Mapper les actions aux limiters
        limiter_map = {
            'login': RateLimitConfig.AUTH_LOGIN,
            'register': RateLimitConfig.AUTH_REGISTER,
            'verify': RateLimitConfig.AUTH_VERIFY,
            'payment': RateLimitConfig.PAYMENT,
        }
        
        limiter = limiter_map.get(action, RateLimitConfig.API_READ)
        is_allowed, info = limiter.is_allowed(identifier)
        
        return {
            'is_blocked': not is_allowed,
            'remaining_attempts': info['remaining'],
            'blocked_until': info['reset_at'] if not is_allowed else None,
            'retry_after': info['retry_after']
        }
    
    @staticmethod
    def record_attempt(identifier: str, action: str = 'login', success: bool = False):
        """
        Enregistre une tentative (compatibilité)
        
        Note: Le nouveau système enregistre automatiquement via is_allowed()
        Cette méthode est conservée pour compatibilité mais ne fait rien
        car le sliding window gère automatiquement les tentatives.
        """
        if success:
            # Réinitialiser le compteur en cas de succès
            limiter_map = {
                'login': RateLimitConfig.AUTH_LOGIN,
                'register': RateLimitConfig.AUTH_REGISTER,
                'verify': RateLimitConfig.AUTH_VERIFY,
                'payment': RateLimitConfig.PAYMENT,
            }
            
            limiter = limiter_map.get(action, RateLimitConfig.API_READ)
            cache_key = limiter._get_cache_key(identifier)
            cache.delete(cache_key)
