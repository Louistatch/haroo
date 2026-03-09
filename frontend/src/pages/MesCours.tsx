import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import { fetchMesInscriptions, fetchCoursEnCours, fetchCoursCompletes, Inscription } from '../api/elearning';

const IconClock = () => <svg width="16" height="16" viewBox="0 0 16 16" fill="none"><circle cx="8" cy="8" r="7" stroke="currentColor" strokeWidth="1.3"/><path d="M8 4v4l3 2" stroke="currentColor" strokeWidth="1.3" strokeLinecap="round"/></svg>;
const IconCheck = () => <svg width="18" height="18" viewBox="0 0 18 18" fill="none"><path d="M15 5L7 13l-4-4" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/></svg>;
const IconPlay = () => <svg width="18" height="18" viewBox="0 0 18 18" fill="none"><path d="M6 4v10l8-5z" fill="currentColor"/></svg>;

export default function MesCours() {
  const navigate = useNavigate();
  const [activeTab, setActiveTab] = useState<'tous' | 'en_cours' | 'completes'>('tous');
  const [inscriptions, setInscriptions] = useState<Inscription[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadInscriptions();
  }, [activeTab]);

  const loadInscriptions = async () => {
    try {
      setLoading(true);
      let data: Inscription[];
      
      if (activeTab === 'en_cours') {
        data = await fetchCoursEnCours();
      } else if (activeTab === 'completes') {
        data = await fetchCoursCompletes();
      } else {
        data = await fetchMesInscriptions();
      }
      
      setInscriptions(data);
    } catch (error) {
      console.error('Erreur chargement:', error);
      setInscriptions([]);
    } finally {
      setLoading(false);
    }
  };

  const stats = {
    total: inscriptions.length,
    enCours: inscriptions.filter(i => !i.est_complete).length,
    completes: inscriptions.filter(i => i.est_complete).length,
    progressionMoyenne: inscriptions.length > 0
      ? Math.round(inscriptions.reduce((sum, i) => sum + i.progression, 0) / inscriptions.length)
      : 0,
  };

  return (
    <div style={{ minHeight: '100vh', background: 'var(--bg)', paddingTop: '5rem' }}>
      <div style={{ maxWidth: 1200, margin: '0 auto', padding: '2rem 1.5rem' }}>
        
        {/* Header */}
        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }}>
          <div style={{ marginBottom: '0.5rem' }}>
            <a href="/elearning" style={{ color: 'var(--text-muted)', fontSize: '0.85rem', textDecoration: 'none' }}>
              ← Retour aux cours
            </a>
          </div>
          <h1 style={{ fontSize: '2rem', fontWeight: 800, color: 'var(--text)', margin: '0 0 0.5rem', letterSpacing: '-0.02em' }}>
            Mes Cours
          </h1>
          <p style={{ color: 'var(--text-muted)', fontSize: '0.95rem', margin: 0 }}>
            Suivez votre progression et continuez votre apprentissage
          </p>
        </motion.div>

        {/* Statistiques */}
        <motion.div initial={{ opacity: 0, y: 16 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.1 }}
          style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: '1rem', margin: '2rem 0' }}>
          <div style={{ background: 'var(--surface)', border: '1px solid var(--border)', borderRadius: '14px', padding: '1.2rem' }}>
            <div style={{ fontSize: '0.75rem', fontWeight: 600, color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.05em', marginBottom: '0.5rem' }}>
              Total cours
            </div>
            <div style={{ fontSize: '2rem', fontWeight: 800, color: 'var(--text)' }}>{stats.total}</div>
          </div>
          <div style={{ background: 'var(--surface)', border: '1px solid var(--border)', borderRadius: '14px', padding: '1.2rem' }}>
            <div style={{ fontSize: '0.75rem', fontWeight: 600, color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.05em', marginBottom: '0.5rem' }}>
              En cours
            </div>
            <div style={{ fontSize: '2rem', fontWeight: 800, color: '#f59e0b' }}>{stats.enCours}</div>
          </div>
          <div style={{ background: 'var(--surface)', border: '1px solid var(--border)', borderRadius: '14px', padding: '1.2rem' }}>
            <div style={{ fontSize: '0.75rem', fontWeight: 600, color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.05em', marginBottom: '0.5rem' }}>
              Complétés
            </div>
            <div style={{ fontSize: '2rem', fontWeight: 800, color: '#16a34a' }}>{stats.completes}</div>
          </div>
          <div style={{ background: 'var(--surface)', border: '1px solid var(--border)', borderRadius: '14px', padding: '1.2rem' }}>
            <div style={{ fontSize: '0.75rem', fontWeight: 600, color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.05em', marginBottom: '0.5rem' }}>
              Progression moyenne
            </div>
            <div style={{ fontSize: '2rem', fontWeight: 800, color: 'var(--primary)' }}>{stats.progressionMoyenne}%</div>
          </div>
        </motion.div>

        {/* Tabs */}
        <motion.div initial={{ opacity: 0, y: 16 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.2 }}
          style={{ display: 'flex', gap: '0.5rem', marginBottom: '2rem', borderBottom: '2px solid var(--border)' }}>
          {[
            { key: 'tous', label: 'Tous les cours', count: stats.total },
            { key: 'en_cours', label: 'En cours', count: stats.enCours },
            { key: 'completes', label: 'Complétés', count: stats.completes },
          ].map(tab => (
            <button
              key={tab.key}
              onClick={() => setActiveTab(tab.key as any)}
              style={{
                padding: '0.75rem 1.5rem',
                background: 'transparent',
                border: 'none',
                borderBottom: activeTab === tab.key ? '3px solid var(--primary)' : '3px solid transparent',
                color: activeTab === tab.key ? 'var(--primary)' : 'var(--text-muted)',
                fontSize: '0.95rem',
                fontWeight: 700,
                cursor: 'pointer',
                transition: 'all 0.2s',
                marginBottom: '-2px',
              }}>
              {tab.label} ({tab.count})
            </button>
          ))}
        </motion.div>

        {/* Liste des cours */}
        {loading && (
          <div style={{ display: 'grid', gap: '1rem' }}>
            {Array.from({ length: 3 }).map((_, i) => (
              <div key={i} style={{ background: 'var(--surface)', border: '1px solid var(--border)', borderRadius: '14px', padding: '1.5rem', height: '140px' }}>
                <div style={{ width: '60%', height: '20px', borderRadius: '6px', background: 'var(--bg)', marginBottom: '0.75rem', animation: 'shimmer 1.5s infinite' }} />
                <div style={{ width: '100%', height: '14px', borderRadius: '6px', background: 'var(--bg)', marginBottom: '0.5rem', animation: 'shimmer 1.5s infinite' }} />
                <div style={{ width: '80%', height: '14px', borderRadius: '6px', background: 'var(--bg)', animation: 'shimmer 1.5s infinite' }} />
              </div>
            ))}
          </div>
        )}

        {!loading && inscriptions.length === 0 && (
          <div style={{ textAlign: 'center', padding: '4rem 2rem', background: 'var(--surface)', border: '1px solid var(--border)', borderRadius: '16px' }}>
            <div style={{ fontSize: '3rem', marginBottom: '1rem' }}>📚</div>
            <h3 style={{ color: 'var(--text)', marginBottom: '0.5rem' }}>Aucun cours</h3>
            <p style={{ color: 'var(--text-muted)', marginBottom: '1.5rem' }}>
              {activeTab === 'completes' 
                ? 'Vous n\'avez pas encore complété de cours'
                : 'Commencez votre apprentissage dès maintenant'}
            </p>
            <button
              onClick={() => navigate('/elearning')}
              style={{ padding: '0.75rem 1.5rem', background: 'var(--primary)', color: 'white', border: 'none', borderRadius: '10px', fontSize: '0.95rem', fontWeight: 600, cursor: 'pointer' }}>
              Parcourir les cours
            </button>
          </div>
        )}

        {!loading && inscriptions.length > 0 && (
          <div style={{ display: 'grid', gap: '1rem' }}>
            {inscriptions.map((inscription, i) => (
              <motion.div
                key={inscription.id}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: i * 0.05 }}
                onClick={() => navigate(`/elearning/${inscription.cours.slug}`)}
                style={{ background: 'var(--surface)', border: '1px solid var(--border)', borderRadius: '14px', padding: '1.5rem', cursor: 'pointer', transition: 'all 0.2s' }}
                whileHover={{ y: -2, boxShadow: '0 8px 24px rgba(0,0,0,0.08)' }}>
                
                <div style={{ display: 'flex', gap: '1.5rem', alignItems: 'start' }}>
                  {/* Thumbnail */}
                  <div style={{ width: 160, height: 90, borderRadius: '10px', overflow: 'hidden', flexShrink: 0, background: 'linear-gradient(135deg, #0e7490, #0891b2)', display: 'flex', alignItems: 'center', justifyContent: 'center', color: 'white', fontSize: '2rem' }}>
                    {inscription.cours.thumbnail ? (
                      <img src={inscription.cours.thumbnail} alt={inscription.cours.titre} style={{ width: '100%', height: '100%', objectFit: 'cover' }} />
                    ) : (
                      '🎓'
                    )}
                  </div>

                  {/* Contenu */}
                  <div style={{ flex: 1 }}>
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'start', marginBottom: '0.75rem' }}>
                      <div>
                        <h3 style={{ fontSize: '1.1rem', fontWeight: 700, color: 'var(--text)', margin: '0 0 0.5rem', lineHeight: 1.3 }}>
                          {inscription.cours.titre}
                        </h3>
                        <div style={{ display: 'flex', gap: '1rem', fontSize: '0.85rem', color: 'var(--text-muted)' }}>
                          <span style={{ display: 'flex', alignItems: 'center', gap: '4px' }}>
                            <IconClock /> {inscription.cours.duree_minutes}min
                          </span>
                          <span>{inscription.cours.categorie_nom}</span>
                          <span>{inscription.cours.niveau}</span>
                        </div>
                      </div>

                      {inscription.est_complete ? (
                        <div style={{ display: 'flex', alignItems: 'center', gap: '6px', padding: '6px 12px', borderRadius: '100px', background: '#dcfce7', color: '#16a34a', fontSize: '0.85rem', fontWeight: 700 }}>
                          <IconCheck /> Complété
                        </div>
                      ) : (
                        <div style={{ display: 'flex', alignItems: 'center', gap: '6px', padding: '6px 12px', borderRadius: '100px', background: '#fef3c7', color: '#f59e0b', fontSize: '0.85rem', fontWeight: 700 }}>
                          <IconPlay /> En cours
                        </div>
                      )}
                    </div>

                    {/* Barre de progression */}
                    <div style={{ marginTop: '1rem' }}>
                      <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '0.5rem' }}>
                        <span style={{ fontSize: '0.85rem', fontWeight: 600, color: 'var(--text-muted)' }}>
                          Progression
                        </span>
                        <span style={{ fontSize: '0.85rem', fontWeight: 700, color: 'var(--primary)' }}>
                          {inscription.progression}%
                        </span>
                      </div>
                      <div style={{ width: '100%', height: '6px', background: 'var(--bg)', borderRadius: '100px', overflow: 'hidden' }}>
                        <div style={{ width: `${inscription.progression}%`, height: '100%', background: 'linear-gradient(90deg, var(--primary-dark), var(--primary))', transition: 'width 0.3s' }} />
                      </div>
                    </div>

                    {/* Date */}
                    <div style={{ marginTop: '0.75rem', fontSize: '0.8rem', color: 'var(--text-muted)' }}>
                      Inscrit le {new Date(inscription.date_inscription).toLocaleDateString('fr-FR')}
                      {inscription.date_completion && (
                        <> • Complété le {new Date(inscription.date_completion).toLocaleDateString('fr-FR')}</>
                      )}
                    </div>
                  </div>
                </div>
              </motion.div>
            ))}
          </div>
        )}
      </div>

      <style>{`
        @keyframes shimmer {
          0% { opacity: 1; }
          50% { opacity: 0.5; }
          100% { opacity: 1; }
        }
      `}</style>
    </div>
  );
}
