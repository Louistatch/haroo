import { describe, it, expect, vi, beforeEach } from 'vitest';
import axios from 'axios';
import { 
  fetchPurchaseHistory, 
  regenerateDownloadLink, 
  buildDownloadUrl,
  PurchaseFilters 
} from '../purchases';

// Mock axios
vi.mock('axios');
const mockedAxios = axios as jest.Mocked<typeof axios>;

describe('Purchases API', () => {
  const mockToken = 'test-token-123';
  const API_BASE_URL = 'http://localhost:8000/api/v1';

  beforeEach(() => {
    vi.clearAllMocks();
  });

  describe('fetchPurchaseHistory', () => {
    it('should fetch purchase history without filters', async () => {
      const mockResponse = {
        data: {
          count: 2,
          next: null,
          previous: null,
          results: [
            {
              id: 1,
              document: 10,
              document_titre: 'Test Document',
              document_culture: 'Maïs',
              document_prix: '5000',
              format_fichier: 'EXCEL',
              transaction_id: 'txn-123',
              transaction_statut: 'SUCCESS',
              lien_telechargement: 'token-abc',
              expiration_lien: '2024-12-31T23:59:59Z',
              lien_expire: false,
              peut_regenerer: true,
              nombre_telechargements: 0,
              created_at: '2024-01-01T00:00:00Z'
            }
          ]
        }
      };

      mockedAxios.get.mockResolvedValue(mockResponse);

      const result = await fetchPurchaseHistory({}, mockToken);

      expect(mockedAxios.get).toHaveBeenCalledWith(
        `${API_BASE_URL}/purchases/history?`,
        {
          headers: { Authorization: `Bearer ${mockToken}` }
        }
      );
      expect(result).toEqual(mockResponse.data);
    });

    it('should fetch purchase history with all filters', async () => {
      const filters: PurchaseFilters = {
        date_debut: '2024-01-01',
        date_fin: '2024-12-31',
        culture: 'Maïs',
        statut: 'SUCCESS',
        lien_expire: true,
        page: 2,
        page_size: 10
      };

      const mockResponse = {
        data: {
          count: 5,
          next: null,
          previous: 'prev-url',
          results: []
        }
      };

      mockedAxios.get.mockResolvedValue(mockResponse);

      const result = await fetchPurchaseHistory(filters, mockToken);

      expect(mockedAxios.get).toHaveBeenCalledWith(
        expect.stringContaining('date_debut=2024-01-01'),
        expect.objectContaining({
          headers: { Authorization: `Bearer ${mockToken}` }
        })
      );
      expect(mockedAxios.get).toHaveBeenCalledWith(
        expect.stringContaining('culture=Ma%C3%AFs'),
        expect.any(Object)
      );
      expect(mockedAxios.get).toHaveBeenCalledWith(
        expect.stringContaining('statut=SUCCESS'),
        expect.any(Object)
      );
      expect(mockedAxios.get).toHaveBeenCalledWith(
        expect.stringContaining('lien_expire=true'),
        expect.any(Object)
      );
      expect(result).toEqual(mockResponse.data);
    });

    it('should handle API errors', async () => {
      mockedAxios.get.mockRejectedValue(new Error('Network error'));

      await expect(fetchPurchaseHistory({}, mockToken)).rejects.toThrow('Network error');
    });
  });

  describe('regenerateDownloadLink', () => {
    it('should regenerate download link successfully', async () => {
      const purchaseId = 123;
      const mockResponse = {
        data: {
          success: true,
          download_url: 'http://example.com/download?token=new-token',
          expiration: '2024-12-31T23:59:59Z',
          message: 'Nouveau lien généré avec succès'
        }
      };

      mockedAxios.post.mockResolvedValue(mockResponse);

      const result = await regenerateDownloadLink(purchaseId, mockToken);

      expect(mockedAxios.post).toHaveBeenCalledWith(
        `${API_BASE_URL}/purchases/history/${purchaseId}/regenerate-link`,
        {},
        {
          headers: { Authorization: `Bearer ${mockToken}` }
        }
      );
      expect(result).toEqual(mockResponse.data);
    });

    it('should handle regeneration errors', async () => {
      const purchaseId = 123;
      mockedAxios.post.mockRejectedValue({
        response: {
          status: 400,
          data: { error: 'Le paiement n\'est pas confirmé' }
        }
      });

      await expect(regenerateDownloadLink(purchaseId, mockToken)).rejects.toMatchObject({
        response: {
          status: 400,
          data: { error: 'Le paiement n\'est pas confirmé' }
        }
      });
    });
  });

  describe('buildDownloadUrl', () => {
    it('should build correct download URL', () => {
      const documentId = 456;
      const token = 'download-token-xyz';

      const url = buildDownloadUrl(documentId, token);

      expect(url).toBe(`${API_BASE_URL}/documents/${documentId}/download?token=${token}`);
    });

    it('should handle special characters in token', () => {
      const documentId = 789;
      const token = 'token-with-special_chars-123';

      const url = buildDownloadUrl(documentId, token);

      expect(url).toBe(`${API_BASE_URL}/documents/${documentId}/download?token=${token}`);
    });
  });
});
