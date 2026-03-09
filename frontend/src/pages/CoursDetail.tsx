import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';
import { fetchCoursDetail, inscrireCours, marquerComplete, assisterLivestream, Cours } from '../api/elearning';
import { useToast } from '../hooks/useToast';
import Toast from '../components/Toast';

const IconPlay = () => <svg width="24" height="24" viewBox="0 0 24 24" fill="none"><path d="M8 5v14l11-7z" fill="currentColor"/></svg>;
const IconCheck = () => <svg width="20" height="20" viewBox="0 0 20 20" fill="none"><path d="M16 6L8 14l-4-4" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/></svg>;
const IconClock = () => <svg width="18" height="18" viewBox="0 0 18 18" fill="none"><circle cx="9" cy="9" r="7" stroke="currentColor" strokeWidth="1.5"/><path d="M9 5v4l3 2" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round"/></svg>;
const IconUsers = () => <svg width="18" height="18" viewBox="0 0 18 18" fill="none"><circle cx="6" cy="5" r="3" stroke="currentColor" strokeWidth="1.5"/><path d="M1 14c0-2.8 2.2-5 5-5s5 2.2 5 5" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round"/><path d="M11 5a3 3 0 100-6M14 14c0-1.7-1-3.2-2.5-4" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round"/></svg>;
const IconCalendar = () => <svg width="18" height="18" viewBox="0 0 18 18" fill="none"><rect x="2" y="3" width="14" height="13" rx="2" stroke="currentColor" strokeWidth="1.5"/><path d="M2 7h14M6 1v4M12 1v4" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round"/></svg>;
const IconLive = () => <svg width="20" height="20" viewBox="0 0 20 20" fill="none"><circle cx="10" cy="10" r="3" fill="currentColor"/><path d="M6 10a4 4 0 018 0M4 10a6 6 0 0112 0M2 10a8 8 0 0116 0" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round"/></svg>;

export default function CoursDetail() {
  const { slug } = useParams<{ slug: string }>();
  const navigate = useNavigate();
  const [cours, setCours] = useState<Cours | null>(null);
  const [loading, setLoading] = useState(true);
  const [inscriptionEnCours, setInscriptionEnCours] = useState(false);
  const { toasts, removeToast, success, error: showError } = useToast();

  useEffect(() => {
    if (slug) {
      loadCours();
    }
  }, [slug]);

  const loadCours = async () => {
    try {
      setLoading(true);
      const data = await fetchCoursDetail(slug!);
      setCours(data);
    } catch (err) {
      showError('Erreur', 'Impossible de charger le cours');
      navigate('/elearning');
    } finally {
      setLoading(false);
    }
  };

  const handleInscrire = async () => {
    if (!cours) return;
    
    const token = localStorage.getItem('access_token');
    if (!token) {
      showError('Connexion requise', 'Veuillez vous connecter pour vous inscrire');
      setTimeout(() => navigate('/login'), 1500);
      return;
    }

    try {
      setInscriptionEnCours(true);
      await inscrireCours(cours.slug);
      success('Inscription réussie', 'Vous êtes maintenant inscrit à ce cours');
      loadCours();
    } catch (err: any) {
      showError('Erreur', err.response?.data?.detail || 'Impossible de s\'inscrire');
    } finally {
      setInscriptionEnCours(false);
    }
  };

  const handleMarquerComplete = async () => {
    if (!cours) return;
    try {
      await marquerComplete(cours.slug);
      success('Cours complété', 'Félicitations pour avoir terminé ce cours!');
      loadCours();
    } catch (err) {
      showError('Erreur', 'Impossible de marquer le cours comme complété');
    }
  };

  const handleAssisterLivestream = async () => {
    if (!cours) return;
    try {
      await assisterLivestream(cours.slug);
      success('Présence enregistrée', 'Votre participation au livestream a été enregistrée');
      if (cours.google_meet_url) {
        window.open(cours.google_meet_url, '_blank');
      }
    } catch (err) {
      showError('Erreur', 'Impossible d\'enregistrer votre présence');
    }
  };

  if (loading) {
    return (
      <div style={{ minHeight: '100vh', background: 'var(--bg)', paddingTop: '5rem', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
        <div style={{ width: 48, height: 48, border: '4px solid var(--border)', borderTop: '4px solid var(--primary)', borderRadius: '50%', animation: 'spin 0.8s linear infinite' }} />
      </div>
    );
  }

  if (!cours) return null;

  const getYouTubeEmbedUrl = (url: string) => {
    const videoId = url.match(/(?:youtube\.com\/(?:[^\/]+\/.+\/|(?:v|e(?:mbed)?)\/|.*[?&]v=)|youtu\.be\/)([^"&?\/\s]{11})/)?.[1];
    return videoId ? `https://www.youtube.com/embed/${videoId}` : null;
  };

  return (
    <>
      <div className="toast-container">
        {toasts.map(t => <Toast key={t.id} {...t} onClose={removeToast} />)}
      </div>

      <div style={{ minHeight: '100vh', background: 'var(--bg)', paddingTop: '4rem' }}>
        
        {/* Lecteur vidéo / Livestream */}
        <div style={{ background: '#000', position: 'relative' }}>
          <div style={{ maxWidth: 1400, margin: '0 auto', padding: '2rem 1.5rem' }}>
            {cours.type_cours === 'LIVESTREAM' && cours.google_meet_url ? (
              <div style={{ position: 'relative', paddingBottom: '56.25%', background: 'linear-gradient(135deg, #dc2626, #ef4444)', borderRadius: '16px', overflow: 'hidden' }}>
                <div style={{ position: 'absolute', inset: 0, display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', color: 'white', padding: '2rem', textAlign: 'center' }}>
                  <motion.div initial={{ scale: 0.8 }} animate={{ scale: 1 }} transition={{ duration: 0.5 }}>
                    <IconLive />
                  </motion.div>
                  <h2 style={{ fontSize: '2rem', fontWeight: 800, margin: '1rem 0 0.5rem' }}>
                    {cours.est_livestream_actif ? 'Cours en direct maintenant!' : 'Livestream programmé'}
                  </h2>
                  {cours.date_livestream && (
                    <p style={{ fontSize: '1.1rem', opacity: 0.9, marginBottom: '2rem' }}>
                      📅 {new Date(cours.date_livestream).toLocaleString('fr-FR', { 
                        dateStyle: 'full', 
                        timeStyle: 'short' 
                      })}
                    </p>
                  )}
                  {cours.est_inscrit && (
                    <button
                      onClick={handleAssisterLivestream}
                      style={{ padding: '1rem 2rem', background: 'white', color: '#dc2626', border: 'none', borderRadius: '12px', fontSize: '1.1rem', fontWeight: 700, cursor: 'pointer', display: 'flex', alignItems: 'center', gap: '10px' }}>
                      <IconPlay /> Rejoindre le livestream
                    </button>
                  )}
                </div>
              </div>
            ) : cours.youtube_url ? (
              <div style={{ position: 'relative', paddingBottom: '56.25%', borderRadius: '16px', overflow: 'hidden' }}>
                <iframe
                  src={getYouTubeEmbedUrl(cours.youtube_url) || ''}
                  style={{ position: 'absolute', top: 0, left: 0, width: '100%', height: '100%', border: 'none' }}
                  allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
                  allowFullScreen
                />
              </div>
            ) : (
              <div style={{ position: 'relative', paddingBottom: '56.25%', background: 'linear-gradient(135deg, #0e7490, #0891b2)', borderRadius: '16px', display: 'flex', alignItems: 'center', justifyContent: 'center', color: 'white', fontSize: '4rem' }}>
                🎓
              </div>
            )}
          </div>
        </div>

        {/* Contenu */}
        <div style={{ maxWidth: 1400, margin: '0 auto', padding: '2rem 1.5rem', display: 'grid', gridTemplateColumns: '1fr 380px', gap: '2rem', alignItems: 'start' }}>
          
          {/* Colonne principale */}
          <div>
            <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }}>
              <div style={{ marginBottom: '0.5rem' }}>
                <a href="/elearning" style={{ color: 'var(--text-muted)', fontSize: '0.85rem', textDecoration: 'none' }}>
                  ← Retour aux cours
                </a>
              </div>
              
              <h1 style={{ fontSize: '2.5rem', fontWeight: 800, color: 'var(--text)', margin: '0 0 1rem', lineHeight: 1.2 }}>
                {cours.titre}
              </h1>

              <div style={{ display: 'flex', gap: '1rem', flexWrap: 'wrap', marginBottom: '2rem' }}>
                <span style={{ display: 'inline-flex', alignItems: 'center', gap: '6px', padding: '6px 14px', borderRadius: '100px', background: 'var(--bg)', color: 'var(--text)', fontSize: '0.9rem', fontWeight: 600 }}>
                  <IconClock /> {cours.duree_minutes} min
                </span>
                <span style={{ display: 'inline-flex', alignItems: 'center', gap: '6px', padding: '6px 14px', borderRadius: '100px', background: 'var(--bg)', color: 'var(--text)', fontSize: '0.9rem', fontWeight: 600 }}>
                  <IconUsers /> {cours.nombre_inscrits} inscrits
                </span>
                <span style={{ padding: '6px 14px', borderRadius: '100px', background: '#dbeafe', color: '#2563eb', fontSize: '0.9rem', fontWeight: 700 }}>
                  {cours.niveau}
                </span>
                {cours.est_gratuit && (
                  <span style={{ padding: '6px 14px', borderRadius: '100px', background: '#dcfce7', color: '#16a34a', fontSize: '0.9rem', fontWeight: 700 }}>
                    GRATUIT
                  </span>
                )}
              </div>

              <div style={{ background: 'var(--surface)', border: '1px solid var(--border)', borderRadius: '16px', padding: '2rem', marginBottom: '2rem' }}>
                <h2 style={{ fontSize: '1.3rem', fontWeight: 700, color: 'var(--text)', margin: '0 0 1rem' }}>
                  Description
                </h2>
                <p style={{ fontSize: '1rem', color: 'var(--text)', lineHeight: 1.7, margin: 0 }}>
                  {cours.description}
                </p>
              </div>

              {cours.resume_ai && (
                <div style={{ background: 'var(--surface)', border: '1px solid var(--border)', borderRadius: '16px', padding: '2rem', marginBottom: '2rem' }}>
                  <h2 style={{ fontSize: '1.3rem', fontWeight: 700, color: 'var(--text)', margin: '0 0 1rem' }}>
                    📝 Résumé AI
                  </h2>
                  <p style={{ fontSize: '0.95rem', color: 'var(--text-muted)', lineHeight: 1.7, margin: 0, whiteSpace: 'pre-wrap' }}>
                    {cours.resume_ai}
                  </p>
                </div>
              )}

              {cours.transcription && (
                <div style={{ background: 'var(--surface)', border: '1px solid var(--border)', borderRadius: '16px', padding: '2rem' }}>
                  <h2 style={{ fontSize: '1.3rem', fontWeight: 700, color: 'var(--text)', margin: '0 0 1rem' }}>
                    📄 Transcription
                  </h2>
                  <div style={{ fontSize: '0.9rem', color: 'var(--text-muted)', lineHeight: 1.8, maxHeight: '400px', overflow: 'auto', whiteSpace: 'pre-wrap' }}>
                    {cours.transcription}
                  </div>
                </div>
              )}
            </motion.div>
          </div>

          {/* Sidebar */}
          <motion.aside initial={{ opacity: 0, x: 20 }} animate={{ opacity: 1, x: 0 }} transition={{ delay: 0.2 }}
            style={{ position: 'sticky', top: '88px' }}>
            <div style={{ background: 'var(--surface)', border: '1px solid var(--border)', borderRadius: '16px', padding: '1.5rem' }}>
              
              {!cours.est_inscrit ? (
                <>
                  <div style={{ fontSize: '2rem', fontWeight: 800, color: 'var(--primary)', marginBottom: '0.5rem' }}>
                    {cours.est_gratuit ? 'Gratuit' : `${parseInt(cours.prix).toLocaleString()} FCFA`}
                  </div>
                  <button
                    onClick={handleInscrire}
                    disabled={inscriptionEnCours}
                    style={{ width: '100%', padding: '1rem', background: 'linear-gradient(135deg, var(--primary-dark), var(--primary))', color: 'white', border: 'none', borderRadius: '12px', fontSize: '1.1rem', fontWeight: 700, cursor: inscriptionEnCours ? 'not-allowed' : 'pointer', opacity: inscriptionEnCours ? 0.6 : 1, marginBottom: '1.5rem' }}>
                    {inscriptionEnCours ? 'Inscription...' : 'S\'inscrire au cours'}
                  </button>
                </>
              ) : (
                <>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '10px', padding: '1rem', background: '#dcfce7', border: '1px solid #16a34a', borderRadius: '12px', marginBottom: '1.5rem' }}>
                    <IconCheck />
                    <span style={{ color: '#16a34a', fontWeight: 700 }}>Vous êtes inscrit</span>
                  </div>
                  
                  {cours.ma_progression && (
                    <div style={{ marginBottom: '1.5rem' }}>
                      <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '0.5rem' }}>
                        <span style={{ fontSize: '0.9rem', fontWeight: 600, color: 'var(--text)' }}>Progression</span>
                        <span style={{ fontSize: '0.9rem', fontWeight: 700, color: 'var(--primary)' }}>
                          {cours.ma_progression.progression}%
                        </span>
                      </div>
                      <div style={{ width: '100%', height: '8px', background: 'var(--bg)', borderRadius: '100px', overflow: 'hidden' }}>
                        <div style={{ width: `${cours.ma_progression.progression}%`, height: '100%', background: 'linear-gradient(90deg, var(--primary-dark), var(--primary))', transition: 'width 0.3s' }} />
                      </div>
                    </div>
                  )}

                  {!cours.ma_progression?.est_complete && (
                    <button
                      onClick={handleMarquerComplete}
                      style={{ width: '100%', padding: '0.9rem', background: 'var(--bg)', border: '1.5px solid var(--border)', borderRadius: '10px', color: 'var(--text)', fontSize: '0.95rem', fontWeight: 600, cursor: 'pointer', marginBottom: '1rem' }}>
                      Marquer comme complété
                    </button>
                  )}

                  <button
                    onClick={() => navigate('/elearning/mes-cours')}
                    style={{ width: '100%', padding: '0.9rem', background: 'transparent', border: '1.5px solid var(--primary)', borderRadius: '10px', color: 'var(--primary)', fontSize: '0.95rem', fontWeight: 600, cursor: 'pointer' }}>
                    Voir mes cours
                  </button>
                </>
              )}

              <div style={{ borderTop: '1px solid var(--border)', paddingTop: '1.5rem', marginTop: '1.5rem' }}>
                <h3 style={{ fontSize: '0.9rem', fontWeight: 700, color: 'var(--text)', margin: '0 0 1rem', textTransform: 'uppercase', letterSpacing: '0.05em' }}>
                  Ce cours inclut
                </h3>
                <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem', fontSize: '0.9rem', color: 'var(--text-muted)' }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                    <span>✓</span> Accès à vie
                  </div>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                    <span>✓</span> {cours.duree_minutes} minutes de contenu
                  </div>
                  {cours.type_cours === 'LIVESTREAM' && (
                    <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                      <span>✓</span> Session en direct
                    </div>
                  )}
                  <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                    <span>✓</span> Certificat de completion
                  </div>
                </div>
              </div>

              <div style={{ borderTop: '1px solid var(--border)', paddingTop: '1.5rem', marginTop: '1.5rem' }}>
                <h3 style={{ fontSize: '0.9rem', fontWeight: 700, color: 'var(--text)', margin: '0 0 0.75rem' }}>
                  Instructeur
                </h3>
                <div style={{ fontSize: '0.95rem', color: 'var(--text)', fontWeight: 600 }}>
                  {cours.instructeur_nom}
                </div>
              </div>
            </div>
          </motion.aside>
        </div>
      </div>

      <style>{`
        @keyframes spin {
          to { transform: rotate(360deg); }
        }
        @media (max-width: 1024px) {
          div[style*="grid-template-columns: 1fr 380px"] {
            grid-template-columns: 1fr !important;
          }
        }
        .toast-container {
          position: fixed; top: 20px; right: 20px; z-index: 9999;
          display: flex; flex-direction: column; gap: 1rem; max-width: 400px;
        }
      `}</style>
    </>
  );
}
