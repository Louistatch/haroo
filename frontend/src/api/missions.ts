import api from './auth';

export interface Mission {
  id: number;
  exploitant: number;
  exploitant_nom: string;
  agronome: number;
  agronome_nom: string;
  description: string;
  budget_propose: string;
  statut: 'DEMANDE' | 'ACCEPTEE' | 'REFUSEE' | 'EN_COURS' | 'TERMINEE' | 'ANNULEE';
  statut_display: string;
  date_debut: string | null;
  date_fin: string | null;
  transaction: number | null;
  created_at: string;
  updated_at: string;
}

export interface MissionCreatePayload {
  agronome: number;
  description: string;
  budget_propose: number;
  date_debut?: string;
  date_fin?: string;
}

export async function getMissions(): Promise<Mission[]> {
  const res = await api.get('/missions/');
  if (Array.isArray(res.data)) return res.data;
  return res.data.results ?? res.data;
}

export async function getMission(id: number): Promise<Mission> {
  const res = await api.get(`/missions/${id}/`);
  return res.data;
}

export async function createMission(payload: MissionCreatePayload): Promise<Mission> {
  const res = await api.post('/missions/', payload);
  return res.data;
}

export async function acceptMission(id: number): Promise<Mission> {
  const res = await api.post(`/missions/${id}/accept/`);
  return res.data;
}

export async function refuseMission(id: number): Promise<Mission> {
  const res = await api.post(`/missions/${id}/refuse/`);
  return res.data;
}

export async function cancelMission(id: number): Promise<Mission> {
  const res = await api.post(`/missions/${id}/cancel/`);
  return res.data;
}

export async function startMission(id: number): Promise<Mission> {
  const res = await api.post(`/missions/${id}/start/`);
  return res.data;
}

export async function completeMission(id: number): Promise<Mission> {
  const res = await api.post(`/missions/${id}/complete/`);
  return res.data;
}
