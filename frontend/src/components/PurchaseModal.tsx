import React from 'react';
import { motion, AnimatePresence } from 'framer-motion';

interface Document {
  id: number;
  titre: string;
  description: string;
  prix: string;
  culture: string;
  region: string;
  prefecture: string;
  canton: string;
}

interface PurchaseModalProps {
  document: Document | null;
  isOpen: boolean;
  onClose: () => void;
  onConfirm: () => void;
  isProcessing: boolean;
}

export default function PurchaseModal({ document, isOpen, onClose, onConfirm, isProcessing }: PurchaseModalProps) {
  if (!document) return null;

  const price = parseInt(document.prix).toLocaleString('fr-FR');
  const location = document.canton || document.prefecture || document.region;

  return (
    <AnimatePresence>
      {isOpen && (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          exit={{ opacity: 0 }}
          onClick={onClose}
          style={{
            position: 'fixed', inset: 0,
            background: 'rgba(0,0,0,0.65)',
            backdropFilter: 'blur(6px)',
            display: 'flex', alignItems: 'center', justifyContent: 'center',
            zIndex: 1000, padding: '1rem',
          }}>
          <motion.div
            initial={{ opacity: 0, scale: 0.92, y: 20 }}
            animate={{ opacity: 1, scale: 1, y: 0, transition: { duration: 0.35, ease: [0.22, 1, 0.36, 1] } }}
            exit={{ opacity: 0, scale: 0.94, y: 10, transition: { duration: 0.2 } }}
            onClick={e => e.stopPropagation()}
            style={{
              background: 'var(--surface)',
              borderRadius: '20px',
              maxWidth: '520px',
              width: '100%',
              border: '1px solid var(--border)',
              boxShadow: '0 32px 80px rgba(0,0,0,0.3)',
              overflow: 'hidden',
            }}>

            {/* Header */}
            <div style={{
              background: 'linear-gradient(135deg, #052e16 0%, #14532d 100%)',
              padding: '1.75rem 2rem',
              position: 'relative',
            }}>
              <button
                onClick={onClose}
                style={{
                  position: 'absolute', top: '1rem', right: '1rem',
                  background: 'rgba(255,255,255,0.15)', border: 'none',
                  width: 34, height: 34, borderRadius: '50%',
                  cursor: 'pointer', color: 'white', fontSize: '1.1rem',
                  display: 'flex', alignItems: 'center', justifyContent: 'center',
                  transition: 'background 0.2s',
                }}
                onMouseEnter={e => (e.currentTarget.style.background = 'rgba(255,255,255,0.3)')}
                onMouseLeave={e => (e.currentTarget.style.background = 'rgba(255,255,255,0.15)')}>
                <svg width="16" height="16" viewBox="0 0 16 16" fill="none"><path d="M3 3l10 10M13 3L3 13" stroke="currentColor" strokeWidth="2" strokeLinecap="round"/></svg>
              </button>

              <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
                <div style={{
                  width: 44, height: 44, borderRadius: '12px',
                  background: 'rgba(74,222,128,0.2)',
                  border: '1px solid rgba(74,222,128,0.3)',
                  display: 'flex', alignItems: 'center', justifyContent: 'center',
                }}>
                  <svg width="22" height="22" viewBox="0 0 22 22" fill="none">
                    <rect x="2" y="5" width="18" height="14" rx="2" stroke="#4ade80" strokeWidth="1.5"/>
                    <path d="M15 5V4a4 4 0 00-8 0v1" stroke="#4ade80" strokeWidth="1.5"/>
                    <path d="M7 11h8M7 15h5" stroke="#4ade80" strokeWidth="1.5" strokeLinecap="round"/>
                  </svg>
                </div>
                <div>
                  <div style={{ color: 'rgba(255,255,255,0.6)', fontSize: '0.75rem', fontWeight: 600, textTransform: 'uppercase', letterSpacing: '0.06em' }}>Confirmation d'achat</div>
                  <h2 style={{ color: 'white', fontSize: '1.2rem', fontWeight: 800, margin: 0 }}>{document.titre}</h2>
                </div>
              </div>
            </div>

            {/* Body */}
            <div style={{ padding: '1.75rem 2rem' }}>

              {/* doc summary */}
              <div style={{
                background: 'var(--bg)',
                borderRadius: '14px',
                padding: '1.25rem',
                marginBottom: '1.25rem',
                border: '1px solid var(--border)',
              }}>
                <p style={{ color: 'var(--text-muted)', fontSize: '0.9rem', lineHeight: 1.6, margin: 0 }}>
                  {document.description}
                </p>
              </div>

              {/* detail rows */}
              <div style={{ marginBottom: '1.5rem' }}>
                {[
                  { label: 'Culture', value: document.culture, icon: <svg width="15" height="15" viewBox="0 0 15 15" fill="none"><path d="M7.5 13V7M7.5 7C7.5 7 5 5 3 6M7.5 7C7.5 7 10 5 12 6" stroke="var(--text-muted)" strokeWidth="1.3" strokeLinecap="round"/><circle cx="7.5" cy="4" r="1.5" stroke="var(--text-muted)" strokeWidth="1.3"/></svg> },
                  { label: 'Localisation', value: location, icon: <svg width="15" height="15" viewBox="0 0 15 15" fill="none"><path d="M7.5 13S3 9 3 6a4.5 4.5 0 019 0c0 3-4.5 7-4.5 7z" stroke="var(--text-muted)" strokeWidth="1.3"/><circle cx="7.5" cy="6" r="1.5" stroke="var(--text-muted)" strokeWidth="1.3"/></svg> },
                ].map(({ label, value, icon }) => (
                  <div key={label} style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', padding: '0.75rem 0', borderBottom: '1px solid var(--border)' }}>
                    <span style={{ color: 'var(--text-secondary)', fontSize: '0.9rem', display: 'flex', alignItems: 'center', gap: 8 }}>
                      {icon} {label}
                    </span>
                    <span style={{ color: 'var(--text)', fontWeight: 600, fontSize: '0.9rem' }}>{value}</span>
                  </div>
                ))}
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', padding: '1rem 0 0', marginTop: '0.25rem' }}>
                  <span style={{ color: 'var(--text-secondary)', fontSize: '0.9rem', display: 'flex', alignItems: 'center', gap: 6 }}><svg width="15" height="15" viewBox="0 0 15 15" fill="none"><rect x="1" y="3" width="13" height="9" rx="1.5" stroke="var(--text-muted)" strokeWidth="1.3"/><path d="M1 6.5h13" stroke="var(--text-muted)" strokeWidth="1.3"/><path d="M3.5 9.5h3" stroke="var(--text-muted)" strokeWidth="1.3" strokeLinecap="round"/></svg> Prix total</span>
                  <span style={{ color: 'var(--primary)', fontSize: '1.5rem', fontWeight: 800 }}>{price} FCFA</span>
                </div>
              </div>

              {/* guarantees */}
              <div style={{ display: 'flex', flexDirection: 'column', gap: '0.6rem' }}>
                {[
                  'Accès immédiat après paiement',
                  'Lien de téléchargement valide 48h',
                  'Paiement sécurisé via Fedapay',
                ].map(text => (
                  <div key={text} style={{ display: 'flex', alignItems: 'center', gap: '0.6rem' }}>
                    <div style={{ width: 20, height: 20, borderRadius: '50%', background: 'rgba(22,163,74,0.1)', display: 'flex', alignItems: 'center', justifyContent: 'center', flexShrink: 0 }}>
                      <svg width="10" height="10" viewBox="0 0 10 10" fill="none">
                        <path d="M2 5l2 2 4-4" stroke="var(--primary)" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round"/>
                      </svg>
                    </div>
                    <span style={{ color: 'var(--text-muted)', fontSize: '0.85rem' }}>{text}</span>
                  </div>
                ))}
              </div>
            </div>

            {/* Footer */}
            <div style={{ padding: '1.25rem 2rem', borderTop: '1px solid var(--border)', display: 'flex', gap: '0.75rem' }}>
              <motion.button
                whileHover={{ scale: 1.02 }} whileTap={{ scale: 0.97 }}
                onClick={onClose}
                disabled={isProcessing}
                style={{
                  flex: '0 0 auto', padding: '0.75rem 1.25rem',
                  background: 'var(--bg)', border: '1.5px solid var(--border)',
                  borderRadius: '12px', color: 'var(--text-secondary)',
                  fontWeight: 600, fontSize: '0.9rem', cursor: isProcessing ? 'not-allowed' : 'pointer',
                  opacity: isProcessing ? 0.5 : 1,
                }}>
                Annuler
              </motion.button>
              <motion.button
                whileHover={!isProcessing ? { scale: 1.02 } : {}}
                whileTap={!isProcessing ? { scale: 0.97 } : {}}
                onClick={onConfirm}
                disabled={isProcessing}
                style={{
                  flex: 1, padding: '0.75rem 1.5rem',
                  background: 'linear-gradient(135deg, var(--primary-dark), var(--primary))',
                  border: 'none', borderRadius: '12px',
                  color: 'white', fontWeight: 700, fontSize: '0.95rem',
                  cursor: isProcessing ? 'not-allowed' : 'pointer',
                  opacity: isProcessing ? 0.7 : 1,
                  display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 8,
                  boxShadow: '0 4px 16px rgba(22,163,74,0.3)',
                }}>
                {isProcessing ? (
                  <>
                    <motion.div
                      animate={{ rotate: 360 }}
                      transition={{ duration: 0.8, repeat: Infinity, ease: 'linear' }}
                      style={{ width: 16, height: 16, border: '2px solid rgba(255,255,255,0.3)', borderTop: '2px solid white', borderRadius: '50%' }}
                    />
                    Traitement...
                  </>
                ) : (
                  <>
                    <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
                      <rect x="1" y="4" width="14" height="10" rx="1.5" stroke="white" strokeWidth="1.3"/>
                      <path d="M1 8h14" stroke="white" strokeWidth="1.3"/>
                      <path d="M5 1v3M11 1v3" stroke="white" strokeWidth="1.3" strokeLinecap="round"/>
                    </svg>
                    Procéder au paiement
                  </>
                )}
              </motion.button>
            </div>
          </motion.div>
        </motion.div>
      )}
    </AnimatePresence>
  );
}
