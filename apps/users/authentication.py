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
        Authentifie la requête en vérifiant le token JWT
        
        Returns:
            tuple (user, token) si authentification réussie
            None si pas de token fourni
            
        Raises:
            AuthenticationFailed si le token est invalide
        """
        auth_header = request.META.get('HTTP_AUTHORIZATION', '')
        
        if not auth_header:
            return None
        
        try:
            # Extraire le token
            parts = auth_header.split()
            
            if len(parts) != 2:
                raise AuthenticationFailed('Format d\'en-tête Authorization invalide')
            
            if parts[0] != self.keyword:
                raise AuthenticationFailed('Type d\'authentification non supporté')
            
            token = parts[1]
            
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
            raise AuthenticationFailed(str(e))
    
    def authenticate_header(self, request):
        """
        Retourne la chaîne à utiliser dans l'en-tête WWW-Authenticate
        """
        return self.keyword
