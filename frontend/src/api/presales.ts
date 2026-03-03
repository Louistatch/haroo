import api from './auth';

export interface Prevente {
  id: number;
  exploitant: number;
  exploitant_nom: string;
  culture: string;
  quantite_estimee: string;
  date_recolte_prevue: string;
  prix_par_tonne: string;
  montant_total: string;
  canton: number;
  canton_nom: string;
  description: string;
  statut: 'DISPONIBLE' | 'ENGAGEE' | 'LIVREE' | 'ANNULEE';
  created_at: string;
}

export interface Engagement {
  id: number;
  prevente: number;
  prevente_detail?: Prevente;
  acheteur: number;
  acheteur_nom: string;
  quantite_engagee: string;
  montant_total: string;
  acompte_20: string;
  transaction_acompte: number | null;
  statut: 'EN_ATTENTE' | 'ACOMPTE_PAYE' | 'LIVRAISON_CONFIRMEE' | 'PAIEMENT_COMPLET' | 'ANNULE';
  date_livraison: string | null;
  created_at: string;
}

export async function getPreventes(params?: any): Promise<Prevente[]> {
  const res = await api.get('/presales/', { params });
  if (Array.isArray(res.data)) return res.data;
  return res.data.results ?? res.data;
}

export async function getPrevente(id: number): Promise<Prevente> {
  const res = await api.get(`/presales/${id}/`);
  return res.data;
}

export async function createPrevente(data: any): Promise<Prevente> {
  const res = await api.post('/presales/', data);
  return res.data;
}

export async function engagerPrevente(preventeId: number, quantite: number): Promise<Engagement> {
  const res = await api.post('/engagements/', {
    prevente: preventeId,
    quantite_engagee: quantite
  });
  return res.data;
}

export async function getMesEngagements(): Promise<Engagement[]> {
  const res = await api.get('/engagements/');
  if (Array.isArray(res.data)) return res.data;
  return res.data.results ?? res.data;
}
