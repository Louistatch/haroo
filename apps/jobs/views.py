from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.db import transaction
from django.utils import timezone
from .models import OffreEmploiSaisonnier, ContratSaisonnier, HeuresTravaillees
from .serializers import (
    OffreListSerializer, OffreDetailSerializer, OffreCreateSerializer,
    ContratSerializer, HeuresSerializer
)
from apps.missions.permissions import IsExploitantVerifie

class IsOuvrier(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and hasattr(request.user, 'ouvrier_profile')

class OffreEmploiViewSet(viewsets.ModelViewSet):
    """
    ViewSet pour la gestion des offres d'emploi saisonnier
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        if self.action == 'list':
            return OffreEmploiSaisonnier.objects.filter(statut='OUVERTE').select_related('exploitant', 'canton')
        return OffreEmploiSaisonnier.objects.all().select_related('exploitant', 'canton')

    def get_serializer_class(self):
        if self.action == 'list':
            return OffreListSerializer
        if self.action == 'create':
            return OffreCreateSerializer
        return OffreDetailSerializer

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy', 'annuler']:
            return [permissions.IsAuthenticated(), IsExploitantVerifie()]
        if self.action == 'postuler':
            return [permissions.IsAuthenticated(), IsOuvrier()]
        return super().get_permissions()

    def perform_create(self, serializer):
        serializer.save(exploitant=self.request.user)

    @action(detail=True, methods=['post'])
    def postuler(self, request, pk=None):
        offre = self.get_object()
        
        if offre.statut != 'OUVERTE':
            return Response({'error': 'Cette offre n\'est plus ouverte'}, status=status.HTTP_400_BAD_REQUEST)
        
        if offre.postes_pourvus >= offre.nombre_postes:
            return Response({'error': 'Tous les postes sont pourvus'}, status=status.HTTP_400_BAD_REQUEST)
        
        if ContratSaisonnier.objects.filter(offre=offre, ouvrier=request.user).exists():
            return Response({'error': 'Vous avez déjà postulé à cette offre'}, status=status.HTTP_400_BAD_REQUEST)
            
        with transaction.atomic():
            contrat = ContratSaisonnier.objects.create(
                offre=offre,
                ouvrier=request.user,
                exploitant=offre.exploitant,
                date_debut=offre.date_debut,
                date_fin=offre.date_fin,
                salaire_horaire=offre.salaire_horaire,
                statut='SIGNE'
            )
            
            offre.postes_pourvus += 1
            if offre.postes_pourvus >= offre.nombre_postes:
                offre.statut = 'POURVUE'
            offre.save()
            
        serializer = ContratSerializer(contrat)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['post'])
    def annuler(self, request, pk=None):
        offre = self.get_object()
        if offre.exploitant != request.user:
            return Response({'error': 'Non autorisé'}, status=status.HTTP_403_FORBIDDEN)
        
        offre.statut = 'EXPIREE'
        offre.save()
        return Response({'status': 'Offre annulée'})


class ContratSaisonnierViewSet(viewsets.ModelViewSet):
    """
    ViewSet pour la gestion des contrats saisonniers
    """
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = ContratSerializer

    def get_queryset(self):
        user = self.request.user
        if hasattr(user, 'exploitant_profile'):
            return ContratSaisonnier.objects.filter(exploitant=user).select_related('offre', 'ouvrier', 'exploitant')
        if hasattr(user, 'ouvrier_profile'):
            return ContratSaisonnier.objects.filter(ouvrier=user).select_related('offre', 'ouvrier', 'exploitant')
        return ContratSaisonnier.objects.none()

    @action(detail=True, methods=['post'])
    def log_heures(self, request, pk=None):
        contrat = self.get_object()
        if contrat.ouvrier != request.user:
            return Response({'error': 'Seul l\'ouvrier peut déclarer ses heures'}, status=status.HTTP_403_FORBIDDEN)
        
        if contrat.statut != 'EN_COURS' and contrat.statut != 'SIGNE':
            return Response({'error': 'Contrat non actif'}, status=status.HTTP_400_BAD_REQUEST)

        serializer = HeuresSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        # Vérifier la date (doit être dans la période du contrat)
        date_heures = serializer.validated_data['date']
        if date_heures < contrat.date_debut or date_heures > contrat.date_fin:
             return Response({'error': 'Date hors période de contrat'}, status=status.HTTP_400_BAD_REQUEST)

        heures = serializer.validated_data['heures']
        montant = heures * contrat.salaire_horaire
        
        serializer.save(contrat=contrat, montant_calcule=montant)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['post'])
    def valider_heures(self, request, pk=None):
        contrat = self.get_object()
        if contrat.exploitant != request.user:
            return Response({'error': 'Seul l\'exploitant peut valider les heures'}, status=status.HTTP_403_FORBIDDEN)
        
        heures_id = request.data.get('heures_id')
        heures_obj = get_object_or_404(HeuresTravaillees, id=heures_id, contrat=contrat)
        
        action_val = request.data.get('action') # 'VALIDER' or 'CONTESTER'
        if action_val == 'VALIDER':
            heures_obj.statut_validation = 'VALIDEE'
        elif action_val == 'CONTESTER':
            heures_obj.statut_validation = 'CONTESTEE'
        else:
            return Response({'error': 'Action invalide'}, status=status.HTTP_400_BAD_REQUEST)
        
        heures_obj.save()
        return Response({'status': 'Heures mises à jour'})
