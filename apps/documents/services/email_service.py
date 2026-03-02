"""
Service d'envoi d'emails pour les documents techniques

Ce service gère l'envoi d'emails pour:
- Confirmation d'achat
- Rappel d'expiration de lien
- Confirmation de régénération de lien
"""
import logging
from typing import Dict, Optional
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.conf import settings
from django.utils.html import strip_tags

from apps.documents.models import AchatDocument

# Import premailer pour l'optimisation CSS inline
try:
    from premailer import transform
    PREMAILER_AVAILABLE = True
except ImportError:
    PREMAILER_AVAILABLE = False
    logging.warning("premailer n'est pas installé. Les emails seront envoyés sans optimisation CSS inline.")

logger = logging.getLogger(__name__)


class EmailService:
    """
    Service centralisé pour l'envoi d'emails liés aux documents
    """
    
    def __init__(self):
        """Initialiser le service d'email"""
        self.from_email = getattr(
            settings, 
            'DEFAULT_FROM_EMAIL', 
            'noreply@haroo.tg'
        )
        self.frontend_url = getattr(
            settings,
            'FRONTEND_URL',
            'http://localhost:5173'
        )
    
    def send_purchase_confirmation(
        self, 
        achat: AchatDocument,
        download_url: str
    ) -> bool:
        """
        Envoyer un email de confirmation d'achat
        
        Args:
            achat: Instance d'AchatDocument
            download_url: URL complète de téléchargement
            
        Returns:
            bool: True si l'email a été envoyé avec succès
            
        Example:
            >>> service = EmailService()
            >>> achat = AchatDocument.objects.get(id=1)
            >>> url = "https://example.com/download?token=abc123"
            >>> service.send_purchase_confirmation(achat, url)
            True
        """
        try:
            # Valider l'email
            if not achat.acheteur.email:
                logger.warning(
                    f"Achat {achat.id}: Utilisateur {achat.acheteur.id} "
                    f"n'a pas d'email"
                )
                return False
            
            # Préparer le contexte
            context = {
                'user': achat.acheteur,
                'document': achat.document,
                'achat': achat,
                'download_url': download_url,
                'expiration_date': achat.expiration_lien,
                'frontend_url': self.frontend_url,
                'purchase_history_url': f"{self.frontend_url}/purchases",
            }
            
            # Rendre les templates
            subject = f"Confirmation d'achat - {achat.document.titre}"
            html_content = self._render_email_template(
                'emails/purchase_confirmation.html',
                context
            )
            text_content = self._render_email_template(
                'emails/purchase_confirmation.txt',
                context
            )
            
            # Créer et envoyer l'email
            email = EmailMultiAlternatives(
                subject=subject,
                body=text_content,
                from_email=self.from_email,
                to=[achat.acheteur.email]
            )
            email.attach_alternative(html_content, "text/html")
            email.send(fail_silently=False)
            
            logger.info(
                f"Email de confirmation envoyé pour achat {achat.id} "
                f"à {achat.acheteur.email}"
            )
            return True
            
        except Exception as e:
            logger.error(
                f"Erreur lors de l'envoi de l'email de confirmation "
                f"pour achat {achat.id}: {str(e)}",
                exc_info=True
            )
            # Ne pas lever l'exception pour ne pas bloquer le processus d'achat
            return False
    
    def send_expiration_reminder(
        self,
        achat: AchatDocument,
        hours_remaining: int
    ) -> bool:
        """
        Envoyer un rappel d'expiration de lien de téléchargement
        
        Args:
            achat: Instance d'AchatDocument
            hours_remaining: Nombre d'heures restantes avant expiration
            
        Returns:
            bool: True si l'email a été envoyé avec succès
            
        Example:
            >>> service = EmailService()
            >>> achat = AchatDocument.objects.get(id=1)
            >>> service.send_expiration_reminder(achat, 24)
            True
        """
        try:
            # Valider l'email
            if not achat.acheteur.email:
                logger.warning(
                    f"Achat {achat.id}: Utilisateur {achat.acheteur.id} "
                    f"n'a pas d'email"
                )
                return False
            
            # Ne pas envoyer si le lien est déjà expiré
            if achat.lien_expire:
                logger.info(
                    f"Achat {achat.id}: Lien déjà expiré, "
                    f"pas d'envoi de rappel"
                )
                return False
            
            # Préparer le contexte
            context = {
                'user': achat.acheteur,
                'document': achat.document,
                'achat': achat,
                'hours_remaining': hours_remaining,
                'expiration_date': achat.expiration_lien,
                'frontend_url': self.frontend_url,
                'purchase_history_url': f"{self.frontend_url}/purchases",
            }
            
            # Rendre les templates
            subject = f"Rappel: Votre lien de téléchargement expire bientôt"
            html_content = self._render_email_template(
                'emails/expiration_reminder.html',
                context
            )
            text_content = self._render_email_template(
                'emails/expiration_reminder.txt',
                context
            )
            
            # Créer et envoyer l'email
            email = EmailMultiAlternatives(
                subject=subject,
                body=text_content,
                from_email=self.from_email,
                to=[achat.acheteur.email]
            )
            email.attach_alternative(html_content, "text/html")
            email.send(fail_silently=False)
            
            logger.info(
                f"Email de rappel d'expiration envoyé pour achat {achat.id} "
                f"à {achat.acheteur.email} ({hours_remaining}h restantes)"
            )
            return True
            
        except Exception as e:
            logger.error(
                f"Erreur lors de l'envoi du rappel d'expiration "
                f"pour achat {achat.id}: {str(e)}",
                exc_info=True
            )
            return False
    
    def send_link_regenerated(
        self,
        achat: AchatDocument,
        download_url: str
    ) -> bool:
        """
        Envoyer une confirmation de régénération de lien
        
        Args:
            achat: Instance d'AchatDocument
            download_url: Nouvelle URL de téléchargement
            
        Returns:
            bool: True si l'email a été envoyé avec succès
            
        Example:
            >>> service = EmailService()
            >>> achat = AchatDocument.objects.get(id=1)
            >>> url = "https://example.com/download?token=xyz789"
            >>> service.send_link_regenerated(achat, url)
            True
        """
        try:
            # Valider l'email
            if not achat.acheteur.email:
                logger.warning(
                    f"Achat {achat.id}: Utilisateur {achat.acheteur.id} "
                    f"n'a pas d'email"
                )
                return False
            
            # Préparer le contexte
            context = {
                'user': achat.acheteur,
                'document': achat.document,
                'achat': achat,
                'download_url': download_url,
                'expiration_date': achat.expiration_lien,
                'frontend_url': self.frontend_url,
                'purchase_history_url': f"{self.frontend_url}/purchases",
            }
            
            # Rendre les templates
            subject = f"Nouveau lien de téléchargement - {achat.document.titre}"
            html_content = self._render_email_template(
                'emails/link_regenerated.html',
                context
            )
            text_content = self._render_email_template(
                'emails/link_regenerated.txt',
                context
            )
            
            # Créer et envoyer l'email
            email = EmailMultiAlternatives(
                subject=subject,
                body=text_content,
                from_email=self.from_email,
                to=[achat.acheteur.email]
            )
            email.attach_alternative(html_content, "text/html")
            email.send(fail_silently=False)
            
            logger.info(
                f"Email de régénération de lien envoyé pour achat {achat.id} "
                f"à {achat.acheteur.email}"
            )
            return True
            
        except Exception as e:
            logger.error(
                f"Erreur lors de l'envoi de l'email de régénération "
                f"pour achat {achat.id}: {str(e)}",
                exc_info=True
            )
            return False
    
    def _render_email_template(
        self,
        template_name: str,
        context: Dict
    ) -> str:
        """
        Rendre un template d'email avec le contexte fourni
        
        Applique premailer pour convertir les CSS en inline styles
        si premailer est disponible (améliore la compatibilité email).
        
        Args:
            template_name: Nom du template (ex: 'emails/purchase_confirmation.html')
            context: Dictionnaire de contexte pour le template
            
        Returns:
            str: Contenu du template rendu (avec CSS inline si HTML)
            
        Raises:
            TemplateDoesNotExist: Si le template n'existe pas
        """
        try:
            html = render_to_string(template_name, context)
            
            # Appliquer premailer uniquement pour les templates HTML
            if PREMAILER_AVAILABLE and template_name.endswith('.html'):
                try:
                    html = transform(html)
                    logger.debug(f"Premailer appliqué sur {template_name}")
                except Exception as e:
                    logger.warning(
                        f"Erreur premailer sur {template_name}: {str(e)}. "
                        f"Utilisation du HTML non optimisé."
                    )
            
            return html
        except Exception as e:
            logger.error(
                f"Erreur lors du rendu du template {template_name}: {str(e)}",
                exc_info=True
            )
            raise
    
    def send_bulk_expiration_reminders(
        self,
        achats: list,
        hours_remaining: int
    ) -> Dict[str, int]:
        """
        Envoyer des rappels d'expiration en masse
        
        Args:
            achats: Liste d'instances AchatDocument
            hours_remaining: Nombre d'heures restantes
            
        Returns:
            dict: Statistiques d'envoi {'success': int, 'failed': int}
            
        Example:
            >>> service = EmailService()
            >>> achats = AchatDocument.objects.filter(...)
            >>> stats = service.send_bulk_expiration_reminders(achats, 24)
            >>> print(f"Envoyés: {stats['success']}, Échoués: {stats['failed']}")
        """
        stats = {'success': 0, 'failed': 0}
        
        logger.info(
            f"Début d'envoi en masse de {len(achats)} rappels d'expiration "
            f"({hours_remaining}h restantes)"
        )
        
        for achat in achats:
            try:
                if self.send_expiration_reminder(achat, hours_remaining):
                    stats['success'] += 1
                else:
                    stats['failed'] += 1
            except Exception as e:
                logger.error(
                    f"Erreur lors de l'envoi du rappel pour achat {achat.id}: {str(e)}"
                )
                stats['failed'] += 1
        
        logger.info(
            f"Envoi en masse terminé: {stats['success']} succès, "
            f"{stats['failed']} échecs"
        )
        
        return stats
