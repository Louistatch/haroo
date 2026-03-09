"""
Service de stockage cloud avec support AWS S3 et Cloudinary
Exigences: 31.3, 31.4
"""
import os
from datetime import timedelta
from typing import Optional
from django.conf import settings
from django.core.files.storage import Storage
from django.utils import timezone


class SecureCloudStorage:
    """
    Service abstrait pour gérer le stockage cloud sécurisé
    """
    
    @staticmethod
    def get_storage_backend() -> Storage:
        """
        Retourne le backend de stockage configuré
        
        Returns:
            Storage: Backend de stockage (Supabase, S3 ou Cloudinary)
        """
        use_supabase = getattr(settings, 'USE_SUPABASE', False)
        use_s3 = getattr(settings, 'USE_S3', False)
        use_cloudinary = getattr(settings, 'USE_CLOUDINARY', False)
        
        if use_supabase:
            from .supabase_storage import SupabaseStorage
            return SupabaseStorage()
        elif use_s3:
            from storages.backends.s3boto3 import S3Boto3Storage
            return S3Boto3Storage()
        elif use_cloudinary:
            from .cloudinary_storage import CloudinaryStorage
            return CloudinaryStorage()
        else:
            from django.core.files.storage import default_storage
            return default_storage
    
    @staticmethod
    def generate_signed_url(
        file_path: str,
        expiration_hours: int = 48
    ) -> Optional[str]:
        """
        Génère une URL signée avec expiration pour un fichier
        
        Args:
            file_path: Chemin du fichier dans le stockage
            expiration_hours: Durée de validité en heures (défaut: 48h)
            
        Returns:
            str: URL signée ou None si erreur
            
        Exigence: 31.4
        """
        use_supabase = getattr(settings, 'USE_SUPABASE', False)
        use_s3 = getattr(settings, 'USE_S3', False)
        use_cloudinary = getattr(settings, 'USE_CLOUDINARY', False)
        
        try:
            if use_supabase:
                return SecureCloudStorage._generate_supabase_signed_url(
                    file_path, expiration_hours
                )
            elif use_s3:
                return SecureCloudStorage._generate_s3_signed_url(
                    file_path, expiration_hours
                )
            elif use_cloudinary:
                return SecureCloudStorage._generate_cloudinary_signed_url(
                    file_path, expiration_hours
                )
            else:
                # En développement, retourner l'URL locale
                from django.urls import reverse
                return f"{settings.MEDIA_URL}{file_path}"
        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Erreur génération URL signée: {e}")
            return None
    
    @staticmethod
    def _generate_supabase_signed_url(
        file_path: str,
        expiration_hours: int
    ) -> str:
        """
        Génère une URL signée Supabase Storage
        """
        from .supabase_storage import SupabaseStorage
        storage = SupabaseStorage()
        return storage.generate_signed_url(file_path, expires_in=expiration_hours * 3600)

    @staticmethod
    def _generate_s3_signed_url(
        file_path: str,
        expiration_hours: int
    ) -> str:
        """
        Génère une URL signée S3
        
        Args:
            file_path: Chemin du fichier
            expiration_hours: Durée de validité en heures
            
        Returns:
            str: URL signée S3
        """
        import boto3
        from botocore.exceptions import ClientError
        
        s3_client = boto3.client(
            's3',
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            region_name=settings.AWS_S3_REGION_NAME
        )
        
        # Générer l'URL signée
        expiration_seconds = expiration_hours * 3600
        
        signed_url = s3_client.generate_presigned_url(
            'get_object',
            Params={
                'Bucket': settings.AWS_STORAGE_BUCKET_NAME,
                'Key': file_path
            },
            ExpiresIn=expiration_seconds
        )
        
        return signed_url
    
    @staticmethod
    def _generate_cloudinary_signed_url(
        file_path: str,
        expiration_hours: int
    ) -> str:
        """
        Génère une URL signée Cloudinary
        
        Args:
            file_path: Chemin du fichier
            expiration_hours: Durée de validité en heures
            
        Returns:
            str: URL signée Cloudinary
        """
        import cloudinary
        import cloudinary.utils
        
        # Configurer Cloudinary
        cloudinary.config(
            cloud_name=settings.CLOUDINARY_CLOUD_NAME,
            api_key=settings.CLOUDINARY_API_KEY,
            api_secret=settings.CLOUDINARY_API_SECRET
        )
        
        # Calculer le timestamp d'expiration
        expiration_timestamp = int(
            (timezone.now() + timedelta(hours=expiration_hours)).timestamp()
        )
        
        # Extraire le public_id du chemin
        public_id = os.path.splitext(file_path)[0]
        
        # Générer l'URL signée
        signed_url = cloudinary.utils.cloudinary_url(
            public_id,
            sign_url=True,
            type='authenticated',
            expires_at=expiration_timestamp
        )[0]
        
        return signed_url
    
    @staticmethod
    def delete_file(file_path: str) -> bool:
        """
        Supprime un fichier du stockage cloud
        
        Args:
            file_path: Chemin du fichier à supprimer
            
        Returns:
            bool: True si succès, False sinon
        """
        try:
            storage = SecureCloudStorage.get_storage_backend()
            if storage.exists(file_path):
                storage.delete(file_path)
                return True
            return False
        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Erreur suppression fichier {file_path}: {e}")
            return False
    
    @staticmethod
    def get_file_url(file_path: str, signed: bool = False) -> Optional[str]:
        """
        Retourne l'URL d'un fichier (signée ou publique)
        
        Args:
            file_path: Chemin du fichier
            signed: Si True, génère une URL signée
            
        Returns:
            str: URL du fichier ou None
        """
        if signed:
            return SecureCloudStorage.generate_signed_url(file_path)
        
        storage = SecureCloudStorage.get_storage_backend()
        try:
            return storage.url(file_path)
        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Erreur récupération URL fichier {file_path}: {e}")
            return None
