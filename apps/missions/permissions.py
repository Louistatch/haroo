"""
Permissions pour la gestion des missions
"""
from rest_framework import permissions


class IsExploitantVerifie(permissions.BasePermission):
    """
    Permission pour vérifier que l'utilisateur est un exploitant vérifié
    """
    message = "Vous devez être un exploitant vérifié pour créer une mission"
    
    def has_permission(self, request, view):
        # Vérifier que l'utilisateur a un profil d'exploitant
        if not hasattr(request.user, 'exploitant_profile'):
            return False
        
        # Vérifier que l'exploitant est vérifié
        return request.user.exploitant_profile.statut_verification == 'VERIFIE'


class IsAgronomeValide(permissions.BasePermission):
    """
    Permission pour vérifier que l'utilisateur est un agronome validé
    """
    message = "Vous devez être un agronome validé pour accepter une mission"
    
    def has_permission(self, request, view):
        # Vérifier que l'utilisateur a un profil d'agronome
        if not hasattr(request.user, 'agronome_profile'):
            return False
        
        # Vérifier que l'agronome est validé
        return request.user.agronome_profile.statut_validation == 'VALIDE'


class IsMissionParticipant(permissions.BasePermission):
    """
    Permission pour vérifier que l'utilisateur est participant de la mission
    (exploitant ou agronome)
    """
    message = "Vous devez être participant de cette mission"
    
    def has_object_permission(self, request, view, obj):
        # Vérifier que l'utilisateur est soit l'exploitant soit l'agronome
        return obj.exploitant == request.user or obj.agronome == request.user
