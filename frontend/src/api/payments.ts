import api from './auth';

// ── Types ──

export type TransactionType =
  | 'ACHAT_DOCUMENT'
  | 'RECRUTEMENT_AGRONOME'
  | 'PREVENTE'
  | 'TRANSPORT'
  | 'ABONNEMENT';

export type TransactionStatus = 'PENDING' | 'SUCCESS' | 'FAILED' | 'REFUNDED';

export type MobileMoneyMode = 'moov_tg' | 'togocel';

export interface PaymentInitResponse {
  success: boolean;
  transaction_id: string;
  fedapay_transaction_id: string;
  payment_url: string;
  token: string;
  message?: string;
}

export interface MobileMoneyResponse {
  success: boolean;
  transaction_id: string;
  fedapay_transaction_id: string;
  mode: string;
  mode_label: string;
  message: string;
}

export interface TransactionStatusResponse {
  transaction_id: string;
  statut: TransactionStatus;
  statut_display: string;
  montant: string;
  type: string;
  fedapay_transaction_id: string | null;
}

export interface PaymentCallbackResponse {
  success: boolean;
  transaction_id: string;
  statut: TransactionStatus;
  statut_display: string;
  montant: string;
  type: string;
  message: string;
}

export interface TransactionDetail {
  id: string;
  type_transaction: string;
  type_transaction_display: string;
  statut: TransactionStatus;
  statut_display: string;
  montant: string;
  montant_display: string;
  commission_plateforme: string;
  commission_display: string;
  reference_externe: string | null;
  fedapay_transaction_id: string | null;
  created_at: string;
  updated_at: string;
}

// ── Initier un paiement (redirection checkout FedaPay) ──

export async function initiatePayment(params: {
  type_transaction: TransactionType;
  montant: number;
  reference_externe?: string;
  description?: string;
}): Promise<PaymentInitResponse> {
  const res = await api.post('/payments/initiate', params);
  return res.data;
}

// ── Paiement Mobile Money direct (sans redirection) ──

export async function payMobileMoney(params: {
  type_transaction: TransactionType;
  montant: number;
  mode: MobileMoneyMode;
  phone_number: string;
  reference_externe?: string;
  description?: string;
}): Promise<MobileMoneyResponse> {
  const res = await api.post('/payments/mobile-money', params);
  return res.data;
}

// ── Vérifier le statut d'une transaction (polling) ──

export async function checkTransactionStatus(
  transactionId: string
): Promise<TransactionStatusResponse> {
  const res = await api.get(`/payments/status/${transactionId}`);
  return res.data;
}

// ── Callback (page de retour après paiement) ──

export async function verifyPaymentCallback(
  fedapayTransactionId: string
): Promise<PaymentCallbackResponse> {
  const res = await api.get('/payments/callback', {
    params: { transaction_id: fedapayTransactionId },
  });
  return res.data;
}

// ── Historique des transactions ──

export async function getTransactionHistory(params?: {
  type?: TransactionType;
  statut?: TransactionStatus;
}): Promise<{ results: TransactionDetail[]; count: number }> {
  const res = await api.get('/payments/transactions/history', { params });
  return res.data;
}

// ── Détail d'une transaction ──

export async function getTransactionDetail(
  transactionId: string
): Promise<TransactionDetail> {
  const res = await api.get(`/payments/transactions/${transactionId}`);
  return res.data;
}

// ── Helpers ──

export const MOBILE_MONEY_MODES: { value: MobileMoneyMode; label: string; icon: string }[] = [
  { value: 'moov_tg', label: 'Moov Money', icon: '📱' },
  { value: 'togocel', label: 'T-Money (Togocel)', icon: '📲' },
];

export function formatFCFA(amount: number | string): string {
  const num = typeof amount === 'string' ? parseInt(amount, 10) : amount;
  return num.toLocaleString('fr-FR') + ' FCFA';
}
