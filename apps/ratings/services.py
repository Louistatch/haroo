"""
Services pour le système de notation
"""
from django.db.models import Avg, Count
from django.contrib.auth import get_user_model
from .models import Notation

User = get_user_model()


class ReputationCalculator:
    """
    Service pour calculer les notes moyennes et gérer la réputation
    Exigence: 27.3, 27.6
    """
    
    @staticmethod
    def update_user_rating(user):
        """
        Mettre à jour la note moyenne d'un utilisateur
        Exigence: 27.3 - Calculer la note moyenne avec deux décimales
        """
        # Calculer la note moyenne et le nombre d'avis
        stats = Notation.objects.filter(
            note=user,
            statut='PUBLIE'
        ).aggregate(
            moyenne=Avg('note_valeur'),
            nombre=Count('id')
        )
        
        moyenne = stats['moyenne'] or 0.0
        nombre = stats['nombre'] or 0
        
        # Arrondir à 2 décimales (Exigence 27.3)
        moyenne = round(moyenne, 2)
        
        # Mettre à jour le profil approprié
        if hasattr(user, 'agronome_profile'):
            user.agronome_profile.note_moyenne = moyenne
            user.agronome_profile.nombre_avis = nombre
            user.agronome_profile.save()
        
        if hasattr(user, 'ouvrier_profile'):
            user.ouvrier_profile.note_moyenne = moyenne
            user.ouvrier_profile.nombre_avis = nombre
            user.ouvrier_profile.save()
        
        # Vérifier si une alerte qualité doit être déclenchée
        QualityAlertService.check_quality_alert(user, moyenne, nombre)
        
        return moyenne, nombre
    
    @staticmethod
    def get_user_rating(user):
        """Obtenir la note moyenne d'un utilisateur"""
        if hasattr(user, 'agronome_profile'):
            return {
                'note_moyenne': float(user.agronome_profile.note_moyenne),
                'nombre_avis': user.agronome_profile.nombre_avis
            }
        
        if hasattr(user, 'ouvrier_profile'):
            return {
                'note_moyenne': float(user.ouvrier_profile.note_moyenne),
                'nombre_avis': user.ouvrier_profile.nombre_avis
            }
        
        return {
            'note_moyenne': 0.0,
            'nombre_avis': 0
        }


class QualityAlertService:
    """
    Service pour gérer les alertes qualité
    Exigence: 27.6
    """
    
    QUALITY_THRESHOLD = 2.5
    MIN_REVIEWS = 10
    
    @staticmethod
    def check_quality_alert(user, moyenne, nombre_avis):
        """
        Vérifier si une alerte qualité doit être déclenchée
        Exigence: 27.6 - Alerte si moyenne < 2.5 sur ≥ 10 avis
        """
        if nombre_avis >= QualityAlertService.MIN_REVIEWS and moyenne < QualityAlertService.QUALITY_THRESHOLD:
            # TODO: Implémenter le système de notification pour envoyer l'alerte
            # Pour l'instant, on log juste l'alerte
            print(f"ALERTE QUALITÉ: {user.get_full_name()} - Note moyenne: {moyenne} sur {nombre_avis} avis")
            return True
        
        return False
    
    @staticmethod
    def get_users_with_quality_alerts():
        """Obtenir la liste des utilisateurs avec alerte qualité"""
        from apps.users.models import AgronomeProfile, OuvrierProfile
        
        alerts = []
        
        # Vérifier les agronomes
        agronomes = AgronomeProfile.objects.filter(
            nombre_avis__gte=QualityAlertService.MIN_REVIEWS,
            note_moyenne__lt=QualityAlertService.QUALITY_THRESHOLD
        ).select_related('user')
        
        for agronome in agronomes:
            alerts.append({
                'user': agronome.user,
                'type': 'agronome',
                'note_moyenne': float(agronome.note_moyenne),
                'nombre_avis': agronome.nombre_avis
            })
        
        # Vérifier les ouvriers
        ouvriers = OuvrierProfile.objects.filter(
            nombre_avis__gte=QualityAlertService.MIN_REVIEWS,
            note_moyenne__lt=QualityAlertService.QUALITY_THRESHOLD
        ).select_related('user')
        
        for ouvrier in ouvriers:
            alerts.append({
                'user': ouvrier.user,
                'type': 'ouvrier',
                'note_moyenne': float(ouvrier.note_moyenne),
                'nombre_avis': ouvrier.nombre_avis
            })
        
        return alerts


class ModerationService:
    """
    Service pour la modération des avis
    Exigence: 27.5
    """
    
    @staticmethod
    def get_moderation_queue():
        """
        Obtenir la file d'attente de modération
        Exigence: 27.5 - Modération des avis signalés
        """
        return Notation.objects.filter(
            statut='SIGNALE'
        ).select_related(
            'notateur', 'note', 'mission'
        ).prefetch_related(
            'signalements'
        ).order_by('-nombre_signalements', '-created_at')
    
    @staticmethod
    def approve_notation(notation):
        """Approuver une notation signalée"""
        notation.statut = 'PUBLIE'
        notation.save()
        
        # Marquer tous les signalements comme traités
        notation.signalements.update(traite=True)
        
        return notation
    
    @staticmethod
    def reject_notation(notation):
        """Rejeter une notation"""
        notation.statut = 'REJETE'
        notation.save()
        
        # Marquer tous les signalements comme traités
        notation.signalements.update(traite=True)
        
        # Recalculer la note moyenne de l'utilisateur
        ReputationCalculator.update_user_rating(notation.note)
        
        return notation
    
    @staticmethod
    def moderate_notation(notation, action='approve'):
        """Modérer une notation (approuver ou rejeter)"""
        if action == 'approve':
            return ModerationService.approve_notation(notation)
        elif action == 'reject':
            return ModerationService.reject_notation(notation)
        else:
            raise ValueError(f"Action de modération invalide: {action}")
