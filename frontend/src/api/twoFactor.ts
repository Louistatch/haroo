import api from './auth';

export interface TwoFactorStatus {
  user_type: string;
  two_factor_required: boolean;
  two_factor_enabled: boolean;
  message: string;
}

export interface TwoFactorSetupData {
  message: string;
  secret: string;
  qr_code: string;
  instructions: string[];
}

export interface TwoFactorEnableResult {
  message: string;
  backup_codes: string[];
  warning: string;
}

export async function get2FAStatus(): Promise<TwoFactorStatus> {
  const res = await api.get('/auth/2fa/status');
  return res.data;
}

export async function setup2FA(): Promise<TwoFactorSetupData> {
  const res = await api.post('/auth/2fa/setup');
  return res.data;
}

export async function enable2FA(token: string): Promise<TwoFactorEnableResult> {
  const res = await api.post('/auth/2fa/enable', { token });
  return res.data;
}

export async function disable2FA(password: string): Promise<{ message: string }> {
  const res = await api.post('/auth/2fa/disable', { password });
  return res.data;
}
