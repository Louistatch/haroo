"""
Serializers pour le découpage administratif du Togo
"""
from rest_framework import serializers
from .models import Region, Prefecture, Canton


class RegionSerializer(serializers.ModelSerializer):
    """Serializer pour les régions"""
    
    class Meta:
        model = Region
        fields = ['id', 'nom', 'code', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']


class PrefectureSerializer(serializers.ModelSerializer):
    """Serializer pour les préfectures"""
    region_nom = serializers.CharField(source='region.nom', read_only=True)
    
    class Meta:
        model = Prefecture
        fields = ['id', 'nom', 'code', 'region', 'region_nom', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']


class CantonSerializer(serializers.ModelSerializer):
    """Serializer pour les cantons"""
    prefecture_nom = serializers.CharField(source='prefecture.nom', read_only=True)
    region_nom = serializers.CharField(source='prefecture.region.nom', read_only=True)
    
    class Meta:
        model = Canton
        fields = [
            'id', 'nom', 'code', 'prefecture', 'prefecture_nom', 
            'region_nom', 'coordonnees_centre', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class RegionDetailSerializer(serializers.ModelSerializer):
    """Serializer détaillé pour les régions avec leurs préfectures"""
    prefectures = PrefectureSerializer(many=True, read_only=True)
    
    class Meta:
        model = Region
        fields = ['id', 'nom', 'code', 'prefectures', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']


class PrefectureDetailSerializer(serializers.ModelSerializer):
    """Serializer détaillé pour les préfectures avec leurs cantons"""
    cantons = CantonSerializer(many=True, read_only=True)
    region = RegionSerializer(read_only=True)
    
    class Meta:
        model = Prefecture
        fields = ['id', 'nom', 'code', 'region', 'cantons', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at']
