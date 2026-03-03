import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { useToast } from '../hooks/useToast';
import Toast from '../components/Toast';
import { getOffres, createOffre, postuler, getContrats, OffreEmploi, Contrat } from '../api/jobs';

const JOB_TYPES = ['Récolte', 'Semis', 'Désherbage', 'Irrigation', 'Taille', 'Entretien', 'Autre'];

const IconBriefcase = () => (
  <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <rect x="2" y="7" width="20" height="14" rx="2" ry="2"/><path d="M16 21V5a2 2 0 00-2-2h-4a2 2 0 00-2 2v16"/>
  </svg>
);

const IconMapPin = () => (
  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0118 0z"/><circle cx="12" cy="10" r="3"/>
  </svg>
);

const IconCalendar = () => (
  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <rect x="3" y="4" width="18" height="18" rx="2" ry="2"/><line x1="16" y1="2" x2="16" y2="6"/><line x1="8" y1="2" x2="8" y2="6"/><line x1="3" y1="10" x2="21" y2="10"/>
  </svg>
);

const IconPlus = () => (
  <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
    <line x1="12" y1="5" x2="12" y2="19"/><line x1="5" y1="12" x2="19" y2="12"/>
  </svg>
);

function getUserType(): string {
  try {
    const token = localStorage.getItem('access_token');
    if (!token) return '';
    const p = JSON.parse(atob(token.split('.')[1]));
    return p.user_type || '';
  } catch { return ''; }
}

const inputStyle: React.CSSProperties = {
  width: '100%',
  padding: '0.75rem',
  borderRadius: '10px',
  border: '1px solid var(--border)',
  background: 'var(--bg)',
  color: 'var(--text)',
  fontSize: '0.95rem',
  boxSizing: 'border-box',
};

const labelStyle: React.CSSProperties = {
  display: 'block',
  marginBottom: '0.4rem',
  fontSize: '0.875rem',
  fontWeight: 600,
  color: 'var(--text)',
};

export default function Jobs() {
  const [activeTab, setActiveTab] = useState<'available' | 'my_offers' | 'contracts'>('available');
  const [offres, setOffres] = useState<OffreEmploi[]>([]);
  const [contrats, setContrats] = useState<Contrat[]>([]);
  const [loading, setLoading] = useState(true);
  const [showModal, setShowModal] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [filterType, setFilterType] = useState('');

  const userType = getUserType();
  const isOuvrier = userType === 'OUVRIER';
  const isExploitant = userType === 'EXPLOITANT';
  const accentColor = isOuvrier ? '#d97706' : '#16a34a';
  const heroBg = isOuvrier
    ? 'linear-gradient(135deg, #78350f 0%, #92400e 100%)'
    : 'linear-gradient(135deg, #064e3b 0%, #065f46 100%)';

  const { toasts, removeToast, success, error: showError } = useToast();

  const fetchData = async () => {
    setLoading(true);
    try {
      if (activeTab === 'available') {
        const data = await getOffres(filterType ? { type_travail: filterType } : {});
        setOffres(data.filter(o => o.statut === 'OUVERTE'));
      } else if (activeTab === 'my_offers') {
        const data = await getOffres({ mine: true });
        setOffres(data);
      } else if (activeTab === 'contracts') {
        const data = await getContrats();
        setContrats(data);
      }
    } catch {
      showError('Erreur', 'Impossible de charger les données');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { fetchData(); }, [activeTab, filterType]);

  const handlePostuler = async (offreId: number) => {
    try {
      await postuler(offreId);
      success('Succès', 'Votre candidature a été enregistrée');
      fetchData();
    } catch {
      showError('Erreur', 'Impossible de postuler à cette offre');
    }
  };

  const handleCreateOffre = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    setIsSubmitting(true);
    const formData = new FormData(e.currentTarget);
    const data: Record<string, string> = {};
    formData.forEach((v, k) => { data[k] = v as string; });
    try {
      await createOffre(data);
      success('Succès', 'Offre publiée avec succès');
      setShowModal(false);
      fetchData();
    } catch {
      showError('Erreur', "Impossible de publier l'offre");
    } finally {
      setIsSubmitting(false);
    }
  };

  const tabBtn = (active: boolean): React.CSSProperties => ({
    padding: '0.75rem 1.5rem',
    borderRadius: '12px',
    border: 'none',
    background: active ? 'white' : 'rgba(255,255,255,0.15)',
    color: active ? accentColor : 'white',
    fontWeight: 700,
    cursor: 'pointer',
    fontSize: '0.9rem',
    transition: 'all 0.2s',
  });

  return (
    <div style={{ minHeight: '100vh', background: 'var(--bg)', padding: '2rem 1.5rem' }}>
      <div style={{ maxWidth: '1100px', margin: '0 auto' }}>

        <div style={{ position: 'fixed', top: '80px', right: '20px', zIndex: 9999, display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
          {toasts.map(t => <Toast key={t.id} {...t} onClose={removeToast} />)}
        </div>

        <div style={{ background: heroBg, padding: '2.5rem 2rem', borderRadius: '20px', color: 'white', marginBottom: '2rem' }}>
          <h1 style={{ fontSize: '2.25rem', fontWeight: 800, margin: '0 0 0.4rem' }}>Emploi Saisonnier</h1>
          <p style={{ opacity: 0.9, fontSize: '1rem', maxWidth: '560px', margin: '0 0 2rem' }}>
            {isOuvrier
              ? 'Trouvez des opportunités de travail dans les fermes près de chez vous.'
              : "Recrutez de la main-d'œuvre qualifiée pour vos travaux saisonniers."}
          </p>
          <div style={{ display: 'flex', gap: '0.75rem', flexWrap: 'wrap' }}>
            <button onClick={() => setActiveTab('available')} style={tabBtn(activeTab === 'available')}>
              Offres disponibles
            </button>
            {isExploitant && (
              <button onClick={() => setActiveTab('my_offers')} style={tabBtn(activeTab === 'my_offers')}>
                Mes offres
              </button>
            )}
            {(isOuvrier || isExploitant) && (
              <button onClick={() => setActiveTab('contracts')} style={tabBtn(activeTab === 'contracts')}>
                Mes contrats
              </button>
            )}
          </div>
        </div>

        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.5rem', flexWrap: 'wrap', gap: '1rem' }}>
          {activeTab === 'available' && (
            <div style={{ display: 'flex', gap: '0.75rem', alignItems: 'center' }}>
              <span style={{ fontWeight: 600, color: 'var(--text-secondary)', fontSize: '0.9rem' }}>Filtrer :</span>
              <select
                value={filterType}
                onChange={e => setFilterType(e.target.value)}
                style={{ padding: '0.5rem 0.75rem', borderRadius: '8px', border: '1px solid var(--border)', background: 'var(--surface)', color: 'var(--text)', fontSize: '0.9rem' }}
              >
                <option value="">Tous les types</option>
                {JOB_TYPES.map(t => <option key={t} value={t}>{t}</option>)}
              </select>
            </div>
          )}
          {isExploitant && activeTab !== 'contracts' && (
            <button
              onClick={() => setShowModal(true)}
              style={{ display: 'flex', alignItems: 'center', gap: '8px', padding: '0.75rem 1.5rem', borderRadius: '12px', border: 'none', background: accentColor, color: 'white', fontWeight: 700, cursor: 'pointer', fontSize: '0.95rem' }}
            >
              <IconPlus /> Publier une offre
            </button>
          )}
        </div>

        {loading ? (
          <div style={{ textAlign: 'center', padding: '4rem', color: 'var(--text-secondary)' }}>
            Chargement...
          </div>
        ) : activeTab !== 'contracts' ? (
          offres.length === 0 ? (
            <div style={{ textAlign: 'center', padding: '4rem', color: 'var(--text-secondary)', background: 'var(--surface)', borderRadius: '16px', border: '1px solid var(--border)' }}>
              <p style={{ fontSize: '1.1rem', margin: 0 }}>Aucune offre d'emploi disponible pour le moment.</p>
            </div>
          ) : (
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(300px, 1fr))', gap: '1.5rem' }}>
              {offres.map(offre => (
                <motion.div
                  key={offre.id}
                  layout
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  style={{ background: 'var(--surface)', border: '1px solid var(--border)', borderRadius: '16px', padding: '1.5rem', display: 'flex', flexDirection: 'column', gap: '1rem' }}
                >
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
                    <span style={{ background: `${accentColor}18`, color: accentColor, padding: '4px 12px', borderRadius: '20px', fontSize: '0.78rem', fontWeight: 700 }}>
                      {offre.type_travail}
                    </span>
                    <span style={{ fontSize: '1.1rem', fontWeight: 800, color: accentColor }}>
                      {parseInt(offre.salaire_horaire).toLocaleString()} FCFA/h
                    </span>
                  </div>

                  <div>
                    <h3 style={{ margin: '0 0 0.4rem', fontSize: '1.1rem', fontWeight: 700 }}>
                      {offre.type_travail} à {offre.canton_nom}
                    </h3>
                    <p style={{ margin: 0, color: 'var(--text-secondary)', fontSize: '0.9rem', lineHeight: 1.5 }}>
                      {offre.description}
                    </p>
                  </div>

                  <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem', fontSize: '0.85rem', color: 'var(--text-secondary)' }}>
                    <span style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
                      <IconMapPin /> {offre.canton_nom}
                    </span>
                    <span style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
                      <IconCalendar /> {new Date(offre.date_debut).toLocaleDateString()} — {new Date(offre.date_fin).toLocaleDateString()}
                    </span>
                    <span style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
                      <IconBriefcase /> {offre.nombre_postes - offre.postes_pourvus} postes restants sur {offre.nombre_postes}
                    </span>
                  </div>

                  {isOuvrier && (
                    <button
                      onClick={() => handlePostuler(offre.id)}
                      disabled={offre.postes_pourvus >= offre.nombre_postes}
                      style={{
                        padding: '0.75rem',
                        borderRadius: '10px',
                        border: 'none',
                        background: offre.postes_pourvus >= offre.nombre_postes ? 'var(--border)' : accentColor,
                        color: 'white',
                        fontWeight: 700,
                        cursor: offre.postes_pourvus >= offre.nombre_postes ? 'not-allowed' : 'pointer',
                        fontSize: '0.95rem',
                      }}
                    >
                      Postuler maintenant
                    </button>
                  )}

                  {isExploitant && (
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', fontSize: '0.8rem', paddingTop: '0.5rem', borderTop: '1px solid var(--border)' }}>
                      <span style={{ color: 'var(--text-secondary)' }}>
                        Publié le {new Date(offre.created_at).toLocaleDateString()}
                      </span>
                      <span style={{ fontWeight: 700, color: offre.statut === 'OUVERTE' ? '#059669' : '#dc2626' }}>
                        {offre.statut}
                      </span>
                    </div>
                  )}
                </motion.div>
              ))}
            </div>
          )
        ) : (
          contrats.length === 0 ? (
            <div style={{ textAlign: 'center', padding: '4rem', color: 'var(--text-secondary)', background: 'var(--surface)', borderRadius: '16px', border: '1px solid var(--border)' }}>
              <p style={{ fontSize: '1.1rem', margin: 0 }}>Vous n'avez aucun contrat actif.</p>
            </div>
          ) : (
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(300px, 1fr))', gap: '1.5rem' }}>
              {contrats.map(contrat => (
                <motion.div
                  key={contrat.id}
                  layout
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  style={{ background: 'var(--surface)', border: '1px solid var(--border)', borderRadius: '16px', padding: '1.5rem' }}
                >
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1rem' }}>
                    <span style={{ background: 'var(--bg)', padding: '4px 12px', borderRadius: '20px', fontSize: '0.78rem', fontWeight: 600 }}>
                      #{contrat.id}
                    </span>
                    <span style={{ color: contrat.statut === 'SIGNE' ? '#059669' : '#2563eb', fontWeight: 700, fontSize: '0.85rem' }}>
                      {contrat.statut}
                    </span>
                  </div>

                  <h3 style={{ margin: '0 0 1rem', fontSize: '1.05rem', fontWeight: 700 }}>
                    {isOuvrier ? `Contrat avec ${contrat.exploitant_nom}` : `Contrat avec ${contrat.ouvrier_nom}`}
                  </h3>

                  <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem', fontSize: '0.9rem' }}>
                    <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                      <span style={{ color: 'var(--text-secondary)' }}>Salaire :</span>
                      <span style={{ fontWeight: 600 }}>{parseInt(contrat.salaire_horaire).toLocaleString()} FCFA/h</span>
                    </div>
                    <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                      <span style={{ color: 'var(--text-secondary)' }}>Période :</span>
                      <span style={{ fontWeight: 600 }}>{new Date(contrat.date_debut).toLocaleDateString()} — {new Date(contrat.date_fin).toLocaleDateString()}</span>
                    </div>
                  </div>
                </motion.div>
              ))}
            </div>
          )
        )}

        <AnimatePresence>
          {showModal && (
            <div style={{ position: 'fixed', inset: 0, background: 'rgba(0,0,0,0.55)', display: 'flex', alignItems: 'center', justifyContent: 'center', zIndex: 1000, padding: '1rem' }}>
              <motion.div
                initial={{ scale: 0.92, opacity: 0 }}
                animate={{ scale: 1, opacity: 1 }}
                exit={{ scale: 0.92, opacity: 0 }}
                style={{ background: 'var(--surface)', padding: '2rem', borderRadius: '20px', width: '100%', maxWidth: '520px', boxShadow: '0 25px 60px rgba(0,0,0,0.25)', maxHeight: '90vh', overflowY: 'auto' }}
              >
                <h2 style={{ margin: '0 0 1.5rem', fontSize: '1.4rem', fontWeight: 800 }}>Publier une offre</h2>
                <form onSubmit={handleCreateOffre}>
                  <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
                    <div>
                      <label style={labelStyle}>Type de travail</label>
                      <select name="type_travail" required style={inputStyle}>
                        {JOB_TYPES.map(t => <option key={t} value={t}>{t}</option>)}
                      </select>
                    </div>

                    <div>
                      <label style={labelStyle}>Description</label>
                      <textarea name="description" placeholder="Décrivez les tâches, conditions, etc." required rows={3} style={{ ...inputStyle, resize: 'vertical' }} />
                    </div>

                    <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem' }}>
                      <div>
                        <label style={labelStyle}>Date début</label>
                        <input name="date_debut" type="date" required style={inputStyle} />
                      </div>
                      <div>
                        <label style={labelStyle}>Date fin</label>
                        <input name="date_fin" type="date" required style={inputStyle} />
                      </div>
                    </div>

                    <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem' }}>
                      <div>
                        <label style={labelStyle}>Salaire horaire (FCFA)</label>
                        <input name="salaire_horaire" type="number" required style={inputStyle} />
                      </div>
                      <div>
                        <label style={labelStyle}>Nombre de postes</label>
                        <input name="nombre_postes" type="number" required style={inputStyle} />
                      </div>
                    </div>

                    <div>
                      <label style={labelStyle}>ID du Canton</label>
                      <input name="canton" type="number" required placeholder="Ex: 1" style={inputStyle} />
                    </div>

                    <div style={{ display: 'flex', gap: '1rem', marginTop: '0.5rem' }}>
                      <button
                        type="button"
                        onClick={() => setShowModal(false)}
                        style={{ flex: 1, padding: '0.75rem', borderRadius: '10px', border: '1px solid var(--border)', background: 'transparent', color: 'var(--text)', fontWeight: 600, cursor: 'pointer', fontSize: '0.95rem' }}
                      >
                        Annuler
                      </button>
                      <button
                        type="submit"
                        disabled={isSubmitting}
                        style={{ flex: 1, padding: '0.75rem', borderRadius: '10px', border: 'none', background: accentColor, color: 'white', fontWeight: 700, cursor: 'pointer', fontSize: '0.95rem', opacity: isSubmitting ? 0.7 : 1 }}
                      >
                        {isSubmitting ? 'Publication...' : 'Publier'}
                      </button>
                    </div>
                  </div>
                </form>
              </motion.div>
            </div>
          )}
        </AnimatePresence>
      </div>
    </div>
  );
}
