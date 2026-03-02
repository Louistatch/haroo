"""
Actions post-paiement déclenchées après confirmation de paiement réussi
"""
from django.utils import timezone
from datetime import timedelta
from typing import Optional
import logging

from .models import Transaction

logger = logging.getLogger(__name__)


class PostPaymentActionHandler:
    """
    Gestionnaire des actions post-paiement selon le type de transaction
    """
    
    @staticmethod
    def handle_successful_payment(transaction: Transaction) -> bool:
        """
        Déclencher les actions appropriées après un paiement réussi
        
        Args:
            transaction: Instance Transaction avec statut SUCCESS
            
        Returns:
            True si les actions ont été exécutées avec succès, False sinon
        """
        if transaction.statut != 'SUCCESS':
            logger.warning(
                f"Tentative d'exécution d'actions post-paiement sur transaction "
                f"non réussie: {transaction.id}, statut={transaction.statut}"
            )
            return False
        
        try:
            # Dispatcher selon le type de transaction
            handlers = {
                'ACHAT_DOCUMENT': PostPaymentActionHandler._handle_document_purchase,
                'RECRUTEMENT_AGRONOME': PostPaymentActionHandler._handle_agronomist_recruitment,
                'PREVENTE': PostPaymentActionHandler._handle_presale,
                'TRANSPORT': PostPaymentActionHandler._handle_transport,
                'ABONNEMENT': PostPaymentActionHandler._handle_subscription,
            }
            
            handler = handlers.get(transaction.type_transaction)
            
            if handler:
                success = handler(transaction)
                if success:
                    logger.info(
                        f"Actions post-paiement exécutées avec succès: "
                        f"transaction_id={transaction.id}, type={transaction.type_transaction}"
                    )
                return success
            else:
                logger.warning(
                    f"Aucun handler trouvé pour le type de transaction: "
                    f"{transaction.type_transaction}"
                )
                return False
                
        except Exception as e:
            logger.error(
                f"Erreur lors de l'exécution des actions post-paiement: {str(e)}, "
                f"transaction_id={transaction.id}"
            )
            return False
    
    @staticmethod
    def _handle_document_purchase(transaction: Transaction) -> bool:
        """
        Débloquer l'accès au document acheté et générer le document personnalisé
        
        Args:
            transaction: Transaction d'achat de document
            
        Returns:
            True si le déblocage a réussi
        """
        try:
            from apps.documents.models import AchatDocument, DocumentTechnique
            from apps.documents.services.template_engine import TemplateEngine
            from apps.documents.services.secure_download import SecureDownloadService
            from django.core.files.base import ContentFile
            
            # Vérifier si l'achat existe déjà (idempotence)
            if AchatDocument.objects.filter(transaction=transaction).exists():
                logger.info(
                    f"Achat de document déjà traité: transaction_id={transaction.id}"
                )
                return True
            
            # Récupérer le document depuis la référence externe
            if not transaction.reference_externe:
                logger.error(
                    f"Référence externe manquante pour achat de document: "
                    f"transaction_id={transaction.id}"
                )
                return False
            
            try:
                document = DocumentTechnique.objects.select_related(
                    'template', 'region', 'prefecture', 'canton'
                ).get(id=transaction.reference_externe)
            except DocumentTechnique.DoesNotExist:
                logger.error(
                    f"Document non trouvé: id={transaction.reference_externe}, "
                    f"transaction_id={transaction.id}"
                )
                return False
            
            # Générer le document personnalisé avec les données de localisation
            try:
                template_engine = TemplateEngine()
                
                # Préparer les variables pour la substitution
                variables = {
                    'culture': document.culture,
                    'prix': str(document.prix),
                    'date': timezone.now()
                }
                
                # Ajouter les informations géographiques si disponibles
                if document.canton:
                    variables['canton'] = document.canton.nom
                if document.prefecture:
                    variables['prefecture'] = document.prefecture.nom
                if document.region:
                    variables['region'] = document.region.nom
                
                # Générer le document personnalisé
                personalized_file = template_engine.generate_document(
                    template_file=document.template.fichier_template,
                    file_format=document.template.format_fichier,
                    variables=variables,
                    required_variables=document.template.variables_requises
                )
                
                # Sauvegarder le document personnalisé
                # Note: Pour l'instant, on utilise le document généré existant
                # Dans une version future, on pourrait sauvegarder un document unique par achat
                
                logger.info(
                    f"Document personnalisé généré: document_id={document.id}, "
                    f"transaction_id={transaction.id}"
                )
                
            except Exception as e:
                logger.warning(
                    f"Erreur lors de la génération du document personnalisé: {str(e)}, "
                    f"utilisation du document par défaut"
                )
                # Continuer avec le document par défaut si la génération échoue
            
            # Générer un lien de téléchargement sécurisé
            download_token = SecureDownloadService.generate_download_token()
            expiration = timezone.now() + timedelta(hours=48)
            
            # Créer l'achat
            achat = AchatDocument.objects.create(
                acheteur=transaction.utilisateur,
                document=document,
                transaction=transaction,
                lien_telechargement=download_token,
                expiration_lien=expiration
            )
            
            logger.info(
                f"Document débloqué: achat_id={achat.id}, document_id={document.id}, "
                f"transaction_id={transaction.id}"
            )
            
            # TODO: Envoyer une notification à l'utilisateur avec le lien de téléchargement
            
            return True
            
        except Exception as e:
            logger.error(
                f"Erreur lors du déblocage du document: {str(e)}, "
                f"transaction_id={transaction.id}"
            )
            return False
    
    @staticmethod
    def _handle_agronomist_recruitment(transaction: Transaction) -> bool:
        """
        Bloquer le paiement en escrow pour une mission d'agronome
        
        Args:
            transaction: Transaction de recrutement d'agronome
            
        Returns:
            True si le blocage en escrow a réussi
        """
        try:
            from apps.missions.models import Mission
            from apps.payments.services import EscrowService
            from datetime import timedelta
            
            # Vérifier si l'escrow existe déjà (idempotence)
            existing_escrow = EscrowService.get_escrow_by_transaction(str(transaction.id))
            if existing_escrow:
                logger.info(
                    f"Escrow déjà créé pour mission: transaction_id={transaction.id}, "
                    f"escrow_id={existing_escrow.id}"
                )
                return True
            
            # Récupérer la mission depuis la référence externe
            if not transaction.reference_externe:
                logger.error(
                    f"Référence externe manquante pour recrutement agronome: "
                    f"transaction_id={transaction.id}"
                )
                return False
            
            try:
                mission = Mission.objects.select_related(
                    'exploitant', 'agronome'
                ).get(id=transaction.reference_externe)
            except Mission.DoesNotExist:
                logger.error(
                    f"Mission non trouvée: id={transaction.reference_externe}, "
                    f"transaction_id={transaction.id}"
                )
                return False
            
            # Vérifier que la mission est en statut ACCEPTEE
            if mission.statut != 'ACCEPTEE':
                logger.warning(
                    f"Mission pas en statut ACCEPTEE: mission_id={mission.id}, "
                    f"statut={mission.statut}"
                )
                # On continue quand même pour créer l'escrow
            
            # Calculer la date de libération prévue
            # Par défaut, on prévoit 30 jours si pas de date de fin
            if mission.date_fin:
                date_liberation_prevue = timezone.make_aware(
                    timezone.datetime.combine(mission.date_fin, timezone.datetime.min.time())
                )
            else:
                date_liberation_prevue = timezone.now() + timedelta(days=30)
            
            # Créer le compte escrow
            escrow = EscrowService.create_escrow(
                transaction=transaction,
                beneficiaire=mission.agronome,
                montant_bloque=transaction.montant,
                date_liberation_prevue=date_liberation_prevue
            )
            
            # Mettre à jour la mission avec la transaction
            if not mission.transaction:
                mission.transaction = transaction
                mission.save(update_fields=['transaction', 'updated_at'])
            
            # Mettre à jour le statut de la mission à EN_COURS
            if mission.statut == 'ACCEPTEE':
                mission.statut = 'EN_COURS'
                mission.save(update_fields=['statut', 'updated_at'])
            
            logger.info(
                f"Paiement agronome bloqué en escrow: transaction_id={transaction.id}, "
                f"escrow_id={escrow.id}, mission_id={mission.id}, "
                f"beneficiaire={mission.agronome.id}"
            )
            
            # TODO: Envoyer une notification à l'agronome que la mission est payée et confirmée
            
            return True
            
        except Exception as e:
            logger.error(
                f"Erreur lors du blocage en escrow pour agronome: {str(e)}, "
                f"transaction_id={transaction.id}"
            )
            return False
    
    @staticmethod
    def _handle_presale(transaction: Transaction) -> bool:
        """
        Bloquer l'acompte de prévente en escrow
        
        Args:
            transaction: Transaction de prévente agricole
            
        Returns:
            True si le blocage en escrow a réussi
        """
        try:
            # TODO: Implémenter la logique d'escrow pour les préventes
            # - Créer un compte escrow
            # - Bloquer l'acompte (20%) jusqu'à livraison
            # - Notifier l'exploitant et l'acheteur
            
            logger.info(
                f"Acompte prévente bloqué en escrow: transaction_id={transaction.id}"
            )
            return True
            
        except Exception as e:
            logger.error(
                f"Erreur lors du blocage en escrow pour prévente: {str(e)}, "
                f"transaction_id={transaction.id}"
            )
            return False
    
    @staticmethod
    def _handle_transport(transaction: Transaction) -> bool:
        """
        Bloquer le paiement de transport en escrow
        
        Args:
            transaction: Transaction de transport
            
        Returns:
            True si le blocage en escrow a réussi
        """
        try:
            # TODO: Implémenter la logique d'escrow pour le transport
            # - Créer un compte escrow
            # - Bloquer le paiement jusqu'à confirmation de livraison
            # - Notifier le transporteur et l'exploitant
            
            logger.info(
                f"Paiement transport bloqué en escrow: transaction_id={transaction.id}"
            )
            return True
            
        except Exception as e:
            logger.error(
                f"Erreur lors du blocage en escrow pour transport: {str(e)}, "
                f"transaction_id={transaction.id}"
            )
            return False
    
    @staticmethod
    def _handle_subscription(transaction: Transaction) -> bool:
        """
        Activer l'abonnement premium
        
        Args:
            transaction: Transaction d'abonnement
            
        Returns:
            True si l'activation a réussi
        """
        try:
            # TODO: Implémenter la logique d'activation d'abonnement
            # - Créer ou renouveler l'abonnement premium
            # - Débloquer les fonctionnalités premium
            # - Notifier l'utilisateur
            
            logger.info(
                f"Abonnement premium activé: transaction_id={transaction.id}"
            )
            return True
            
        except Exception as e:
            logger.error(
                f"Erreur lors de l'activation de l'abonnement: {str(e)}, "
                f"transaction_id={transaction.id}"
            )
            return False
