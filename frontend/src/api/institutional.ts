import api from './auth';

export interface AggregatedStats {
  total_utilisateurs: number;
  total_exploitants: number;
  total_agronomes: number;
  total_ouvriers: number;
  total_missions: number;
  total_transactions: number;
  volume_transactions: number;
}

export interface PrefectureStats {
  prefecture: string;
  exploitants: number;
  agronomes: number;
  missions: number;
  volume_transactions: number;
}

export interface MonthlyTrend {
  mois: string;
  inscriptions: number;
  missions: number;
  transactions: number;
}

export interface TransactionBreakdown {
  type: string;
  count: number;
  volume: number;
}

export interface InstitutionalDashboard {
  aggregated: AggregatedStats;
  by_prefecture: PrefectureStats[];
  monthly_trends: MonthlyTrend[];
  transaction_breakdown: TransactionBreakdown[];
}

export async function getDashboard(): Promise<InstitutionalDashboard> {
  const res = await api.get('/institutional/dashboard/');
  return res.data;
}

export async function getAggregatedStats(): Promise<AggregatedStats> {
  const res = await api.get('/institutional/statistics/aggregated/');
  return res.data;
}

export async function getStatsByPrefecture(): Promise<PrefectureStats[]> {
  const res = await api.get('/institutional/statistics/by-prefecture/');
  return Array.isArray(res.data) ? res.data : (res.data.results ?? []);
}

export async function getMonthlyTrends(): Promise<MonthlyTrend[]> {
  const res = await api.get('/institutional/statistics/trends/');
  return Array.isArray(res.data) ? res.data : (res.data.results ?? []);
}

export async function getTransactionBreakdown(): Promise<TransactionBreakdown[]> {
  const res = await api.get('/institutional/statistics/transactions/');
  return Array.isArray(res.data) ? res.data : (res.data.results ?? []);
}

export async function exportReport(format: 'excel' | 'pdf' = 'excel'): Promise<Blob> {
  const res = await api.get('/institutional/reports/export/', {
    params: { format },
    responseType: 'blob',
  });
  return res.data;
}
