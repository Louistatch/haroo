import axios from 'axios';

const API_BASE_URL = 'http://localhost:8000/api/v1';

export interface Purchase {
  id: number;
  document: number;
  document_titre: string;
  document_culture: string;
  document_prix: string;
  format_fichier: string;
  transaction_id: string;
  transaction_statut: 'SUCCESS' | 'PENDING' | 'FAILED';
  lien_telechargement: string;
  expiration_lien: string;
  lien_expire: boolean;
  peut_regenerer: boolean;
  nombre_telechargements: number;
  created_at: string;
}

export interface PurchaseFilters {
  date_debut?: string;
  date_fin?: string;
  culture?: string;
  statut?: string;
  lien_expire?: boolean;
  page?: number;
  page_size?: number;
}

export interface PurchaseHistoryResponse {
  count: number;
  next: string | null;
  previous: string | null;
  results: Purchase[];
}

export interface RegenerateResult {
  success: boolean;
  download_url: string;
  expiration: string;
  message: string;
}

/**
 * Fetch purchase history with optional filters
 * @param filters - Optional filters for date, culture, status, expiration
 * @param token - JWT access token
 * @returns Promise with purchase history response
 */
export async function fetchPurchaseHistory(
  filters: PurchaseFilters = {},
  token: string
): Promise<PurchaseHistoryResponse> {
  const params = new URLSearchParams();
  
  // Add filters to query params
  if (filters.date_debut) {
    params.append('date_debut', filters.date_debut);
  }
  if (filters.date_fin) {
    params.append('date_fin', filters.date_fin);
  }
  if (filters.culture) {
    params.append('culture', filters.culture);
  }
  if (filters.statut) {
    params.append('statut', filters.statut);
  }
  if (filters.lien_expire !== undefined) {
    params.append('lien_expire', filters.lien_expire.toString());
  }
  if (filters.page) {
    params.append('page', filters.page.toString());
  }
  if (filters.page_size) {
    params.append('page_size', filters.page_size.toString());
  }

  const response = await axios.get<PurchaseHistoryResponse>(
    `${API_BASE_URL}/purchases/history?${params}`,
    {
      headers: { Authorization: `Bearer ${token}` }
    }
  );

  return response.data;
}

/**
 * Regenerate an expired download link
 * @param purchaseId - ID of the purchase
 * @param token - JWT access token
 * @returns Promise with new download URL and expiration
 */
export async function regenerateDownloadLink(
  purchaseId: number,
  token: string
): Promise<RegenerateResult> {
  const response = await axios.post<RegenerateResult>(
    `${API_BASE_URL}/purchases/history/${purchaseId}/regenerate-link`,
    {},
    {
      headers: { Authorization: `Bearer ${token}` }
    }
  );

  return response.data;
}

/**
 * Build download URL for a purchase
 * @param documentId - ID of the document
 * @param token - Download token
 * @returns Full download URL
 */
export function buildDownloadUrl(documentId: number, token: string): string {
  return `${API_BASE_URL}/documents/${documentId}/download?token=${token}`;
}
