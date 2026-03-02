"""
Backend de stockage Cloudinary personnalisé
"""
from django.core.files.storage import Storage
from django.conf import settings
from django.core.files.base import File
from django.utils.deconstruct import deconstructible
import cloudinary
import cloudinary.uploader
import cloudinary.api
from typing import Optional
import os


@deconstructible
class CloudinaryStorage(Storage):
    """
    Backend de stockage personnalisé pour Cloudinary
    """
    
    def __init__(self):
        """Initialise la configuration Cloudinary"""
        cloudinary.config(
            cloud_name=getattr(settings, 'CLOUDINARY_CLOUD_NAME', ''),
            api_key=getattr(settings, 'CLOUDINARY_API_KEY', ''),
            api_secret=getattr(settings, 'CLOUDINARY_API_SECRET', ''),
            secure=True
        )
    
    def _save(self, name: str, content: File) -> str:
        """
        Sauvegarde un fichier sur Cloudinary
        
        Args:
            name: Nom du fichier
            content: Contenu du fichier
            
        Returns:
            str: Chemin du fichier sauvegardé
        """
        # Extraire le dossier et le nom de fichier
        folder = os.path.dirname(name)
        filename = os.path.basename(name)
        
        # Upload vers Cloudinary
        result = cloudinary.uploader.upload(
            content,
            folder=folder,
            public_id=os.path.splitext(filename)[0],
            resource_type='auto',
            overwrite=False,
            unique_filename=True
        )
        
        # Retourner le public_id comme chemin
        return result['public_id']
    
    def _open(self, name: str, mode: str = 'rb') -> File:
        """
        Ouvre un fichier depuis Cloudinary
        
        Args:
            name: Nom du fichier
            mode: Mode d'ouverture
            
        Returns:
            File: Fichier ouvert
        """
        # Cloudinary ne supporte pas l'ouverture directe
        # Retourner l'URL du fichier
        from django.core.files.base import ContentFile
        import requests
        
        url = self.url(name)
        response = requests.get(url)
        return ContentFile(response.content, name=name)
    
    def exists(self, name: str) -> bool:
        """
        Vérifie si un fichier existe sur Cloudinary
        
        Args:
            name: Nom du fichier
            
        Returns:
            bool: True si le fichier existe
        """
        try:
            cloudinary.api.resource(name)
            return True
        except cloudinary.api.NotFound:
            return False
        except Exception:
            return False
    
    def delete(self, name: str) -> None:
        """
        Supprime un fichier de Cloudinary
        
        Args:
            name: Nom du fichier
        """
        try:
            cloudinary.uploader.destroy(name)
        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Erreur suppression fichier Cloudinary {name}: {e}")
    
    def url(self, name: str) -> str:
        """
        Retourne l'URL publique d'un fichier
        
        Args:
            name: Nom du fichier
            
        Returns:
            str: URL du fichier
        """
        return cloudinary.utils.cloudinary_url(name, secure=True)[0]
    
    def size(self, name: str) -> int:
        """
        Retourne la taille d'un fichier
        
        Args:
            name: Nom du fichier
            
        Returns:
            int: Taille en octets
        """
        try:
            resource = cloudinary.api.resource(name)
            return resource.get('bytes', 0)
        except Exception:
            return 0
    
    def get_available_name(self, name: str, max_length: Optional[int] = None) -> str:
        """
        Retourne un nom de fichier disponible
        
        Args:
            name: Nom souhaité
            max_length: Longueur maximale
            
        Returns:
            str: Nom disponible
        """
        # Cloudinary gère automatiquement les noms uniques
        return name
