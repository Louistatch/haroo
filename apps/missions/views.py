"""
Vues pour la gestion des missions
"""
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from django.db import transaction as db_transaction

from .models import Mission
from .serializers import (
    MissionCreateSerializer,
    MissionDetailSerializer,
    MissionListSerializer,
    MissionAcceptSerializer,
    MissionCompleteSerializer
)
from .permissions import IsExploitantVerifie, IsAgronomeValide, IsMissionParticipant


class MissionViewSet(viewsets.ModelViewSet):
    """
    ViewSet pour la gestion des missions
    """
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """Retourner les missions de l'utilisateur"""
        user = self.request.user
        
        # Les exploitants voient leurs missions créées
        # Les agronomes voient leurs missions reçues
        if hasattr(user, 'exploitant_profile'):
            return Mission.objects.filter(exploitant=user).select_related(
                'exploitant', 'agronome', 'transaction'
            )
        elif hasattr(user, 'agronome_profile'):
            return Mission.objects.filter(agronome=user).select_related(
                'exploitant', 'agronome', 'transaction'
            )
        
        return Mission.objects.none()
    
    def get_serializer_class(self):
        """Retourner le serializer approprié"""
        if self.action == 'create':
            return MissionCreateSerializer
        elif self.action == 'list':
            return MissionListSerializer
        elif self.action == 'accept':
            return MissionAcceptSerializer
        elif self.action == 'complete':
            return MissionCompleteSerializer
        return MissionDetailSerializer
    
    def get_permissions(self):
        """Permissions spécifiques par action"""
        if self.action == 'create':
            return [IsAuthenticated(), IsExploitantVerifie()]
        elif self.action == 'accept':
            return [IsAuthenticated(), IsAgronomeValide(), IsMissionParticipant()]
        elif self.action == 'complete':
            return [IsAuthenticated(), IsMissionParticipant()]
        return super().get_permissions()
    
    def create(self, request, *args, **kwargs):
        """
        Créer une nouvelle mission
        POST /api/v1/missions/create
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        # Créer la mission
        mission = serializer.save()
        
        # Retourner les détails de la mission créée
        detail_serializer = MissionDetailSerializer(mission)
        return Response(
            detail_serializer.data,
            status=status.HTTP_201_CREATED
        )
    
    @action(detail=True, methods=['post'], url_path='accept')
    def accept(self, request, pk=None):
        """
        Accepter une mission
        POST /api/v1/missions/{id}/accept
        
        Après acceptation, l'exploitant doit payer avant que la mission ne commence.
        Le paiement sera bloqué en escrow jusqu'à la fin de la mission.
        """
        mission = self.get_object()
        
        # Vérifier que la mission est en statut DEMANDE
        if mission.statut != 'DEMANDE':
            return Response(
                {'error': 'Cette mission ne peut pas être acceptée (statut invalide)'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Vérifier que l'utilisateur est bien l'agronome de la mission
        if mission.agronome != request.user:
            return Response(
                {'error': 'Vous n\'êtes pas l\'agronome de cette mission'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Mettre à jour le statut à ACCEPTEE
        # L'exploitant devra maintenant payer pour que la mission passe à EN_COURS
        with db_transaction.atomic():
            mission.statut = 'ACCEPTEE'
            mission.save()
        
        # Retourner les détails de la mission avec instructions de paiement
        serializer = MissionDetailSerializer(mission)
        response_data = serializer.data
        response_data['message'] = (
            "Mission acceptée. L'exploitant doit maintenant effectuer le paiement "
            "pour que la mission puisse commencer. Le paiement sera bloqué en escrow "
            "jusqu'à la fin de la mission."
        )
        response_data['payment_required'] = True
        response_data['payment_amount'] = float(mission.budget_propose)
        
        return Response(response_data)
    
    @action(detail=True, methods=['post'], url_path='complete')
    def complete(self, request, pk=None):
        """
        Marquer une mission comme terminée et libérer le paiement en escrow
        POST /api/v1/missions/{id}/complete
        
        Lorsque l'exploitant confirme la fin de la mission, le paiement bloqué
        en escrow est libéré et transféré à l'agronome moins la commission de 10%.
        """
        mission = self.get_object()
        
        # Vérifier que la mission est en statut EN_COURS ou ACCEPTEE
        if mission.statut not in ['ACCEPTEE', 'EN_COURS']:
            return Response(
                {'error': 'Cette mission ne peut pas être terminée (statut invalide)'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Vérifier que l'utilisateur est l'exploitant de la mission
        if mission.exploitant != request.user:
            return Response(
                {'error': 'Seul l\'exploitant peut marquer la mission comme terminée'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Vérifier qu'il y a une transaction et un paiement
        if not mission.transaction:
            return Response(
                {
                    'error': 'Aucun paiement associé à cette mission. '
                             'Le paiement doit être effectué avant de terminer la mission.'
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Vérifier que le paiement est réussi
        if mission.transaction.statut != 'SUCCESS':
            return Response(
                {
                    'error': f'Le paiement n\'est pas confirmé (statut: {mission.transaction.get_statut_display()}). '
                             'Veuillez attendre la confirmation du paiement.'
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            # Libérer le paiement en escrow
            from apps.payments.services import EscrowService
            
            escrow = EscrowService.get_escrow_by_transaction(str(mission.transaction.id))
            
            if not escrow:
                return Response(
                    {
                        'error': 'Aucun compte escrow trouvé pour cette mission. '
                                 'Veuillez contacter le support.'
                    },
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
            
            if escrow.statut != 'BLOQUE':
                return Response(
                    {
                        'error': f'Le paiement a déjà été traité (statut: {escrow.get_statut_display()})'
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Libérer l'escrow et transférer à l'agronome
            with db_transaction.atomic():
                release_result = EscrowService.release_escrow(escrow.id)
                
                # Mettre à jour le statut de la mission
                mission.statut = 'TERMINEE'
                mission.save()
            
            # Retourner les détails de la mission avec informations de paiement
            serializer = MissionDetailSerializer(mission)
            response_data = serializer.data
            response_data['message'] = (
                f"Mission terminée avec succès. Le paiement de {release_result['montant_net']} FCFA "
                f"(montant net après commission de {release_result['commission']} FCFA) "
                f"a été transféré à l'agronome."
            )
            response_data['payment_released'] = True
            response_data['payment_details'] = {
                'montant_brut': release_result['montant_brut'],
                'commission': release_result['commission'],
                'montant_net': release_result['montant_net'],
                'date_liberation': release_result['date_liberation']
            }
            
            return Response(response_data)
            
        except ValueError as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Erreur lors de la libération de l'escrow: {str(e)}")
            return Response(
                {
                    'error': 'Une erreur est survenue lors du traitement du paiement. '
                             'Veuillez contacter le support.'
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
