"""
Vues pour la conformité réglementaire
Exigences: 45.1, 45.2, 45.3, 45.4, 45.5, 45.6, 33.6
"""
from django.http import JsonResponse, HttpResponse
from django.shortcuts import get_object_or_404
from rest_framework import status, viewsets
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, IsAdminUser, AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import (
    CGUAcceptance,
    ElectronicReceipt,
    AccountDeletionRequest,
    DataRetentionPolicy
)
from .serializers import (
    CGUAcceptanceSerializer,
    AcceptCGUSerializer,
    ElectronicReceiptSerializer,
    AccountDeletionRequestSerializer,
    CreateDeletionRequestSerializer,
    DataExportSerializer,
    DataRetentionPolicySerializer
)
from .services import (
    CGUService,
    ReceiptService,
    DataExportService,
    AccountDeletionService,
    DataRetentionService
)


@api_view(['GET'])
@permission_classes([AllowAny])
def cgu_view(request):
    """
    Affiche les conditions générales d'utilisation
    Exigence: 45.2
    """
    cgu_content = {
        'version': CGUService.CURRENT_CGU_VERSION,
        'title': 'Conditions Générales d\'Utilisation',
        'last_updated': '2024-01-01',
        'sections': [
            {
                'title': '1. Objet',
                'content': 'Les présentes Conditions Générales d\'Utilisation (CGU) régissent l\'utilisation de la Plateforme Agricole Intelligente du Togo.'
            },
            {
                'title': '2. Acceptation des CGU',
                'content': 'L\'utilisation de la plateforme implique l\'acceptation pleine et entière des présentes CGU.'
            },
            {
                'title': '3. Services proposés',
                'content': 'La plateforme propose des services de vente de documents techniques, de recrutement d\'agronomes, de prévente agricole et d\'optimisation logistique.'
            },
            {
                'title': '4. Inscription et compte utilisateur',
                'content': 'L\'inscription nécessite un numéro de téléphone togolais valide et l\'acceptation explicite des présentes CGU.'
            },
            {
                'title': '5. Protection des données personnelles',
                'content': 'Vos données personnelles sont protégées conformément à la loi togolaise sur la protection des données. Consultez notre politique de confidentialité pour plus de détails.'
            },
            {
                'title': '6. Paiements',
                'content': 'Les paiements sont traités via Fedapay. La plateforme applique des commissions selon le type de transaction.'
            },
            {
                'title': '7. Responsabilités',
                'content': 'Les utilisateurs sont responsables de l\'exactitude des informations fournies et du respect des engagements pris sur la plateforme.'
            },
            {
                'title': '8. Résiliation',
                'content': 'Vous pouvez demander la suppression de votre compte à tout moment. Les données de transaction seront conservées pendant 10 ans pour conformité fiscale.'
            },
            {
                'title': '9. Modification des CGU',
                'content': 'La plateforme se réserve le droit de modifier les présentes CGU. Les utilisateurs seront notifiés des modifications.'
            },
            {
                'title': '10. Droit applicable',
                'content': 'Les présentes CGU sont régies par le droit togolais.'
            }
        ]
    }
    return Response(cgu_content)


@api_view(['GET'])
@permission_classes([AllowAny])
def privacy_policy_view(request):
    """
    Affiche la politique de confidentialité
    Exigence: 45.2
    """
    privacy_content = {
        'version': '1.0',
        'title': 'Politique de Confidentialité',
        'last_updated': '2024-01-01',
        'sections': [
            {
                'title': '1. Collecte des données',
                'content': 'Nous collectons les données nécessaires au fonctionnement de la plateforme : informations de profil, coordonnées, données de transaction.'
            },
            {
                'title': '2. Utilisation des données',
                'content': 'Vos données sont utilisées pour fournir les services de la plateforme, améliorer l\'expérience utilisateur et respecter nos obligations légales.'
            },
            {
                'title': '3. Protection des données',
                'content': 'Nous mettons en œuvre des mesures de sécurité techniques et organisationnelles pour protéger vos données : chiffrement HTTPS/TLS, hachage des mots de passe, contrôle d\'accès.'
            },
            {
                'title': '4. Partage des données',
                'content': 'Vos données ne sont pas vendues à des tiers. Elles peuvent être partagées avec nos partenaires de paiement (Fedapay) dans le cadre des transactions.'
            },
            {
                'title': '5. Rétention des données',
                'content': 'Les données de transaction sont conservées pendant 10 ans pour conformité fiscale. Les autres données sont conservées selon notre politique de rétention.'
            },
            {
                'title': '6. Vos droits',
                'content': 'Vous disposez d\'un droit d\'accès, de rectification, de suppression et d\'export de vos données personnelles.'
            },
            {
                'title': '7. Export des données',
                'content': 'Vous pouvez demander l\'export de toutes vos données personnelles au format JSON à tout moment.'
            },
            {
                'title': '8. Suppression du compte',
                'content': 'Vous pouvez demander la suppression de votre compte. Vos données seront anonymisées, sauf les données de transaction conservées pour conformité fiscale.'
            },
            {
                'title': '9. Cookies',
                'content': 'Nous utilisons des cookies essentiels pour le fonctionnement de la plateforme (authentification, sessions).'
            },
            {
                'title': '10. Contact',
                'content': 'Pour toute question concernant vos données personnelles, contactez-nous via la plateforme.'
            }
        ]
    }
    return Response(privacy_content)


class CGUAcceptanceViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet pour l'historique des acceptations CGU
    Exigence: 45.3
    """
    serializer_class = CGUAcceptanceSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return CGUAcceptance.objects.filter(user=self.request.user)
    
    @action(detail=False, methods=['post'])
    def accept(self, request):
        """
        Enregistre l'acceptation des CGU
        Exigence: 45.3
        """
        serializer = AcceptCGUSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        # Récupérer l'IP et le user agent
        ip_address = self._get_client_ip(request)
        user_agent = request.META.get('HTTP_USER_AGENT', '')
        
        # Enregistrer l'acceptation
        version = serializer.validated_data.get('version_cgu')
        acceptance = CGUService.record_acceptance(
            user=request.user,
            ip_address=ip_address,
            user_agent=user_agent,
            version=version
        )
        
        return Response(
            CGUAcceptanceSerializer(acceptance).data,
            status=status.HTTP_201_CREATED
        )
    
    @action(detail=False, methods=['get'])
    def current_status(self, request):
        """
        Vérifie si l'utilisateur a accepté la version actuelle des CGU
        """
        has_accepted = CGUService.has_accepted_current_version(request.user)
        return Response({
            'has_accepted_current_version': has_accepted,
            'current_version': CGUService.CURRENT_CGU_VERSION
        })
    
    def _get_client_ip(self, request):
        """Récupère l'adresse IP du client"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip


class ElectronicReceiptViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet pour les reçus électroniques
    Exigence: 45.5
    """
    serializer_class = ElectronicReceiptSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return ElectronicReceipt.objects.filter(
            transaction__utilisateur=self.request.user
        ).select_related('transaction')
    
    @action(detail=True, methods=['get'])
    def download_pdf(self, request, pk=None):
        """
        Télécharge le PDF du reçu
        """
        receipt = self.get_object()
        
        if not receipt.pdf_file:
            return Response(
                {'error': 'PDF non disponible'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        response = HttpResponse(receipt.pdf_file.read(), content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="{receipt.receipt_number}.pdf"'
        return response


class AccountDeletionViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet pour les demandes de suppression de compte
    Exigence: 45.4
    """
    serializer_class = AccountDeletionRequestSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        if self.request.user.is_staff:
            return AccountDeletionRequest.objects.all()
        return AccountDeletionRequest.objects.filter(user=self.request.user)
    
    @action(detail=False, methods=['post'])
    def request_deletion(self, request):
        """
        Crée une demande de suppression de compte
        Exigence: 45.4
        """
        serializer = CreateDeletionRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        reason = serializer.validated_data.get('reason', '')
        deletion_request = AccountDeletionService.request_deletion(
            user=request.user,
            reason=reason
        )
        
        return Response(
            AccountDeletionRequestSerializer(deletion_request, context={'request': request}).data,
            status=status.HTTP_201_CREATED
        )
    
    @action(detail=True, methods=['post'], permission_classes=[IsAdminUser])
    def process(self, request, pk=None):
        """
        Traite une demande de suppression (admin uniquement)
        """
        deletion_request = self.get_object()
        
        try:
            processed_request = AccountDeletionService.process_deletion(
                deletion_request=deletion_request,
                admin_user=request.user
            )
            return Response(
                AccountDeletionRequestSerializer(processed_request, context={'request': request}).data
            )
        except ValueError as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )


class DataExportView(APIView):
    """
    Vue pour l'export des données personnelles
    Exigence: 33.6
    """
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        """
        Exporte toutes les données personnelles de l'utilisateur
        Exigence: 33.6
        """
        serializer = DataExportSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        # Générer l'export JSON
        data_json = DataExportService.export_user_data(request.user)
        
        # Retourner le fichier JSON
        response = HttpResponse(data_json, content_type='application/json')
        response['Content-Disposition'] = f'attachment; filename="user_{request.user.id}_data_export.json"'
        return response


class DataRetentionPolicyViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet pour les politiques de rétention (lecture seule pour utilisateurs)
    Exigence: 45.6
    """
    serializer_class = DataRetentionPolicySerializer
    permission_classes = [IsAuthenticated]
    queryset = DataRetentionPolicy.objects.filter(is_active=True)
