"""
Serializers pour les documents techniques
"""
from rest_framework import serializers
from .models import DocumentTechnique, DocumentTemplate, AchatDocument
from apps.locations.models import Region, Prefecture, Canton


class DocumentTechniqueListSerializer(serializers.ModelSerializer):
    """
    Serializer pour la liste des documents techniques
    """
    region_nom = serializers.CharField(source='region.nom', read_only=True)
    prefecture_nom = serializers.CharField(source='prefecture.nom', read_only=True)
    canton_nom = serializers.CharField(source='canton.nom', read_only=True)
    type_document = serializers.CharField(source='template.type_document', read_only=True)
    format_fichier = serializers.CharField(source='template.format_fichier', read_only=True)
    
    class Meta:
        model = DocumentTechnique
        fields = [
            'id',
            'titre',
            'description',
            'prix',
            'region',
            'region_nom',
            'prefecture',
            'prefecture_nom',
            'canton',
            'canton_nom',
            'culture',
            'type_document',
            'format_fichier',
            'created_at',
        ]
        read_only_fields = ['id', 'created_at']


class DocumentTechniqueDetailSerializer(serializers.ModelSerializer):
    """
    Serializer pour les détails d'un document technique
    """
    region_nom = serializers.CharField(source='region.nom', read_only=True)
    prefecture_nom = serializers.CharField(source='prefecture.nom', read_only=True)
    canton_nom = serializers.CharField(source='canton.nom', read_only=True)
    type_document = serializers.CharField(source='template.type_document', read_only=True)
    type_document_display = serializers.CharField(source='template.get_type_document_display', read_only=True)
    format_fichier = serializers.CharField(source='template.format_fichier', read_only=True)
    format_fichier_display = serializers.CharField(source='template.get_format_fichier_display', read_only=True)
    template_info = serializers.SerializerMethodField()
    
    class Meta:
        model = DocumentTechnique
        fields = [
            'id',
            'titre',
            'description',
            'prix',
            'region',
            'region_nom',
            'prefecture',
            'prefecture_nom',
            'canton',
            'canton_nom',
            'culture',
            'type_document',
            'type_document_display',
            'format_fichier',
            'format_fichier_display',
            'template_info',
            'actif',
            'created_at',
            'updated_at',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_template_info(self, obj):
        """
        Retourne les informations du template
        """
        return {
            'id': obj.template.id,
            'titre': obj.template.titre,
            'version': obj.template.version,
        }



class PurchaseDocumentSerializer(serializers.Serializer):
    """
    Serializer pour l'achat d'un document
    """
    document_id = serializers.IntegerField(required=True)
    callback_url = serializers.URLField(required=False, allow_blank=True)
    
    def validate_document_id(self, value):
        """Valider que le document existe et est actif"""
        try:
            document = DocumentTechnique.objects.get(id=value, actif=True)
        except DocumentTechnique.DoesNotExist:
            raise serializers.ValidationError("Document non trouvé ou inactif")
        return value


class AchatDocumentSerializer(serializers.ModelSerializer):
    """
    Serializer pour l'historique des achats de documents
    """
    acheteur = serializers.PrimaryKeyRelatedField(read_only=True)
    document_titre = serializers.CharField(source='document.titre', read_only=True)
    document_culture = serializers.CharField(source='document.culture', read_only=True)
    document_prix = serializers.DecimalField(
        source='document.prix',
        max_digits=10,
        decimal_places=2,
        read_only=True
    )
    format_fichier = serializers.CharField(
        source='document.template.format_fichier',
        read_only=True
    )
    transaction_statut = serializers.CharField(
        source='transaction.statut',
        read_only=True
    )
    transaction_id = serializers.UUIDField(source='transaction.id', read_only=True)
    lien_expire = serializers.SerializerMethodField()
    peut_regenerer = serializers.SerializerMethodField()
    
    class Meta:
        model = AchatDocument
        fields = [
            'id',
            'acheteur',
            'document',
            'document_titre',
            'document_culture',
            'document_prix',
            'format_fichier',
            'transaction_id',
            'transaction_statut',
            'lien_telechargement',
            'expiration_lien',
            'lien_expire',
            'peut_regenerer',
            'nombre_telechargements',
            'created_at',
        ]
        read_only_fields = ['id', 'created_at']
    
    def get_lien_expire(self, obj):
        """Vérifier si le lien a expiré"""
        from apps.documents.services.secure_download import SecureDownloadService
        return SecureDownloadService.is_link_expired(obj)
    
    def get_peut_regenerer(self, obj):
        """Vérifier si le lien peut être régénéré"""
        return obj.transaction.statut == 'SUCCESS'


class DownloadLinkSerializer(serializers.Serializer):
    """
    Serializer pour les liens de téléchargement
    """
    download_url = serializers.URLField(read_only=True)
    token = serializers.CharField(read_only=True)
    expiration = serializers.DateTimeField(read_only=True)
    document_id = serializers.IntegerField(read_only=True)
    document_titre = serializers.CharField(read_only=True)
    format_fichier = serializers.CharField(read_only=True)
