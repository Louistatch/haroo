from rest_framework import serializers
from .models import PreventeAgricole, EngagementPrevente
from apps.locations.models import Canton


class PreventeListSerializer(serializers.ModelSerializer):
    exploitant_nom = serializers.CharField(source='exploitant.get_full_name', read_only=True)
    canton_nom = serializers.CharField(source='canton_production.nom', read_only=True)

    class Meta:
        model = PreventeAgricole
        fields = [
            'id', 'exploitant_nom', 'culture', 'quantite_estimee', 
            'date_recolte_prevue', 'prix_par_tonne', 'montant_total', 
            'canton_nom', 'statut', 'description', 'created_at'
        ]


class PreventeDetailSerializer(serializers.ModelSerializer):
    exploitant_nom = serializers.CharField(source='exploitant.get_full_name', read_only=True)
    canton_nom = serializers.CharField(source='canton_production.nom', read_only=True)

    class Meta:
        model = PreventeAgricole
        fields = [
            'id', 'exploitant', 'exploitant_nom', 'culture', 'quantite_estimee', 
            'date_recolte_prevue', 'prix_par_tonne', 'montant_total', 
            'canton_nom', 'canton_production', 'statut', 'description', 
            'created_at', 'updated_at'
        ]


class PreventeCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = PreventeAgricole
        fields = [
            'culture', 'quantite_estimee', 'date_recolte_prevue', 
            'prix_par_tonne', 'canton_production', 'description'
        ]

    def validate_date_recolte_prevue(self, value):
        from datetime import date, timedelta
        if value < date.today() + timedelta(days=30):
            raise serializers.ValidationError("La date de récolte prévue doit être au moins 30 jours dans le futur.")
        return value


class EngagementSerializer(serializers.ModelSerializer):
    acheteur_nom = serializers.CharField(source='acheteur.get_full_name', read_only=True)
    prevente_culture = serializers.CharField(source='prevente.culture', read_only=True)

    class Meta:
        model = EngagementPrevente
        fields = [
            'id', 'prevente', 'prevente_culture', 'acheteur', 'acheteur_nom', 
            'quantite_engagee', 'montant_total', 'acompte_20', 
            'transaction_acompte', 'statut', 'date_livraison', 'created_at'
        ]
        read_only_fields = ['acheteur', 'montant_total', 'acompte_20', 'statut', 'transaction_acompte']

    def validate_quantite_engagee(self, value):
        prevente = self.initial_data.get('prevente')
        if prevente:
            try:
                p = PreventeAgricole.objects.get(id=prevente)
                if value > p.quantite_estimee:
                    raise serializers.ValidationError("La quantité engagée ne peut pas dépasser la quantité estimée de la prévente.")
            except PreventeAgricole.DoesNotExist:
                pass
        return value
