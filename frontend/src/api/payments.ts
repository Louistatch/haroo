import axios from 'axios';

const API_BASE_URL = '/api/v1';

export interface PaymentCallbackResponse {
  success: boolean;
  transaction_id: string;
  statut: 'PENDING' | 'SUCCESS' | 'FAILED' | 'REFUNDED';
  statut_display: string;
  montant: string;
  type: string;
  message: string;
}

export interface TransactionDetail {
  id: string;
  type_transaction: string;
  type_transaction_display: string;
  statut: 'PENDING' | 'SUCCESS' | 'FAILED' | 'REFUNDED';
  statut_display: string;
  montant: string;
  reference_externe: string | null;
  fedapay_transaction_id: string | null;
  created_at: string;
  updated_at: string;
}

/**
 * Verify payment status from callback
 * @param fedapayTransactionId - Fedapay transaction ID from URL
 * @returns Promise with payment verification result
 */
export async function verifyPaymentCallback(
  fedapayTransactionId: string
): Promise<PaymentCallbackResponse> {
  const response = await axios.get<PaymentCallbackResponse>(
    `${API_BASE_URL}/payments/callback`,
    {
      params: { transaction_id: fedapayTransactionId }
    }
  );

  return response.data;
}

/**
 * Get transaction details
 * @param transactionId - Internal transaction ID
 * @param token - JWT access token
 * @returns Promise with transaction details
 */
export async function getTransactionDetail(
  transactionId: string,
  token: string
): Promise<TransactionDetail> {
  const response = await axios.get<TransactionDetail>(
    `${API_BASE_URL}/transactions/${transactionId}`,
    {
      headers: { Authorization: `Bearer ${token}` }
    }
  );

  return response.data;
}
