"""
Vues pour les documents techniques
"""
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.core.cache import cache
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from django.http import FileResponse, Http404
from django.core.exceptions import ValidationError
from django.urls import reverse
import logging

from .models import DocumentTechnique, AchatDocument
from .serializers import (
    DocumentTechniqueListSerializer,
    DocumentTechniqueDetailSerializer,
    PurchaseDocumentSerializer,
    AchatDocumentSerializer,
    DownloadLinkSerializer
)
from .filters import DocumentTechniqueFilter
from .services.secure_download import SecureDownloadService
from apps.payments.services import TransactionService, FedapayService

logger = logging.getLogger(__name__)


class DocumentTechniqueViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet pour les documents techniques
    
    Endpoints:
    - GET /api/v1/documents/ - Liste des documents avec filtres
    - GET /api/v1/documents/{id}/ - Détails d'un document
    
    Filtres disponibles:
    - region: ID de la région
    - prefecture: ID de la préfecture
    - canton: ID du canton
    - culture: Nom de la culture
    - type: Type de document (COMPTE_EXPLOITATION, ITINERAIRE_TECHNIQUE)
    - prix_min: Prix minimum
    - prix_max: Prix maximum
    
    Recherche:
    - search: Recherche dans titre, description, culture
    
    Tri:
    - ordering: Tri par prix, created_at (préfixe - pour ordre décroissant)
    """
    queryset = DocumentTechnique.objects.filter(actif=True).select_related(
        'template', 'region', 'prefecture', 'canton'
    )
    permission_classes = [AllowAny]  # Catalogue public
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = DocumentTechniqueFilter
    search_fields = ['titre', 'description', 'culture']
    ordering_fields = ['prix', 'created_at']
    ordering = ['-created_at']
    
    def get_serializer_class(self):
        """
        Retourne le serializer approprié selon l'action
        """
        if self.action == 'retrieve':
            return DocumentTechniqueDetailSerializer
        return DocumentTechniqueListSerializer
    
    def get_cache_key(self):
        """
        Génère une clé de cache basée sur les paramètres de requête
        """
        query_params = self.request.query_params.dict()
        # Trier les paramètres pour avoir une clé cohérente
        sorted_params = sorted(query_params.items())
        params_str = '&'.join([f"{k}={v}" for k, v in sorted_params])
        return f"documents_list:{params_str}"
    
    def list(self, request, *args, **kwargs):
        """
        Liste des documents avec cache Redis
        """
        # Générer la clé de cache
        cache_key = self.get_cache_key()
        
        # Vérifier le cache
        cached_response = cache.get(cache_key)
        if cached_response is not None:
            return Response(cached_response)
        
        # Si pas en cache, exécuter la requête normale
        response = super().list(request, *args, **kwargs)
        
        # Mettre en cache pour 5 minutes (300 secondes)
        if response.status_code == 200:
            cache.set(cache_key, response.data, timeout=300)
        
        return response
    
    def retrieve(self, request, *args, **kwargs):
        """
        Détails d'un document avec cache Redis
        """
        document_id = kwargs.get('pk')
        cache_key = f"document_detail:{document_id}"
        
        # Vérifier le cache
        cached_response = cache.get(cache_key)
        if cached_response is not None:
            return Response(cached_response)
        
        # Si pas en cache, exécuter la requête normale
        response = super().retrieve(request, *args, **kwargs)
        
        # Mettre en cache pour 10 minutes (600 secondes)
        if response.status_code == 200:
            cache.set(cache_key, response.data, timeout=600)
        
        return response
    
    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def purchase(self, request, pk=None):
        """
        POST /api/v1/documents/{id}/purchase
        
        Initier l'achat d'un document technique
        
        Body:
        {
            "callback_url": "https://example.com/callback"  # optionnel
        }
        
        Returns:
        {
            "success": true,
            "transaction_id": "uuid",
            "payment_url": "https://checkout.fedapay.com/...",
            "message": "Redirection vers Fedapay"
        }
        
        Exigences: 3.4, 4.1, 5.1
        """
        try:
            # Récupérer le document (sans filtrer par actif pour pouvoir vérifier)
            try:
                document = DocumentTechnique.objects.get(pk=pk)
            except DocumentTechnique.DoesNotExist:
                return Response(
                    {
                        "success": False,
                        "error": "Document non trouvé"
                    },
                    status=status.HTTP_404_NOT_FOUND
                )
            
            # Vérifier que le document est actif
            if not document.actif:
                return Response(
                    {
                        "success": False,
                        "error": "Ce document n'est plus disponible à l'achat"
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Vérifier si l'utilisateur a déjà acheté ce document
            existing_purchase = AchatDocument.objects.filter(
                acheteur=request.user,
                document=document,
                transaction__statut='SUCCESS'
            ).first()
            
            if existing_purchase:
                # L'utilisateur a déjà acheté ce document
                # Générer un nouveau lien si expiré
                download_info = SecureDownloadService.generate_signed_url(existing_purchase)
                download_url = request.build_absolute_uri(
                    reverse('document-download', kwargs={'pk': document.id})
                ) + f"?token={download_info['token']}"
                
                return Response(
                    {
                        "success": True,
                        "already_purchased": True,
                        "message": "Vous avez déjà acheté ce document",
                        "download_url": download_url,
                        "expiration": download_info['expiration']
                    },
                    status=status.HTTP_200_OK
                )
            
            # Créer la transaction
            transaction = TransactionService.create_transaction(
                utilisateur=request.user,
                type_transaction='ACHAT_DOCUMENT',
                montant=document.prix,
                reference_externe=str(document.id)
            )
            
            # Déterminer l'URL de callback
            callback_url = request.data.get('callback_url')
            if not callback_url:
                callback_url = request.build_absolute_uri(
                    reverse('payments:payment-callback')
                )
            
            # Initialiser le paiement Fedapay
            fedapay_service = FedapayService()
            payment_data = fedapay_service.initiate_payment(
                transaction=transaction,
                callback_url=callback_url,
                description=f"Achat document: {document.titre}"
            )
            
            logger.info(
                f"Achat de document initié: document_id={document.id}, "
                f"user_id={request.user.id}, transaction_id={transaction.id}"
            )
            
            return Response(
                {
                    "success": True,
                    "transaction_id": str(transaction.id),
                    "payment_url": payment_data['payment_url'],
                    "message": "Redirection vers Fedapay pour finaliser le paiement"
                },
                status=status.HTTP_201_CREATED
            )
            
        except Exception as e:
            logger.error(
                f"Erreur lors de l'achat de document: {str(e)}, "
                f"document_id={pk}, user_id={request.user.id}"
            )
            return Response(
                {
                    "success": False,
                    "error": str(e),
                    "message": "Échec de l'initialisation de l'achat"
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=True, methods=['get'], permission_classes=[IsAuthenticated])
    def download(self, request, pk=None):
        """
        GET /api/v1/documents/{id}/download?token=<token>
        
        Télécharger un document acheté avec un token valide
        
        Query params:
        - token: Token de téléchargement sécurisé
        
        Returns:
        - Fichier du document (Excel ou Word)
        
        Exigences: 5.2, 5.5
        """
        token = request.query_params.get('token')
        
        if not token:
            return Response(
                {
                    "success": False,
                    "error": "Token de téléchargement manquant"
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            # Valider le token
            achat = SecureDownloadService.validate_download_token(
                document_id=pk,
                token=token,
                user=request.user
            )
            
            # Obtenir l'adresse IP
            ip_address = self._get_client_ip(request)
            
            # Enregistrer le téléchargement
            SecureDownloadService.track_download(achat, ip_address)
            
            # Retourner le fichier
            document = achat.document
            file_path = document.fichier_genere.path
            
            # Déterminer le type MIME
            if document.template.format_fichier == 'EXCEL':
                content_type = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
                extension = 'xlsx'
            else:  # WORD
                content_type = 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
                extension = 'docx'
            
            # Nom du fichier pour le téléchargement
            filename = f"{document.titre.replace(' ', '_')}.{extension}"
            
            logger.info(
                f"Document téléchargé: achat_id={achat.id}, "
                f"document_id={document.id}, user_id={request.user.id}, "
                f"ip={ip_address}"
            )
            
            response = FileResponse(
                open(file_path, 'rb'),
                content_type=content_type
            )
            response['Content-Disposition'] = f'attachment; filename="{filename}"'
            
            return response
            
        except ValidationError as e:
            return Response(
                {
                    "success": False,
                    "error": str(e)
                },
                status=status.HTTP_403_FORBIDDEN
            )
        except Exception as e:
            logger.error(
                f"Erreur lors du téléchargement: {str(e)}, "
                f"document_id={pk}, user_id={request.user.id}"
            )
            return Response(
                {
                    "success": False,
                    "error": "Erreur lors du téléchargement du document"
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    def _get_client_ip(self, request):
        """Obtenir l'adresse IP du client"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip



class PurchaseHistoryViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet pour l'historique des achats de documents
    
    Endpoints:
    - GET /api/v1/purchases/history - Liste des achats de l'utilisateur
    - GET /api/v1/purchases/history/{id} - Détails d'un achat
    - POST /api/v1/purchases/history/{id}/regenerate-link - Régénérer un lien expiré
    
    Filtres disponibles:
    - date_debut: Date de début (format ISO 8601)
    - date_fin: Date de fin (format ISO 8601)
    - type_document: Type de document (COMPTE_EXPLOITATION, ITINERAIRE_TECHNIQUE)
    - culture: Nom de la culture (recherche partielle)
    - statut: Statut de la transaction (SUCCESS, PENDING, FAILED)
    - lien_expire: Filtrer par lien expiré (true/false)
    
    Exigences: 5.3, 5.4, 5.5
    """
    permission_classes = [IsAuthenticated]
    serializer_class = AchatDocumentSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_class = None  # Will be imported to avoid circular import
    search_fields = ['document__titre', 'document__culture']
    ordering_fields = ['created_at', 'document__prix', 'nombre_telechargements']
    ordering = ['-created_at']
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Import here to avoid circular import
        from .filters import AchatDocumentFilter
        self.filterset_class = AchatDocumentFilter
    
    def get_queryset(self):
        """Filtrer les achats de l'utilisateur connecté"""
        return AchatDocument.objects.filter(
            acheteur=self.request.user
        ).select_related(
            'document',
            'document__template',
            'document__region',
            'document__prefecture',
            'document__canton',
            'transaction'
        ).order_by('-created_at')
    
    @action(detail=True, methods=['post'])
    def regenerate_link(self, request, pk=None):
        """
        POST /api/v1/purchases/history/{id}/regenerate-link
        
        Régénérer un lien de téléchargement expiré
        
        Returns:
        {
            "success": true,
            "download_url": "...",
            "expiration": "2024-01-15T12:00:00Z",
            "message": "Nouveau lien généré"
        }
        
        Exigence: 5.4
        """
        try:
            achat = self.get_object()
            
            # Régénérer le lien
            download_info = SecureDownloadService.regenerate_link(achat)
            
            # Construire l'URL de téléchargement
            download_url = request.build_absolute_uri(
                reverse('document-download', kwargs={'pk': achat.document.id})
            ) + f"?token={download_info['token']}"
            
            logger.info(
                f"Lien régénéré: achat_id={achat.id}, user_id={request.user.id}"
            )
            
            return Response(
                {
                    "success": True,
                    "download_url": download_url,
                    "expiration": download_info['expiration'],
                    "message": "Nouveau lien de téléchargement généré avec succès"
                },
                status=status.HTTP_200_OK
            )
            
        except ValidationError as e:
            return Response(
                {
                    "success": False,
                    "error": str(e)
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            logger.error(
                f"Erreur lors de la régénération du lien: {str(e)}, "
                f"achat_id={pk}, user_id={request.user.id}"
            )
            return Response(
                {
                    "success": False,
                    "error": "Erreur lors de la régénération du lien"
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
