import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import { fetchCategories, fetchCours, Categorie, Cours } from '../api/elearning';

const IconVideo = () => <svg width="20" height="20" viewBox="0 0 20 20" fill="none"><path d="M2 4a2 2 0 012-2h8a2 2 0 012 2v12a2 2 0 01-2 2H4a2 2 0 01-2-2V4z" stroke="currentColor" strokeWidth="1.5"/><path d="M14 7l4-2v10l-4-2" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round"/></svg>;
const IconLive = () => <svg width="20" height="20" viewBox="0 0 20 20" fill="none"><circle cx="10" cy="10" r="3" fill="currentColor"/><path d="M6 10a4 4 0 018 0M4 10a6 6 0 0112 0M2 10a8 8 0 0116 0" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round"/></svg>;
const IconClock = () => <svg width="16" height="16" viewBox="0 0 16 16" fill="none"><circle cx="8" cy="8" r="7" stroke="currentColor" strokeWidth="1.3"/><path d="M8 4v4l3 2" stroke="currentColor" strokeWidth="1.3" strokeLinecap="round"/></svg>;
const IconUsers = () => <svg width="16" height="16" viewBox="0 0 16 16" fill="none"><circle cx="6" cy="5" r="3" stroke="currentColor" strokeWidth="1.3"/><path d="M1 14c0-2.8 2.2-5 5-5s5 2.2 5 5" stroke="currentColor" strokeWidth="1.3" strokeLinecap="round"/><path d="M11 5a3 3 0 100-6M14 14c0-1.7-1-3.2-2.5-4" stroke="currentColor" strokeWidth="1.3" strokeLinecap="round"/></svg>;
const IconFilter = () => <svg width="18" height="18" viewBox="0 0 18 18" fill="none"><path d="M2 4h14M5 9h8M8 14h2" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round"/></svg>;

export default function Elearning() {
  const navigate = useNavigate();
  const [categories, setCategories] = useState<Categorie[]>([]);
  const [cours, setCours] = useState<Cours[]>([]);
  const [loading, setLoading] = useState(true);
  const [filters, setFilters] = useState({
    categorie: '',
    type: '',
    niveau: '',
    gratuit: false,
    search: '',
  });

  useEffect(() => {
    loadData();
  }, [filters]);

  const loadData = async () => {
    try {
      setLoading(true);
      
      // Construire les paramètres en excluant les valeurs vides
      const params: any = {};
      if (filters.categorie) params.categorie = filters.categorie;
      if (filters.type) params.type = filters.type;
      if (filters.niveau) params.niveau = filters.niveau;
      if (filters.gratuit) params.gratuit = 'true';
      if (filters.search) params.search = filters.search;
      
      const [categoriesData, coursData] = await Promise.all([
        fetchCategories(),
        fetchCours(params),
      ]);
      setCategories(categoriesData);
      setCours(coursData.results || coursData);
    } catch (error) {
      console.error('Erreur chargement:', error);
    } finally {
      setLoading(false);
    }
  };

  const hasActiveFilters = filters.categorie || filters.type || filters.niveau || filters.gratuit || filters.search;

  return (
    <div style={{ minHeight: '100vh', background: 'var(--bg)' }}>
      
      {/* Hero */}
      <div style={{
        background: 'linear-gradient(135deg, #0e7490 0%, #0891b2 50%, #06b6d4 100%)',
        padding: '5rem 2rem 4rem',
        position: 'relative',
        overflow: 'hidden',
      }}>
        <div style={{ position: 'absolute', inset: 0, backgroundImage: 'radial-gradient(circle at 20% 50%, rgba(255,255,255,0.1) 0%, transparent 50%)' }} />
        <div style={{ maxWidth: 1200, margin: '0 auto', position: 'relative' }}>
          <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }}>
            <div style={{ display: 'inline-flex', alignItems: 'center', gap: '8px', background: 'rgba(255,255,255,0.15)', border: '1px solid rgba(255,255,255,0.3)', borderRadius: '100px', padding: '6px 16px', marginBottom: '1.5rem' }}>
              <span style={{ width: 8, height: 8, borderRadius: '50%', background: '#4ade80', display: 'inline-block' }} />
              <span style={{ color: 'white', fontSize: '0.85rem', fontWeight: 600 }}>FORMATION AGRICOLE</span>
            </div>
            <h1 style={{ fontSize: 'clamp(2rem, 5vw, 3rem)', fontWeight: 800, color: 'white', margin: '0 0 1rem', lineHeight: 1.2 }}>
              Apprenez l'Agriculture Moderne
            </h1>
            <p style={{ color: 'rgba(255,255,255,0.8)', fontSize: '1.1rem', maxWidth: 600, margin: 0 }}>
              Cours vidéo, livestreams et formations pratiques pour développer vos compétences agricoles
            </p>
          </motion.div>
        </div>
      </div>

      <div style={{ maxWidth: 1400, margin: '0 auto', padding: '2.5rem 1.5rem', display: 'grid', gridTemplateColumns: '280px 1fr', gap: '2rem', alignItems: 'start' }}>
        
        {/* Sidebar Filtres */}
        <motion.aside initial={{ opacity: 0, x: -20 }} animate={{ opacity: 1, x: 0 }}
          style={{ background: 'var(--surface)', border: '1px solid var(--border)', borderRadius: '16px', padding: '1.5rem', position: 'sticky', top: '88px' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '1.5rem' }}>
            <IconFilter />
            <h3 style={{ fontSize: '1rem', fontWeight: 700, color: 'var(--text)', margin: 0 }}>Filtres</h3>
            {hasActiveFilters && (
              <span style={{ marginLeft: 'auto', background: 'var(--primary)', color: 'white', borderRadius: '100px', padding: '2px 10px', fontSize: '0.75rem', fontWeight: 600 }}>
                Actifs
              </span>
            )}
          </div>

          <div style={{ marginBottom: '1.25rem' }}>
            <label style={{ display: 'block', fontSize: '0.8rem', fontWeight: 600, color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.06em', marginBottom: '0.5rem' }}>
              Rechercher
            </label>
            <input
              type="text"
              placeholder="Titre du cours..."
              value={filters.search}
              onChange={e => setFilters({ ...filters, search: e.target.value })}
              style={{ width: '100%', padding: '0.6rem 0.9rem', border: '1.5px solid var(--border)', borderRadius: '10px', background: 'var(--bg)', color: 'var(--text)', fontSize: '0.9rem', outline: 'none', boxSizing: 'border-box' }}
            />
          </div>

          <div style={{ marginBottom: '1.25rem' }}>
            <label style={{ display: 'block', fontSize: '0.8rem', fontWeight: 600, color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.06em', marginBottom: '0.5rem' }}>
              Catégorie
            </label>
            <select
              value={filters.categorie}
              onChange={e => setFilters({ ...filters, categorie: e.target.value })}
              style={{ width: '100%', padding: '0.6rem 0.9rem', border: '1.5px solid var(--border)', borderRadius: '10px', background: 'var(--bg)', color: 'var(--text)', fontSize: '0.9rem', outline: 'none', cursor: 'pointer' }}>
              <option value="">Toutes</option>
              {categories.map(cat => <option key={cat.id} value={cat.slug}>{cat.icone} {cat.nom}</option>)}
            </select>
          </div>

          <div style={{ marginBottom: '1.25rem' }}>
            <label style={{ display: 'block', fontSize: '0.8rem', fontWeight: 600, color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.06em', marginBottom: '0.5rem' }}>
              Type
            </label>
            <select
              value={filters.type}
              onChange={e => setFilters({ ...filters, type: e.target.value })}
              style={{ width: '100%', padding: '0.6rem 0.9rem', border: '1.5px solid var(--border)', borderRadius: '10px', background: 'var(--bg)', color: 'var(--text)', fontSize: '0.9rem', outline: 'none', cursor: 'pointer' }}>
              <option value="">Tous</option>
              <option value="VIDEO">Vidéo</option>
              <option value="LIVESTREAM">Livestream</option>
              <option value="PLAYLIST">Playlist</option>
            </select>
          </div>

          <div style={{ marginBottom: '1.25rem' }}>
            <label style={{ display: 'block', fontSize: '0.8rem', fontWeight: 600, color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.06em', marginBottom: '0.5rem' }}>
              Niveau
            </label>
            <select
              value={filters.niveau}
              onChange={e => setFilters({ ...filters, niveau: e.target.value })}
              style={{ width: '100%', padding: '0.6rem 0.9rem', border: '1.5px solid var(--border)', borderRadius: '10px', background: 'var(--bg)', color: 'var(--text)', fontSize: '0.9rem', outline: 'none', cursor: 'pointer' }}>
              <option value="">Tous</option>
              <option value="DEBUTANT">Débutant</option>
              <option value="INTERMEDIAIRE">Intermédiaire</option>
              <option value="AVANCE">Avancé</option>
            </select>
          </div>

          <div style={{ marginBottom: '1.5rem' }}>
            <label style={{ display: 'flex', alignItems: 'center', gap: '8px', cursor: 'pointer' }}>
              <input
                type="checkbox"
                checked={filters.gratuit}
                onChange={e => setFilters({ ...filters, gratuit: e.target.checked })}
                style={{ width: 18, height: 18, cursor: 'pointer' }}
              />
              <span style={{ fontSize: '0.9rem', color: 'var(--text)' }}>Cours gratuits uniquement</span>
            </label>
          </div>

          {hasActiveFilters && (
            <button
              onClick={() => setFilters({ categorie: '', type: '', niveau: '', gratuit: false, search: '' })}
              style={{ width: '100%', padding: '0.6rem', background: 'transparent', border: '1.5px solid var(--border)', borderRadius: '10px', color: 'var(--text-muted)', fontSize: '0.9rem', fontWeight: 600, cursor: 'pointer' }}>
              Réinitialiser
            </button>
          )}
        </motion.aside>

        {/* Liste des cours */}
        <main>
          {!loading && (
            <div style={{ marginBottom: '1.5rem', color: 'var(--text-muted)', fontSize: '0.9rem' }}>
              <strong style={{ color: 'var(--text)' }}>{cours.length}</strong> cours trouvé{cours.length !== 1 ? 's' : ''}
            </div>
          )}

          {loading && (
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(320px, 1fr))', gap: '1.25rem' }}>
              {Array.from({ length: 6 }).map((_, i) => (
                <div key={i} style={{ background: 'var(--surface)', border: '1px solid var(--border)', borderRadius: '16px', padding: '1rem', height: '320px' }}>
                  <div style={{ width: '100%', height: '180px', borderRadius: '12px', background: 'var(--bg)', marginBottom: '1rem', animation: 'shimmer 1.5s infinite' }} />
                  <div style={{ width: '70%', height: '20px', borderRadius: '6px', background: 'var(--bg)', marginBottom: '0.75rem', animation: 'shimmer 1.5s infinite' }} />
                  <div style={{ width: '100%', height: '14px', borderRadius: '6px', background: 'var(--bg)', animation: 'shimmer 1.5s infinite' }} />
                </div>
              ))}
            </div>
          )}

          {!loading && cours.length === 0 && (
            <div style={{ textAlign: 'center', padding: '4rem 2rem', background: 'var(--surface)', border: '1px solid var(--border)', borderRadius: '16px' }}>
              <div style={{ fontSize: '3rem', marginBottom: '1rem' }}>📚</div>
              <h3 style={{ color: 'var(--text)', marginBottom: '0.5rem' }}>Aucun cours trouvé</h3>
              <p style={{ color: 'var(--text-muted)' }}>Essayez de modifier vos filtres</p>
            </div>
          )}

          {!loading && cours.length > 0 && (
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(320px, 1fr))', gap: '1.25rem' }}>
              {cours.map((c, i) => (
                <motion.div
                  key={c.id}
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: i * 0.05 }}
                  whileHover={{ y: -4 }}
                  onClick={() => navigate(`/elearning/${c.slug}`)}
                  style={{ background: 'var(--surface)', border: '1px solid var(--border)', borderRadius: '16px', overflow: 'hidden', cursor: 'pointer', transition: 'box-shadow 0.2s' }}
                  onMouseEnter={e => e.currentTarget.style.boxShadow = '0 12px 32px rgba(0,0,0,0.12)'}
                  onMouseLeave={e => e.currentTarget.style.boxShadow = 'none'}>
                  
                  {/* Thumbnail */}
                  <div style={{ position: 'relative', width: '100%', height: '180px', background: 'var(--bg)' }}>
                    {c.thumbnail ? (
                      <img src={c.thumbnail} alt={c.titre} style={{ width: '100%', height: '100%', objectFit: 'cover' }} />
                    ) : (
                      <div style={{ width: '100%', height: '100%', display: 'flex', alignItems: 'center', justifyContent: 'center', background: 'linear-gradient(135deg, #0e7490, #0891b2)', color: 'white', fontSize: '3rem' }}>
                        {c.type_cours === 'LIVESTREAM' ? '📡' : '🎓'}
                      </div>
                    )}
                    
                    {/* Badge type */}
                    <div style={{ position: 'absolute', top: '0.75rem', left: '0.75rem', display: 'flex', gap: '0.5rem' }}>
                      {c.type_cours === 'LIVESTREAM' && (
                        <span style={{ display: 'inline-flex', alignItems: 'center', gap: '5px', padding: '4px 10px', borderRadius: '100px', background: c.est_livestream_actif ? '#dc2626' : '#f59e0b', color: 'white', fontSize: '0.75rem', fontWeight: 700 }}>
                          <IconLive /> {c.est_livestream_actif ? 'EN DIRECT' : 'Livestream'}
                        </span>
                      )}
                      {c.type_cours === 'VIDEO' && (
                        <span style={{ display: 'inline-flex', alignItems: 'center', gap: '5px', padding: '4px 10px', borderRadius: '100px', background: 'rgba(0,0,0,0.7)', color: 'white', fontSize: '0.75rem', fontWeight: 600 }}>
                          <IconVideo /> Vidéo
                        </span>
                      )}
                      {c.est_gratuit && (
                        <span style={{ padding: '4px 10px', borderRadius: '100px', background: '#16a34a', color: 'white', fontSize: '0.75rem', fontWeight: 700 }}>
                          GRATUIT
                        </span>
                      )}
                    </div>
                  </div>

                  {/* Contenu */}
                  <div style={{ padding: '1.25rem' }}>
                    <h3 style={{ fontSize: '1.05rem', fontWeight: 700, color: 'var(--text)', margin: '0 0 0.5rem', lineHeight: 1.3 }}>
                      {c.titre}
                    </h3>
                    <p style={{ fontSize: '0.85rem', color: 'var(--text-muted)', lineHeight: 1.5, marginBottom: '1rem', display: '-webkit-box', WebkitLineClamp: 2, WebkitBoxOrient: 'vertical', overflow: 'hidden' }}>
                      {c.description}
                    </p>

                    <div style={{ display: 'flex', gap: '1rem', fontSize: '0.8rem', color: 'var(--text-muted)', marginBottom: '1rem' }}>
                      <span style={{ display: 'flex', alignItems: 'center', gap: '4px' }}>
                        <IconClock /> {c.duree_minutes}min
                      </span>
                      <span style={{ display: 'flex', alignItems: 'center', gap: '4px' }}>
                        <IconUsers /> {c.nombre_inscrits}
                      </span>
                      <span style={{ padding: '2px 8px', borderRadius: '100px', background: 'var(--bg)', fontSize: '0.75rem', fontWeight: 600 }}>
                        {c.niveau}
                      </span>
                    </div>

                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', paddingTop: '1rem', borderTop: '1px solid var(--border)' }}>
                      <div style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>
                        Par {c.instructeur_nom}
                      </div>
                      {c.est_inscrit && (
                        <span style={{ padding: '4px 10px', borderRadius: '100px', background: '#dcfce7', color: '#16a34a', fontSize: '0.75rem', fontWeight: 700 }}>
                          Inscrit
                        </span>
                      )}
                    </div>
                  </div>
                </motion.div>
              ))}
            </div>
          )}
        </main>
      </div>

      <style>{`
        @keyframes shimmer {
          0% { opacity: 1; }
          50% { opacity: 0.5; }
          100% { opacity: 1; }
        }
        @media (max-width: 900px) {
          div[style*="grid-template-columns: 280px 1fr"] {
            grid-template-columns: 1fr !important;
          }
        }
      `}</style>
    </div>
  );
}
