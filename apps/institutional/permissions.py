"""
Permissions pour le dashboard institutionnel
Exigences: 25.1, 25.2
"""
from rest_framework import permissions


class IsInstitutionalUser(permissions.BasePermission):
    """
    Permission pour vérifier que l'utilisateur est un compte institutionnel
    avec 2FA activé
    
    Exigences: 25.1, 25.2
    """
    
    message = "Accès réservé aux comptes institutionnels avec authentification 2FA activée"
    
    def has_permission(self, request, view):
        """
        Vérifie que l'utilisateur est authentifié, est de type INSTITUTION,
        et a activé l'authentification à deux facteurs
        """
        # Vérifier que l'utilisateur est authentifié
        if not request.user or not request.user.is_authenticated:
            return False
        
        # Vérifier que l'utilisateur est de type INSTITUTION
        if request.user.user_type != 'INSTITUTION':
            return False
        
        # Vérifier que le 2FA est activé (Exigence 25.2)
        if not request.user.two_factor_enabled:
            self.message = "L'authentification à deux facteurs doit être activée pour accéder au dashboard institutionnel"
            return False
        
        # Vérifier que le profil institution existe
        if not hasattr(request.user, 'institution_profile'):
            return False
        
        return True
