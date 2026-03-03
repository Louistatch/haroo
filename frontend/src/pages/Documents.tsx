import React, { useState, useEffect, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import { motion, AnimatePresence } from 'framer-motion';
import { useToast } from '../hooks/useToast';
import Toast from '../components/Toast';
import PurchaseModal from '../components/PurchaseModal';
import { fetchPurchaseHistory, buildDownloadUrl } from '../api/purchases';
import api from '../api/auth';

interface Document {
  id: number;
  titre: string;
  description: string;
  prix: string;
  culture: string;
  region: string;
  prefecture: string;
  canton: string;
  is_purchased?: boolean;
  lien_telechargement?: string;
}

const CULTURES = ['Maïs', 'Riz', 'Manioc', 'Tomate', 'Oignon', 'Arachide', 'Niébé', 'Sorgho'];
const REGIONS = ['Maritime', 'Plateaux', 'Centrale', 'Kara', 'Savanes'];

const CULTURE_COLORS: Record<string, string> = {
  Maïs: '#f59e0b', Riz: '#3b82f6', Manioc: '#8b5cf6', Tomate: '#ef4444',
  Oignon: '#f97316', Arachide: '#d97706', Niébé: '#10b981', Sorgho: '#6366f1',
};

const DocumentIcon = () => (
  <svg width="40" height="40" viewBox="0 0 40 40" fill="none">
    <rect width="40" height="40" rx="10" fill="var(--primary)" fillOpacity="0.1" />
    <path d="M12 10h11l7 7v13a2 2 0 01-2 2H12a2 2 0 01-2-2V12a2 2 0 012-2z" stroke="var(--primary)" strokeWidth="1.5" fill="none"/>
    <path d="M23 10v7h7" stroke="var(--primary)" strokeWidth="1.5" fill="none"/>
    <path d="M16 22h8M16 26h5" stroke="var(--primary)" strokeWidth="1.5" strokeLinecap="round"/>
  </svg>
);

const DownloadIcon = () => (
  <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
    <path d="M8 2v8M5 7l3 3 3-3M3 13h10" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round"/>
  </svg>
);

const CartIcon = () => (
  <svg width="16" height="16" viewBox="0 0 16 16" fill="none">
    <path d="M1 1h2l1.5 7.5h7l1.5-5H4.5" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round"/>
    <circle cx="6.5" cy="13" r="1" fill="currentColor"/>
    <circle cx="11.5" cy="13" r="1" fill="currentColor"/>
  </svg>
);

const FilterIcon = () => (
  <svg width="18" height="18" viewBox="0 0 18 18" fill="none">
    <path d="M2 4h14M5 9h8M8 14h2" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round"/>
  </svg>
);

const cardVariants = {
  hidden: { opacity: 0, y: 24 },
  visible: (i: number) => ({
    opacity: 1, y: 0,
    transition: { delay: i * 0.06, duration: 0.4, ease: [0.22, 1, 0.36, 1] },
  }),
};

export default function Documents() {
  const [documents, setDocuments] = useState<Document[]>([]);
  const [loading, setLoading] = useState(true);
  const [filters, setFilters] = useState({ culture: '', region: '', search: '' });
  const [selectedDocument, setSelectedDocument] = useState<Document | null>(null);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [isProcessing, setIsProcessing] = useState(false);
  const [purchasedDocuments, setPurchasedDocuments] = useState<Set<number>>(new Set());
  const [sidebarOpen, setSidebarOpen] = useState(false);

  const navigate = useNavigate();
  const { toasts, removeToast, success, error: showError, info } = useToast();

  const hasActiveFilters = filters.culture !== '' || filters.region !== '' || filters.search !== '';

  const checkPurchasedDocuments = useCallback(async () => {
    try {
      const token = localStorage.getItem('access_token');
      if (!token) { setPurchasedDocuments(new Set()); return; }
      const history = await fetchPurchaseHistory({ page_size: 1000 }, token);
      const ids = new Set(
        history.results
          .filter(p => p.transaction_statut === 'SUCCESS' && !p.lien_expire)
          .map(p => p.document)
      );
      setPurchasedDocuments(ids);
    } catch { setPurchasedDocuments(new Set()); }
  }, []);

  const fetchDocuments = useCallback(async () => {
    try {
      const params = new URLSearchParams();
      if (filters.culture) params.append('culture', filters.culture);
      if (filters.region) params.append('region', filters.region);
      if (filters.search) params.append('search', filters.search);
      const response = await api.get(`/documents/?${params}`);
      const docs = (response.data.results || []).map((doc: Document) => ({
        ...doc,
        is_purchased: purchasedDocuments.has(doc.id),
      }));
      setDocuments(docs);
    } catch (err: any) {
      const status = err.response?.status;
      if (status === 500) showError('Erreur serveur', 'Le serveur rencontre des difficultés');
      else if (err.code === 'ERR_NETWORK') showError('Erreur réseau', 'Impossible de contacter le serveur');
      else showError('Erreur', 'Impossible de charger les documents');
      setDocuments([]);
    }
  }, [filters, purchasedDocuments, showError]);

  useEffect(() => {
    const load = async () => {
      setLoading(true);
      await checkPurchasedDocuments();
      await fetchDocuments();
      setLoading(false);
    };
    load();
  }, [filters]);

  const handlePurchaseClick = (doc: Document) => {
    const token = localStorage.getItem('access_token');
    if (!token) {
      info('Connexion requise', 'Veuillez vous connecter pour acheter un document');
      setTimeout(() => navigate('/login'), 1500);
      return;
    }
    if (doc.is_purchased) handleDownload(doc);
    else { setSelectedDocument(doc); setIsModalOpen(true); }
  };

  const handleConfirmPurchase = async () => {
    if (!selectedDocument) return;
    try {
      setIsProcessing(true);
      const response = await api.post(`/documents/${selectedDocument.id}/purchase`, {});
      if (response.data.already_purchased) {
        success('Déjà acheté', 'Vous possédez déjà ce document');
        setIsModalOpen(false);
        await checkPurchasedDocuments();
        await fetchDocuments();
      } else if (response.data.payment_url) {
        info('Redirection', 'Redirection vers la page de paiement...');
        setTimeout(() => { window.location.href = response.data.payment_url; }, 1000);
      }
    } catch (err: any) {
      if (err.response?.status === 401) {
        showError('Session expirée', 'Veuillez vous reconnecter');
        setTimeout(() => navigate('/login'), 2000);
      } else {
        showError('Erreur', err.response?.data?.error || 'Impossible de procéder à l\'achat');
      }
    } finally { setIsProcessing(false); }
  };

  const handleDownload = async (doc: Document) => {
    try {
      const token = localStorage.getItem('access_token');
      if (!token) { showError('Non authentifié', 'Veuillez vous connecter'); navigate('/login'); return; }
      const history = await fetchPurchaseHistory({ page_size: 1000 }, token);
      const purchase = history.results.find(p => p.document === doc.id && p.transaction_statut === 'SUCCESS');
      if (purchase) {
        if (purchase.lien_expire) {
          showError('Lien expiré', 'Le lien de téléchargement a expiré');
          setTimeout(() => navigate('/purchases'), 2000);
        } else {
          window.open(buildDownloadUrl(purchase.document, purchase.lien_telechargement), '_blank');
          success('Téléchargement', 'Le document va s\'ouvrir dans un nouvel onglet');
        }
      }
    } catch { showError('Erreur', 'Impossible de télécharger le document'); }
  };

  return (
    <>
      <div className="toast-container">
        {toasts.map(t => <Toast key={t.id} {...t} onClose={removeToast} />)}
      </div>
      <PurchaseModal
        document={selectedDocument} isOpen={isModalOpen}
        onClose={() => setIsModalOpen(false)}
        onConfirm={handleConfirmPurchase} isProcessing={isProcessing}
      />

      <div style={{ minHeight: '100vh', background: 'var(--bg)' }}>

        {/* ── HERO ── */}
        <div style={{
          background: 'linear-gradient(135deg, #052e16 0%, #14532d 50%, #166534 100%)',
          padding: '5rem 2rem 4rem',
          position: 'relative',
          overflow: 'hidden',
        }}>
          <div style={{
            position: 'absolute', inset: 0,
            backgroundImage: 'radial-gradient(circle at 20% 50%, rgba(74,222,128,0.08) 0%, transparent 50%), radial-gradient(circle at 80% 20%, rgba(34,197,94,0.06) 0%, transparent 40%)',
          }} />
          <div style={{ position: 'absolute', inset: 0, backgroundImage: 'linear-gradient(rgba(255,255,255,0.02) 1px, transparent 1px), linear-gradient(90deg, rgba(255,255,255,0.02) 1px, transparent 1px)', backgroundSize: '60px 60px' }} />
          <div style={{ maxWidth: '800px', margin: '0 auto', textAlign: 'center', position: 'relative' }}>
            <motion.div initial={{ opacity: 0, y: -10 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.5 }}
              style={{ display: 'inline-flex', alignItems: 'center', gap: '8px', background: 'rgba(74,222,128,0.15)', border: '1px solid rgba(74,222,128,0.3)', borderRadius: '100px', padding: '6px 16px', marginBottom: '1.5rem' }}>
              <span style={{ width: 8, height: 8, borderRadius: '50%', background: '#4ade80', display: 'inline-block' }} />
              <span style={{ color: '#86efac', fontSize: '0.85rem', fontWeight: 600, letterSpacing: '0.05em' }}>BIBLIOTHÈQUE TECHNIQUE</span>
            </motion.div>
            <motion.h1 initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.6, delay: 0.1 }}
              style={{ fontSize: 'clamp(2rem, 5vw, 3.2rem)', fontWeight: 800, color: 'white', marginBottom: '1rem', lineHeight: 1.2 }}>
              Documents Techniques
              <span style={{ display: 'block', color: '#4ade80' }}>Agricoles</span>
            </motion.h1>
            <motion.p initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.6, delay: 0.2 }}
              style={{ color: 'rgba(255,255,255,0.7)', fontSize: '1.15rem', maxWidth: '560px', margin: '0 auto 2.5rem' }}>
              Guides pratiques et comptes d'exploitation élaborés par des experts, adaptés à chaque région du Togo.
            </motion.p>
            <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.6, delay: 0.3 }}
              style={{ display: 'flex', gap: '2rem', justifyContent: 'center', flexWrap: 'wrap' }}>
              {[['12+', 'Documents'], ['6', 'Cultures'], ['5', 'Régions']].map(([num, label]) => (
                <div key={label} style={{ textAlign: 'center' }}>
                  <div style={{ fontSize: '1.8rem', fontWeight: 800, color: '#4ade80' }}>{num}</div>
                  <div style={{ fontSize: '0.8rem', color: 'rgba(255,255,255,0.5)', fontWeight: 500, textTransform: 'uppercase', letterSpacing: '0.08em' }}>{label}</div>
                </div>
              ))}
            </motion.div>
          </div>
        </div>

        {/* ── CONTENT ── */}
        <div style={{ maxWidth: '1400px', margin: '0 auto', padding: '2.5rem 1.5rem', display: 'grid', gridTemplateColumns: '280px 1fr', gap: '2rem', alignItems: 'start' }}
          className="docs-layout">

          {/* ── SIDEBAR ── */}
          <motion.aside initial={{ opacity: 0, x: -20 }} animate={{ opacity: 1, x: 0 }} transition={{ duration: 0.5, delay: 0.2 }}
            style={{ background: 'var(--surface)', borderRadius: '16px', border: '1px solid var(--border)', padding: '1.5rem', position: 'sticky', top: '88px' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '1.5rem' }}>
              <FilterIcon />
              <h3 style={{ fontSize: '1rem', fontWeight: 700, color: 'var(--text)', margin: 0 }}>Filtres</h3>
              {hasActiveFilters && (
                <span style={{ marginLeft: 'auto', background: 'var(--primary)', color: 'white', borderRadius: '100px', padding: '2px 10px', fontSize: '0.75rem', fontWeight: 600 }}>
                  Actifs
                </span>
              )}
            </div>

            <div style={{ marginBottom: '1.25rem' }}>
              <label style={{ display: 'block', fontSize: '0.8rem', fontWeight: 600, color: 'var(--text-secondary)', textTransform: 'uppercase', letterSpacing: '0.06em', marginBottom: '0.5rem' }}>Rechercher</label>
              <input type="text" placeholder="Nom du document..." value={filters.search}
                onChange={e => setFilters({ ...filters, search: e.target.value })}
                style={{ width: '100%', padding: '0.6rem 0.9rem', border: '1.5px solid var(--border)', borderRadius: '10px', background: 'var(--bg)', color: 'var(--text)', fontSize: '0.9rem', outline: 'none', boxSizing: 'border-box', transition: 'border-color 0.2s' }}
                onFocus={e => (e.target.style.borderColor = 'var(--primary)')}
                onBlur={e => (e.target.style.borderColor = 'var(--border)')} />
            </div>

            <div style={{ marginBottom: '1.25rem' }}>
              <label style={{ display: 'block', fontSize: '0.8rem', fontWeight: 600, color: 'var(--text-secondary)', textTransform: 'uppercase', letterSpacing: '0.06em', marginBottom: '0.5rem' }}>Culture</label>
              <select value={filters.culture} onChange={e => setFilters({ ...filters, culture: e.target.value })}
                style={{ width: '100%', padding: '0.6rem 0.9rem', border: '1.5px solid var(--border)', borderRadius: '10px', background: 'var(--bg)', color: 'var(--text)', fontSize: '0.9rem', outline: 'none', cursor: 'pointer' }}>
                <option value="">Toutes les cultures</option>
                {CULTURES.map(c => <option key={c} value={c}>{c}</option>)}
              </select>
            </div>

            <div style={{ marginBottom: '1.5rem' }}>
              <label style={{ display: 'block', fontSize: '0.8rem', fontWeight: 600, color: 'var(--text-secondary)', textTransform: 'uppercase', letterSpacing: '0.06em', marginBottom: '0.5rem' }}>Région</label>
              <select value={filters.region} onChange={e => setFilters({ ...filters, region: e.target.value })}
                style={{ width: '100%', padding: '0.6rem 0.9rem', border: '1.5px solid var(--border)', borderRadius: '10px', background: 'var(--bg)', color: 'var(--text)', fontSize: '0.9rem', outline: 'none', cursor: 'pointer' }}>
                <option value="">Toutes les régions</option>
                {REGIONS.map(r => <option key={r} value={r}>{r}</option>)}
              </select>
            </div>

            {hasActiveFilters && (
              <button onClick={() => setFilters({ culture: '', region: '', search: '' })}
                style={{ width: '100%', padding: '0.6rem', background: 'transparent', border: '1.5px solid var(--border)', borderRadius: '10px', color: 'var(--text-secondary)', fontSize: '0.9rem', fontWeight: 600, cursor: 'pointer', transition: 'all 0.2s' }}
                onMouseEnter={e => { (e.currentTarget as HTMLButtonElement).style.borderColor = 'var(--primary)'; (e.currentTarget as HTMLButtonElement).style.color = 'var(--primary)'; }}
                onMouseLeave={e => { (e.currentTarget as HTMLButtonElement).style.borderColor = 'var(--border)'; (e.currentTarget as HTMLButtonElement).style.color = 'var(--text-secondary)'; }}>
                Réinitialiser les filtres
              </button>
            )}
          </motion.aside>

          {/* ── GRID ── */}
          <main>
            {/* results count */}
            {!loading && (
              <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ duration: 0.4 }}
                style={{ marginBottom: '1.5rem', color: 'var(--text-secondary)', fontSize: '0.9rem' }}>
                <strong style={{ color: 'var(--text)' }}>{documents.length}</strong> document{documents.length !== 1 ? 's' : ''} trouvé{documents.length !== 1 ? 's' : ''}
              </motion.div>
            )}

            {/* skeleton */}
            {loading && (
              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(300px, 1fr))', gap: '1.25rem' }}>
                {Array.from({ length: 6 }).map((_, i) => (
                  <div key={i} style={{ background: 'var(--surface)', borderRadius: '16px', border: '1px solid var(--border)', padding: '1.5rem', height: '260px' }}>
                    <div style={{ width: 48, height: 48, borderRadius: 10, background: 'var(--bg-secondary)', marginBottom: '1rem', animation: 'shimmer 1.5s infinite' }} />
                    <div style={{ height: 20, borderRadius: 6, background: 'var(--bg-secondary)', marginBottom: '0.75rem', width: '70%', animation: 'shimmer 1.5s infinite' }} />
                    <div style={{ height: 14, borderRadius: 6, background: 'var(--bg-secondary)', marginBottom: '0.5rem', animation: 'shimmer 1.5s infinite' }} />
                    <div style={{ height: 14, borderRadius: 6, background: 'var(--bg-secondary)', width: '80%', animation: 'shimmer 1.5s infinite' }} />
                  </div>
                ))}
              </div>
            )}

            {/* empty */}
            {!loading && documents.length === 0 && (
              <motion.div initial={{ opacity: 0, scale: 0.95 }} animate={{ opacity: 1, scale: 1 }} transition={{ duration: 0.4 }}
                style={{ textAlign: 'center', padding: '5rem 2rem', background: 'var(--surface)', borderRadius: '16px', border: '1px solid var(--border)' }}>
                <div style={{ width: 56, height: 56, borderRadius: '16px', background: 'var(--bg)', border: '1.5px solid var(--border)', display: 'flex', alignItems: 'center', justifyContent: 'center', margin: '0 auto 1rem' }}>
                  <svg width="26" height="26" viewBox="0 0 26 26" fill="none"><path d="M3 7a2 2 0 012-2h5l2 2h9a2 2 0 012 2v10a2 2 0 01-2 2H5a2 2 0 01-2-2V7z" stroke="var(--text-muted)" strokeWidth="1.5" strokeLinejoin="round"/></svg>
                </div>
                <h3 style={{ color: 'var(--text)', marginBottom: '0.5rem' }}>Aucun document trouvé</h3>
                <p style={{ color: 'var(--text-muted)' }}>Essayez de modifier vos filtres de recherche</p>
              </motion.div>
            )}

            {/* cards */}
            {!loading && documents.length > 0 && (
              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(300px, 1fr))', gap: '1.25rem' }}>
                <AnimatePresence>
                  {documents.map((doc, i) => {
                    const cultureColor = CULTURE_COLORS[doc.culture] || 'var(--primary)';
                    return (
                      <motion.div key={doc.id} custom={i} variants={cardVariants} initial="hidden" animate="visible" layout
                        style={{
                          background: 'var(--surface)', borderRadius: '16px',
                          border: doc.is_purchased ? `1.5px solid var(--primary)` : '1px solid var(--border)',
                          padding: '1.5rem', display: 'flex', flexDirection: 'column',
                          position: 'relative', overflow: 'hidden', cursor: 'default',
                          transition: 'box-shadow 0.25s, transform 0.25s',
                        }}
                        whileHover={{ y: -4, boxShadow: '0 12px 32px rgba(0,0,0,0.12)' }}>

                        {/* accent top border */}
                        <div style={{ position: 'absolute', top: 0, left: 0, right: 0, height: '3px', background: cultureColor, borderRadius: '16px 16px 0 0' }} />

                        {/* purchased badge */}
                        {doc.is_purchased && (
                          <motion.div initial={{ scale: 0 }} animate={{ scale: 1 }} transition={{ type: 'spring', stiffness: 300 }}
                            style={{ position: 'absolute', top: '1rem', right: '1rem', background: 'var(--primary)', color: 'white', borderRadius: '100px', padding: '4px 12px', fontSize: '0.75rem', fontWeight: 700, display: 'flex', alignItems: 'center', gap: '5px' }}>
                            <svg width="10" height="10" viewBox="0 0 10 10" fill="none"><path d="M2 5l2 2 4-4" stroke="white" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round"/></svg>
                            Acheté
                          </motion.div>
                        )}

                        <div style={{ marginBottom: '1rem', marginTop: '0.25rem' }}>
                          <DocumentIcon />
                        </div>

                        <h3 style={{ fontSize: '1.05rem', fontWeight: 700, color: 'var(--text)', marginBottom: '0.6rem', lineHeight: 1.4, paddingRight: doc.is_purchased ? '70px' : '0' }}>
                          {doc.titre}
                        </h3>
                        <p style={{ fontSize: '0.88rem', color: 'var(--text-muted)', lineHeight: 1.6, flexGrow: 1, marginBottom: '1rem' }}>
                          {doc.description}
                        </p>

                        <div style={{ display: 'flex', gap: '0.5rem', flexWrap: 'wrap', marginBottom: '1.25rem' }}>
                          <span style={{ display: 'inline-flex', alignItems: 'center', gap: '5px', padding: '4px 10px', borderRadius: '100px', background: `${cultureColor}18`, color: cultureColor, fontSize: '0.78rem', fontWeight: 600 }}>
                            <svg width="11" height="11" viewBox="0 0 11 11" fill="none"><path d="M5.5 9.5V5.5M5.5 5.5C5.5 5.5 3.5 3.5 2 4M5.5 5.5C5.5 5.5 7.5 3.5 9 4" stroke="currentColor" strokeWidth="1.2" strokeLinecap="round"/><circle cx="5.5" cy="2.5" r="1.5" stroke="currentColor" strokeWidth="1.2"/></svg>
                            {doc.culture}
                          </span>
                          <span style={{ display: 'inline-flex', alignItems: 'center', gap: '5px', padding: '4px 10px', borderRadius: '100px', background: 'var(--bg-secondary)', color: 'var(--text-secondary)', fontSize: '0.78rem', fontWeight: 500 }}>
                            <svg width="11" height="11" viewBox="0 0 11 11" fill="none"><path d="M5.5 10S2 7 2 4.5a3.5 3.5 0 017 0C9 7 5.5 10 5.5 10z" stroke="currentColor" strokeWidth="1.2"/><circle cx="5.5" cy="4.5" r="1.2" stroke="currentColor" strokeWidth="1.2"/></svg>
                            {doc.canton || doc.prefecture || doc.region}
                          </span>
                        </div>

                        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', paddingTop: '1rem', borderTop: '1px solid var(--border)' }}>
                          <div>
                            <div style={{ fontSize: '1.3rem', fontWeight: 800, color: 'var(--primary)' }}>
                              {parseInt(doc.prix).toLocaleString()}
                            </div>
                            <div style={{ fontSize: '0.7rem', color: 'var(--text-muted)', fontWeight: 500 }}>FCFA</div>
                          </div>
                          <motion.button whileHover={{ scale: 1.04 }} whileTap={{ scale: 0.96 }}
                            onClick={() => handlePurchaseClick(doc)}
                            style={{
                              display: 'inline-flex', alignItems: 'center', gap: '7px',
                              padding: '0.6rem 1.2rem',
                              background: doc.is_purchased ? 'linear-gradient(135deg, #1d4ed8, #3b82f6)' : 'linear-gradient(135deg, var(--primary-dark), var(--primary))',
                              color: 'white', border: 'none', borderRadius: '10px',
                              fontWeight: 700, fontSize: '0.88rem', cursor: 'pointer',
                              boxShadow: doc.is_purchased ? '0 4px 12px rgba(59,130,246,0.3)' : '0 4px 12px rgba(22,163,74,0.3)',
                            }}>
                            {doc.is_purchased ? <><DownloadIcon /> Télécharger</> : <><CartIcon /> Acheter</>}
                          </motion.button>
                        </div>
                      </motion.div>
                    );
                  })}
                </AnimatePresence>
              </div>
            )}
          </main>
        </div>
      </div>

      <style>{`
        @keyframes shimmer {
          0% { opacity: 1; }
          50% { opacity: 0.5; }
          100% { opacity: 1; }
        }
        @media (max-width: 900px) {
          .docs-layout { grid-template-columns: 1fr !important; }
        }
        .toast-container {
          position: fixed; top: 20px; right: 20px; z-index: 9999;
          display: flex; flex-direction: column; gap: 1rem; max-width: 400px;
        }
      `}</style>
    </>
  );
}
