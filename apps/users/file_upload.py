"""
Service de gestion des uploads de fichiers pour les profils utilisateurs
Exigences: 31.1, 31.2, 31.3, 31.5, 31.6
"""
import os
from django.conf import settings
from django.core.files.uploadedfile import UploadedFile
from django.core.exceptions import ValidationError
from apps.core.file_security import AntivirusService, MimeTypeValidator
from apps.core.storage import SecureCloudStorage
import logging

logger = logging.getLogger(__name__)


class FileUploadService:
    """
    Service pour gérer l'upload de fichiers avec validation
    """
    
    # Extensions autorisées pour les photos de profil
    ALLOWED_IMAGE_EXTENSIONS = ['jpg', 'jpeg', 'png']
    
    # Taille maximale pour les photos de profil (5 Mo)
    MAX_IMAGE_SIZE = 5 * 1024 * 1024  # 5 MB
    
    # Types MIME autorisés pour les images
    ALLOWED_IMAGE_MIME_TYPES = [
        'image/jpeg',
        'image/png',
    ]
    
    @staticmethod
    def validate_image_file(file: UploadedFile) -> dict:
        """
        Valide un fichier image uploadé
        
        Args:
            file: Fichier uploadé
            
        Returns:
            dict: Résultat de la validation avec 'is_valid' et 'errors'
            
        Exigences: 31.2, 31.5, 31.6
        """
        errors = []
        
        # Vérifier que le fichier existe
        if not file:
            return {
                'is_valid': False,
                'errors': ['Aucun fichier fourni']
            }
        
        # Vérifier la taille du fichier (Exigence 31.2)
        if file.size > FileUploadService.MAX_IMAGE_SIZE:
            errors.append(
                f'Le fichier est trop volumineux. Taille maximale: '
                f'{FileUploadService.MAX_IMAGE_SIZE / (1024 * 1024):.0f} Mo'
            )
        
        # Vérifier l'extension du fichier (Exigence 31.1)
        file_extension = os.path.splitext(file.name)[1].lower().lstrip('.')
        if file_extension not in FileUploadService.ALLOWED_IMAGE_EXTENSIONS:
            errors.append(
                f'Extension de fichier non autorisée. Extensions autorisées: '
                f'{", ".join(FileUploadService.ALLOWED_IMAGE_EXTENSIONS)}'
            )
        
        # Vérifier le type MIME (Exigence 31.5)
        mime_validation = MimeTypeValidator.validate_mime_type(file, category='image')
        if not mime_validation['is_valid']:
            errors.extend(mime_validation['errors'])
        
        # Vérifier que le fichier est bien une image valide
        try:
            from PIL import Image
            from io import BytesIO
            
            # Essayer d'ouvrir l'image avec Pillow
            image = Image.open(BytesIO(file.read()))
            image.verify()
            
            # Réinitialiser le pointeur du fichier
            file.seek(0)
            
        except Exception as e:
            errors.append('Le fichier n\'est pas une image valide')
        
        # Scanner le fichier pour les virus (Exigence 31.5, 31.6)
        if len(errors) == 0:  # Seulement si les autres validations passent
            scan_result = AntivirusService.scan_file(file)
            if not scan_result['is_safe']:
                errors.append(
                    f'Fichier rejeté pour raison de sécurité: {scan_result["details"]}'
                )
                logger.warning(
                    f'Fichier malveillant détecté: {file.name} - {scan_result["details"]}'
                )
        
        return {
            'is_valid': len(errors) == 0,
            'errors': errors
        }
    
    @staticmethod
    def validate_document_file(file: UploadedFile) -> dict:
        """
        Valide un fichier document uploadé (PDF, Excel, Word)
        
        Args:
            file: Fichier uploadé
            
        Returns:
            dict: Résultat de la validation avec 'is_valid' et 'errors'
            
        Exigences: 31.1, 31.2, 31.5, 31.6
        """
        errors = []
        
        # Extensions autorisées pour les documents
        allowed_extensions = ['pdf', 'xlsx', 'xls', 'docx', 'doc']
        
        # Taille maximale pour les documents (10 Mo) - Exigence 31.2
        max_size = 10 * 1024 * 1024  # 10 MB
        
        # Vérifier que le fichier existe
        if not file:
            return {
                'is_valid': False,
                'errors': ['Aucun fichier fourni']
            }
        
        # Vérifier la taille du fichier
        if file.size > max_size:
            errors.append(
                f'Le fichier est trop volumineux. Taille maximale: '
                f'{max_size / (1024 * 1024):.0f} Mo'
            )
        
        # Vérifier l'extension du fichier
        file_extension = os.path.splitext(file.name)[1].lower().lstrip('.')
        if file_extension not in allowed_extensions:
            errors.append(
                f'Extension de fichier non autorisée. Extensions autorisées: '
                f'{", ".join(allowed_extensions)}'
            )
        
        # Vérifier le type MIME (Exigence 31.5)
        mime_validation = MimeTypeValidator.validate_mime_type(file, category='document')
        if not mime_validation['is_valid']:
            errors.extend(mime_validation['errors'])
        
        # Scanner le fichier pour les virus (Exigence 31.5, 31.6)
        if len(errors) == 0:  # Seulement si les autres validations passent
            scan_result = AntivirusService.scan_file(file)
            if not scan_result['is_safe']:
                errors.append(
                    f'Fichier rejeté pour raison de sécurité: {scan_result["details"]}'
                )
                logger.warning(
                    f'Fichier malveillant détecté: {file.name} - {scan_result["details"]}'
                )
        
        return {
            'is_valid': len(errors) == 0,
            'errors': errors
        }
    
    @staticmethod
    def sanitize_filename(filename: str) -> str:
        """
        Nettoie un nom de fichier pour éviter les problèmes de sécurité
        
        Args:
            filename: Nom du fichier original
            
        Returns:
            str: Nom de fichier nettoyé
            
        Exigence: 31.5
        """
        import re
        
        # Garder uniquement les caractères alphanumériques, tirets, underscores et points
        filename = re.sub(r'[^\w\s\-\.]', '', filename)
        
        # Remplacer les espaces par des underscores
        filename = filename.replace(' ', '_')
        
        # Limiter la longueur du nom de fichier
        name, ext = os.path.splitext(filename)
        if len(name) > 50:
            name = name[:50]
        
        return f"{name}{ext}"
    
    @staticmethod
    def get_upload_path(instance, filename: str, folder: str = 'profiles') -> str:
        """
        Génère un chemin d'upload unique pour un fichier
        
        Args:
            instance: Instance du modèle
            filename: Nom du fichier
            folder: Dossier de destination
            
        Returns:
            str: Chemin d'upload
            
        Exigence: 31.3
        """
        import uuid
        from datetime import datetime
        
        # Nettoyer le nom de fichier
        clean_filename = FileUploadService.sanitize_filename(filename)
        
        # Générer un nom unique
        ext = os.path.splitext(clean_filename)[1]
        unique_filename = f"{uuid.uuid4().hex}{ext}"
        
        # Organiser par date pour faciliter la gestion
        date_path = datetime.now().strftime('%Y/%m/%d')
        
        return os.path.join(folder, date_path, unique_filename)
