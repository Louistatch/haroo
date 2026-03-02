/**
 * Unit tests for Documents component enhancements
 */

import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, waitFor, fireEvent } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import Documents from '../Documents';
import * as purchasesApi from '../../api/purchases';

vi.mock('axios');
vi.mock('../../api/purchases');
vi.mock('react-router-dom', async () => {
  const actual = await vi.importActual('react-router-dom');
  return {
    ...actual,
    useNavigate: () => vi.fn(),
  };
});

const mockDocuments = {
  count: 2,
  results: [
    {
      id: 1,
      titre: 'Guide Maïs Maritime',
      description: 'Guide complet pour la culture du maïs',
      prix: '5000',
      culture: 'Maïs',
      region: 'Maritime',
      prefecture: 'Golfe',
      canton: 'Lomé',
    },
    {
      id: 2,
      titre: 'Guide Riz Plateaux',
      description: 'Itinéraire technique pour le riz',
      prix: '7500',
      culture: 'Riz',
      region: 'Plateaux',
      prefecture: 'Kloto',
      canton: 'Kpalimé',
    },
  ],
};

const mockPurchaseHistory = {
  count: 1,
  results: [
    {
      id: 1,
      document: 1,
      transaction_statut: 'SUCCESS',
      lien_expire: false,
      lien_telechargement: 'token123',
    },
  ],
};

describe('Documents Component Enhancements', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    localStorage.setItem('access_token', 'fake-token');
  });

  it('should display purchased badge for owned documents', async () => {
    const axios = await import('axios');
    vi.mocked(axios.default.get).mockResolvedValue({ data: mockDocuments });
    vi.mocked(purchasesApi.fetchPurchaseHistory).mockResolvedValue(mockPurchaseHistory);

    render(
      <BrowserRouter>
        <Documents />
      </BrowserRouter>
    );

    await waitFor(() => {
      expect(screen.getByText(/Acheté/i)).toBeInTheDocument();
    });
  });

  it('should show download button for purchased documents', async () => {
    const axios = await import('axios');
    vi.mocked(axios.default.get).mockResolvedValue({ data: mockDocuments });
    vi.mocked(purchasesApi.fetchPurchaseHistory).mockResolvedValue(mockPurchaseHistory);

    render(
      <BrowserRouter>
        <Documents />
      </BrowserRouter>
    );

    await waitFor(() => {
      const downloadButtons = screen.getAllByText(/Télécharger/i);
      expect(downloadButtons.length).toBeGreaterThan(0);
    });
  });

  it('should show purchase button for non-purchased documents', async () => {
    const axios = await import('axios');
    vi.mocked(axios.default.get).mockResolvedValue({ data: mockDocuments });
    vi.mocked(purchasesApi.fetchPurchaseHistory).mockResolvedValue({
      count: 0,
      results: [],
    });

    render(
      <BrowserRouter>
        <Documents />
      </BrowserRouter>
    );

    await waitFor(() => {
      const purchaseButtons = screen.getAllByText(/Acheter/i);
      expect(purchaseButtons.length).toBe(2);
    });
  });

  it('should open purchase modal on buy click', async () => {
    const axios = await import('axios');
    vi.mocked(axios.default.get).mockResolvedValue({ data: mockDocuments });
    vi.mocked(purchasesApi.fetchPurchaseHistory).mockResolvedValue({
      count: 0,
      results: [],
    });

    render(
      <BrowserRouter>
        <Documents />
      </BrowserRouter>
    );

    await waitFor(() => {
      expect(screen.getByText('Guide Maïs Maritime')).toBeInTheDocument();
    });

    const purchaseButtons = screen.getAllByText(/Acheter/i);
    fireEvent.click(purchaseButtons[0]);

    await waitFor(() => {
      expect(screen.getByText(/Confirmer l'achat/i)).toBeInTheDocument();
    });
  });

  it('should display document details in modal', async () => {
    const axios = await import('axios');
    vi.mocked(axios.default.get).mockResolvedValue({ data: mockDocuments });
    vi.mocked(purchasesApi.fetchPurchaseHistory).mockResolvedValue({
      count: 0,
      results: [],
    });

    render(
      <BrowserRouter>
        <Documents />
      </BrowserRouter>
    );

    await waitFor(() => {
      expect(screen.getByText('Guide Maïs Maritime')).toBeInTheDocument();
    });

    const purchaseButtons = screen.getAllByText(/Acheter/i);
    fireEvent.click(purchaseButtons[0]);

    await waitFor(() => {
      expect(screen.getByText('Guide Maïs Maritime')).toBeInTheDocument();
      expect(screen.getByText(/5\.000 FCFA/i)).toBeInTheDocument();
    });
  });

  it('should close modal on cancel', async () => {
    const axios = await import('axios');
    vi.mocked(axios.default.get).mockResolvedValue({ data: mockDocuments });
    vi.mocked(purchasesApi.fetchPurchaseHistory).mockResolvedValue({
      count: 0,
      results: [],
    });

    render(
      <BrowserRouter>
        <Documents />
      </BrowserRouter>
    );

    await waitFor(() => {
      expect(screen.getByText('Guide Maïs Maritime')).toBeInTheDocument();
    });

    const purchaseButtons = screen.getAllByText(/Acheter/i);
    fireEvent.click(purchaseButtons[0]);

    await waitFor(() => {
      expect(screen.getByText(/Confirmer l'achat/i)).toBeInTheDocument();
    });

    const cancelButton = screen.getByText(/Annuler/i);
    fireEvent.click(cancelButton);

    await waitFor(() => {
      expect(screen.queryByText(/Confirmer l'achat/i)).not.toBeInTheDocument();
    });
  });

  it('should filter documents by culture', async () => {
    const axios = await import('axios');
    vi.mocked(axios.default.get).mockResolvedValue({ data: mockDocuments });
    vi.mocked(purchasesApi.fetchPurchaseHistory).mockResolvedValue({
      count: 0,
      results: [],
    });

    render(
      <BrowserRouter>
        <Documents />
      </BrowserRouter>
    );

    await waitFor(() => {
      expect(screen.getByText('Guide Maïs Maritime')).toBeInTheDocument();
    });

    const cultureSelect = screen.getByLabelText(/Culture/i);
    fireEvent.change(cultureSelect, { target: { value: 'Maïs' } });

    await waitFor(() => {
      expect(axios.default.get).toHaveBeenCalledWith(
        expect.stringContaining('culture=Ma%C3%AFs')
      );
    });
  });

  it('should show skeleton loaders while loading', () => {
    const axios = await import('axios');
    vi.mocked(axios.default.get).mockImplementation(() => new Promise(() => {}));
    vi.mocked(purchasesApi.fetchPurchaseHistory).mockImplementation(
      () => new Promise(() => {})
    );

    render(
      <BrowserRouter>
        <Documents />
      </BrowserRouter>
    );

    const skeletons = document.querySelectorAll('.skeleton');
    expect(skeletons.length).toBeGreaterThan(0);
  });

  it('should show toast on error', async () => {
    const axios = await import('axios');
    vi.mocked(axios.default.get).mockRejectedValue(new Error('Network error'));
    vi.mocked(purchasesApi.fetchPurchaseHistory).mockResolvedValue({
      count: 0,
      results: [],
    });

    render(
      <BrowserRouter>
        <Documents />
      </BrowserRouter>
    );

    await waitFor(() => {
      expect(screen.getByText(/Erreur/i)).toBeInTheDocument();
    });
  });

  it('should show empty state when no documents', async () => {
    const axios = await import('axios');
    vi.mocked(axios.default.get).mockResolvedValue({
      data: { count: 0, results: [] },
    });
    vi.mocked(purchasesApi.fetchPurchaseHistory).mockResolvedValue({
      count: 0,
      results: [],
    });

    render(
      <BrowserRouter>
        <Documents />
      </BrowserRouter>
    );

    await waitFor(() => {
      expect(screen.getByText(/Aucun document trouvé/i)).toBeInTheDocument();
    });
  });
});
