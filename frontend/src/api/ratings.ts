import api from './auth';

export interface RatingUser {
  id: number;
  first_name: string;
  last_name: string;
  phone_number: string;
}

export interface Rating {
  id: number;
  notateur: RatingUser;
  note: RatingUser;
  note_valeur: number;
  commentaire: string;
  mission: number | null;
  statut: 'PUBLIE' | 'SIGNALE' | 'MODERE' | 'REJETE';
  nombre_signalements?: number;
  created_at: string;
  updated_at: string;
}

export interface CreateRatingPayload {
  note_valeur: number;
  commentaire: string;
  mission: number;
}

export interface ReportPayload {
  motif: 'INAPPROPRIE' | 'FAUX' | 'SPAM' | 'HARCÈLEMENT' | 'AUTRE';
  description?: string;
}

export async function getRatings(params?: { user_id?: number; note?: number }): Promise<Rating[]> {
  const query = params ? '?' + new URLSearchParams(
    Object.fromEntries(Object.entries(params).filter(([, v]) => v !== undefined).map(([k, v]) => [k, String(v)]))
  ).toString() : '';
  const res = await api.get(`/ratings/${query}`);
  if (Array.isArray(res.data)) return res.data;
  return res.data.results ?? res.data;
}

export async function createRating(payload: CreateRatingPayload): Promise<Rating> {
  const res = await api.post('/ratings/', payload);
  return res.data;
}

export async function reportRating(id: number, payload: ReportPayload): Promise<{ message: string }> {
  const res = await api.post(`/ratings/${id}/report/`, payload);
  return res.data;
}
