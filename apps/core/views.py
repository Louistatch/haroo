"""
TASK-7.3: Health Check & Performance Stats endpoints

/api/v1/health/ - Vérifie DB, Redis, Celery
/api/v1/health/detailed/ - Détails complets (admin)
"""
import time
import logging
from django.db import connection
from django.core.cache import cache
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny, IsAdminUser
from rest_framework.response import Response
from rest_framework import status
from drf_spectacular.utils import extend_schema, OpenApiResponse

logger = logging.getLogger('haroo.requests')


@extend_schema(
    summary="Health Check",
    description="Vérifie l'état de santé de l'application (DB, Redis, Celery).",
    responses={
        200: OpenApiResponse(description='Service healthy'),
        503: OpenApiResponse(description='Service unhealthy'),
    },
    tags=['Monitoring'],
)
@api_view(['GET'])
@permission_classes([AllowAny])
def health_check(request):
    """
    Health check endpoint.
    Retourne 200 si tous les services sont opérationnels, 503 sinon.
    """
    checks = {}
    healthy = True

    # 1. Database check
    try:
        start = time.monotonic()
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            cursor.fetchone()
        db_time = round((time.monotonic() - start) * 1000, 2)
        checks['database'] = {'status': 'healthy', 'response_time_ms': db_time}
    except Exception as e:
        checks['database'] = {'status': 'unhealthy', 'error': str(e)}
        healthy = False

    # 2. Redis / Cache check
    try:
        start = time.monotonic()
        cache.set('health_check_ping', 'pong', 10)
        result = cache.get('health_check_ping')
        redis_time = round((time.monotonic() - start) * 1000, 2)
        if result == 'pong':
            checks['redis'] = {'status': 'healthy', 'response_time_ms': redis_time}
        else:
            checks['redis'] = {'status': 'unhealthy', 'error': 'Unexpected cache response'}
            healthy = False
    except Exception as e:
        checks['redis'] = {'status': 'unhealthy', 'error': str(e)}
        healthy = False

    # 3. Celery check (best-effort, non-blocking)
    try:
        from haroo.celery import app as celery_app
        inspector = celery_app.control.inspect(timeout=2.0)
        ping_result = inspector.ping()
        if ping_result:
            workers = list(ping_result.keys())
            checks['celery'] = {
                'status': 'healthy',
                'workers': len(workers),
            }
        else:
            checks['celery'] = {'status': 'unavailable', 'workers': 0}
            # Celery down n'est pas critique pour le health check basique
    except Exception as e:
        checks['celery'] = {'status': 'unavailable', 'error': str(e)}

    overall_status = 'healthy' if healthy else 'unhealthy'
    http_status = status.HTTP_200_OK if healthy else status.HTTP_503_SERVICE_UNAVAILABLE

    return Response({
        'status': overall_status,
        'checks': checks,
    }, status=http_status)
@api_view(['GET'])
@permission_classes([AllowAny])
def ping(request):
    """Lightweight ping for Railway healthcheck — no DB, no cache."""
    return Response({'status': 'ok'})


@api_view(['GET'])
@permission_classes([AllowAny])
def auth_debug(request):
    """Debug endpoint to test auth header parsing (no secrets exposed)."""
    auth_header = request.META.get('HTTP_AUTHORIZATION', '')
    has_token = bool(auth_header and auth_header.startswith('Bearer '))
    result = {'has_auth_header': has_token}
    if has_token:
        token = auth_header.split(' ', 1)[1]
        result['token_length'] = len(token)
        result['token_prefix'] = token[:20] + '...'
        try:
            from apps.users.services import JWTAuthService
            payload = JWTAuthService.verify_token(token, token_type='access')
            if payload:
                result['token_valid'] = True
                result['user_id'] = payload.get('user_id')
                result['user_type'] = payload.get('user_type')
            else:
                result['token_valid'] = False
                result['reason'] = 'verify_token returned None'
        except Exception as e:
            result['token_valid'] = False
            result['reason'] = str(e)
    return Response(result)


@extend_schema(
    summary="Health Check détaillé (admin)",
    description="Retourne des métriques détaillées sur l'état du système. Réservé aux administrateurs.",
    responses={
        200: OpenApiResponse(description='Détails système'),
        401: OpenApiResponse(description='Non authentifié'),
        403: OpenApiResponse(description='Non autorisé'),
    },
    tags=['Monitoring'],
)
@api_view(['GET'])
@permission_classes([IsAdminUser])
def health_check_detailed(request):
    """
    Health check détaillé avec métriques système.
    Réservé aux administrateurs.
    """
    import django
    import sys
    import os

    checks = {}

    # Database
    try:
        start = time.monotonic()
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            cursor.fetchone()
            # Nombre de connexions actives (PostgreSQL)
            cursor.execute(
                "SELECT count(*) FROM pg_stat_activity WHERE state = 'active'"
            )
            active_connections = cursor.fetchone()[0]
        db_time = round((time.monotonic() - start) * 1000, 2)
        checks['database'] = {
            'status': 'healthy',
            'response_time_ms': db_time,
            'active_connections': active_connections,
            'engine': connection.vendor,
        }
    except Exception as e:
        checks['database'] = {'status': 'unhealthy', 'error': str(e)}

    # Redis
    try:
        start = time.monotonic()
        cache.set('health_check_detailed', 'ok', 10)
        cache.get('health_check_detailed')
        redis_time = round((time.monotonic() - start) * 1000, 2)
        checks['redis'] = {
            'status': 'healthy',
            'response_time_ms': redis_time,
        }
    except Exception as e:
        checks['redis'] = {'status': 'unhealthy', 'error': str(e)}

    # Celery
    try:
        from haroo.celery import app as celery_app
        inspector = celery_app.control.inspect(timeout=2.0)
        stats = inspector.stats()
        active = inspector.active()
        checks['celery'] = {
            'status': 'healthy' if stats else 'unavailable',
            'workers': len(stats) if stats else 0,
            'active_tasks': sum(len(v) for v in active.values()) if active else 0,
        }
    except Exception as e:
        checks['celery'] = {'status': 'unavailable', 'error': str(e)}

    # System info
    system_info = {
        'python_version': sys.version.split()[0],
        'django_version': django.__version__,
        'debug_mode': os.environ.get('DEBUG', 'False'),
        'pid': os.getpid(),
    }

    return Response({
        'status': 'healthy' if all(
            c.get('status') == 'healthy'
            for c in checks.values()
            if c.get('status') != 'unavailable'
        ) else 'unhealthy',
        'checks': checks,
        'system': system_info,
    })



@extend_schema(
    summary="Assistant IA Haroo",
    description="Envoyer un message à l'assistant IA pour obtenir de l'aide sur la plateforme.",
    request={
        'application/json': {
            'type': 'object',
            'properties': {
                'message': {'type': 'string', 'description': 'Message de l\'utilisateur'},
                'context': {
                    'type': 'object',
                    'properties': {
                        'page': {'type': 'string'},
                        'user_type': {'type': 'string'},
                        'cours_titre': {'type': 'string'},
                    }
                }
            },
            'required': ['message']
        }
    },
    responses={
        200: OpenApiResponse(description='Réponse de l\'assistant'),
        400: OpenApiResponse(description='Requête invalide'),
    },
    tags=['AI Assistant'],
)
@api_view(['POST'])
@permission_classes([AllowAny])
def ai_chat(request):
    """
    Endpoint pour discuter avec l'assistant IA Haroo.
    """
    from .ai_assistant import ai_assistant
    
    message = request.data.get('message')
    if not message:
        return Response(
            {'error': 'Le champ "message" est requis'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Utiliser l'ID de session ou l'ID utilisateur
    session_id = request.session.session_key or str(request.user.id if request.user.is_authenticated else 'anonymous')
    
    # Contexte additionnel
    context = request.data.get('context', {})
    if request.user.is_authenticated:
        context['user_type'] = request.user.type if hasattr(request.user, 'type') else 'utilisateur'
    
    try:
        response_text = ai_assistant.send_message(session_id, message, context)
        return Response({
            'response': response_text,
            'session_id': session_id
        })
    except Exception as e:
        logger.error(f"Erreur AI Assistant: {str(e)}")
        return Response(
            {'error': 'Erreur lors du traitement de votre message'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@extend_schema(
    summary="Réinitialiser la session de chat IA",
    description="Efface l'historique de conversation avec l'assistant IA.",
    responses={
        200: OpenApiResponse(description='Session réinitialisée'),
    },
    tags=['AI Assistant'],
)
@api_view(['POST'])
@permission_classes([AllowAny])
def ai_chat_reset(request):
    """
    Réinitialiser la session de chat avec l'assistant IA.
    """
    from .ai_assistant import ai_assistant
    
    session_id = request.session.session_key or str(request.user.id if request.user.is_authenticated else 'anonymous')
    ai_assistant.clear_session(session_id)
    
    return Response({'message': 'Session de chat réinitialisée'})
