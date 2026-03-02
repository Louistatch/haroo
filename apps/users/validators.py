"""
Validateurs personnalisés pour les mots de passe
"""
import string
from django.core.exceptions import ValidationError
from django.utils.translation import gettext as _


class CustomPasswordValidator:
    """
    Validateur de mot de passe personnalisé selon les exigences de sécurité
    
    Exigences:
    - Minimum 8 caractères
    - Au moins une majuscule
    - Au moins un chiffre
    - Au moins un caractère spécial
    """
    
    def validate(self, password, user=None):
        """Valide le mot de passe"""
        errors = []
        
        if len(password) < 8:
            errors.append(_("Le mot de passe doit contenir au moins 8 caractères."))
        
        if not any(c.isupper() for c in password):
            errors.append(_("Le mot de passe doit contenir au moins une majuscule."))
        
        if not any(c.isdigit() for c in password):
            errors.append(_("Le mot de passe doit contenir au moins un chiffre."))
        
        if not any(c in string.punctuation for c in password):
            errors.append(_("Le mot de passe doit contenir au moins un caractère spécial."))
        
        if errors:
            raise ValidationError(errors)
    
    def get_help_text(self):
        """Retourne le texte d'aide pour le validateur"""
        return _(
            "Votre mot de passe doit contenir au moins 8 caractères, "
            "une majuscule, un chiffre et un caractère spécial."
        )
