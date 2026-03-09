import api from './auth';

export interface DashboardStats {
  utilisateurs: {
    total: number;
    par_type: Record<string, number>;
    nouveaux_30j: number;
    nouveaux_7j: number;
    inscriptions_quotidiennes: { date: string; count: number }[];
  };
  missions: { total?: number; en_cours?: number; terminees?: number; en_attente?: number };
  emplois: { total?: number; publiees?: number; en_attente?: number };
  preventes: { total?: number; actives?: number };
  paiements: { total_transactions?: number; completed?: number; volume_total?: number };
  moderation: { total_notations?: number; signalees?: number; note_moyenne_globale?: number };
  messagerie: { total_conversations?: number; total_messages?: number; messages_signales?: number };
  notifications: { total?: number; non_lues?: number };
}

export interface AdminUser {
  id: number;
  username: string;
  first_name: string;
  last_name: string;
  email: string;
  phone_number: string;
  user_type: string;
  is_active: boolean;
  date_joined: string;
}

export async function getDashboardStats(): Promise<DashboardStats> {
  const res = await api.get('/admin/dashboard/');
  return res.data;
}

export async function getAdminUsers(params?: { search?: string; user_type?: string; is_active?: string; page?: number }): Promise<{ total: number; page: number; per_page: number; results: AdminUser[] }> {
  const res = await api.get('/admin/users/', { params });
  return res.data;
}

export async function suspendUser(userId: number, justification: string): Promise<void> {
  await api.post(`/admin/users/${userId}/suspend/`, { justification });
}

export async function activateUser(userId: number): Promise<void> {
  await api.post(`/admin/users/${userId}/activate/`);
}

export async function getModerationQueue() {
  const res = await api.get('/ratings/moderation-queue/');
  return res.data;
}

export async function moderateRating(id: number, action: 'approve' | 'reject') {
  const res = await api.post(`/ratings/${id}/moderate/`, { action });
  return res.data;
}

export async function getQualityAlerts() {
  const res = await api.get('/ratings/quality-alerts/');
  return res.data;
}
