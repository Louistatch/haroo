"""
Service de téléchargement sécurisé avec URLs signées temporaires
Génère des liens de téléchargement valides pendant 48 heures
"""
import secrets
import hashlib
import hmac
from datetime import timedelta
from typing import Optional, Dict
from django.utils import timezone
from django.conf import settings
from django.core.exceptions import ValidationError
import logging

from apps.documents.models import AchatDocument

logger = logging.getLogger(__name__)


class SecureDownloadService:
    """
    Service pour générer et valider des liens de téléchargement sécurisés
    
    Exigences: 5.1, 5.4, 5.5
    """
    
    # Durée de validité des liens: 48 heures
    LINK_VALIDITY_HOURS = 48
    
    @staticmethod
    def generate_download_token() -> str:
        """
        Génère un token de téléchargement sécurisé
        
        Returns:
            Token URL-safe de 32 caractères
            
        Exigence: 5.1
        """
        return secrets.token_urlsafe(32)
    
    @staticmethod
    def generate_signed_url(achat: AchatDocument) -> Dict[str, any]:
        """
        Génère une URL signée pour le téléchargement d'un document
        
        Args:
            achat: Instance AchatDocument
            
        Returns:
            Dict contenant l'URL, le token et la date d'expiration
            
        Exigence: 5.1
        """
        # Générer un nouveau token si nécessaire
        if not achat.lien_telechargement or SecureDownloadService.is_link_expired(achat):
            achat.lien_telechargement = SecureDownloadService.generate_download_token()
            achat.expiration_lien = timezone.now() + timedelta(
                hours=SecureDownloadService.LINK_VALIDITY_HOURS
            )
            achat.save(update_fields=['lien_telechargement', 'expiration_lien', 'updated_at'])
            
            logger.info(
                f"Nouveau lien de téléchargement généré: achat_id={achat.id}, "
                f"expiration={achat.expiration_lien}"
            )
        
        return {
            'token': achat.lien_telechargement,
            'expiration': achat.expiration_lien,
            'document_id': achat.document.id,
            'achat_id': achat.id
        }
    
    @staticmethod
    def is_link_expired(achat: AchatDocument) -> bool:
        """
        Vérifie si un lien de téléchargement a expiré
        
        Args:
            achat: Instance AchatDocument
            
        Returns:
            True si le lien a expiré, False sinon
            
        Exigence: 5.4
        """
        if not achat.expiration_lien:
            return True
        
        return timezone.now() > achat.expiration_lien
    
    @staticmethod
    def validate_download_token(
        document_id: int,
        token: str,
        user
    ) -> Optional[AchatDocument]:
        """
        Valide un token de téléchargement
        
        Args:
            document_id: ID du document
            token: Token de téléchargement
            user: Utilisateur effectuant le téléchargement
            
        Returns:
            Instance AchatDocument si valide, None sinon
            
        Raises:
            ValidationError: Si le token est invalide ou expiré
            
        Exigences: 5.1, 5.4
        """
        try:
            achat = AchatDocument.objects.select_related(
                'document', 'acheteur', 'transaction'
            ).get(
                document_id=document_id,
                lien_telechargement=token
            )
            
            # Vérifier que l'utilisateur est bien l'acheteur
            if achat.acheteur != user:
                logger.warning(
                    f"Tentative de téléchargement non autorisée: "
                    f"achat_id={achat.id}, user_id={user.id}, "
                    f"acheteur_id={achat.acheteur.id}"
                )
                raise ValidationError("Vous n'êtes pas autorisé à télécharger ce document")
            
            # Vérifier que le paiement est confirmé
            if achat.transaction.statut != 'SUCCESS':
                logger.warning(
                    f"Tentative de téléchargement avec paiement non confirmé: "
                    f"achat_id={achat.id}, transaction_status={achat.transaction.statut}"
                )
                raise ValidationError("Le paiement n'a pas été confirmé")
            
            # Vérifier l'expiration
            if SecureDownloadService.is_link_expired(achat):
                logger.info(
                    f"Lien de téléchargement expiré: achat_id={achat.id}, "
                    f"expiration={achat.expiration_lien}"
                )
                raise ValidationError(
                    "Le lien de téléchargement a expiré. "
                    "Veuillez régénérer un nouveau lien depuis votre historique d'achats."
                )
            
            return achat
            
        except AchatDocument.DoesNotExist:
            logger.warning(
                f"Token de téléchargement invalide: document_id={document_id}, "
                f"user_id={user.id}"
            )
            raise ValidationError("Lien de téléchargement invalide")
    
    @staticmethod
    def regenerate_link(achat: AchatDocument) -> Dict[str, any]:
        """
        Régénère un lien de téléchargement expiré
        
        Args:
            achat: Instance AchatDocument
            
        Returns:
            Dict contenant le nouveau token et la date d'expiration
            
        Exigence: 5.4
        """
        # Vérifier que le paiement est toujours valide
        if achat.transaction.statut != 'SUCCESS':
            raise ValidationError("Le paiement n'est pas confirmé")
        
        # Générer un nouveau token
        achat.lien_telechargement = SecureDownloadService.generate_download_token()
        achat.expiration_lien = timezone.now() + timedelta(
            hours=SecureDownloadService.LINK_VALIDITY_HOURS
        )
        achat.save(update_fields=['lien_telechargement', 'expiration_lien', 'updated_at'])
        
        logger.info(
            f"Lien de téléchargement régénéré: achat_id={achat.id}, "
            f"nouvelle_expiration={achat.expiration_lien}"
        )
        
        return {
            'token': achat.lien_telechargement,
            'expiration': achat.expiration_lien,
            'document_id': achat.document.id,
            'achat_id': achat.id
        }
    
    @staticmethod
    def track_download(achat: AchatDocument, ip_address: str) -> None:
        """
        Enregistre un téléchargement avec horodatage et adresse IP
        
        Args:
            achat: Instance AchatDocument
            ip_address: Adresse IP de l'utilisateur
            
        Exigence: 5.5
        """
        # Incrémenter le compteur de téléchargements
        achat.nombre_telechargements += 1
        achat.save(update_fields=['nombre_telechargements', 'updated_at'])
        
        # Créer un enregistrement de téléchargement
        from apps.documents.models import DownloadLog
        DownloadLog.objects.create(
            achat=achat,
            ip_address=ip_address,
            timestamp=timezone.now()
        )
        
        logger.info(
            f"Téléchargement enregistré: achat_id={achat.id}, "
            f"ip={ip_address}, count={achat.nombre_telechargements}"
        )
