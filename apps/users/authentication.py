"""
Backend d'authentification JWT personnalisé
"""
from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed
from django.contrib.auth import get_user_model

from .services import JWTAuthService

User = get_user_model()


class JWTAuthentication(BaseAuthentication):
    """
    Authentification basée sur JWT
    
    Les clients doivent s'authentifier en incluant le token dans l'en-tête:
    Authorization: Bearer <token>
    """
    
    keyword = 'Bearer'
    
    def authenticate(self, request):
        """
        Authentifie la requête en vérifiant le token JWT (Header ou Cookie)
        
        Returns:
            tuple (user, token) si authentification réussie
            None si pas de token fourni
            
        Raises:
            AuthenticationFailed si le token est invalide
        """
        # Essayer d'abord l'en-tête Authorization
        auth_header = request.META.get('HTTP_AUTHORIZATION', '')
        token = None
        
        if auth_header:
            parts = auth_header.split()
            if len(parts) == 2 and parts[0] == self.keyword:
                token = parts[1]
        
        # Si pas de header, essayer le cookie
        if not token:
            token = request.COOKIES.get('access_token')
        
        if not token:
            return None
        
        try:
            # Vérifier le token
            payload = JWTAuthService.verify_token(token, token_type='access')
            
            if not payload:
                raise AuthenticationFailed('Token invalide ou expiré')
            
            # Récupérer l'utilisateur
            try:
                user = User.objects.get(id=payload['user_id'])
            except User.DoesNotExist:
                raise AuthenticationFailed('Utilisateur non trouvé')
            
            if not user.is_active:
                raise AuthenticationFailed('Compte utilisateur désactivé')
            
            return (user, token)
            
        except Exception as e:
            if 'invalide' in str(e).lower() or 'expiré' in str(e).lower():
                raise AuthenticationFailed(str(e))
            raise AuthenticationFailed('Token invalide ou expiré')
    
    def authenticate_header(self, request):
        """
        Retourne la chaîne à utiliser dans l'en-tête WWW-Authenticate
        """
        return self.keyword
