"""
Signaux Django pour invalidation automatique du cache

Ces signaux invalident automatiquement le cache Redis lorsque
les modèles sont modifiés, garantissant la cohérence des données.
"""
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from apps.core.performance import CacheManager
from .models import User, AgronomeProfile, ExploitantProfile, DocumentJustificatif
import logging

logger = logging.getLogger(__name__)


@receiver(post_save, sender=User)
def invalidate_user_cache_on_save(sender, instance, created, **kwargs):
    """
    Invalide le cache utilisateur après création ou modification
    
    Déclenché après:
    - Création d'un nouvel utilisateur
    - Modification du profil utilisateur
    - Changement de statut (actif/inactif)
    """
    try:
        CacheManager.invalidate_user(instance.id)
        
        if not created:
            logger.debug(f"Cache invalidé pour l'utilisateur {instance.id}")
    except Exception as e:
        logger.error(f"Erreur lors de l'invalidation du cache utilisateur: {e}")


@receiver(post_save, sender=AgronomeProfile)
def invalidate_agronomist_cache_on_save(sender, instance, created, **kwargs):
    """
    Invalide le cache agronome après création ou modification
    
    Déclenché après:
    - Validation/rejet d'un agronome
    - Modification du profil agronome
    - Changement de spécialisations
    """
    try:
        # Invalider le cache de l'agronome spécifique
        CacheManager.invalidate(f'agronomist_details:{instance.id}')
        CacheManager.invalidate(f'agronomist_public_detail:{instance.user.id}')
        
        # Invalider la liste des agronomes
        CacheManager.invalidate_agronomist_list()
        
        # Invalider aussi le cache utilisateur
        CacheManager.invalidate_user(instance.user.id)
        
        if not created:
            logger.debug(f"Cache invalidé pour l'agronome {instance.id}")
    except Exception as e:
        logger.error(f"Erreur lors de l'invalidation du cache agronome: {e}")


@receiver(post_delete, sender=AgronomeProfile)
def invalidate_agronomist_cache_on_delete(sender, instance, **kwargs):
    """
    Invalide le cache agronome après suppression
    """
    try:
        CacheManager.invalidate(f'agronomist_details:{instance.id}')
        CacheManager.invalidate(f'agronomist_public_detail:{instance.user.id}')
        CacheManager.invalidate_agronomist_list()
        
        logger.debug(f"Cache invalidé après suppression de l'agronome {instance.id}")
    except Exception as e:
        logger.error(f"Erreur lors de l'invalidation du cache agronome: {e}")


@receiver(post_save, sender=ExploitantProfile)
def invalidate_exploitant_cache_on_save(sender, instance, created, **kwargs):
    """
    Invalide le cache exploitant après création ou modification
    
    Déclenché après:
    - Vérification d'une exploitation
    - Modification du profil exploitant
    - Changement de statut de vérification
    """
    try:
        # Invalider le cache de l'exploitant spécifique
        CacheManager.invalidate(f'exploitant_details:{instance.id}')
        
        # Invalider le cache utilisateur
        CacheManager.invalidate_user(instance.user.id)
        
        if not created:
            logger.debug(f"Cache invalidé pour l'exploitant {instance.id}")
    except Exception as e:
        logger.error(f"Erreur lors de l'invalidation du cache exploitant: {e}")


@receiver(post_delete, sender=ExploitantProfile)
def invalidate_exploitant_cache_on_delete(sender, instance, **kwargs):
    """
    Invalide le cache exploitant après suppression
    """
    try:
        CacheManager.invalidate(f'exploitant_details:{instance.id}')
        
        logger.debug(f"Cache invalidé après suppression de l'exploitant {instance.id}")
    except Exception as e:
        logger.error(f"Erreur lors de l'invalidation du cache exploitant: {e}")


@receiver(post_save, sender=DocumentJustificatif)
def invalidate_document_cache_on_save(sender, instance, created, **kwargs):
    """
    Invalide le cache après ajout/modification d'un document
    
    Déclenché après:
    - Upload d'un nouveau document
    - Validation/rejet d'un document
    """
    try:
        # Invalider le cache de l'agronome associé
        if hasattr(instance, 'agronome_profile') and instance.agronome_profile:
            CacheManager.invalidate(f'agronomist_details:{instance.agronome_profile.id}')
            CacheManager.invalidate(f'agronomist_public_detail:{instance.agronome_profile.user.id}')
            CacheManager.invalidate_agronomist_list()
        
        if not created:
            logger.debug(f"Cache invalidé après modification du document {instance.id}")
    except Exception as e:
        logger.error(f"Erreur lors de l'invalidation du cache document: {e}")


@receiver(post_delete, sender=DocumentJustificatif)
def invalidate_document_cache_on_delete(sender, instance, **kwargs):
    """
    Invalide le cache après suppression d'un document
    """
    try:
        if hasattr(instance, 'agronome_profile') and instance.agronome_profile:
            CacheManager.invalidate(f'agronomist_details:{instance.agronome_profile.id}')
            CacheManager.invalidate(f'agronomist_public_detail:{instance.agronome_profile.user.id}')
            CacheManager.invalidate_agronomist_list()
        
        logger.debug(f"Cache invalidé après suppression du document {instance.id}")
    except Exception as e:
        logger.error(f"Erreur lors de l'invalidation du cache document: {e}")
