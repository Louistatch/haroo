/**
 * Unit tests for PurchaseHistory component
 * 
 * Note: These tests require Vitest and React Testing Library to be installed.
 * Install with: npm install -D vitest @testing-library/react @testing-library/jest-dom
 */

import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, waitFor, fireEvent } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import PurchaseHistory from '../PurchaseHistory';
import * as purchasesApi from '../../api/purchases';

// Mock the API module
vi.mock('../../api/purchases');
vi.mock('react-router-dom', async () => {
  const actual = await vi.importActual('react-router-dom');
  return {
    ...actual,
    useNavigate: () => vi.fn(),
  };
});

const mockPurchases = {
  count: 2,
  next: null,
  previous: null,
  results: [
    {
      id: 1,
      document: 1,
      document_titre: 'Guide Maïs Maritime',
      document_culture: 'Maïs',
      document_prix: '5000',
      format_fichier: 'PDF',
      transaction_id: 'txn_123',
      transaction_statut: 'SUCCESS',
      lien_telechargement: 'token123',
      expiration_lien: '2024-12-31T23:59:59Z',
      lien_expire: false,
      peut_regenerer: true,
      nombre_telechargements: 2,
      created_at: '2024-01-01T10:00:00Z',
    },
    {
      id: 2,
      document: 2,
      document_titre: 'Guide Riz Plateaux',
      document_culture: 'Riz',
      document_prix: '7500',
      format_fichier: 'EXCEL',
      transaction_id: 'txn_456',
      transaction_statut: 'SUCCESS',
      lien_telechargement: 'token456',
      expiration_lien: '2023-12-31T23:59:59Z',
      lien_expire: true,
      peut_regenerer: true,
      nombre_telechargements: 0,
      created_at: '2023-12-01T10:00:00Z',
    },
  ],
};

describe('PurchaseHistory Component', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    localStorage.setItem('access_token', 'fake-token');
  });

  it('should render loading state initially', () => {
    vi.mocked(purchasesApi.fetchPurchaseHistory).mockImplementation(
      () => new Promise(() => {}) // Never resolves
    );

    render(
      <BrowserRouter>
        <PurchaseHistory />
      </BrowserRouter>
    );

    expect(screen.getByText(/chargement/i)).toBeInTheDocument();
  });

  it('should display purchases after loading', async () => {
    vi.mocked(purchasesApi.fetchPurchaseHistory).mockResolvedValue(mockPurchases);

    render(
      <BrowserRouter>
        <PurchaseHistory />
      </BrowserRouter>
    );

    await waitFor(() => {
      expect(screen.getByText('Guide Maïs Maritime')).toBeInTheDocument();
      expect(screen.getByText('Guide Riz Plateaux')).toBeInTheDocument();
    });
  });

  it('should show total count', async () => {
    vi.mocked(purchasesApi.fetchPurchaseHistory).mockResolvedValue(mockPurchases);

    render(
      <BrowserRouter>
        <PurchaseHistory />
      </BrowserRouter>
    );

    await waitFor(() => {
      expect(screen.getByText(/Total: 2 achats/i)).toBeInTheDocument();
    });
  });

  it('should display expired badge for expired links', async () => {
    vi.mocked(purchasesApi.fetchPurchaseHistory).mockResolvedValue(mockPurchases);

    render(
      <BrowserRouter>
        <PurchaseHistory />
      </BrowserRouter>
    );

    await waitFor(() => {
      const expiredBadges = screen.getAllByText(/Expiré/i);
      expect(expiredBadges.length).toBeGreaterThan(0);
    });
  });

  it('should filter purchases by culture', async () => {
    vi.mocked(purchasesApi.fetchPurchaseHistory).mockResolvedValue(mockPurchases);

    render(
      <BrowserRouter>
        <PurchaseHistory />
      </BrowserRouter>
    );

    await waitFor(() => {
      expect(screen.getByText('Guide Maïs Maritime')).toBeInTheDocument();
    });

    const cultureInput = screen.getByPlaceholderText(/Ex: Maïs, Riz/i);
    fireEvent.change(cultureInput, { target: { value: 'Maïs' } });

    // Wait for debounce
    await waitFor(() => {
      expect(purchasesApi.fetchPurchaseHistory).toHaveBeenCalledWith(
        expect.objectContaining({ culture: 'Maïs' }),
        'fake-token'
      );
    }, { timeout: 500 });
  });

  it('should handle pagination', async () => {
    const largeMockData = {
      ...mockPurchases,
      count: 50,
    };
    vi.mocked(purchasesApi.fetchPurchaseHistory).mockResolvedValue(largeMockData);

    render(
      <BrowserRouter>
        <PurchaseHistory />
      </BrowserRouter>
    );

    await waitFor(() => {
      expect(screen.getByText(/Page 1 sur 3/i)).toBeInTheDocument();
    });

    const nextButton = screen.getByText(/Suivant/i);
    fireEvent.click(nextButton);

    await waitFor(() => {
      expect(purchasesApi.fetchPurchaseHistory).toHaveBeenCalledWith(
        expect.objectContaining({ page: 2 }),
        'fake-token'
      );
    });
  });

  it('should handle regenerate link action', async () => {
    vi.mocked(purchasesApi.fetchPurchaseHistory).mockResolvedValue(mockPurchases);
    vi.mocked(purchasesApi.regenerateDownloadLink).mockResolvedValue({
      success: true,
      download_url: 'http://example.com/download',
      expiration: '2025-01-01T00:00:00Z',
      message: 'Lien régénéré avec succès',
    });

    render(
      <BrowserRouter>
        <PurchaseHistory />
      </BrowserRouter>
    );

    await waitFor(() => {
      expect(screen.getByText('Guide Riz Plateaux')).toBeInTheDocument();
    });

    const regenerateButtons = screen.getAllByText(/Régénérer le lien/i);
    fireEvent.click(regenerateButtons[0]);

    await waitFor(() => {
      expect(purchasesApi.regenerateDownloadLink).toHaveBeenCalledWith(2, 'fake-token');
    });
  });

  it('should show error state on API failure', async () => {
    vi.mocked(purchasesApi.fetchPurchaseHistory).mockRejectedValue(
      new Error('Network error')
    );

    render(
      <BrowserRouter>
        <PurchaseHistory />
      </BrowserRouter>
    );

    await waitFor(() => {
      expect(screen.getByText(/Erreur/i)).toBeInTheDocument();
    });
  });

  it('should show empty state when no purchases', async () => {
    vi.mocked(purchasesApi.fetchPurchaseHistory).mockResolvedValue({
      count: 0,
      next: null,
      previous: null,
      results: [],
    });

    render(
      <BrowserRouter>
        <PurchaseHistory />
      </BrowserRouter>
    );

    await waitFor(() => {
      expect(screen.getByText(/Aucun achat trouvé/i)).toBeInTheDocument();
    });
  });

  it('should reset filters', async () => {
    vi.mocked(purchasesApi.fetchPurchaseHistory).mockResolvedValue(mockPurchases);

    render(
      <BrowserRouter>
        <PurchaseHistory />
      </BrowserRouter>
    );

    await waitFor(() => {
      expect(screen.getByText('Guide Maïs Maritime')).toBeInTheDocument();
    });

    const cultureInput = screen.getByPlaceholderText(/Ex: Maïs, Riz/i);
    fireEvent.change(cultureInput, { target: { value: 'Maïs' } });

    const resetButton = screen.getByText(/Réinitialiser les filtres/i);
    fireEvent.click(resetButton);

    expect(cultureInput).toHaveValue('');
  });
});
