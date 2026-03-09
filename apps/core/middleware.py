"""
TASK-7.2: Middleware de logging structuré

RequestLoggingMiddleware - Log chaque requête HTTP en JSON avec:
- user_id, IP, method, path, status_code, duration
- Logs séparés: app, errors, security
"""
import time
import logging
import json
from django.utils.deprecation import MiddlewareMixin


logger = logging.getLogger('haroo.requests')
security_logger = logging.getLogger('haroo.security')


class RequestLoggingMiddleware(MiddlewareMixin):
    """
    Middleware qui log chaque requête HTTP avec métadonnées structurées.
    
    Logs:
    - Toutes les requêtes dans haroo.requests
    - Erreurs 4xx/5xx dans haroo.errors
    - Événements de sécurité dans haroo.security
    """

    # Paths à exclure du logging (health checks, static, etc.)
    EXCLUDED_PATHS = [
        '/api/v1/health/',
        '/static/',
        '/media/',
        '/favicon.ico',
    ]

    # Paths sensibles (login, register, password) - ne pas logger le body
    SENSITIVE_PATHS = [
        '/login', '/register', '/password', '/token', '/2fa',
        '/cookies',
    ]

    def process_request(self, request):
        """Enregistre le timestamp de début"""
        request._start_time = time.monotonic()

    def process_response(self, request, response):
        """Log la requête complète avec durée et métadonnées"""
        # Ignorer les paths exclus
        path = request.path
        if any(path.startswith(ep) for ep in self.EXCLUDED_PATHS):
            return response

        duration_ms = 0
        if hasattr(request, '_start_time'):
            duration_ms = round((time.monotonic() - request._start_time) * 1000, 2)

        # Construire le log structuré
        user_id = None
        if hasattr(request, 'user') and request.user.is_authenticated:
            user_id = request.user.id

        log_data = {
            'method': request.method,
            'path': path,
            'status_code': response.status_code,
            'duration_ms': duration_ms,
            'user_id': user_id,
            'ip': self._get_client_ip(request),
            'user_agent': request.META.get('HTTP_USER_AGENT', '')[:200],
            'content_length': response.get('Content-Length', 0),
        }

        # Query params (sans données sensibles)
        if request.GET:
            log_data['query_params'] = {
                k: v for k, v in request.GET.items()
                if 'password' not in k.lower() and 'token' not in k.lower()
            }

        # Log selon le status code
        if response.status_code >= 500:
            logging.getLogger('haroo.errors').error(
                'Server error: %(method)s %(path)s %(status_code)s',
                log_data,
                extra=log_data,
            )
        elif response.status_code >= 400:
            logger.warning(
                'Client error: %(method)s %(path)s %(status_code)s',
                log_data,
                extra=log_data,
            )
        elif duration_ms > 1000:
            logger.warning(
                'Slow request: %(method)s %(path)s %(duration_ms)sms',
                log_data,
                extra=log_data,
            )
        else:
            logger.info(
                '%(method)s %(path)s %(status_code)s %(duration_ms)sms',
                log_data,
                extra=log_data,
            )

        # Log de sécurité pour les tentatives de login échouées
        if response.status_code == 401 and any(
            s in path for s in ['/login', '/token', '/2fa']
        ):
            security_logger.warning(
                'Failed auth attempt: %(method)s %(path)s from %(ip)s',
                log_data,
                extra=log_data,
            )

        # Log de sécurité pour rate limiting (429)
        if response.status_code == 429:
            security_logger.warning(
                'Rate limited: %(method)s %(path)s from %(ip)s',
                log_data,
                extra=log_data,
            )

        return response

    def _get_client_ip(self, request):
        """Récupère l'IP réelle du client"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            return x_forwarded_for.split(',')[0].strip()
        return request.META.get('REMOTE_ADDR', '')
