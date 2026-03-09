import api from './auth';

export interface CGUAcceptance {
  id: number;
  version: string;
  accepted_at: string;
}

export interface DataExportRequest {
  id: number;
  status: string;
  requested_at: string;
  completed_at: string | null;
  download_url: string | null;
}

export async function getCGU(): Promise<string> {
  const res = await api.get('/compliance/cgu/');
  return res.data.content ?? res.data;
}

export async function getPrivacyPolicy(): Promise<string> {
  const res = await api.get('/compliance/privacy-policy/');
  return res.data.content ?? res.data;
}

export async function acceptCGU(version: string): Promise<CGUAcceptance> {
  const res = await api.post('/compliance/cgu-acceptances/', { version });
  return res.data;
}

export async function requestDataExport(): Promise<DataExportRequest> {
  const res = await api.post('/compliance/data-export/');
  return res.data;
}

export async function getDataExportStatus(): Promise<DataExportRequest> {
  const res = await api.get('/compliance/data-export/');
  return res.data;
}

export async function requestAccountDeletion(reason?: string): Promise<{ detail: string }> {
  const res = await api.post('/compliance/account-deletion/', { reason });
  return res.data;
}
