from django import forms
from django.contrib import admin
from .models import DocumentTemplate, DocumentTechnique, AchatDocument, DownloadLog


class DocumentTemplateForm(forms.ModelForm):
    class Meta:
        model = DocumentTemplate
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['variables_requises'].required = False

    def clean_variables_requises(self):
        val = self.cleaned_data.get('variables_requises')
        if val is None or val == '' or val == []:
            return []
        return val


@admin.register(DocumentTemplate)
class DocumentTemplateAdmin(admin.ModelAdmin):
    form = DocumentTemplateForm
    list_display = ['titre', 'type_document', 'format_fichier', 'version', 'created_at']
    list_filter = ['type_document', 'format_fichier']
    search_fields = ['titre', 'description']
    ordering = ['-created_at']


@admin.register(DocumentTechnique)
class DocumentTechniqueAdmin(admin.ModelAdmin):
    list_display = ['titre', 'culture', 'prix', 'canton', 'actif', 'created_at']
    list_filter = ['actif', 'culture', 'region', 'prefecture']
    search_fields = ['titre', 'description', 'culture']
    ordering = ['-created_at']


@admin.register(AchatDocument)
class AchatDocumentAdmin(admin.ModelAdmin):
    list_display = ['acheteur', 'document', 'transaction', 'nombre_telechargements', 'expiration_lien', 'created_at']
    list_filter = ['created_at']
    search_fields = ['acheteur__username', 'acheteur__email', 'document__titre']
    readonly_fields = ['lien_telechargement', 'expiration_lien', 'nombre_telechargements', 'created_at', 'updated_at']
    ordering = ['-created_at']
    
    def has_add_permission(self, request):
        """Empêcher la création manuelle d'achats (créés automatiquement par webhook)"""
        return False


@admin.register(DownloadLog)
class DownloadLogAdmin(admin.ModelAdmin):
    list_display = ['achat', 'ip_address', 'timestamp']
    list_filter = ['timestamp']
    search_fields = ['achat__document__titre', 'ip_address']
    readonly_fields = ['achat', 'ip_address', 'timestamp', 'created_at', 'updated_at']
    ordering = ['-timestamp']
    
    def has_add_permission(self, request):
        """Les logs sont créés automatiquement"""
        return False
    
    def has_change_permission(self, request, obj=None):
        """Les logs ne peuvent pas être modifiés"""
        return False
