"""
API endpoints pour l'upload de fichiers vers Supabase Storage.
"""
import logging
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes, parser_classes
from rest_framework.parsers import MultiPartParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from django.conf import settings

from apps.users.file_upload import FileUploadService
from apps.core.supabase_storage import (
    SupabaseProfileStorage,
    SupabaseDocumentStorage,
    SupabaseJustificatifStorage,
    SupabaseMessagingStorage,
)

logger = logging.getLogger(__name__)

BUCKET_MAP = {
    'profiles': SupabaseProfileStorage,
    'documents': SupabaseDocumentStorage,
    'justificatifs': SupabaseJustificatifStorage,
    'messaging': SupabaseMessagingStorage,
}


@api_view(['POST'])
@permission_classes([IsAuthenticated])
@parser_classes([MultiPartParser])
def upload_file(request):
    """
    Upload un fichier vers Supabase Storage.
    
    POST /api/v1/storage/upload/
    Form data:
      - file: fichier à uploader
      - bucket: profiles | documents | justificatifs | messaging
      - folder: sous-dossier optionnel (ex: "cni", "diplomes")
    """
    file = request.FILES.get('file')
    bucket_name = request.data.get('bucket', 'documents')
    folder = request.data.get('folder', '')

    if not file:
        return Response({'error': 'Aucun fichier fourni.'}, status=status.HTTP_400_BAD_REQUEST)

    if bucket_name not in BUCKET_MAP:
        return Response(
            {'error': f'Bucket invalide. Choix: {", ".join(BUCKET_MAP.keys())}'},
            status=status.HTTP_400_BAD_REQUEST,
        )

    # Validation selon le type
    if bucket_name == 'profiles':
        validation = FileUploadService.validate_image_file(file)
    else:
        validation = FileUploadService.validate_document_file(file)

    if not validation['is_valid']:
        return Response({'errors': validation['errors']}, status=status.HTTP_400_BAD_REQUEST)

    # Upload
    try:
        storage = BUCKET_MAP[bucket_name]()
        result = storage.upload_file(file, folder=folder or bucket_name)
        logger.info(
            "Upload réussi: user=%s bucket=%s path=%s",
            request.user.id, bucket_name, result['path'],
        )
        return Response(result, status=status.HTTP_201_CREATED)
    except Exception as e:
        logger.error("Erreur upload Supabase: %s", e)
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def get_signed_url(request):
    """
    Génère une URL signée pour un fichier privé.
    
    POST /api/v1/storage/signed-url/
    JSON: { "bucket": "documents", "path": "documents/2026/03/06/abc.pdf" }
    """
    bucket_name = request.data.get('bucket', 'documents')
    file_path = request.data.get('path', '')

    if not file_path:
        return Response({'error': 'Chemin du fichier requis.'}, status=status.HTTP_400_BAD_REQUEST)

    if bucket_name not in BUCKET_MAP:
        return Response({'error': 'Bucket invalide.'}, status=status.HTTP_400_BAD_REQUEST)

    try:
        storage = BUCKET_MAP[bucket_name]()
        url = storage.generate_signed_url(file_path, expires_in=3600)
        return Response({'url': url, 'expires_in': 3600})
    except Exception as e:
        logger.error("Erreur signed URL: %s", e)
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_file(request):
    """
    Supprime un fichier de Supabase Storage.
    
    DELETE /api/v1/storage/delete/
    JSON: { "bucket": "documents", "path": "documents/2026/03/06/abc.pdf" }
    """
    bucket_name = request.data.get('bucket', 'documents')
    file_path = request.data.get('path', '')

    if not file_path:
        return Response({'error': 'Chemin du fichier requis.'}, status=status.HTTP_400_BAD_REQUEST)

    if bucket_name not in BUCKET_MAP:
        return Response({'error': 'Bucket invalide.'}, status=status.HTTP_400_BAD_REQUEST)

    try:
        storage = BUCKET_MAP[bucket_name]()
        storage.delete(file_path)
        return Response({'message': 'Fichier supprimé.'})
    except Exception as e:
        logger.error("Erreur suppression: %s", e)
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
