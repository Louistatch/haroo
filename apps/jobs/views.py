from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from django.db import transaction
from django.utils import timezone
from decimal import Decimal
from .models import (
    OffreEmploiSaisonnier, ContratSaisonnier, HeuresTravaillees,
    AnnonceCollective, ParticipationAnnonce, AnnonceOuvrier, SEUIL_HECTARES
)
from .serializers import (
    OffreListSerializer, OffreDetailSerializer, OffreCreateSerializer,
    ContratSerializer, HeuresSerializer,
    AnnonceCollectiveListSerializer, AnnonceCollectiveDetailSerializer,
    AnnonceCollectiveCreateSerializer, ParticipationSerializer
)


def get_exploitant_superficie(user):
    """Retourne la superficie de l'exploitant ou 0."""
    try:
        return user.exploitant_profile.superficie_totale
    except Exception:
        return Decimal('0')


def exploitant_peut_publier_directement(user):
    """
    Un exploitant peut publier directement s'il a >= 10 ha
    ET est vérifié par l'admin.
    """
    try:
        profile = user.exploitant_profile
        return (
            profile.superficie_totale >= SEUIL_HECTARES
            and profile.statut_verification == 'VERIFIE'
        )
    except Exception:
        return False


def _check_profil_complet(user):
    """Vérifie que l'exploitant a rempli son profil (canton + superficie)."""
    try:
        p = user.exploitant_profile
        return bool(p.canton_principal_id and p.superficie_totale > 0)
    except Exception:
        return False


class IsExploitant(permissions.BasePermission):
    message = "Vous devez être un exploitant."

    def has_permission(self, request, view):
        return (
            request.user.is_authenticated
            and getattr(request.user, 'user_type', '') == 'EXPLOITANT'
        )


class IsOuvrier(permissions.BasePermission):
    def has_permission(self, request, view):
        return (
            request.user.is_authenticated
            and getattr(request.user, 'user_type', '') == 'OUVRIER'
        )


class OffreEmploiViewSet(viewsets.ModelViewSet):
    """Gestion des offres d'emploi saisonnier."""
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        qs = OffreEmploiSaisonnier.objects.all().select_related('exploitant', 'canton')
        user = self.request.user
        
        # Filtrage par canton pour les ouvriers
        if getattr(user, 'user_type', '') == 'OUVRIER':
            try:
                ouvrier_profile = user.ouvrier_profile
                cantons_ids = list(ouvrier_profile.cantons_disponibles.values_list('id', flat=True))
                if cantons_ids:
                    qs = qs.filter(canton_id__in=cantons_ids)
            except Exception:
                pass
        
        if self.request.query_params.get('mine') == 'true':
            qs = qs.filter(exploitant=self.request.user)
        elif self.action == 'list':
            qs = qs.filter(statut='OUVERTE')
        type_travail = self.request.query_params.get('type_travail')
        if type_travail:
            qs = qs.filter(type_travail=type_travail)
        return qs

    def get_serializer_class(self):
        if self.action == 'list':
            return OffreListSerializer
        if self.action == 'create':
            return OffreCreateSerializer
        return OffreDetailSerializer

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy', 'annuler']:
            return [permissions.IsAuthenticated(), IsExploitant()]
        if self.action == 'postuler':
            return [permissions.IsAuthenticated(), IsOuvrier()]
        return super().get_permissions()

    def create(self, request, *args, **kwargs):
        """
        Création d'offre : seuls les exploitants >= 10 ha vérifiés
        peuvent publier directement. Sinon → erreur avec redirect vers annonce.
        """
        if not _check_profil_complet(request.user):
            return Response({
                'error': 'profil_incomplet',
                'detail': (
                    "Veuillez d'abord compléter votre profil d'exploitation "
                    "(localisation, superficie) avant de publier."
                ),
            }, status=status.HTTP_403_FORBIDDEN)
        if not exploitant_peut_publier_directement(request.user):
            return Response({
                'error': 'publication_directe_impossible',
                'detail': (
                    "Votre exploitation doit avoir au moins 10 hectares et être "
                    "vérifiée par l'administration pour publier directement. "
                    "Veuillez créer une annonce collective."
                ),
                'superficie': str(get_exploitant_superficie(request.user)),
                'seuil': str(SEUIL_HECTARES),
            }, status=status.HTTP_403_FORBIDDEN)
        return super().create(request, *args, **kwargs)

    def perform_create(self, serializer):
        serializer.save(exploitant=self.request.user)

    @action(detail=False, methods=['get'], url_path='eligibilite')
    def check_eligibilite(self, request):
        """Vérifie si l'exploitant peut publier directement."""
        user = request.user
        superficie = get_exploitant_superficie(user)
        verifie = False
        profil_complet = False
        canton_id = None
        canton_nom = ''
        try:
            profile = user.exploitant_profile
            verifie = profile.statut_verification == 'VERIFIE'
            profil_complet = bool(
                profile.canton_principal_id
                and profile.superficie_totale > 0
            )
            if profile.canton_principal_id:
                canton_id = profile.canton_principal_id
                canton_nom = profile.canton_principal.nom
        except Exception:
            pass

        return Response({
            'peut_publier_directement': exploitant_peut_publier_directement(user),
            'superficie': str(superficie),
            'seuil': str(SEUIL_HECTARES),
            'verifie': verifie,
            'profil_complet': profil_complet,
            'canton_id': canton_id,
            'canton_nom': canton_nom,
        })

    @action(detail=True, methods=['post'])
    def postuler(self, request, pk=None):
        offre = self.get_object()
        if offre.statut != 'OUVERTE':
            return Response({'error': "Cette offre n'est plus ouverte"}, status=status.HTTP_400_BAD_REQUEST)
        if offre.postes_pourvus >= offre.nombre_postes:
            return Response({'error': 'Tous les postes sont pourvus'}, status=status.HTTP_400_BAD_REQUEST)
        if ContratSaisonnier.objects.filter(offre=offre, ouvrier=request.user).exists():
            return Response({'error': 'Vous avez déjà postulé à cette offre'}, status=status.HTTP_400_BAD_REQUEST)

        with transaction.atomic():
            contrat = ContratSaisonnier.objects.create(
                offre=offre, ouvrier=request.user, exploitant=offre.exploitant,
                date_debut=offre.date_debut, date_fin=offre.date_fin,
                salaire_horaire=offre.salaire_horaire, statut='SIGNE'
            )
            offre.postes_pourvus += 1
            if offre.postes_pourvus >= offre.nombre_postes:
                offre.statut = 'POURVUE'
            offre.save()

        return Response(ContratSerializer(contrat).data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['post'])
    def annuler(self, request, pk=None):
        offre = self.get_object()
        if offre.exploitant != request.user:
            return Response({'error': 'Non autorisé'}, status=status.HTTP_403_FORBIDDEN)
        offre.statut = 'EXPIREE'
        offre.save()
        return Response({'status': 'Offre annulée'})


class AnnonceCollectiveViewSet(viewsets.ModelViewSet):
    """
    Annonces collectives pour les exploitants < 10 ha.
    Durée 2 jours. Si le quota n'est pas atteint, l'annonce expire.
    """
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        qs = AnnonceCollective.objects.all().select_related('createur', 'canton')

        # Auto-expirer les annonces dépassées
        AnnonceCollective.objects.filter(
            statut='EN_ATTENTE',
            date_expiration__lt=timezone.now()
        ).update(statut='EXPIREE')

        mine = self.request.query_params.get('mine')
        if mine == 'true':
            qs = qs.filter(
                participations__exploitant=self.request.user
            ).distinct() | qs.filter(createur=self.request.user)
            return qs.distinct()

        canton_id = self.request.query_params.get('canton')
        if canton_id:
            qs = qs.filter(canton_id=canton_id)

        if self.action == 'list':
            qs = qs.filter(statut='EN_ATTENTE')

        return qs

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return AnnonceCollectiveDetailSerializer
        if self.action == 'create':
            return AnnonceCollectiveCreateSerializer
        return AnnonceCollectiveListSerializer

    def get_permissions(self):
        if self.action in ['create', 'rejoindre']:
            return [permissions.IsAuthenticated(), IsExploitant()]
        return super().get_permissions()

    def create(self, request, *args, **kwargs):
        if not _check_profil_complet(request.user):
            return Response({
                'error': 'profil_incomplet',
                'detail': (
                    "Veuillez d'abord compléter votre profil d'exploitation "
                    "(localisation, superficie) avant de créer une annonce."
                ),
            }, status=status.HTTP_403_FORBIDDEN)
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        superficie = get_exploitant_superficie(request.user)

        with transaction.atomic():
            annonce = serializer.save(
                createur=request.user,
                superficie_cumulee=superficie,
            )
            # Le créateur est automatiquement participant
            ParticipationAnnonce.objects.create(
                annonce=annonce,
                exploitant=request.user,
                superficie_apportee=superficie,
            )
            # Si le créateur a déjà >= seuil, valider directement
            if annonce.quota_atteint:
                self._publier_annonce(annonce)

        out = AnnonceCollectiveDetailSerializer(annonce, context={'request': request})
        return Response(out.data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['post'])
    def rejoindre(self, request, pk=None):
        """Un exploitant de la même zone rejoint l'annonce."""
        annonce = self.get_object()

        if annonce.statut != 'EN_ATTENTE':
            return Response({'error': "Cette annonce n'accepte plus de participants."},
                            status=status.HTTP_400_BAD_REQUEST)
        if annonce.est_expiree:
            annonce.statut = 'EXPIREE'
            annonce.save()
            return Response({'error': "Cette annonce a expiré."}, status=status.HTTP_400_BAD_REQUEST)
        if ParticipationAnnonce.objects.filter(annonce=annonce, exploitant=request.user).exists():
            return Response({'error': "Vous participez déjà à cette annonce."},
                            status=status.HTTP_400_BAD_REQUEST)

        superficie = get_exploitant_superficie(request.user)
        if superficie <= 0:
            return Response({
                'error': "Veuillez d'abord renseigner votre superficie dans votre profil."
            }, status=status.HTTP_400_BAD_REQUEST)

        with transaction.atomic():
            ParticipationAnnonce.objects.create(
                annonce=annonce,
                exploitant=request.user,
                superficie_apportee=superficie,
            )
            annonce.superficie_cumulee += superficie
            annonce.save()

            if annonce.quota_atteint:
                self._publier_annonce(annonce)

        out = AnnonceCollectiveDetailSerializer(annonce, context={'request': request})
        return Response(out.data)

    def _publier_annonce(self, annonce):
        """Convertit l'annonce collective en offre d'emploi publiée."""
        offre = OffreEmploiSaisonnier.objects.create(
            exploitant=annonce.createur,
            type_travail=annonce.type_travail,
            description=annonce.description,
            canton=annonce.canton,
            date_debut=annonce.date_debut,
            date_fin=annonce.date_fin,
            salaire_horaire=annonce.salaire_horaire,
            nombre_postes=annonce.nombre_postes,
            est_collective=True,
        )
        annonce.statut = 'VALIDEE'
        annonce.offre_generee = offre
        annonce.save()


class ContratSaisonnierViewSet(viewsets.ModelViewSet):
    """Gestion des contrats saisonniers."""
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = ContratSerializer

    def get_queryset(self):
        user = self.request.user
        user_type = getattr(user, 'user_type', '')
        if user_type == 'EXPLOITANT':
            return ContratSaisonnier.objects.filter(exploitant=user).select_related('offre', 'ouvrier', 'exploitant')
        if user_type == 'OUVRIER':
            return ContratSaisonnier.objects.filter(ouvrier=user).select_related('offre', 'ouvrier', 'exploitant')
        return ContratSaisonnier.objects.none()

    @action(detail=True, methods=['post'])
    def log_heures(self, request, pk=None):
        contrat = self.get_object()
        if contrat.ouvrier != request.user:
            return Response({'error': "Seul l'ouvrier peut déclarer ses heures"}, status=status.HTTP_403_FORBIDDEN)
        if contrat.statut not in ('EN_COURS', 'SIGNE'):
            return Response({'error': 'Contrat non actif'}, status=status.HTTP_400_BAD_REQUEST)

        serializer = HeuresSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

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
            return Response({'error': "Seul l'exploitant peut valider les heures"}, status=status.HTTP_403_FORBIDDEN)

        heures_id = request.data.get('heures_id')
        heures_obj = get_object_or_404(HeuresTravaillees, id=heures_id, contrat=contrat)

        action_val = request.data.get('action')
        if action_val == 'VALIDER':
            heures_obj.statut_validation = 'VALIDEE'
        elif action_val == 'CONTESTER':
            heures_obj.statut_validation = 'CONTESTEE'
        else:
            return Response({'error': 'Action invalide'}, status=status.HTTP_400_BAD_REQUEST)

        heures_obj.save()
        return Response({'status': 'Heures mises à jour'})



class AnnonceOuvrierViewSet(viewsets.ModelViewSet):
    """
    Annonces de disponibilité créées par les ouvriers.
    Les ouvriers proposent leurs services aux exploitants.
    """
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        from .models import AnnonceOuvrier
        qs = AnnonceOuvrier.objects.all().prefetch_related('cantons_disponibles')
        
        # Auto-expirer les annonces
        AnnonceOuvrier.objects.filter(
            statut='ACTIVE',
            date_expiration__lt=timezone.now()
        ).update(statut='EXPIREE')
        
        # Filtrer par canton pour les exploitants
        user = self.request.user
        if getattr(user, 'user_type', '') == 'EXPLOITANT':
            try:
                exploitant_profile = user.exploitant_profile
                if exploitant_profile.canton_principal_id:
                    qs = qs.filter(
                        cantons_disponibles__id=exploitant_profile.canton_principal_id
                    ).distinct()
            except Exception:
                pass
        
        # Mes annonces
        mine = self.request.query_params.get('mine')
        if mine == 'true':
            qs = qs.filter(ouvrier=user)
        elif self.action == 'list':
            # Liste publique = annonces actives uniquement
            qs = qs.filter(statut='ACTIVE')
        
        return qs

    def get_serializer_class(self):
        from .serializers import (
            AnnonceOuvrierListSerializer,
            AnnonceOuvrierDetailSerializer,
            AnnonceOuvrierCreateSerializer
        )
        if self.action == 'retrieve':
            return AnnonceOuvrierDetailSerializer
        if self.action == 'create':
            return AnnonceOuvrierCreateSerializer
        return AnnonceOuvrierListSerializer

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [permissions.IsAuthenticated(), IsOuvrier()]
        return super().get_permissions()

    def perform_create(self, serializer):
        serializer.save(ouvrier=self.request.user)

    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated, IsOuvrier])
    def rejoindre(self, request, pk=None):
        """
        Permet à un ouvrier de rejoindre une annonce collective d'équipe.
        """
        from .models import AnnonceOuvrier
        annonce = self.get_object()
        
        if annonce.type_annonce != 'COLLECTIVE':
            return Response(
                {'error': 'Cette annonce n\'est pas une annonce collective'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if annonce.statut != 'EN_ATTENTE':
            return Response(
                {'error': 'Cette annonce n\'accepte plus de nouveaux membres'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if request.user == annonce.ouvrier:
            return Response(
                {'error': 'Vous êtes déjà le créateur de cette annonce'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Vérifier si l'utilisateur a déjà rejoint
        membres = annonce.membres_rejoints or []
        if any(m.get('user_id') == request.user.id for m in membres):
            return Response(
                {'error': 'Vous avez déjà rejoint cette annonce'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Ajouter le membre
        membres.append({
            'user_id': request.user.id,
            'nom': request.user.last_name,
            'prenom': request.user.first_name,
            'telephone': getattr(request.user, 'telephone', ''),
            'date_rejointe': timezone.now().isoformat()
        })
        
        annonce.membres_rejoints = membres
        annonce.nb_membres_actuels = len(membres) + 1  # +1 pour le créateur
        annonce.save()
        
        return Response({
            'message': 'Vous avez rejoint l\'équipe avec succès',
            'nb_membres_actuels': annonce.nb_membres_actuels,
            'progression': annonce.progression
        })
    @action(detail=True, methods=['post'])
    def desactiver(self, request, pk=None):
        """Désactiver une annonce"""
        annonce = self.get_object()
        if annonce.ouvrier != request.user:
            return Response(
                {'error': 'Non autorisé'},
                status=status.HTTP_403_FORBIDDEN
            )
        annonce.statut = 'INACTIVE'
        annonce.save()
        return Response({'status': 'Annonce désactivée'})

    @action(detail=True, methods=['post'])
    def reactiver(self, request, pk=None):
        """Réactiver une annonce"""
        annonce = self.get_object()
        if annonce.ouvrier != request.user:
            return Response(
                {'error': 'Non autorisé'},
                status=status.HTTP_403_FORBIDDEN
            )
        if annonce.est_expiree:
            return Response(
                {'error': 'Cette annonce a expiré'},
                status=status.HTTP_400_BAD_REQUEST
            )
        annonce.statut = 'ACTIVE'
        annonce.save()
        return Response({'status': 'Annonce réactivée'})
