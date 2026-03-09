"""
Vues pour le système de notation
"""
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db.models import Q
from django.db import transaction
from .models import Notation, SignalementNotation
from .serializers import (
    NotationCreateSerializer,
    NotationListSerializer,
    NotationDetailSerializer,
    SignalementNotationSerializer
)
from .services import ReputationCalculator, ModerationService, QualityAlertService


class NotationViewSet(viewsets.ModelViewSet):
    """
    ViewSet pour la gestion des notations
    
    Endpoints:
    - POST /api/v1/ratings/create - Créer une notation
    - GET /api/v1/ratings/ - Lister les notations (avec filtres)
    - GET /api/v1/ratings/{id}/ - Détails d'une notation
    - POST /api/v1/ratings/{id}/report/ - Signaler une notation
    
    Exigences: 27.1, 27.2, 27.4, 27.5
    """
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """
        Filtrer les notations
        Exigence: 27.4 - Filtrer par note
        """
        queryset = Notation.objects.select_related(
            'notateur', 'note', 'mission'
        ).filter(statut='PUBLIE')
        
        # Filtrer par utilisateur noté
        user_id = self.request.query_params.get('user_id')
        if user_id:
            queryset = queryset.filter(note_id=user_id)
        
        # Filtrer par type (missions uniquement pour l'instant)
        type_filter = self.request.query_params.get('type')
        if type_filter == 'mission':
            queryset = queryset.filter(mission__isnull=False)
        
        # Filtrer par note (valeur)
        note_valeur = self.request.query_params.get('note')
        if note_valeur:
            try:
                queryset = queryset.filter(note_valeur=int(note_valeur))
            except ValueError:
                pass
        
        # Tri par date décroissante (Exigence 27.4)
        return queryset.order_by('-created_at')
    
    def get_serializer_class(self):
        """Retourner le serializer approprié selon l'action"""
        if self.action == 'create':
            return NotationCreateSerializer
        elif self.action == 'retrieve':
            return NotationDetailSerializer
        return NotationListSerializer
    
    @transaction.atomic
    def create(self, request, *args, **kwargs):
        """
        Créer une nouvelle notation
        Exigences: 27.1, 27.2
        """
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        # Créer la notation
        notation = serializer.save()
        
        # Mettre à jour la note moyenne de l'utilisateur noté
        ReputationCalculator.update_user_rating(notation.note)
        
        # Retourner la notation créée
        response_serializer = NotationDetailSerializer(notation)
        return Response(
            response_serializer.data,
            status=status.HTTP_201_CREATED
        )
    
    @action(detail=True, methods=['post'], url_path='report')
    def report(self, request, pk=None):
        """
        Signaler une notation comme inappropriée
        Exigence: 27.5
        """
        notation = self.get_object()
        
        serializer = SignalementNotationSerializer(
            data={'notation': notation.id, **request.data},
            context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        
        # Créer le signalement
        signalement = serializer.save()
        
        # Incrémenter le compteur de signalements
        notation.nombre_signalements += 1
        
        # Si plus de 3 signalements, marquer comme signalé
        if notation.nombre_signalements >= 3:
            notation.statut = 'SIGNALE'
        
        notation.save()
        
        return Response(
            {
                'message': 'Notation signalée avec succès',
                'signalement_id': signalement.id
            },
            status=status.HTTP_201_CREATED
        )


    @action(detail=False, methods=['get'], url_path='moderation-queue')
    def moderation_queue(self, request):
        """
        File d'attente de modération (admin uniquement)
        GET /api/v1/ratings/moderation-queue/
        """
        if not request.user.is_staff and request.user.user_type != 'ADMIN':
            return Response({'detail': 'Accès réservé aux administrateurs.'}, status=status.HTTP_403_FORBIDDEN)

        queue = ModerationService.get_moderation_queue()
        serializer = NotationDetailSerializer(queue, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['post'], url_path='moderate')
    def moderate(self, request, pk=None):
        """
        Modérer une notation (approuver/rejeter) - admin uniquement
        POST /api/v1/ratings/{id}/moderate/
        Body: {"action": "approve"} ou {"action": "reject"}
        """
        if not request.user.is_staff and request.user.user_type != 'ADMIN':
            return Response({'detail': 'Accès réservé aux administrateurs.'}, status=status.HTTP_403_FORBIDDEN)

        notation = self.get_object()
        action_type = request.data.get('action')

        if action_type not in ('approve', 'reject'):
            return Response({'detail': 'Action invalide. Utilisez "approve" ou "reject".'}, status=status.HTTP_400_BAD_REQUEST)

        result = ModerationService.moderate_notation(notation, action_type)
        serializer = NotationDetailSerializer(result)
        return Response(serializer.data)

    @action(detail=False, methods=['get'], url_path='quality-alerts')
    def quality_alerts(self, request):
        """
        Alertes qualité (utilisateurs avec moyenne < 2.5) - admin uniquement
        GET /api/v1/ratings/quality-alerts/
        """
        if not request.user.is_staff and request.user.user_type != 'ADMIN':
            return Response({'detail': 'Accès réservé aux administrateurs.'}, status=status.HTTP_403_FORBIDDEN)

        alerts = QualityAlertService.get_users_with_quality_alerts()
        data = [{
            'user_id': a['user'].id,
            'user_name': a['user'].get_full_name(),
            'type': a['type'],
            'note_moyenne': a['note_moyenne'],
            'nombre_avis': a['nombre_avis']
        } for a in alerts]
        return Response(data)

