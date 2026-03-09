import React, { useState, useEffect, useRef } from 'react';
import { useSearchParams, useNavigate } from 'react-router-dom';
import { motion, AnimatePresence } from 'framer-motion';
import {
  initiatePayment,
  payMobileMoney,
  checkTransactionStatus,
  MOBILE_MONEY_MODES,
  formatFCFA,
  type MobileMoneyMode,
  type TransactionType,
  type TransactionStatus,
} from '../api/payments';

const STATUS_LABELS: Record<TransactionStatus, { label: string; color: string; icon: string }> = {
  PENDING: { label: 'En attente', color: '#f59e0b', icon: '⏳' },
  SUCCESS: { label: 'Réussi', color: '#16a34a', icon: '✓' },
  FAILED: { label: 'Échoué', color: '#dc2626', icon: '✗' },
  REFUNDED: { label: 'Remboursé', color: '#6366f1', icon: '↩' },
};

export default function Payment() {
  const [params] = useSearchParams();
  const navigate = useNavigate();

  // From URL: ?type=ACHAT_DOCUMENT&montant=5000&ref=doc_123&desc=Achat+doc
  const typeParam = (params.get('type') || 'ACHAT_DOCUMENT') as TransactionType;
  const montantParam = parseInt(params.get('montant') || '0', 10);
  const refParam = params.get('ref') || '';
  const descParam = params.get('desc') || '';

  const [step, setStep] = useState<'choose' | 'mobile' | 'polling' | 'result'>('choose');
  const [mode, setMode] = useState<MobileMoneyMode>('moov_tg');
  const [phone, setPhone] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [transactionId, setTransactionId] = useState('');
  const [status, setStatus] = useState<TransactionStatus | null>(null);
  const pollRef = useRef<ReturnType<typeof setInterval> | null>(null);

  // Cleanup polling on unmount
  useEffect(() => () => { if (pollRef.current) clearInterval(pollRef.current); }, []);

  // ── Redirect to FedaPay checkout ──
  async function handleCheckout() {
    setLoading(true); setError('');
    try {
      const res = await initiatePayment({
        type_transaction: typeParam,
        montant: montantParam,
        reference_externe: refParam,
        description: descParam,
      });
      if (res.payment_url) {
        window.location.href = res.payment_url;
      } else {
        setError("URL de paiement non reçue");
      }
    } catch (e: any) {
      setError(e?.response?.data?.error || e?.message || "Erreur lors de l'initiation");
    } finally { setLoading(false); }
  }

  // ── Mobile Money direct ──
  async function handleMobileMoney(e: React.FormEvent) {
    e.preventDefault();
    if (!phone || phone.length < 8) { setError('Numéro invalide'); return; }
    setLoading(true); setError('');
    try {
      const res = await payMobileMoney({
        type_transaction: typeParam,
        montant: montantParam,
        mode,
        phone_number: phone,
        reference_externe: refParam,
        description: descParam,
      });
      setTransactionId(res.transaction_id);
      setStep('polling');
      startPolling(res.transaction_id);
    } catch (e: any) {
      setError(e?.response?.data?.error || e?.response?.data?.errors?.phone_number?.[0] || "Erreur paiement");
    } finally { setLoading(false); }
  }

  // ── Poll transaction status ──
  function startPolling(txnId: string) {
    let attempts = 0;
    pollRef.current = setInterval(async () => {
      attempts++;
      try {
        const res = await checkTransactionStatus(txnId);
        if (res.statut !== 'PENDING') {
          setStatus(res.statut);
          setStep('result');
          if (pollRef.current) clearInterval(pollRef.current);
        }
      } catch { /* ignore polling errors */ }
      if (attempts >= 60) { // 2 minutes max
        if (pollRef.current) clearInterval(pollRef.current);
        setStatus('PENDING');
        setStep('result');
      }
    }, 2000);
  }

  const card: React.CSSProperties = {
    background: 'var(--surface)', border: '1px solid var(--border)',
    borderRadius: 16, padding: '2rem', maxWidth: 480, margin: '0 auto',
  };
  const btn: React.CSSProperties = {
    width: '100%', padding: '0.85rem', borderRadius: 12, border: 'none',
    fontWeight: 700, fontSize: '0.95rem', cursor: 'pointer', transition: 'all 0.2s',
  };
  const input: React.CSSProperties = {
    width: '100%', padding: '0.75rem 1rem', borderRadius: 10,
    border: '1.5px solid var(--border)', fontSize: '1rem',
    background: 'var(--bg)', color: 'var(--text)', outline: 'none',
    boxSizing: 'border-box',
  };

  return (
    <div style={{ minHeight: '100vh', background: 'var(--bg)', paddingTop: '6rem' }}>
      <div style={{ maxWidth: 520, margin: '0 auto', padding: '0 1.5rem' }}>

        {/* Header */}
        <motion.div initial={{ opacity: 0, y: 16 }} animate={{ opacity: 1, y: 0 }}
          style={{ textAlign: 'center', marginBottom: '2rem' }}>
          <h1 style={{ fontSize: '1.5rem', fontWeight: 800, color: 'var(--text)', margin: 0 }}>
            Paiement
          </h1>
          {montantParam > 0 && (
            <p style={{ fontSize: '2rem', fontWeight: 800, color: 'var(--primary)', margin: '0.5rem 0 0' }}>
              {formatFCFA(montantParam)}
            </p>
          )}
          {descParam && (
            <p style={{ color: 'var(--text-muted)', fontSize: '0.9rem', margin: '0.25rem 0 0' }}>
              {descParam}
            </p>
          )}
        </motion.div>

        <AnimatePresence mode="wait">
          {/* ── Step 1: Choose payment method ── */}
          {step === 'choose' && (
            <motion.div key="choose" initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }} style={card}>
              <p style={{ fontWeight: 700, marginBottom: '1.25rem', color: 'var(--text)' }}>
                Choisissez votre mode de paiement
              </p>

              {/* Mobile Money options */}
              <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem', marginBottom: '1.25rem' }}>
                {MOBILE_MONEY_MODES.map(m => (
                  <motion.button key={m.value} whileHover={{ scale: 1.01 }} whileTap={{ scale: 0.98 }}
                    onClick={() => { setMode(m.value); setStep('mobile'); }}
                    style={{
                      ...btn,
                      background: 'var(--bg)', color: 'var(--text)',
                      border: '1.5px solid var(--border)', display: 'flex',
                      alignItems: 'center', gap: '0.75rem', justifyContent: 'flex-start',
                    }}>
                    <span style={{ fontSize: '1.5rem' }}>{m.icon}</span>
                    <span>{m.label}</span>
                  </motion.button>
                ))}
              </div>

              <div style={{ textAlign: 'center', color: 'var(--text-muted)', fontSize: '0.82rem', margin: '1rem 0' }}>
                — ou —
              </div>

              {/* FedaPay checkout redirect */}
              <motion.button whileHover={{ scale: 1.01 }} whileTap={{ scale: 0.98 }}
                onClick={handleCheckout} disabled={loading}
                style={{
                  ...btn, background: 'var(--primary)', color: '#fff',
                  opacity: loading ? 0.6 : 1,
                }}>
                {loading ? 'Redirection...' : '💳 Payer via FedaPay Checkout'}
              </motion.button>

              {error && (
                <p style={{ color: '#dc2626', fontSize: '0.85rem', marginTop: '0.75rem', textAlign: 'center' }}>
                  {error}
                </p>
              )}
            </motion.div>
          )}

          {/* ── Step 2: Mobile Money form ── */}
          {step === 'mobile' && (
            <motion.div key="mobile" initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }} style={card}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '1.25rem' }}>
                <button onClick={() => { setStep('choose'); setError(''); }}
                  style={{ background: 'none', border: 'none', cursor: 'pointer', fontSize: '1.2rem', color: 'var(--text-muted)' }}>
                  ←
                </button>
                <p style={{ fontWeight: 700, color: 'var(--text)', margin: 0 }}>
                  {MOBILE_MONEY_MODES.find(m => m.value === mode)?.icon}{' '}
                  {MOBILE_MONEY_MODES.find(m => m.value === mode)?.label}
                </p>
              </div>

              <form onSubmit={handleMobileMoney} style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
                <div>
                  <label style={{ display: 'block', fontSize: '0.82rem', fontWeight: 600, color: 'var(--text-muted)', marginBottom: 4 }}>
                    Numéro de téléphone
                  </label>
                  <div style={{ display: 'flex', alignItems: 'center', gap: 0 }}>
                    <span style={{
                      padding: '0.75rem 0.75rem', background: 'var(--border)', borderRadius: '10px 0 0 10px',
                      fontSize: '0.9rem', color: 'var(--text-muted)', border: '1.5px solid var(--border)', borderRight: 'none',
                    }}>+228</span>
                    <input
                      type="tel" value={phone} onChange={e => setPhone(e.target.value.replace(/\D/g, '').slice(0, 8))}
                      placeholder="90 12 34 56" maxLength={8} autoFocus
                      style={{ ...input, borderRadius: '0 10px 10px 0' }}
                    />
                  </div>
                </div>

                <motion.button type="submit" whileHover={{ scale: 1.01 }} whileTap={{ scale: 0.98 }}
                  disabled={loading || phone.length < 8}
                  style={{
                    ...btn, background: 'var(--primary)', color: '#fff',
                    opacity: (loading || phone.length < 8) ? 0.5 : 1,
                  }}>
                  {loading ? 'Envoi en cours...' : `Payer ${formatFCFA(montantParam)}`}
                </motion.button>

                {error && (
                  <p style={{ color: '#dc2626', fontSize: '0.85rem', textAlign: 'center' }}>{error}</p>
                )}

                <p style={{ fontSize: '0.78rem', color: 'var(--text-muted)', textAlign: 'center' }}>
                  Vous recevrez une demande de paiement sur votre téléphone.
                  Validez avec votre code PIN.
                </p>
              </form>
            </motion.div>
          )}

          {/* ── Step 3: Polling ── */}
          {step === 'polling' && (
            <motion.div key="polling" initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}
              style={{ ...card, textAlign: 'center' }}>
              <motion.div animate={{ rotate: 360 }} transition={{ duration: 1.2, repeat: Infinity, ease: 'linear' }}
                style={{ width: 48, height: 48, border: '3px solid var(--border)', borderTop: '3px solid var(--primary)', borderRadius: '50%', margin: '0 auto 1.5rem' }} />
              <p style={{ fontWeight: 700, color: 'var(--text)', fontSize: '1.1rem' }}>
                En attente de validation
              </p>
              <p style={{ color: 'var(--text-muted)', fontSize: '0.88rem' }}>
                Validez le paiement sur votre téléphone avec votre code PIN.
              </p>
            </motion.div>
          )}

          {/* ── Step 4: Result ── */}
          {step === 'result' && status && (
            <motion.div key="result" initial={{ opacity: 0, scale: 0.95 }} animate={{ opacity: 1, scale: 1 }} exit={{ opacity: 0 }}
              style={{ ...card, textAlign: 'center' }}>
              <div style={{
                width: 64, height: 64, borderRadius: '50%', margin: '0 auto 1rem',
                background: `${STATUS_LABELS[status].color}15`,
                display: 'flex', alignItems: 'center', justifyContent: 'center',
                fontSize: '2rem', color: STATUS_LABELS[status].color,
              }}>
                {STATUS_LABELS[status].icon}
              </div>
              <p style={{ fontWeight: 800, fontSize: '1.2rem', color: STATUS_LABELS[status].color }}>
                {STATUS_LABELS[status].label}
              </p>
              <p style={{ color: 'var(--text-muted)', fontSize: '0.88rem', margin: '0.5rem 0 1.5rem' }}>
                {status === 'SUCCESS' && 'Votre paiement a été effectué avec succès.'}
                {status === 'FAILED' && 'Le paiement a échoué. Vérifiez votre solde et réessayez.'}
                {status === 'PENDING' && 'Le paiement est toujours en cours de traitement.'}
                {status === 'REFUNDED' && 'Votre paiement a été remboursé.'}
              </p>

              <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
                {status === 'SUCCESS' && (
                  <motion.button whileHover={{ scale: 1.01 }} whileTap={{ scale: 0.98 }}
                    onClick={() => navigate('/purchases')}
                    style={{ ...btn, background: 'var(--primary)', color: '#fff' }}>
                    Voir mes achats
                  </motion.button>
                )}
                {status === 'FAILED' && (
                  <motion.button whileHover={{ scale: 1.01 }} whileTap={{ scale: 0.98 }}
                    onClick={() => { setStep('choose'); setError(''); setStatus(null); }}
                    style={{ ...btn, background: 'var(--primary)', color: '#fff' }}>
                    Réessayer
                  </motion.button>
                )}
                <motion.button whileHover={{ scale: 1.01 }} whileTap={{ scale: 0.98 }}
                  onClick={() => navigate('/home')}
                  style={{ ...btn, background: 'var(--bg)', color: 'var(--text)', border: '1.5px solid var(--border)' }}>
                  Retour à l'accueil
                </motion.button>
              </div>
            </motion.div>
          )}
        </AnimatePresence>

        {/* Sandbox notice */}
        <p style={{ textAlign: 'center', fontSize: '0.75rem', color: 'var(--text-muted)', marginTop: '2rem' }}>
          🔒 Paiement sécurisé via FedaPay · Environnement sandbox
        </p>
      </div>
    </div>
  );
}
