from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Card


class CardVerifyView(APIView):
    """
    Public endpoint — verifies a card number and returns profile + contextual data.
    Called by FaîtiereHub to serve non-FAITIERE card post-scan experiences.
    """
    authentication_classes = []
    permission_classes = []

    def get(self, request, card_number):
        # Normalize
        card_number = card_number.upper().strip()

        try:
            card = Card.objects.select_related(
                'ouvrier__user',
                'acheteur__user',
                'agronome__user',
            ).get(card_number=card_number)
        except Card.DoesNotExist:
            return Response(
                {'valid': False, 'error': 'Carte non trouvée'},
                status=status.HTTP_404_NOT_FOUND
            )

        if not card.is_active:
            return Response({
                'valid': False,
                'card_type': card.card_type,
                'card': {
                    'card_number': card.card_number,
                    'status': card.statut,
                    'expiry_date': str(card.expiry_date) if card.expiry_date else None,
                },
                'error': 'Carte expirée ou révoquée'
            }, status=status.HTTP_200_OK)

        response_data = {
            'valid': True,
            'card_type': card.card_type,
            'card': {
                'card_number': card.card_number,
                'status': card.statut,
                'expiry_date': str(card.expiry_date) if card.expiry_date else None,
                'created_at': card.created_at.isoformat(),
            }
        }

        if card.card_type == 'OUVRIER' and card.ouvrier:
            ouvrier = card.ouvrier
            user = ouvrier.user
            response_data['ouvrier'] = {
                'first_name': user.first_name,
                'last_name': user.last_name,
                'phone': user.phone_number,
                'photo_url': card.get_holder_photo(),
                'competences': ouvrier.competences if isinstance(ouvrier.competences, list) else [],
                'cantons_disponibles': list(ouvrier.cantons_disponibles.values_list('nom', flat=True)),
                'disponible': ouvrier.disponible,
                'tarif_journalier': None,
                'note_moyenne': float(ouvrier.note_moyenne),
                'nombre_avis': ouvrier.nombre_avis,
            }
            # Fetch open job offers in his cantons
            from apps.jobs.models import OffreEmploiSaisonnier
            cantons = ouvrier.cantons_disponibles.all()
            offres = OffreEmploiSaisonnier.objects.filter(
                canton__in=cantons, statut='OUVERTE'
            ).select_related('canton').order_by('-created_at')[:5]
            response_data['offres'] = [
                {
                    'id': str(o.id),
                    'titre': o.type_travail,
                    'culture': None,
                    'description': o.description,
                    'canton': str(o.canton),
                    'date_debut': str(o.date_debut),
                    'date_fin': str(o.date_fin),
                    'tarif_journalier': float(o.salaire_horaire) if o.salaire_horaire else None,
                    'nombre_ouvriers': o.nombre_postes,
                }
                for o in offres
            ]

        elif card.card_type == 'ACHETEUR' and card.acheteur:
            acheteur = card.acheteur
            user = acheteur.user
            response_data['acheteur'] = {
                'first_name': user.first_name,
                'last_name': user.last_name,
                'phone': user.phone_number,
                'photo_url': card.get_holder_photo(),
                'type_acheteur': acheteur.type_acheteur,
                'nom_organisation': None,
                'produits_interesses': acheteur.produits_interesses if isinstance(acheteur.produits_interesses, list) else [],
                'cantons_intervention': list(acheteur.cantons_intervention.values_list('nom', flat=True)),
            }
            # Fetch available pre-sales, optionally filtered by the buyer's prefecture
            from apps.presales.models import PreventeAgricole
            qs = PreventeAgricole.objects.filter(
                statut='DISPONIBLE'
            ).select_related('canton_production').order_by('-created_at')
            if acheteur.prefecture_id:
                qs = qs.filter(canton_production__prefecture_id=acheteur.prefecture_id)
            preventes = qs[:5]
            response_data['preventes'] = [
                {
                    'id': str(p.id),
                    'culture': p.culture,
                    'quantite_estimee': float(p.quantite_estimee),
                    'prix_par_kg': float(p.prix_par_tonne / 1000) if p.prix_par_tonne else 0,
                    'date_recolte_prevue': str(p.date_recolte_prevue),
                    'canton': str(p.canton_production),
                    'description': p.description or '',
                }
                for p in preventes
            ]

        elif card.card_type == 'AGRONOME' and card.agronome:
            agronome = card.agronome
            user = agronome.user
            # Safely resolve location names via the canton FK chain
            canton_name = None
            prefecture_name = None
            region_name = None
            if agronome.canton_rattachement_id:
                try:
                    canton = agronome.canton_rattachement
                    canton_name = str(canton)
                    prefecture_name = str(canton.prefecture)
                    region_name = str(canton.prefecture.region)
                except Exception:
                    pass
            response_data['agronome'] = {
                'first_name': user.first_name,
                'last_name': user.last_name,
                'phone': user.phone_number,
                'photo_url': card.get_holder_photo(),
                'specialisations': agronome.specialisations if isinstance(agronome.specialisations, list) else [],
                'canton': canton_name,
                'prefecture': prefecture_name,
                'region': region_name,
                'badge_valide': agronome.badge_valide,
                'statut_validation': agronome.statut_validation,
                'disponible_missions': True,
                'note_moyenne': float(agronome.note_moyenne),
                'nombre_missions': agronome.nombre_avis,
            }
            # Fetch pending missions assigned to this agronome
            # Mission.statut choices: DEMANDE, ACCEPTEE, REFUSEE, EN_COURS, TERMINEE, ANNULEE
            # We surface DEMANDE (open requests) and EN_COURS (active) missions
            from apps.missions.models import Mission
            missions_qs = Mission.objects.filter(
                agronome=agronome.user,
                statut__in=['DEMANDE', 'EN_COURS']
            ).select_related('exploitant').order_by('-created_at')[:5]
            response_data['missions'] = [
                {
                    'id': str(m.id),
                    'description': m.description,
                    'statut': m.statut,
                    'budget_propose': float(m.budget_propose) if m.budget_propose else None,
                    'date_debut': str(m.date_debut) if m.date_debut else None,
                    'date_fin': str(m.date_fin) if m.date_fin else None,
                    'exploitant': m.exploitant.get_full_name() if m.exploitant else None,
                }
                for m in missions_qs
            ]

        return Response(response_data)
