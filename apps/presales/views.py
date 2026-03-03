from rest_framework import viewsets, permissions, status, decorators
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from .models import PreventeAgricole, EngagementPrevente
from .serializers import (
    PreventeListSerializer, PreventeDetailSerializer, 
    PreventeCreateSerializer, EngagementSerializer
)
from apps.payments.models import Transaction
from decimal import Decimal


class PreventeViewSet(viewsets.ModelViewSet):
    """
    ViewSet pour gérer les préventes agricoles
    """
    queryset = PreventeAgricole.objects.all()

    def get_serializer_class(self):
        if self.action == 'list':
            return PreventeListSerializer
        if self.action == 'create':
            return PreventeCreateSerializer
        return PreventeDetailSerializer

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            permission_classes = [permissions.AllowAny]
        else:
            permission_classes = [permissions.IsAuthenticated]
        return [permission() for permission in permission_classes]

    def perform_create(self, serializer):
        # TODO: Vérifier que l'exploitant est vérifié
        serializer.save(exploitant=self.request.user)

    @decorators.action(detail=True, methods=['post'], url_path='annuler')
    def annuler(self, request, pk=None):
        prevente = self.get_object()
        if prevente.exploitant != request.user:
            return Response({"detail": "Vous n'avez pas l'autorisation d'annuler cette prévente."}, status=status.HTTP_403_FORBIDDEN)
        
        if prevente.statut not in ['DISPONIBLE']:
            return Response({"detail": "Cette prévente ne peut plus être annulée."}, status=status.HTTP_400_BAD_REQUEST)
        
        prevente.statut = 'ANNULEE'
        prevente.save()
        return Response({"status": "Prévente annulée"})

    @decorators.action(detail=True, methods=['post'], url_path='confirmer_livraison')
    def confirmer_livraison(self, request, pk=None):
        prevente = self.get_object()
        if prevente.exploitant != request.user:
            return Response({"detail": "Vous n'avez pas l'autorisation de confirmer la livraison de cette prévente."}, status=status.HTTP_403_FORBIDDEN)
        
        prevente.statut = 'LIVREE'
        prevente.save()
        
        # Mettre à jour les engagements
        prevente.engagements.filter(statut='ACOMPTE_PAYE').update(statut='LIVRAISON_CONFIRMEE')
        
        return Response({"status": "Livraison confirmée"})


class EngagementViewSet(viewsets.ModelViewSet):
    """
    ViewSet pour gérer les engagements sur les préventes
    """
    queryset = EngagementPrevente.objects.all()
    serializer_class = EngagementSerializer

    def get_queryset(self):
        return EngagementPrevente.objects.filter(acheteur=self.request.user)

    def create(self, request, *args, **kwargs):
        prevente_id = request.data.get('prevente')
        quantite = Decimal(request.data.get('quantite_engagee', 0))
        
        prevente = get_object_or_404(PreventeAgricole, id=prevente_id)
        
        if prevente.statut != 'DISPONIBLE':
            return Response({"detail": "Cette prévente n'est plus disponible."}, status=status.HTTP_400_BAD_REQUEST)
        
        montant_total = quantite * prevente.prix_par_tonne
        acompte_20 = montant_total * Decimal('0.20')
        
        # Création de l'engagement
        engagement = EngagementPrevente.objects.create(
            prevente=prevente,
            acheteur=request.user,
            quantite_engagee=quantite,
            montant_total=montant_total,
            acompte_20=acompte_20,
            statut='EN_ATTENTE'
        )
        
        # Initialisation de la transaction d'acompte
        transaction = Transaction.objects.create(
            utilisateur=request.user,
            type_transaction='PREVENTE',
            montant=acompte_20,
            statut='PENDING'
        )
        
        engagement.transaction_acompte = transaction
        engagement.save()
        
        # Mettre à jour le statut de la prévente si nécessaire
        # Si on engage toute la quantité, ou une partie significative
        # prevente.statut = 'ENGAGEE'
        # prevente.save()
        
        serializer = self.get_serializer(engagement)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @decorators.action(detail=True, methods=['post'], url_path='confirmer')
    def confirmer(self, request, pk=None):
        """
        Confirmation de l'engagement après paiement de l'acompte (simulé ici ou via webhook plus tard)
        """
        engagement = self.get_object()
        
        # Dans un vrai scénario, on vérifierait la transaction Fedapay
        if engagement.transaction_acompte and engagement.transaction_acompte.statut == 'SUCCESS':
            engagement.statut = 'ACOMPTE_PAYE'
            engagement.save()
            return Response({"status": "Engagement confirmé"})
        
        return Response({"detail": "Le paiement de l'acompte n'a pas encore été confirmé."}, status=status.HTTP_400_BAD_REQUEST)
