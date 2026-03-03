import React, { useState, useEffect, useCallback } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { getAgronomists } from '../api/auth';

interface AgronomistUser {
  id: number;
  first_name: string;
  last_name: string;
  phone_number: string;
}

interface Canton {
  nom: string;
  prefecture: { nom: string; region: { nom: string; }; };
}

interface Agronomist {
  id: number;
  user: AgronomistUser;
  specialisations: string[];
  canton_rattachement: Canton;
  note_moyenne: string;
  nombre_avis: number;
  badge_valide: boolean;
}

const REGIONS = ['Maritime', 'Plateaux', 'Centrale', 'Kara', 'Savanes'];
const SPECIALISATIONS = ['Maraîchage', 'Céréaliculture', 'Arboriculture', 'Élevage', 'Irrigation', 'Agroforesterie'];

const SPEC_COLORS: Record<string, string> = {
  Maraîchage: '#10b981', Céréaliculture: '#f59e0b', Arboriculture: '#8b5cf6',
  Élevage: '#ef4444', Irrigation: '#3b82f6', Agroforesterie: '#06b6d4',
};

const AVATAR_GRADIENTS = [
  'linear-gradient(135deg, #16a34a, #4ade80)',
  'linear-gradient(135deg, #1d4ed8, #60a5fa)',
  'linear-gradient(135deg, #7c3aed, #c084fc)',
  'linear-gradient(135deg, #dc2626, #f87171)',
  'linear-gradient(135deg, #d97706, #fbbf24)',
  'linear-gradient(135deg, #0891b2, #67e8f9)',
];

function StarRating({ value }: { value: number }) {
  return (
    <div style={{ display: 'flex', gap: 2 }}>
      {Array.from({ length: 5 }).map((_, i) => {
        const filled = i + 1 <= value;
        const half = !filled && i + 0.5 <= value;
        return (
          <svg key={i} width="14" height="14" viewBox="0 0 14 14" fill="none">
            <path d="M7 1l1.5 3.5L12 5l-2.5 2.5.5 3.5L7 9.5 4 11l.5-3.5L2 5l3.5-.5L7 1z"
              fill={filled || half ? '#f59e0b' : 'none'}
              stroke={filled || half ? '#f59e0b' : '#d1d5db'}
              strokeWidth="1" fillOpacity={half ? 0.5 : 1} />
          </svg>
        );
      })}
    </div>
  );
}

const cardVariants = {
  hidden: { opacity: 0, y: 28 },
  visible: (i: number) => ({
    opacity: 1, y: 0,
    transition: { delay: i * 0.07, duration: 0.45, ease: [0.22, 1, 0.36, 1] },
  }),
};

const modalVariants = {
  hidden: { opacity: 0, scale: 0.92, y: 20 },
  visible: { opacity: 1, scale: 1, y: 0, transition: { duration: 0.35, ease: [0.22, 1, 0.36, 1] } },
  exit: { opacity: 0, scale: 0.94, y: 10, transition: { duration: 0.2 } },
};

export default function Agronomists() {
  const [agronomists, setAgronomists] = useState<Agronomist[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [filters, setFilters] = useState({ region: '', specialisation: '', search: '' });
  const [selected, setSelected] = useState<Agronomist | null>(null);

  const hasFilters = filters.region !== '' || filters.specialisation !== '' || filters.search !== '';

  const fetchAgronomists = useCallback(async () => {
    try {
      setLoading(true); setError('');
      const params: Record<string, string> = {};
      if (filters.region) params.region = filters.region;
      if (filters.specialisation) params.specialisation = filters.specialisation;
      if (filters.search) params.search = filters.search;
      const data = await getAgronomists(params);
      setAgronomists(data.results || []);
    } catch {
      setError('Impossible de charger les agronomes. Veuillez réessayer.');
      setAgronomists([]);
    } finally { setLoading(false); }
  }, [filters]);

  useEffect(() => { fetchAgronomists(); }, [fetchAgronomists]);

  const getAvatarGradient = (id: number) => AVATAR_GRADIENTS[id % AVATAR_GRADIENTS.length];

  const getInitials = (a: Agronomist) =>
    ((a.user.first_name?.[0] || '') + (a.user.last_name?.[0] || '')).toUpperCase() || 'AG';

  return (
    <div style={{ minHeight: '100vh', background: 'var(--bg)' }}>

      {/* ── HERO ── */}
      <div style={{
        background: 'linear-gradient(135deg, #1e1b4b 0%, #312e81 50%, #4338ca 100%)',
        padding: '5rem 2rem 4rem', position: 'relative', overflow: 'hidden',
      }}>
        <div style={{ position: 'absolute', inset: 0, backgroundImage: 'radial-gradient(circle at 25% 60%, rgba(139,92,246,0.12) 0%, transparent 50%), radial-gradient(circle at 75% 30%, rgba(99,102,241,0.1) 0%, transparent 40%)' }} />
        <div style={{ position: 'absolute', inset: 0, backgroundImage: 'linear-gradient(rgba(255,255,255,0.02) 1px, transparent 1px), linear-gradient(90deg, rgba(255,255,255,0.02) 1px, transparent 1px)', backgroundSize: '60px 60px' }} />
        <div style={{ maxWidth: '800px', margin: '0 auto', textAlign: 'center', position: 'relative' }}>
          <motion.div initial={{ opacity: 0, y: -10 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.5 }}
            style={{ display: 'inline-flex', alignItems: 'center', gap: 8, background: 'rgba(167,139,250,0.15)', border: '1px solid rgba(167,139,250,0.3)', borderRadius: '100px', padding: '6px 16px', marginBottom: '1.5rem' }}>
            <span style={{ width: 8, height: 8, borderRadius: '50%', background: '#a78bfa', display: 'inline-block' }} />
            <span style={{ color: '#c4b5fd', fontSize: '0.85rem', fontWeight: 600, letterSpacing: '0.05em' }}>EXPERTS CERTIFIÉS</span>
          </motion.div>
          <motion.h1 initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.6, delay: 0.1 }}
            style={{ fontSize: 'clamp(2rem, 5vw, 3.2rem)', fontWeight: 800, color: 'white', marginBottom: '1rem', lineHeight: 1.2 }}>
            Annuaire des Agronomes
            <span style={{ display: 'block', color: '#a78bfa' }}>Validés</span>
          </motion.h1>
          <motion.p initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.6, delay: 0.2 }}
            style={{ color: 'rgba(255,255,255,0.65)', fontSize: '1.1rem', maxWidth: '520px', margin: '0 auto 2.5rem' }}>
            Connectez-vous avec des experts agricoles qualifiés, localement présents dans chaque région du Togo.
          </motion.p>
          <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.6, delay: 0.3 }}
            style={{ display: 'flex', gap: '2rem', justifyContent: 'center', flexWrap: 'wrap' }}>
            {[['100%', 'Certifiés'], ['6', 'Spécialités'], ['5', 'Régions']].map(([num, label]) => (
              <div key={label} style={{ textAlign: 'center' }}>
                <div style={{ fontSize: '1.8rem', fontWeight: 800, color: '#a78bfa' }}>{num}</div>
                <div style={{ fontSize: '0.8rem', color: 'rgba(255,255,255,0.45)', fontWeight: 500, textTransform: 'uppercase', letterSpacing: '0.08em' }}>{label}</div>
              </div>
            ))}
          </motion.div>
        </div>
      </div>

      {/* ── LAYOUT ── */}
      <div style={{ maxWidth: '1400px', margin: '0 auto', padding: '2.5rem 1.5rem', display: 'grid', gridTemplateColumns: '280px 1fr', gap: '2rem', alignItems: 'start' }}
        className="agro-layout">

        {/* ── SIDEBAR ── */}
        <motion.aside initial={{ opacity: 0, x: -20 }} animate={{ opacity: 1, x: 0 }} transition={{ duration: 0.5, delay: 0.2 }}
          style={{ background: 'var(--surface)', borderRadius: '16px', border: '1px solid var(--border)', padding: '1.5rem', position: 'sticky', top: '88px' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: '1.5rem' }}>
            <svg width="18" height="18" viewBox="0 0 18 18" fill="none"><circle cx="8" cy="8" r="5" stroke="var(--text-secondary)" strokeWidth="1.5"/><path d="M12 12l3 3" stroke="var(--text-secondary)" strokeWidth="1.5" strokeLinecap="round"/></svg>
            <h3 style={{ fontSize: '1rem', fontWeight: 700, color: 'var(--text)', margin: 0 }}>Rechercher</h3>
            {hasFilters && (
              <span style={{ marginLeft: 'auto', background: '#6366f1', color: 'white', borderRadius: '100px', padding: '2px 10px', fontSize: '0.75rem', fontWeight: 600 }}>Actifs</span>
            )}
          </div>

          {[
            { key: 'search', label: 'Nom ou téléphone', type: 'input', placeholder: 'Rechercher...' },
          ].map(f => (
            <div key={f.key} style={{ marginBottom: '1.25rem' }}>
              <label style={{ display: 'block', fontSize: '0.8rem', fontWeight: 600, color: 'var(--text-secondary)', textTransform: 'uppercase', letterSpacing: '0.06em', marginBottom: '0.5rem' }}>{f.label}</label>
              <input type="text" placeholder={f.placeholder} value={filters.search}
                onChange={e => setFilters({ ...filters, search: e.target.value })}
                style={{ width: '100%', padding: '0.6rem 0.9rem', border: '1.5px solid var(--border)', borderRadius: '10px', background: 'var(--bg)', color: 'var(--text)', fontSize: '0.9rem', outline: 'none', boxSizing: 'border-box' }}
                onFocus={e => (e.target.style.borderColor = '#6366f1')}
                onBlur={e => (e.target.style.borderColor = 'var(--border)')} />
            </div>
          ))}

          <div style={{ marginBottom: '1.25rem' }}>
            <label style={{ display: 'block', fontSize: '0.8rem', fontWeight: 600, color: 'var(--text-secondary)', textTransform: 'uppercase', letterSpacing: '0.06em', marginBottom: '0.5rem' }}>Région</label>
            <select value={filters.region} onChange={e => setFilters({ ...filters, region: e.target.value })}
              style={{ width: '100%', padding: '0.6rem 0.9rem', border: '1.5px solid var(--border)', borderRadius: '10px', background: 'var(--bg)', color: 'var(--text)', fontSize: '0.9rem', outline: 'none', cursor: 'pointer' }}>
              <option value="">Toutes les régions</option>
              {REGIONS.map(r => <option key={r} value={r}>{r}</option>)}
            </select>
          </div>

          <div style={{ marginBottom: '1.5rem' }}>
            <label style={{ display: 'block', fontSize: '0.8rem', fontWeight: 600, color: 'var(--text-secondary)', textTransform: 'uppercase', letterSpacing: '0.06em', marginBottom: '0.5rem' }}>Spécialisation</label>
            <select value={filters.specialisation} onChange={e => setFilters({ ...filters, specialisation: e.target.value })}
              style={{ width: '100%', padding: '0.6rem 0.9rem', border: '1.5px solid var(--border)', borderRadius: '10px', background: 'var(--bg)', color: 'var(--text)', fontSize: '0.9rem', outline: 'none', cursor: 'pointer' }}>
              <option value="">Toutes</option>
              {SPECIALISATIONS.map(s => <option key={s} value={s}>{s}</option>)}
            </select>
          </div>

          {hasFilters && (
            <button onClick={() => setFilters({ region: '', specialisation: '', search: '' })}
              style={{ width: '100%', padding: '0.6rem', background: 'transparent', border: '1.5px solid var(--border)', borderRadius: '10px', color: 'var(--text-secondary)', fontSize: '0.9rem', fontWeight: 600, cursor: 'pointer', transition: 'all 0.2s' }}
              onMouseEnter={e => { (e.currentTarget as HTMLButtonElement).style.borderColor = '#6366f1'; (e.currentTarget as HTMLButtonElement).style.color = '#6366f1'; }}
              onMouseLeave={e => { (e.currentTarget as HTMLButtonElement).style.borderColor = 'var(--border)'; (e.currentTarget as HTMLButtonElement).style.color = 'var(--text-secondary)'; }}>
              Réinitialiser les filtres
            </button>
          )}
        </motion.aside>

        {/* ── MAIN ── */}
        <main>
          {/* count */}
          {!loading && !error && (
            <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ duration: 0.4 }}
              style={{ marginBottom: '1.5rem', color: 'var(--text-secondary)', fontSize: '0.9rem' }}>
              <strong style={{ color: 'var(--text)' }}>{agronomists.length}</strong> agronome{agronomists.length !== 1 ? 's' : ''} trouvé{agronomists.length !== 1 ? 's' : ''}
            </motion.div>
          )}

          {/* loading skeleton */}
          {loading && (
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(280px, 1fr))', gap: '1.25rem' }}>
              {Array.from({ length: 6 }).map((_, i) => (
                <div key={i} style={{ background: 'var(--surface)', borderRadius: '16px', border: '1px solid var(--border)', overflow: 'hidden' }}>
                  <div style={{ height: '100px', background: 'var(--bg-secondary)', animation: 'shimmer 1.5s infinite' }} />
                  <div style={{ padding: '1.25rem' }}>
                    <div style={{ width: 64, height: 64, borderRadius: '50%', background: 'var(--bg-secondary)', margin: '-2rem auto 0.75rem', border: '4px solid var(--surface)', animation: 'shimmer 1.5s infinite' }} />
                    <div style={{ height: 18, borderRadius: 6, background: 'var(--bg-secondary)', marginBottom: '0.5rem', width: '60%', margin: '0 auto 0.5rem', animation: 'shimmer 1.5s infinite' }} />
                    <div style={{ height: 12, borderRadius: 6, background: 'var(--bg-secondary)', width: '80%', margin: '0 auto', animation: 'shimmer 1.5s infinite' }} />
                  </div>
                </div>
              ))}
            </div>
          )}

          {/* error */}
          {!loading && error && (
            <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }}
              style={{ textAlign: 'center', padding: '4rem 2rem', background: 'var(--surface)', borderRadius: '16px', border: '1px solid var(--border)' }}>
              <div style={{ fontSize: '2.5rem', marginBottom: '1rem' }}>⚠️</div>
              <p style={{ color: 'var(--text-muted)', marginBottom: '1.5rem' }}>{error}</p>
              <button onClick={fetchAgronomists}
                style={{ padding: '0.6rem 1.5rem', background: '#6366f1', color: 'white', border: 'none', borderRadius: '10px', fontWeight: 600, cursor: 'pointer' }}>
                Réessayer
              </button>
            </motion.div>
          )}

          {/* empty */}
          {!loading && !error && agronomists.length === 0 && (
            <motion.div initial={{ opacity: 0, scale: 0.95 }} animate={{ opacity: 1, scale: 1 }} transition={{ duration: 0.4 }}
              style={{ textAlign: 'center', padding: '5rem 2rem', background: 'var(--surface)', borderRadius: '16px', border: '1px solid var(--border)' }}>
              <div style={{ fontSize: '3rem', marginBottom: '1rem' }}>👨‍🌾</div>
              <h3 style={{ color: 'var(--text)', marginBottom: '0.5rem' }}>Aucun agronome trouvé</h3>
              <p style={{ color: 'var(--text-muted)' }}>Essayez de modifier vos critères de recherche</p>
            </motion.div>
          )}

          {/* grid */}
          {!loading && !error && agronomists.length > 0 && (
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(280px, 1fr))', gap: '1.25rem' }}>
              {agronomists.map((agro, i) => {
                const gradient = getAvatarGradient(agro.id);
                const rating = parseFloat(agro.note_moyenne) || 0;
                return (
                  <motion.div key={agro.id} custom={i} variants={cardVariants} initial="hidden" animate="visible"
                    style={{
                      background: 'var(--surface)', borderRadius: '16px',
                      border: '1px solid var(--border)', overflow: 'hidden',
                      display: 'flex', flexDirection: 'column',
                    }}
                    whileHover={{ y: -4, boxShadow: '0 16px 40px rgba(0,0,0,0.12)' }}
                    transition={{ duration: 0.25 }}>

                    {/* header band */}
                    <div style={{ height: '72px', background: gradient, position: 'relative' }}>
                      {agro.badge_valide && (
                        <div style={{ position: 'absolute', top: '0.6rem', right: '0.6rem', background: 'rgba(255,255,255,0.2)', backdropFilter: 'blur(8px)', border: '1px solid rgba(255,255,255,0.3)', borderRadius: '100px', padding: '3px 10px', display: 'flex', alignItems: 'center', gap: 5 }}>
                          <svg width="10" height="10" viewBox="0 0 10 10" fill="none"><path d="M2 5l2 2 4-4" stroke="white" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round"/></svg>
                          <span style={{ color: 'white', fontSize: '0.7rem', fontWeight: 700 }}>Validé</span>
                        </div>
                      )}
                    </div>

                    {/* avatar */}
                    <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', padding: '0 1.25rem 1.25rem' }}>
                      <div style={{ width: 68, height: 68, borderRadius: '50%', background: gradient, display: 'flex', alignItems: 'center', justifyContent: 'center', border: '4px solid var(--surface)', marginTop: '-34px', boxShadow: '0 4px 16px rgba(0,0,0,0.15)', flexShrink: 0 }}>
                        <span style={{ color: 'white', fontSize: '1.4rem', fontWeight: 800 }}>{getInitials(agro)}</span>
                      </div>

                      <h3 style={{ fontSize: '1.1rem', fontWeight: 700, color: 'var(--text)', marginTop: '0.75rem', marginBottom: '0.25rem', textAlign: 'center' }}>
                        {agro.user.first_name} {agro.user.last_name}
                      </h3>

                      {/* rating */}
                      <div style={{ display: 'flex', alignItems: 'center', gap: 6, marginBottom: '0.75rem' }}>
                        <StarRating value={rating} />
                        <span style={{ fontSize: '0.8rem', color: 'var(--text-muted)', fontWeight: 500 }}>
                          {rating.toFixed(1)} ({agro.nombre_avis})
                        </span>
                      </div>

                      {/* location */}
                      <div style={{ display: 'flex', alignItems: 'center', gap: 5, marginBottom: '1rem', color: 'var(--text-muted)', fontSize: '0.85rem' }}>
                        <svg width="12" height="12" viewBox="0 0 12 12" fill="none"><path d="M6 1C4.34 1 3 2.34 3 4c0 2.25 3 7 3 7s3-4.75 3-7c0-1.66-1.34-3-3-3z" stroke="currentColor" strokeWidth="1.2"/><circle cx="6" cy="4" r="1" fill="currentColor"/></svg>
                        {agro.canton_rattachement.nom}, {agro.canton_rattachement.prefecture.nom}
                      </div>

                      {/* specs */}
                      <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.4rem', justifyContent: 'center', marginBottom: '1.25rem', width: '100%' }}>
                        {agro.specialisations.slice(0, 3).map((spec, idx) => {
                          const color = SPEC_COLORS[spec] || '#6366f1';
                          return (
                            <span key={idx} style={{ padding: '3px 10px', borderRadius: '100px', background: `${color}18`, color, fontSize: '0.75rem', fontWeight: 600 }}>
                              {spec}
                            </span>
                          );
                        })}
                      </div>

                      {/* cta */}
                      <motion.button whileHover={{ scale: 1.03 }} whileTap={{ scale: 0.97 }}
                        onClick={() => setSelected(agro)}
                        style={{ width: '100%', padding: '0.65rem', background: gradient, color: 'white', border: 'none', borderRadius: '10px', fontWeight: 700, fontSize: '0.9rem', cursor: 'pointer', display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 7 }}>
                        <svg width="14" height="14" viewBox="0 0 14 14" fill="none"><path d="M2 2h10v8a1 1 0 01-1 1H3a1 1 0 01-1-1V2z" stroke="white" strokeWidth="1.2"/><path d="M5 7h4M5 5h4M2 2l5 3 5-3" stroke="white" strokeWidth="1.2" strokeLinecap="round"/></svg>
                        Voir le profil
                      </motion.button>
                    </div>
                  </motion.div>
                );
              })}
            </div>
          )}
        </main>
      </div>

      {/* ── MODAL ── */}
      <AnimatePresence>
        {selected && (
          <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}
            onClick={() => setSelected(null)}
            style={{ position: 'fixed', inset: 0, background: 'rgba(0,0,0,0.6)', backdropFilter: 'blur(6px)', display: 'flex', alignItems: 'center', justifyContent: 'center', zIndex: 1000, padding: '1rem' }}>
            <motion.div variants={modalVariants} initial="hidden" animate="visible" exit="exit"
              onClick={e => e.stopPropagation()}
              style={{ background: 'var(--surface)', borderRadius: '20px', maxWidth: '520px', width: '100%', maxHeight: '90vh', overflowY: 'auto', border: '1px solid var(--border)', boxShadow: '0 32px 80px rgba(0,0,0,0.3)', position: 'relative' }}>

              {/* modal header */}
              <div style={{ background: getAvatarGradient(selected.id), padding: '2rem 2rem 1rem', borderRadius: '20px 20px 0 0', textAlign: 'center', position: 'relative' }}>
                <button onClick={() => setSelected(null)}
                  style={{ position: 'absolute', top: '1rem', right: '1rem', background: 'rgba(255,255,255,0.2)', border: 'none', width: 36, height: 36, borderRadius: '50%', cursor: 'pointer', color: 'white', fontSize: '1.2rem', display: 'flex', alignItems: 'center', justifyContent: 'center', transition: 'background 0.2s' }}
                  onMouseEnter={e => (e.currentTarget.style.background = 'rgba(255,255,255,0.35)')}
                  onMouseLeave={e => (e.currentTarget.style.background = 'rgba(255,255,255,0.2)')}>
                  ✕
                </button>
                <div style={{ width: 80, height: 80, borderRadius: '50%', background: 'rgba(255,255,255,0.25)', backdropFilter: 'blur(10px)', border: '3px solid rgba(255,255,255,0.4)', display: 'flex', alignItems: 'center', justifyContent: 'center', margin: '0 auto 1rem' }}>
                  <span style={{ color: 'white', fontSize: '2rem', fontWeight: 800 }}>{getInitials(selected)}</span>
                </div>
                <h2 style={{ color: 'white', fontSize: '1.4rem', fontWeight: 800, margin: '0 0 0.25rem' }}>
                  {selected.user.first_name} {selected.user.last_name}
                </h2>
                {selected.badge_valide && (
                  <div style={{ display: 'inline-flex', alignItems: 'center', gap: 5, background: 'rgba(255,255,255,0.2)', border: '1px solid rgba(255,255,255,0.3)', borderRadius: '100px', padding: '4px 12px' }}>
                    <svg width="10" height="10" viewBox="0 0 10 10" fill="none"><path d="M2 5l2 2 4-4" stroke="white" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round"/></svg>
                    <span style={{ color: 'white', fontSize: '0.8rem', fontWeight: 700 }}>Agronome Validé</span>
                  </div>
                )}
              </div>

              {/* modal body */}
              <div style={{ padding: '1.75rem 2rem' }}>
                {/* rating */}
                <div style={{ background: 'var(--bg)', borderRadius: '12px', padding: '1rem 1.25rem', marginBottom: '1.25rem', display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                  <div>
                    <div style={{ fontSize: '0.75rem', fontWeight: 600, color: 'var(--text-secondary)', textTransform: 'uppercase', letterSpacing: '0.06em', marginBottom: '0.4rem' }}>Évaluation</div>
                    <StarRating value={parseFloat(selected.note_moyenne) || 0} />
                  </div>
                  <div style={{ textAlign: 'right' }}>
                    <div style={{ fontSize: '1.6rem', fontWeight: 800, color: 'var(--text)' }}>{(parseFloat(selected.note_moyenne) || 0).toFixed(1)}</div>
                    <div style={{ fontSize: '0.78rem', color: 'var(--text-muted)' }}>{selected.nombre_avis} avis</div>
                  </div>
                </div>

                {/* info grid */}
                {[
                  {
                    icon: <svg width="16" height="16" viewBox="0 0 16 16" fill="none"><path d="M2 2.5A1.5 1.5 0 013.5 1h.5a2 2 0 012 2v1a2 2 0 01-2 2H3L2 8s1 5 6 6c5-1 6-6 6-6l-1-2H11a2 2 0 01-2-2V3a2 2 0 012-2h.5A1.5 1.5 0 0114 2.5" stroke="var(--primary)" strokeWidth="1.2"/></svg>,
                    label: 'Téléphone',
                    value: selected.user.phone_number,
                  },
                  {
                    icon: <svg width="16" height="16" viewBox="0 0 16 16" fill="none"><path d="M8 1C5.24 1 3 3.24 3 6c0 3.75 5 9 5 9s5-5.25 5-9c0-2.76-2.24-5-5-5z" stroke="#6366f1" strokeWidth="1.2"/><circle cx="8" cy="6" r="2" fill="#6366f1"/></svg>,
                    label: 'Localisation',
                    value: `${selected.canton_rattachement.nom} · ${selected.canton_rattachement.prefecture.nom} · Région ${selected.canton_rattachement.prefecture.region.nom}`,
                  },
                ].map(({ icon, label, value }) => (
                  <div key={label} style={{ display: 'flex', gap: '1rem', alignItems: 'flex-start', marginBottom: '1.25rem', paddingBottom: '1.25rem', borderBottom: '1px solid var(--border)' }}>
                    <div style={{ width: 36, height: 36, borderRadius: '10px', background: 'var(--bg)', display: 'flex', alignItems: 'center', justifyContent: 'center', flexShrink: 0, border: '1px solid var(--border)' }}>
                      {icon}
                    </div>
                    <div>
                      <div style={{ fontSize: '0.75rem', fontWeight: 600, color: 'var(--text-secondary)', textTransform: 'uppercase', letterSpacing: '0.06em', marginBottom: '0.3rem' }}>{label}</div>
                      <div style={{ fontSize: '0.95rem', fontWeight: 600, color: 'var(--text)' }}>{value}</div>
                    </div>
                  </div>
                ))}

                {/* specialisations */}
                <div>
                  <div style={{ fontSize: '0.75rem', fontWeight: 600, color: 'var(--text-secondary)', textTransform: 'uppercase', letterSpacing: '0.06em', marginBottom: '0.75rem' }}>Spécialisations</div>
                  <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.5rem' }}>
                    {selected.specialisations.map((spec, i) => {
                      const color = SPEC_COLORS[spec] || '#6366f1';
                      return (
                        <span key={i} style={{ padding: '6px 14px', borderRadius: '100px', background: `${color}18`, color, fontSize: '0.85rem', fontWeight: 600, border: `1px solid ${color}30` }}>
                          {spec}
                        </span>
                      );
                    })}
                  </div>
                </div>
              </div>

              {/* modal footer */}
              <div style={{ padding: '1.25rem 2rem', borderTop: '1px solid var(--border)', display: 'flex', gap: '0.75rem' }}>
                <motion.a whileHover={{ scale: 1.02 }} whileTap={{ scale: 0.97 }}
                  href={`tel:${selected.user.phone_number}`}
                  style={{ flex: 1, padding: '0.75rem', background: getAvatarGradient(selected.id), color: 'white', border: 'none', borderRadius: '12px', fontWeight: 700, fontSize: '0.95rem', cursor: 'pointer', textAlign: 'center', textDecoration: 'none', display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 8 }}>
                  <svg width="16" height="16" viewBox="0 0 16 16" fill="none"><path d="M2 2.5A1.5 1.5 0 013.5 1h.5a2 2 0 012 2v1a2 2 0 01-2 2H3L2 8s1 5 6 6c5-1 6-6 6-6l-1-2H11a2 2 0 01-2-2V3a2 2 0 012-2h.5A1.5 1.5 0 0114 2.5" stroke="white" strokeWidth="1.3"/></svg>
                  Appeler
                </motion.a>
                <motion.button whileHover={{ scale: 1.02 }} whileTap={{ scale: 0.97 }}
                  onClick={() => setSelected(null)}
                  style={{ padding: '0.75rem 1.25rem', background: 'var(--bg)', color: 'var(--text-secondary)', border: '1.5px solid var(--border)', borderRadius: '12px', fontWeight: 600, fontSize: '0.9rem', cursor: 'pointer' }}>
                  Fermer
                </motion.button>
              </div>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>

      <style>{`
        @keyframes shimmer {
          0% { opacity: 1; } 50% { opacity: 0.5; } 100% { opacity: 1; }
        }
        @media (max-width: 900px) {
          .agro-layout { grid-template-columns: 1fr !important; }
        }
      `}</style>
    </div>
  );
}
