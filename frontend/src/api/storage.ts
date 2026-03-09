/**
 * Service d'upload de fichiers vers Supabase Storage.
 * Upload direct côté client pour les fichiers publics (profiles),
 * ou via le backend pour les fichiers privés (documents, justificatifs).
 */
import { supabase, BUCKETS, type BucketName } from '../lib/supabase';
import api from './auth';

// ---- Upload direct via Supabase JS (photos de profil publiques) ----

export async function uploadProfilePhoto(file: File, userId: string): Promise<string> {
  const ext = file.name.split('.').pop()?.toLowerCase() || 'jpg';
  const path = `${userId}/${Date.now()}.${ext}`;

  const { error } = await supabase.storage
    .from(BUCKETS.profiles)
    .upload(path, file, { contentType: file.type, upsert: true });

  if (error) throw new Error(`Erreur upload photo: ${error.message}`);

  const { data } = supabase.storage.from(BUCKETS.profiles).getPublicUrl(path);
  return data.publicUrl;
}

export async function deleteProfilePhoto(path: string): Promise<void> {
  const { error } = await supabase.storage.from(BUCKETS.profiles).remove([path]);
  if (error) throw new Error(`Erreur suppression photo: ${error.message}`);
}

// ---- Upload via backend API (fichiers privés avec validation serveur) ----

interface UploadResult {
  path: string;
  url: string;
  bucket: string;
}

export async function uploadFile(
  file: File,
  bucket: BucketName = 'documents',
  folder: string = ''
): Promise<UploadResult> {
  const formData = new FormData();
  formData.append('file', file);
  formData.append('bucket', bucket);
  if (folder) formData.append('folder', folder);

  const response = await api.post('/storage/upload/', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  });
  return response.data;
}

export async function getSignedUrl(bucket: BucketName, path: string): Promise<string> {
  const response = await api.post('/storage/signed-url/', { bucket, path });
  return response.data.url;
}

export async function deleteStorageFile(bucket: BucketName, path: string): Promise<void> {
  await api.delete('/storage/delete/', { data: { bucket, path } });
}

// ---- Helpers ----

const IMAGE_EXTENSIONS = ['jpg', 'jpeg', 'png'];
const DOC_EXTENSIONS = ['pdf', 'xlsx', 'xls', 'docx', 'doc'];
const MAX_IMAGE_SIZE = 5 * 1024 * 1024; // 5 MB
const MAX_DOC_SIZE = 10 * 1024 * 1024;  // 10 MB

export function validateFile(file: File, type: 'image' | 'document' = 'document'): string | null {
  const ext = file.name.split('.').pop()?.toLowerCase() || '';
  const allowed = type === 'image' ? IMAGE_EXTENSIONS : DOC_EXTENSIONS;
  const maxSize = type === 'image' ? MAX_IMAGE_SIZE : MAX_DOC_SIZE;

  if (!allowed.includes(ext)) {
    return `Extension non autorisée. Autorisées: ${allowed.join(', ')}`;
  }
  if (file.size > maxSize) {
    return `Fichier trop volumineux. Max: ${maxSize / (1024 * 1024)} Mo`;
  }
  return null;
}
