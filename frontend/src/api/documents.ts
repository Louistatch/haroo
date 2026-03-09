import api from './auth';

export interface DocumentTechnique {
  id: number;
  titre: string;
  description: string;
  prix: string;
  culture: string;
  region: string;
  prefecture: string;
  canton: string;
  is_purchased?: boolean;
  lien_telechargement?: string;
  created_at: string;
}

export async function getDocuments(params?: Record<string, string>): Promise<DocumentTechnique[]> {
  const query = params ? '?' + new URLSearchParams(params).toString() : '';
  const res = await api.get(`/documents/${query}`);
  return res.data.results ?? res.data;
}

export async function getDocument(id: number): Promise<DocumentTechnique> {
  const res = await api.get(`/documents/${id}/`);
  return res.data;
}

export async function purchaseDocument(id: number): Promise<any> {
  const res = await api.post(`/documents/${id}/purchase/`);
  return res.data;
}
