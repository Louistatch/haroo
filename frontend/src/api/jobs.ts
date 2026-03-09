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
  est_collective?: boolean;
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

export interface Participation {
  id: number;
  exploitant: number;
  exploitant_nom: string;
  superficie_apportee: string;
  created_at: string;
}

export interface AnnonceCollective {
  id: number;
  createur_nom: string;
  type_travail: string;
  description: string;
  canton_nom: string;
  date_debut: string;
  date_fin: string;
  salaire_horaire: string;
  nombre_postes: number;
  superficie_cumulee: string;
  seuil_hectares: string;
  date_expiration: string;
  statut: string;
  nb_participants: number;
  progression: number;
  participations?: Participation[];
  created_at: string;
}

export interface Eligibilite {
  peut_publier_directement: boolean;
  superficie: string;
  seuil: string;
  verifie: boolean;
  profil_complet: boolean;
  canton_id: number | null;
  canton_nom: string;
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

export async function checkEligibilite(): Promise<Eligibilite> {
  const res = await api.get('/jobs/eligibilite/');
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

// --- Annonces collectives ---

export async function getAnnonces(params?: Record<string, any>): Promise<AnnonceCollective[]> {
  const res = await api.get('/annonces-collectives/', { params });
  return Array.isArray(res.data) ? res.data : (res.data.results || []);
}

export async function createAnnonce(data: any): Promise<AnnonceCollective> {
  const res = await api.post('/annonces-collectives/', data);
  return res.data;
}

export async function rejoindreAnnonce(annonceId: number): Promise<AnnonceCollective> {
  const res = await api.post(`/annonces-collectives/${annonceId}/rejoindre/`);
  return res.data;
}

// --- Annonces d'ouvriers ---

export interface MembreEquipe {
  nom: string;
  prenom: string;
  telephone: string;
}

export interface AnnonceOuvrier {
  id: number;
  ouvrier: number;
  ouvrier_nom: string;
  titre: string;
  description: string;
  competences: string[];
  cantons_noms: string[];
  tarif_horaire_min: string;
  date_disponibilite_debut: string;
  date_disponibilite_fin: string | null;
  statut: string;
  type_annonce: 'INDIVIDUELLE' | 'COLLECTIVE';
  equipe_complete: boolean;
  nb_membres_actuels: number;
  progression: number;
  date_expiration: string;
  membres_equipe?: MembreEquipe[];
  membres_rejoints?: any[];
  created_at: string;
}

export async function getAnnoncesOuvriers(params?: Record<string, any>): Promise<AnnonceOuvrier[]> {
  const res = await api.get('/annonces-ouvriers/', { params });
  return Array.isArray(res.data) ? res.data : (res.data.results || []);
}

export async function createAnnonceOuvrier(data: any): Promise<AnnonceOuvrier> {
  const res = await api.post('/annonces-ouvriers/', data);
  return res.data;
}

export async function rejoindreAnnonceOuvrier(annonceId: number): Promise<any> {
  const res = await api.post(`/annonces-ouvriers/${annonceId}/rejoindre/`);
  return res.data;
}

export async function desactiverAnnonceOuvrier(annonceId: number): Promise<any> {
  const res = await api.post(`/annonces-ouvriers/${annonceId}/desactiver/`);
  return res.data;
}

export async function reactiverAnnonceOuvrier(annonceId: number): Promise<any> {
  const res = await api.post(`/annonces-ouvriers/${annonceId}/reactiver/`);
  return res.data;
}
