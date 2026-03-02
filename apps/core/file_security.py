"""
Service de sécurité pour les fichiers uploadés
Exigences: 31.5, 31.6
"""
import os
import subprocess
from typing import Dict, Optional
from django.core.files.uploadedfile import UploadedFile
from django.conf import settings
import logging

logger = logging.getLogger(__name__)


class AntivirusService:
    """
    Service de scan antivirus pour les fichiers uploadés
    Exigence: 31.5, 31.6
    """
    
    @staticmethod
    def scan_file(file: UploadedFile) -> Dict[str, any]:
        """
        Scanne un fichier pour détecter les virus et malwares
        
        Args:
            file: Fichier uploadé à scanner
            
        Returns:
            dict: Résultat du scan avec 'is_safe', 'threat_found', 'details'
            
        Exigence: 31.5, 31.6
        """
        # Vérifier si ClamAV est disponible
        if AntivirusService._is_clamav_available():
            return AntivirusService._scan_with_clamav(file)
        else:
            # Fallback: scan basique par signatures
            logger.warning("ClamAV non disponible, utilisation du scan basique")
            return AntivirusService._basic_scan(file)
    
    @staticmethod
    def _is_clamav_available() -> bool:
        """
        Vérifie si ClamAV est installé et disponible
        
        Returns:
            bool: True si ClamAV est disponible
        """
        try:
            result = subprocess.run(
                ['clamscan', '--version'],
                capture_output=True,
                timeout=5
            )
            return result.returncode == 0
        except (FileNotFoundError, subprocess.TimeoutExpired):
            return False
    
    @staticmethod
    def _scan_with_clamav(file: UploadedFile) -> Dict[str, any]:
        """
        Scanne un fichier avec ClamAV
        
        Args:
            file: Fichier à scanner
            
        Returns:
            dict: Résultat du scan
        """
        import tempfile
        
        try:
            # Créer un fichier temporaire
            with tempfile.NamedTemporaryFile(delete=False) as temp_file:
                # Écrire le contenu du fichier uploadé
                for chunk in file.chunks():
                    temp_file.write(chunk)
                temp_file_path = temp_file.name
            
            # Réinitialiser le pointeur du fichier
            file.seek(0)
            
            # Scanner avec ClamAV
            result = subprocess.run(
                ['clamscan', '--no-summary', temp_file_path],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            # Supprimer le fichier temporaire
            os.unlink(temp_file_path)
            
            # Analyser le résultat
            # ClamAV retourne 0 si aucun virus, 1 si virus trouvé
            is_safe = result.returncode == 0
            threat_found = 'FOUND' in result.stdout
            
            return {
                'is_safe': is_safe and not threat_found,
                'threat_found': threat_found,
                'details': result.stdout.strip() if threat_found else 'Aucune menace détectée',
                'scanner': 'ClamAV'
            }
            
        except subprocess.TimeoutExpired:
            logger.error("Timeout lors du scan ClamAV")
            return {
                'is_safe': False,
                'threat_found': False,
                'details': 'Timeout lors du scan antivirus',
                'scanner': 'ClamAV'
            }
        except Exception as e:
            logger.error(f"Erreur lors du scan ClamAV: {e}")
            # En cas d'erreur, rejeter par sécurité
            return {
                'is_safe': False,
                'threat_found': False,
                'details': f'Erreur lors du scan: {str(e)}',
                'scanner': 'ClamAV'
            }
    
    @staticmethod
    def _basic_scan(file: UploadedFile) -> Dict[str, any]:
        """
        Scan basique par signatures de fichiers malveillants connus
        
        Args:
            file: Fichier à scanner
            
        Returns:
            dict: Résultat du scan
        """
        # Signatures de fichiers malveillants connus (exemples)
        malicious_signatures = [
            b'X5O!P%@AP[4\\PZX54(P^)7CC)7}$EICAR',  # EICAR test file
            b'MZ\x90\x00',  # Executable Windows (potentiellement dangereux)
        ]
        
        try:
            # Lire le début du fichier
            file.seek(0)
            file_header = file.read(1024)
            file.seek(0)
            
            # Vérifier les signatures
            for signature in malicious_signatures:
                if signature in file_header:
                    return {
                        'is_safe': False,
                        'threat_found': True,
                        'details': 'Signature malveillante détectée',
                        'scanner': 'Basic'
                    }
            
            # Vérifier les extensions dangereuses dans le contenu
            dangerous_extensions = [b'.exe', b'.bat', b'.cmd', b'.scr', b'.vbs']
            for ext in dangerous_extensions:
                if ext in file_header:
                    logger.warning(f"Extension dangereuse détectée dans {file.name}")
            
            return {
                'is_safe': True,
                'threat_found': False,
                'details': 'Aucune menace détectée (scan basique)',
                'scanner': 'Basic'
            }
            
        except Exception as e:
            logger.error(f"Erreur lors du scan basique: {e}")
            return {
                'is_safe': False,
                'threat_found': False,
                'details': f'Erreur lors du scan: {str(e)}',
                'scanner': 'Basic'
            }


class MimeTypeValidator:
    """
    Validateur de types MIME pour sécuriser les uploads
    Exigence: 31.1, 31.5
    """
    
    # Types MIME autorisés par catégorie
    ALLOWED_MIME_TYPES = {
        'image': [
            'image/jpeg',
            'image/png',
            'image/gif',
        ],
        'document': [
            'application/pdf',
            'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',  # .xlsx
            'application/vnd.ms-excel',  # .xls
            'application/vnd.openxmlformats-officedocument.wordprocessingml.document',  # .docx
            'application/msword',  # .doc
        ],
    }
    
    @staticmethod
    def validate_mime_type(file: UploadedFile, category: str = 'document') -> Dict[str, any]:
        """
        Valide le type MIME d'un fichier
        
        Args:
            file: Fichier uploadé
            category: Catégorie de fichier ('image' ou 'document')
            
        Returns:
            dict: Résultat de la validation
            
        Exigence: 31.1, 31.5
        """
        errors = []
        
        # Vérifier le type MIME déclaré
        declared_mime = getattr(file, 'content_type', None)
        
        if not declared_mime:
            errors.append("Type MIME non fourni")
            return {'is_valid': False, 'errors': errors}
        
        # Vérifier si le type MIME est autorisé
        allowed_types = MimeTypeValidator.ALLOWED_MIME_TYPES.get(category, [])
        
        if declared_mime not in allowed_types:
            errors.append(
                f"Type MIME non autorisé: {declared_mime}. "
                f"Types autorisés: {', '.join(allowed_types)}"
            )
        
        # Vérifier le type MIME réel avec python-magic si disponible
        try:
            import magic
            file.seek(0)
            file_content = file.read(2048)
            file.seek(0)
            
            mime = magic.Magic(mime=True)
            actual_mime = mime.from_buffer(file_content)
            
            if actual_mime != declared_mime:
                logger.warning(
                    f"Type MIME déclaré ({declared_mime}) différent du type réel ({actual_mime})"
                )
                
                # Vérifier si le type réel est autorisé
                if actual_mime not in allowed_types:
                    errors.append(
                        f"Type MIME réel non autorisé: {actual_mime}"
                    )
        except ImportError:
            # python-magic non disponible, utiliser seulement le type déclaré
            logger.debug("python-magic non disponible, validation MIME basique")
        except Exception as e:
            logger.error(f"Erreur validation MIME: {e}")
        
        return {
            'is_valid': len(errors) == 0,
            'errors': errors
        }
