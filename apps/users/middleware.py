"""
Middleware pour le rate limiting et la sécurité

Note: Le middleware RateLimitMiddleware a été remplacé par AdvancedRateLimitMiddleware
dans apps/core/rate_limiting.py pour une meilleure performance et fonctionnalités.

Cette version est conservée pour compatibilité mais n'est plus utilisée.
"""
from django.http import JsonResponse
from django.core.cache import cache
from datetime import datetime, timedelta


class RateLimitMiddleware:
    """
    Middleware pour limiter le nombre de requêtes par IP
    
    DEPRECATED: Utilisez AdvancedRateLimitMiddleware de apps/core/rate_limiting.py
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
        self.rate_limit = 100  # Nombre de requêtes
        self.time_window = 60  # Fenêtre de temps en secondes (1 minute)
    
    def __call__(self, request):
        # Récupérer l'IP du client
        ip = self.get_client_ip(request)
        
        # Vérifier le rate limit pour les endpoints sensibles
        if self.is_sensitive_endpoint(request.path):
            if not self.check_rate_limit(ip):
                return JsonResponse({
                    'error': 'Trop de requêtes. Veuillez réessayer plus tard.'
                }, status=429)
        
        response = self.get_response(request)
        return response
    
    def get_client_ip(self, request):
        """Récupère l'adresse IP du client"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip
    
    def is_sensitive_endpoint(self, path):
        """Vérifie si l'endpoint est sensible"""
        sensitive_paths = [
            '/api/v1/auth/login',
            '/api/v1/auth/register',
            '/api/v1/auth/verify-sms',
        ]
        return any(path.startswith(p) for p in sensitive_paths)
    
    def check_rate_limit(self, ip):
        """Vérifie si l'IP a dépassé la limite"""
        cache_key = f'rate_limit_global:{ip}'
        requests = cache.get(cache_key, [])
        
        # Filtrer les requêtes dans la fenêtre de temps
        now = datetime.utcnow()
        cutoff = now - timedelta(seconds=self.time_window)
        requests = [r for r in requests if datetime.fromisoformat(r) > cutoff]
        
        # Vérifier la limite
        if len(requests) >= self.rate_limit:
            return False
        
        # Ajouter la requête actuelle
        requests.append(now.isoformat())
        cache.set(cache_key, requests, timeout=self.time_window)
        
        return True


class SecurityHeadersMiddleware:
    """
    Middleware pour ajouter des en-têtes de sécurité
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        response = self.get_response(request)
        
        # Ajouter les en-têtes de sécurité
        response['X-Content-Type-Options'] = 'nosniff'
        response['X-Frame-Options'] = 'DENY'
        response['X-XSS-Protection'] = '1; mode=block'
        response['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains'
        
        return response



class Enforce2FAMiddleware:
    """
    Middleware pour forcer l'activation du 2FA pour les comptes institutionnels
    
    Exigences: 25.2
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
        # Endpoints exemptés de la vérification 2FA
        self.exempt_paths = [
            '/api/v1/auth/login',
            '/api/v1/auth/register',
            '/api/v1/auth/verify-sms',
            '/api/v1/auth/resend-sms',
            '/api/v1/auth/refresh-token',
            '/api/v1/auth/2fa/',  # Tous les endpoints 2FA
            '/admin/',
            '/static/',
            '/media/',
        ]
    
    def __call__(self, request):
        # Vérifier si l'utilisateur est authentifié
        if hasattr(request, 'user') and request.user.is_authenticated:
            # Vérifier si c'est un compte institutionnel
            if request.user.user_type == 'INSTITUTION':
                # Vérifier si le 2FA est activé
                if not request.user.two_factor_enabled:
                    # Vérifier si l'endpoint est exempté
                    if not self.is_exempt_path(request.path):
                        return JsonResponse({
                            'error': 'Le 2FA est obligatoire pour les comptes institutionnels.',
                            'message': 'Veuillez activer le 2FA avant d\'accéder à cette ressource.',
                            'action_required': 'setup_2fa',
                            'setup_url': '/api/v1/auth/2fa/setup'
                        }, status=403)
        
        response = self.get_response(request)
        return response
    
    def is_exempt_path(self, path):
        """Vérifie si le chemin est exempté de la vérification 2FA"""
        return any(path.startswith(exempt) for exempt in self.exempt_paths)


class SessionActivityMiddleware:
    """
    Middleware pour mettre à jour l'activité de la session à chaque requête
    
    Exigences: 40.1
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        # Vérifier si l'utilisateur est authentifié
        if hasattr(request, 'user') and request.user.is_authenticated:
            # Récupérer le token depuis l'en-tête Authorization
            auth_header = request.META.get('HTTP_AUTHORIZATION', '')
            
            if auth_header and auth_header.startswith('Bearer '):
                token = auth_header.split(' ')[1]
                
                # Mettre à jour l'activité de la session
                from apps.users.session_service import SessionManagementService
                SessionManagementService.update_session_activity(request.user.id, token)
        
        response = self.get_response(request)
        return response

