"""
Backend de stockage Supabase Storage pour Django
Intégration avec le projet Supabase: rvhwbxzquglqvhwklaum.supabase.co

Buckets:
  - profiles  (public)  : Photos de profil utilisateurs
  - documents (private) : Documents techniques agricoles
  - justificatifs (private) : Pièces justificatives (CNI, diplômes)
  - messaging (private) : Pièces jointes messagerie
"""
import os
import uuid
import logging
from datetime import datetime
from io import BytesIO
from typing import Optional

from django.conf import settings
from django.core.files.base import ContentFile
from django.core.files.storage import Storage
from django.utils.deconstruct import deconstructible

logger = logging.getLogger(__name__)


def get_supabase_client():
    """Retourne un client Supabase configuré (singleton-like via module cache)."""
    from supabase import create_client
    url = getattr(settings, 'SUPABASE_URL', '')
    key = getattr(settings, 'SUPABASE_SERVICE_KEY', '')
    if not url or not key:
        raise ValueError("SUPABASE_URL et SUPABASE_SERVICE_KEY requis dans settings.")
    return create_client(url, key)


# Buckets et leur visibilité
BUCKETS = {
    'profiles': {'public': True},
    'documents': {'public': False},
    'justificatifs': {'public': False},
    'messaging': {'public': False},
}


def ensure_buckets_exist():
    """Crée les buckets Supabase s'ils n'existent pas encore."""
    client = get_supabase_client()
    existing = {b.name for b in client.storage.list_buckets()}
    for name, opts in BUCKETS.items():
        if name not in existing:
            client.storage.create_bucket(name, options={'public': opts['public']})
            logger.info("Bucket Supabase créé: %s (public=%s)", name, opts['public'])


@deconstructible
class SupabaseStorage(Storage):
    """
    Django Storage backend utilisant Supabase Storage.
    Utilisé comme DEFAULT_FILE_STORAGE quand USE_SUPABASE=True.
    """

    def __init__(self, bucket_name: str = None):
        self.bucket_name = bucket_name or getattr(
            settings, 'SUPABASE_STORAGE_BUCKET', 'documents'
        )

    @property
    def _client(self):
        return get_supabase_client()

    @property
    def _bucket(self):
        return self._client.storage.from_(self.bucket_name)

    # ---- Django Storage API ----

    @staticmethod
    def _sanitize_key(name: str) -> str:
        """Nettoie le nom de fichier pour Supabase (ASCII, sans espaces ni accents)."""
        import unicodedata, re
        # Normaliser les accents → ASCII
        name = unicodedata.normalize('NFKD', name).encode('ascii', 'ignore').decode('ascii')
        # Remplacer espaces et caractères spéciaux par _
        name = re.sub(r'[^\w./\-]', '_', name)
        # Supprimer les _ multiples
        name = re.sub(r'_+', '_', name)
        return name

    def _save(self, name: str, content) -> str:
        name = self._sanitize_key(name)
        data = content.read()
        content_type = getattr(content, 'content_type', 'application/octet-stream')
        self._bucket.upload(
            path=name,
            file=data,
            file_options={"content-type": content_type, "upsert": "true"},
        )
        logger.info("Fichier uploadé sur Supabase: %s/%s", self.bucket_name, name)
        return name

    def exists(self, name: str) -> bool:
        try:
            self._bucket.list(os.path.dirname(name))
            # list returns files in directory; check if our file is there
            files = self._bucket.list(os.path.dirname(name) or '')
            return any(f['name'] == os.path.basename(name) for f in files)
        except Exception:
            return False

    def delete(self, name: str):
        try:
            self._bucket.remove([name])
            logger.info("Fichier supprimé de Supabase: %s/%s", self.bucket_name, name)
        except Exception as e:
            logger.error("Erreur suppression Supabase %s: %s", name, e)

    def url(self, name: str) -> str:
        bucket_info = BUCKETS.get(self.bucket_name, {})
        if bucket_info.get('public', False):
            return self._bucket.get_public_url(name)
        # URL signée 1h pour les buckets privés
        return self.generate_signed_url(name, expires_in=3600)

    def size(self, name: str) -> int:
        try:
            files = self._bucket.list(os.path.dirname(name) or '')
            for f in files:
                if f['name'] == os.path.basename(name):
                    return f.get('metadata', {}).get('size', 0)
        except Exception:
            pass
        return 0

    def listdir(self, path: str):
        files = self._bucket.list(path or '')
        dirs, filenames = [], []
        for f in files:
            if f.get('id') is None:
                dirs.append(f['name'])
            else:
                filenames.append(f['name'])
        return dirs, filenames

    # ---- Helpers ----

    def generate_signed_url(self, name: str, expires_in: int = 3600) -> str:
        """Génère une URL signée avec expiration (secondes)."""
        result = self._bucket.create_signed_url(name, expires_in)
        return result.get('signedURL', '')

    def upload_file(self, file, folder: str, filename: str = None) -> dict:
        """
        Upload un fichier avec chemin organisé par date.
        Retourne {'path': ..., 'url': ..., 'bucket': ...}
        """
        ext = os.path.splitext(file.name)[1].lower()
        unique_name = filename or f"{uuid.uuid4().hex}{ext}"
        date_path = datetime.now().strftime('%Y/%m/%d')
        full_path = f"{folder}/{date_path}/{unique_name}"

        content_type = getattr(file, 'content_type', 'application/octet-stream')
        data = file.read()
        file.seek(0)

        self._bucket.upload(
            path=full_path,
            file=data,
            file_options={"content-type": content_type, "upsert": "true"},
        )

        bucket_info = BUCKETS.get(self.bucket_name, {})
        if bucket_info.get('public', False):
            url = self._bucket.get_public_url(full_path)
        else:
            url = self.generate_signed_url(full_path)

        return {
            'path': full_path,
            'url': url,
            'bucket': self.bucket_name,
        }


class SupabaseProfileStorage(SupabaseStorage):
    """Storage pour les photos de profil (bucket public)."""
    def __init__(self):
        super().__init__(bucket_name='profiles')


class SupabaseDocumentStorage(SupabaseStorage):
    """Storage pour les documents techniques (bucket privé)."""
    def __init__(self):
        super().__init__(bucket_name='documents')


class SupabaseJustificatifStorage(SupabaseStorage):
    """Storage pour les pièces justificatives (bucket privé)."""
    def __init__(self):
        super().__init__(bucket_name='justificatifs')


class SupabaseMessagingStorage(SupabaseStorage):
    """Storage pour les pièces jointes messagerie (bucket privé)."""
    def __init__(self):
        super().__init__(bucket_name='messaging')
