import api from './auth';

export interface OffreEmploi {
  id: number;
  type_travail: string;
  description: string;
  canton_nom: string;
  date_debut: string;
  date_fin: string;
  salaire_horaire: string;
  nombre_postes: number;
  postes_pourvus: number;
  statut: string;
  exploitant_nom: string;
  created_at: string;
}

export interface Contrat {
  id: number;
  offre: number;
  offre_details?: OffreEmploi;
  ouvrier_nom: string;
  exploitant_nom: string;
  statut: string;
  salaire_horaire: string;
  date_debut: string;
  date_fin: string;
}

export async function getOffres(params?: Record<string, any>): Promise<OffreEmploi[]> {
  const res = await api.get('/jobs/', { params });
  return Array.isArray(res.data) ? res.data : (res.data.results || []);
}

export async function getOffre(id: number): Promise<OffreEmploi> {
  const res = await api.get(`/jobs/${id}/`);
  return res.data;
}

export async function createOffre(data: any): Promise<OffreEmploi> {
  const res = await api.post('/jobs/', data);
  return res.data;
}

export async function postuler(offreId: number): Promise<Contrat> {
  const res = await api.post(`/jobs/${offreId}/postuler/`);
  return res.data;
}

export async function getContrats(): Promise<Contrat[]> {
  const res = await api.get('/contrats/');
  return Array.isArray(res.data) ? res.data : (res.data.results || []);
}

export async function logHeures(contratId: number, data: any): Promise<any> {
  const res = await api.post(`/contrats/${contratId}/log_heures/`, data);
  return res.data;
}
