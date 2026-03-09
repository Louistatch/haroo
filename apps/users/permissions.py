"""
Permissions personnalisées pour Haroo.
Système de vérification strict : les utilisateurs non vérifiés
ne peuvent pas accéder aux fonctionnalités sensibles.
"""
from rest_framework.permissions import BasePermission


class IsVerifiedUser(BasePermission):
    """
    Autorise uniquement les utilisateurs dont le profil est vérifié/validé.
    - EXPLOITANT : statut_verification == 'VERIFIE'
    - AGRONOME   : statut_validation == 'VALIDE'
    - OUVRIER    : phone_verified == True (pas de profil à valider)
    - ACHETEUR   : phone_verified == True
    - INSTITUTION: toujours autorisé (validé manuellement par admin)
    - ADMIN      : toujours autorisé
    """
    message = "Votre compte doit être vérifié pour accéder à cette fonctionnalité."

    def has_permission(self, request, view):
        user = request.user
        if not user or not user.is_authenticated:
            return False

        if user.user_type in ('ADMIN', 'INSTITUTION'):
            return True

        if user.user_type == 'EXPLOITANT':
            profile = getattr(user, 'exploitant_profile', None)
            return profile is not None and profile.statut_verification == 'VERIFIE'

        if user.user_type == 'AGRONOME':
            profile = getattr(user, 'agronome_profile', None)
            return profile is not None and profile.statut_validation == 'VALIDE'

        # Ouvrier et Acheteur : vérification téléphone suffit
        return user.phone_verified


def get_verification_status(user):
    """
    Retourne un dict décrivant le statut de vérification de l'utilisateur.
    Utilisé par le frontend pour afficher la bannière appropriée.
    """
    base = {
        'is_verified': False,
        'status': 'NON_VERIFIE',
        'status_label': 'Non vérifié',
        'message': '',
        'action_required': '',
        'can_use_platform': False,
    }

    if user.user_type in ('ADMIN',):
        base.update(is_verified=True, status='VALIDE', status_label='Administrateur',
                     can_use_platform=True)
        return base

    if user.user_type == 'INSTITUTION':
        base.update(is_verified=True, status='VALIDE', status_label='Institution vérifiée',
                     can_use_platform=True)
        return base

    if user.user_type == 'EXPLOITANT':
        profile = getattr(user, 'exploitant_profile', None)
        if profile is None:
            base.update(
                message="Vous devez soumettre une demande de vérification de votre exploitation.",
                action_required='SUBMIT_VERIFICATION',
            )
        elif profile.statut_verification == 'VERIFIE':
            base.update(is_verified=True, status='VERIFIE', status_label='Exploitation vérifiée',
                         can_use_platform=True)
        elif profile.statut_verification == 'EN_ATTENTE':
            base.update(
                status='EN_ATTENTE', status_label='En attente de vérification',
                message="Votre demande de vérification est en cours d'examen par notre équipe.",
                action_required='WAIT',
            )
        elif profile.statut_verification == 'REJETE':
            base.update(
                status='REJETE', status_label='Vérification rejetée',
                message=profile.motif_rejet or "Votre demande a été rejetée. Veuillez soumettre une nouvelle demande.",
                action_required='RESUBMIT',
            )
        else:
            base.update(
                message="Soumettez vos documents pour vérifier votre exploitation.",
                action_required='SUBMIT_VERIFICATION',
            )
        return base

    if user.user_type == 'AGRONOME':
        profile = getattr(user, 'agronome_profile', None)
        if profile is None:
            base.update(
                message="Votre profil agronome n'est pas encore créé.",
                action_required='COMPLETE_PROFILE',
            )
        elif profile.statut_validation == 'VALIDE':
            base.update(is_verified=True, status='VALIDE', status_label='Agronome certifié',
                         can_use_platform=True)
        elif profile.statut_validation == 'EN_ATTENTE':
            base.update(
                status='EN_ATTENTE', status_label='En attente de validation',
                message="Votre dossier est en cours de validation par notre équipe.",
                action_required='WAIT',
            )
        elif profile.statut_validation == 'REJETE':
            base.update(
                status='REJETE', status_label='Validation rejetée',
                message=profile.motif_rejet or "Votre dossier a été rejeté. Veuillez le compléter et resoumettre.",
                action_required='RESUBMIT',
            )
        else:
            base.update(
                message="Complétez votre dossier professionnel pour être validé.",
                action_required='COMPLETE_PROFILE',
            )
        return base

    # OUVRIER, ACHETEUR : vérification téléphone
    if user.phone_verified:
        base.update(is_verified=True, status='VERIFIE', status_label='Compte vérifié',
                     can_use_platform=True)
    else:
        base.update(
            message="Vérifiez votre numéro de téléphone pour activer votre compte.",
            action_required='VERIFY_PHONE',
        )

    return base
