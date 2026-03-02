/**
 * Unit tests for PaymentSuccess component
 */

import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, waitFor } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import PaymentSuccess from '../PaymentSuccess';
import * as paymentsApi from '../../api/payments';
import * as purchasesApi from '../../api/purchases';

vi.mock('../../api/payments');
vi.mock('../../api/purchases');
vi.mock('react-router-dom', async () => {
  const actual = await vi.importActual('react-router-dom');
  return {
    ...actual,
    useNavigate: () => vi.fn(),
    useSearchParams: () => [new URLSearchParams('transaction_id=fedapay_123')],
  };
});

const mockPaymentResponse = {
  success: true,
  transaction_id: 'txn_123',
  statut: 'SUCCESS',
  statut_display: 'Payé',
  montant: '5000',
  type: 'Achat de document',
  message: 'Paiement réussi',
};

const mockPurchaseHistory = {
  count: 1,
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
      nombre_telechargements: 0,
      created_at: '2024-01-01T10:00:00Z',
    },
  ],
};

describe('PaymentSuccess Component', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    localStorage.setItem('access_token', 'fake-token');
  });

  it('should show loading state initially', () => {
    vi.mocked(paymentsApi.verifyPaymentCallback).mockImplementation(
      () => new Promise(() => {})
    );

    render(
      <BrowserRouter>
        <PaymentSuccess />
      </BrowserRouter>
    );

    expect(screen.getByText(/Vérification du paiement/i)).toBeInTheDocument();
  });

  it('should display success state for successful payment', async () => {
    vi.mocked(paymentsApi.verifyPaymentCallback).mockResolvedValue(mockPaymentResponse);
    vi.mocked(purchasesApi.fetchPurchaseHistory).mockResolvedValue(mockPurchaseHistory);

    render(
      <BrowserRouter>
        <PaymentSuccess />
      </BrowserRouter>
    );

    await waitFor(() => {
      expect(screen.getByText(/Paiement réussi/i)).toBeInTheDocument();
      expect(screen.getByText('Guide Maïs Maritime')).toBeInTheDocument();
    });
  });

  it('should display document details', async () => {
    vi.mocked(paymentsApi.verifyPaymentCallback).mockResolvedValue(mockPaymentResponse);
    vi.mocked(purchasesApi.fetchPurchaseHistory).mockResolvedValue(mockPurchaseHistory);

    render(
      <BrowserRouter>
        <PaymentSuccess />
      </BrowserRouter>
    );

    await waitFor(() => {
      expect(screen.getByText('Guide Maïs Maritime')).toBeInTheDocument();
      expect(screen.getByText('Maïs')).toBeInTheDocument();
      expect(screen.getByText(/5\.000 FCFA/i)).toBeInTheDocument();
    });
  });

  it('should show expiration notice', async () => {
    vi.mocked(paymentsApi.verifyPaymentCallback).mockResolvedValue(mockPaymentResponse);
    vi.mocked(purchasesApi.fetchPurchaseHistory).mockResolvedValue(mockPurchaseHistory);

    render(
      <BrowserRouter>
        <PaymentSuccess />
      </BrowserRouter>
    );

    await waitFor(() => {
      expect(screen.getByText(/Lien de téléchargement valide pendant 48h/i)).toBeInTheDocument();
    });
  });

  it('should display failed payment state', async () => {
    vi.mocked(paymentsApi.verifyPaymentCallback).mockResolvedValue({
      ...mockPaymentResponse,
      statut: 'FAILED',
    });

    render(
      <BrowserRouter>
        <PaymentSuccess />
      </BrowserRouter>
    );

    await waitFor(() => {
      expect(screen.getByText(/Paiement échoué/i)).toBeInTheDocument();
    });
  });

  it('should display pending payment state', async () => {
    vi.mocked(paymentsApi.verifyPaymentCallback).mockResolvedValue({
      ...mockPaymentResponse,
      statut: 'PENDING',
    });

    render(
      <BrowserRouter>
        <PaymentSuccess />
      </BrowserRouter>
    );

    await waitFor(() => {
      expect(screen.getByText(/Paiement en cours/i)).toBeInTheDocument();
    });
  });

  it('should handle missing transaction_id', async () => {
    vi.mocked(paymentsApi.verifyPaymentCallback).mockRejectedValue({
      response: { status: 400 },
    });

    render(
      <BrowserRouter>
        <PaymentSuccess />
      </BrowserRouter>
    );

    await waitFor(() => {
      expect(screen.getByText(/Erreur/i)).toBeInTheDocument();
    });
  });

  it('should handle 404 error', async () => {
    vi.mocked(paymentsApi.verifyPaymentCallback).mockRejectedValue({
      response: { status: 404 },
    });

    render(
      <BrowserRouter>
        <PaymentSuccess />
      </BrowserRouter>
    );

    await waitFor(() => {
      expect(screen.getByText(/Transaction introuvable/i)).toBeInTheDocument();
    });
  });

  it('should show download button for successful payment', async () => {
    vi.mocked(paymentsApi.verifyPaymentCallback).mockResolvedValue(mockPaymentResponse);
    vi.mocked(purchasesApi.fetchPurchaseHistory).mockResolvedValue(mockPurchaseHistory);

    render(
      <BrowserRouter>
        <PaymentSuccess />
      </BrowserRouter>
    );

    await waitFor(() => {
      expect(screen.getByText(/Télécharger maintenant/i)).toBeInTheDocument();
    });
  });

  it('should show link to purchase history', async () => {
    vi.mocked(paymentsApi.verifyPaymentCallback).mockResolvedValue(mockPaymentResponse);
    vi.mocked(purchasesApi.fetchPurchaseHistory).mockResolvedValue(mockPurchaseHistory);

    render(
      <BrowserRouter>
        <PaymentSuccess />
      </BrowserRouter>
    );

    await waitFor(() => {
      expect(screen.getByText(/Voir mes achats/i)).toBeInTheDocument();
    });
  });
});
