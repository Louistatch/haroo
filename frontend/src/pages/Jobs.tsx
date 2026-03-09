import { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { useToast } from '../hooks/useToast';
import Toast from '../components/Toast';
import AnnonceOuvrierModal from '../components/AnnonceOuvrierModal';
import {
  getOffres, createOffre, postuler, getContrats, checkEligibilite,
  getAnnonces, createAnnonce, rejoindreAnnonce,
  getAnnoncesOuvriers, createAnnonceOuvrier, desactiverAnnonceOuvrier, rejoindreAnnonceOuvrier,
  OffreEmploi, Contrat, AnnonceCollective, AnnonceOuvrier, Eligibilite, MembreEquipe
} from '../api/jobs';
import { getRegions, getPrefectures, getCantons, Region, Prefecture, Canton } from '../api/locations';

const JOB_TYPES = ['Récolte', 'Semis', 'Désherbage', 'Irrigation', 'Taille', 'Entretien', 'Autre'];
const COMPETENCES_OPTIONS = ['Récolte', 'Semis', 'Désherbage', 'Irrigation', 'Taille', 'Entretien', 'Labour', 'Traitement', 'Autre'];

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
const IconUsers = () => (
  <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <path d="M17 21v-2a4 4 0 00-4-4H5a4 4 0 00-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M23 21v-2a4 4 0 00-3-3.87"/><path d="M16 3.13a4 4 0 010 7.75"/>
  </svg>
);

function getUserType(): string {
  try {
    const token = localStorage.getItem('access_token');
    if (!token) return '';
    return JSON.parse(atob(token.split('.')[1])).user_type || '';
  } catch { return ''; }
}

const inputStyle: React.CSSProperties = {
  width: '100%', padding: '0.75rem', borderRadius: '10px',
  border: '1px solid var(--border)', background: 'var(--bg)',
  color: 'var(--text)', fontSize: '0.95rem', boxSizing: 'border-box',
};
const labelStyle: React.CSSProperties = {
  display: 'block', marginBottom: '0.4rem', fontSize: '0.875rem', fontWeight: 600, color: 'var(--text)',
};

function timeLeft(dateStr: string): string {
  const diff = new Date(dateStr).getTime() - Date.now();
  if (diff <= 0) return 'Expiré';
  const h = Math.floor(diff / 3600000);
  const m = Math.floor((diff % 3600000) / 60000);
  if (h > 24) return `${Math.floor(h / 24)}j ${h % 24}h`;
  return `${h}h ${m}min`;
}

/* ─── Annonce Collective Card ─── */
function AnnonceCard({ annonce, isExploitant, onRejoindre }: {
  annonce: AnnonceCollective; isExploitant: boolean;
  onRejoindre: (id: number) => void;
}) {
  const pct = annonce.progression;
  const expired = new Date(annonce.date_expiration).getTime() < Date.now();
  return (
    <motion.div layout initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }}
      style={{ background: 'var(--surface)', border: '1px solid var(--border)', borderRadius: '16px', padding: '1.5rem', display: 'flex', flexDirection: 'column', gap: '1rem' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
        <span style={{ background: '#7c3aed18', color: '#7c3aed', padding: '4px 12px', borderRadius: '20px', fontSize: '0.78rem', fontWeight: 700, display: 'flex', alignItems: 'center', gap: 4 }}>
          <IconUsers /> Collective
        </span>
        <span style={{ fontSize: '0.78rem', fontWeight: 600, color: expired ? '#dc2626' : '#d97706' }}>
          {expired ? 'Expiré' : `⏱ ${timeLeft(annonce.date_expiration)}`}
        </span>
      </div>
      <div>
        <h3 style={{ margin: '0 0 0.3rem', fontSize: '1.05rem', fontWeight: 700 }}>
          {annonce.type_travail} à {annonce.canton_nom}
        </h3>
        <p style={{ margin: 0, color: 'var(--text-secondary)', fontSize: '0.88rem', lineHeight: 1.5 }}>
          {annonce.description}
        </p>
      </div>
      {/* Progress bar */}
      <div>
        <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.8rem', marginBottom: '0.3rem' }}>
          <span style={{ color: 'var(--text-secondary)' }}>
            {annonce.nb_participants} participant{annonce.nb_participants > 1 ? 's' : ''}
          </span>
          <span style={{ fontWeight: 700, color: pct >= 100 ? '#16a34a' : '#7c3aed' }}>
            {parseFloat(annonce.superficie_cumulee).toFixed(1)} / {parseFloat(annonce.seuil_hectares).toFixed(0)} ha ({pct.toFixed(0)}%)
          </span>
        </div>
        <div style={{ height: 8, borderRadius: 4, background: 'var(--border)', overflow: 'hidden' }}>
          <div style={{ height: '100%', width: `${Math.min(pct, 100)}%`, borderRadius: 4, background: pct >= 100 ? '#16a34a' : '#7c3aed', transition: 'width 0.5s' }} />
        </div>
      </div>
      <div style={{ display: 'flex', flexDirection: 'column', gap: '0.4rem', fontSize: '0.85rem', color: 'var(--text-secondary)' }}>
        <span style={{ display: 'flex', alignItems: 'center', gap: '6px' }}><IconCalendar /> {new Date(annonce.date_debut).toLocaleDateString()} — {new Date(annonce.date_fin).toLocaleDateString()}</span>
        <span style={{ display: 'flex', alignItems: 'center', gap: '6px' }}><IconMapPin /> {annonce.canton_nom}</span>
        <span style={{ display: 'flex', alignItems: 'center', gap: '6px' }}><IconBriefcase /> {parseInt(annonce.salaire_horaire).toLocaleString()} FCFA/h · {annonce.nombre_postes} postes</span>
      </div>
      {isExploitant && annonce.statut === 'EN_ATTENTE' && !expired && (
        <button onClick={() => onRejoindre(annonce.id)}
          style={{ padding: '0.75rem', borderRadius: '10px', border: 'none', background: '#7c3aed', color: 'white', fontWeight: 700, cursor: 'pointer', fontSize: '0.95rem' }}>
          Rejoindre cette annonce
        </button>
      )}
      {annonce.statut === 'VALIDEE' && (
        <div style={{ padding: '0.6rem', borderRadius: '10px', background: '#dcfce7', color: '#16a34a', fontWeight: 700, textAlign: 'center', fontSize: '0.88rem' }}>
          ✓ Quota atteint — Offre publiée
        </div>
      )}
    </motion.div>
  );
}

/* ─── Main Component ─── */
export default function Jobs() {
  const [activeTab, setActiveTab] = useState<'available' | 'my_offers' | 'contracts' | 'annonces' | 'annonces_ouvriers'>('available');
  const [offres, setOffres] = useState<OffreEmploi[]>([]);
  const [contrats, setContrats] = useState<Contrat[]>([]);
  const [annonces, setAnnonces] = useState<AnnonceCollective[]>([]);
  const [annoncesOuvriers, setAnnoncesOuvriers] = useState<AnnonceOuvrier[]>([]);
  const [eligibilite, setEligibilite] = useState<Eligibilite | null>(null);
  const [loading, setLoading] = useState(true);
  const [showModal, setShowModal] = useState<'offre' | 'annonce' | 'annonce_ouvrier' | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [filterType, setFilterType] = useState('');

  // États pour le formulaire d'annonce ouvrier
  const [selectedCompetences, setSelectedCompetences] = useState<string[]>([]);
  const [regions, setRegions] = useState<Region[]>([]);
  const [prefectures, setPrefectures] = useState<Prefecture[]>([]);
  const [cantons, setCantons] = useState<Canton[]>([]);
  const [selectedRegion, setSelectedRegion] = useState<number | null>(null);
  const [selectedPrefecture, setSelectedPrefecture] = useState<number | null>(null);
  const [selectedCantons, setSelectedCantons] = useState<number[]>([]);
  const [showTeamAlert, setShowTeamAlert] = useState(false);
  const [hasTeam, setHasTeam] = useState<boolean | null>(null);
  const [teamMembers, setTeamMembers] = useState<MembreEquipe[]>(
    Array(7).fill(null).map(() => ({ nom: '', prenom: '', telephone: '' }))
  );
  const [typeAnnonce, setTypeAnnonce] = useState<'INDIVIDUELLE' | 'COLLECTIVE'>('INDIVIDUELLE');

  const userType = getUserType();
  const isOuvrier = userType === 'OUVRIER';
  const isExploitant = userType === 'EXPLOITANT';
  const accentColor = isOuvrier ? '#d97706' : '#16a34a';
  const heroBg = isOuvrier
    ? 'linear-gradient(135deg, #78350f 0%, #92400e 100%)'
    : 'linear-gradient(135deg, #064e3b 0%, #065f46 100%)';

  const { toasts, removeToast, success, error: showError } = useToast();

  useEffect(() => {
    if (isExploitant) {
      checkEligibilite().then(setEligibilite).catch(() => {});
    }
  }, [isExploitant]);

  // Charger les régions au montage
  useEffect(() => {
    getRegions().then(setRegions).catch(() => {});
  }, []);

  // Charger les préfectures quand une région est sélectionnée
  useEffect(() => {
    if (selectedRegion) {
      getPrefectures(selectedRegion).then(setPrefectures).catch(() => {});
      setSelectedPrefecture(null);
      setCantons([]);
      setSelectedCantons([]);
    }
  }, [selectedRegion]);

  // Charger les cantons quand une préfecture est sélectionnée
  useEffect(() => {
    if (selectedPrefecture) {
      getCantons(selectedPrefecture).then(setCantons).catch(() => {});
      setSelectedCantons([]);
    }
  }, [selectedPrefecture]);

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
      } else if (activeTab === 'annonces') {
        const data = await getAnnonces(isExploitant ? {} : {});
        setAnnonces(data);
      } else if (activeTab === 'annonces_ouvriers') {
        const data = await getAnnoncesOuvriers(isOuvrier ? { mine: true } : {});
        setAnnoncesOuvriers(data);
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

  const handleRejoindre = async (annonceId: number) => {
    try {
      await rejoindreAnnonce(annonceId);
      success('Succès', 'Vous avez rejoint l\'annonce collective');
      fetchData();
    } catch (err: any) {
      const msg = err?.response?.data?.error || "Impossible de rejoindre l'annonce";
      showError('Erreur', msg);
    }
  };

  const handlePublish = () => {
    if (!isExploitant) return;
    if (eligibilite && !eligibilite.profil_complet) {
      showError('Profil incomplet', "Veuillez d'abord compléter votre profil d'exploitation (localisation, superficie) dans votre profil.");
      return;
    }
    if (eligibilite?.peut_publier_directement) {
      setShowModal('offre');
    } else {
      setShowModal('annonce');
    }
  };

  const handleCreateOffre = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    setIsSubmitting(true);
    const fd = new FormData(e.currentTarget);
    const data: Record<string, string> = {};
    fd.forEach((v, k) => { data[k] = v as string; });
    try {
      await createOffre(data);
      success('Succès', 'Offre publiée avec succès');
      setShowModal(null);
      fetchData();
    } catch (err: any) {
      const detail = err?.response?.data?.detail || err?.response?.data?.error || "Impossible de publier l'offre";
      if (err?.response?.data?.error === 'publication_directe_impossible') {
        showError('Non éligible', detail);
        setShowModal('annonce');
      } else if (err?.response?.data?.error === 'profil_incomplet') {
        showError('Profil incomplet', detail);
        setShowModal(null);
      } else {
        showError('Erreur', detail);
      }
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleCreateAnnonce = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    setIsSubmitting(true);
    const fd = new FormData(e.currentTarget);
    const data: Record<string, string> = {};
    fd.forEach((v, k) => { data[k] = v as string; });
    try {
      const result = await createAnnonce(data);
      if (result.statut === 'VALIDEE') {
        success('Succès', 'Quota atteint ! Votre offre a été publiée directement.');
      } else {
        success('Annonce créée', 'Les exploitants de votre zone ont 2 jours pour rejoindre.');
      }
      setShowModal(null);
      setActiveTab('annonces');
      fetchData();
    } catch (err: any) {
      showError('Erreur', err?.response?.data?.detail || err?.response?.data?.error || "Impossible de créer l'annonce");
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleCreateAnnonceOuvrier = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    setIsSubmitting(true);
    const fd = new FormData(e.currentTarget);
    
    // Calcul du tarif avec commission de 20%
    const tarifBrut = 1000; // FCFA par heure
    
    const data: any = {
      titre: fd.get('titre') as string,
      description: fd.get('description') as string,
      competences: selectedCompetences,
      cantons_disponibles: selectedCantons,
      tarif_horaire_min: tarifBrut.toString(),
      date_disponibilite_debut: fd.get('date_disponibilite_debut') as string,
      date_disponibilite_fin: fd.get('date_disponibilite_fin') as string || undefined,
      type_annonce: typeAnnonce,
      equipe_complete: typeAnnonce === 'INDIVIDUELLE' && hasTeam === true,
      membres_equipe: typeAnnonce === 'INDIVIDUELLE' && hasTeam === true ? teamMembers : undefined,
    };
    
    try {
      await createAnnonceOuvrier(data);
      success('Succès', typeAnnonce === 'COLLECTIVE' 
        ? 'Votre annonce collective a été créée. Les autres ouvriers ont 2 jours pour rejoindre.'
        : 'Votre annonce de disponibilité a été publiée.');
      setShowModal(null);
      setActiveTab('annonces_ouvriers');
      // Réinitialiser les sélections
      setSelectedCompetences([]);
      setSelectedRegion(null);
      setSelectedPrefecture(null);
      setSelectedCantons([]);
      setShowTeamAlert(false);
      setHasTeam(null);
      setTeamMembers(Array(7).fill(null).map(() => ({ nom: '', prenom: '', telephone: '' })));
      setTypeAnnonce('INDIVIDUELLE');
      fetchData();
    } catch (err: any) {
      showError('Erreur', err?.response?.data?.detail || err?.response?.data?.error || "Impossible de créer l'annonce");
    } finally {
      setIsSubmitting(false);
    }
  };

  const tabBtn = (active: boolean): React.CSSProperties => ({
    padding: '0.75rem 1.5rem', borderRadius: '12px', border: 'none',
    background: active ? 'white' : 'rgba(255,255,255,0.15)',
    color: active ? accentColor : 'white', fontWeight: 700,
    cursor: 'pointer', fontSize: '0.9rem', transition: 'all 0.2s',
  });

  return (
    <div style={{ minHeight: '100vh', background: 'var(--bg)', padding: '2rem 1.5rem' }}>
      <div style={{ maxWidth: '1100px', margin: '0 auto' }}>
        <div style={{ position: 'fixed', top: '80px', right: '20px', zIndex: 9999, display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
          {toasts.map(t => <Toast key={t.id} {...t} onClose={removeToast} />)}
        </div>

        {/* Hero */}
        <div style={{ background: heroBg, padding: '2.5rem 2rem', borderRadius: '20px', color: 'white', marginBottom: '2rem' }}>
          <h1 style={{ fontSize: '2.25rem', fontWeight: 800, margin: '0 0 0.4rem' }}>Emploi Saisonnier</h1>
          <p style={{ opacity: 0.9, fontSize: '1rem', maxWidth: '560px', margin: '0 0 2rem' }}>
            {isOuvrier
              ? 'Trouvez des opportunités de travail dans les fermes près de chez vous.'
              : "Recrutez de la main-d'œuvre qualifiée pour vos travaux saisonniers."}
          </p>

          {/* Profile incomplete banner */}
          {isExploitant && eligibilite && !eligibilite.profil_complet && (
            <div style={{ background: 'rgba(239,68,68,0.15)', borderRadius: '12px', padding: '0.8rem 1rem', marginBottom: '1.25rem', fontSize: '0.85rem', lineHeight: 1.5, display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <span>⚠️ <span style={{ fontWeight: 700 }}>Profil incomplet :</span> Renseignez la localisation et la superficie de votre exploitation pour publier des offres.</span>
              <button onClick={() => window.location.href = '/me'}
                style={{ padding: '0.5rem 1rem', borderRadius: '8px', border: 'none', background: 'white', color: '#dc2626', fontWeight: 700, cursor: 'pointer', fontSize: '0.82rem', whiteSpace: 'nowrap', marginLeft: '1rem' }}>
                Compléter mon profil
              </button>
            </div>
          )}

          {/* Eligibility banner for exploitants */}
          {isExploitant && eligibilite && eligibilite.profil_complet && !eligibilite.peut_publier_directement && (
            <div style={{ background: 'rgba(255,255,255,0.12)', borderRadius: '12px', padding: '0.8rem 1rem', marginBottom: '1.25rem', fontSize: '0.85rem', lineHeight: 1.5 }}>
              <span style={{ fontWeight: 700 }}>ℹ️ Votre exploitation :</span> {parseFloat(eligibilite.superficie).toFixed(1)} ha
              {!eligibilite.verifie && ' · Non vérifiée'}
              <br />
              Pour publier directement, il faut ≥ {eligibilite.seuil} ha et être vérifié.
              Sinon, créez une <span style={{ fontWeight: 700 }}>annonce collective</span> pour regrouper les exploitants de votre zone.
            </div>
          )}

          <div style={{ display: 'flex', gap: '0.75rem', flexWrap: 'wrap' }}>
            <button onClick={() => setActiveTab('available')} style={tabBtn(activeTab === 'available')}>Offres disponibles</button>
            {isExploitant && <button onClick={() => setActiveTab('annonces')} style={tabBtn(activeTab === 'annonces')}>Annonces collectives</button>}
            {isExploitant && <button onClick={() => setActiveTab('my_offers')} style={tabBtn(activeTab === 'my_offers')}>Mes offres</button>}
            <button onClick={() => setActiveTab('annonces_ouvriers')} style={tabBtn(activeTab === 'annonces_ouvriers')}>
              {isOuvrier ? 'Mes annonces' : 'Ouvriers disponibles'}
            </button>
            {(isOuvrier || isExploitant) && <button onClick={() => setActiveTab('contracts')} style={tabBtn(activeTab === 'contracts')}>Mes contrats</button>}
          </div>
        </div>

        {/* Toolbar */}
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.5rem', flexWrap: 'wrap', gap: '1rem' }}>
          {activeTab === 'available' && (
            <div style={{ display: 'flex', gap: '0.75rem', alignItems: 'center' }}>
              <span style={{ fontWeight: 600, color: 'var(--text-secondary)', fontSize: '0.9rem' }}>Filtrer :</span>
              <select value={filterType} onChange={e => setFilterType(e.target.value)}
                style={{ padding: '0.5rem 0.75rem', borderRadius: '8px', border: '1px solid var(--border)', background: 'var(--surface)', color: 'var(--text)', fontSize: '0.9rem' }}>
                <option value="">Tous les types</option>
                {JOB_TYPES.map(t => <option key={t} value={t}>{t}</option>)}
              </select>
            </div>
          )}
          {isExploitant && (activeTab === 'available' || activeTab === 'my_offers' || activeTab === 'annonces') && (
            <button onClick={handlePublish}
              style={{ display: 'flex', alignItems: 'center', gap: '8px', padding: '0.75rem 1.5rem', borderRadius: '12px', border: 'none', background: eligibilite?.peut_publier_directement ? accentColor : '#7c3aed', color: 'white', fontWeight: 700, cursor: 'pointer', fontSize: '0.95rem' }}>
              <IconPlus /> {eligibilite?.peut_publier_directement ? 'Publier une offre' : 'Créer une annonce collective'}
            </button>
          )}
          {isOuvrier && activeTab === 'annonces_ouvriers' && (
            <button onClick={() => setShowModal('annonce_ouvrier')}
              style={{ display: 'flex', alignItems: 'center', gap: '8px', padding: '0.75rem 1.5rem', borderRadius: '12px', border: 'none', background: accentColor, color: 'white', fontWeight: 700, cursor: 'pointer', fontSize: '0.95rem' }}>
              <IconPlus /> Proposer ma disponibilité
            </button>
          )}
        </div>

        {/* Content */}
        {loading ? (
          <div style={{ textAlign: 'center', padding: '4rem', color: 'var(--text-secondary)' }}>Chargement...</div>
        ) : activeTab === 'annonces' ? (
          annonces.length === 0 ? (
            <div style={{ textAlign: 'center', padding: '4rem', color: 'var(--text-secondary)', background: 'var(--surface)', borderRadius: '16px', border: '1px solid var(--border)' }}>
              <p style={{ fontSize: '1.1rem', margin: '0 0 0.5rem' }}>Aucune annonce collective en cours.</p>
              <p style={{ fontSize: '0.9rem', margin: 0, opacity: 0.7 }}>Créez-en une pour regrouper les exploitants de votre zone.</p>
            </div>
          ) : (
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(320px, 1fr))', gap: '1.5rem' }}>
              {annonces.map(a => <AnnonceCard key={a.id} annonce={a} isExploitant={isExploitant} onRejoindre={handleRejoindre} />)}
            </div>
          )
        ) : activeTab === 'annonces_ouvriers' ? (
          annoncesOuvriers.length === 0 ? (
            <div style={{ textAlign: 'center', padding: '4rem', color: 'var(--text-secondary)', background: 'var(--surface)', borderRadius: '16px', border: '1px solid var(--border)' }}>
              <p style={{ fontSize: '1.1rem', margin: '0 0 0.5rem' }}>
                {isOuvrier ? 'Vous n\'avez pas encore créé d\'annonce.' : 'Aucun ouvrier disponible dans votre zone.'}
              </p>
              {isOuvrier && (
                <p style={{ fontSize: '0.9rem', margin: 0, opacity: 0.7 }}>Proposez votre disponibilité aux exploitants de votre zone.</p>
              )}
            </div>
          ) : (
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(320px, 1fr))', gap: '1.5rem' }}>
              {annoncesOuvriers.map(annonce => (
                <motion.div key={annonce.id} layout initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }}
                  style={{ background: 'var(--surface)', border: '1px solid var(--border)', borderRadius: '16px', padding: '1.5rem', display: 'flex', flexDirection: 'column', gap: '1rem' }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
                    <span style={{ background: `${accentColor}18`, color: accentColor, padding: '4px 12px', borderRadius: '20px', fontSize: '0.78rem', fontWeight: 700 }}>
                      {annonce.statut === 'ACTIVE' ? '✓ Disponible' : 'Inactive'}
                    </span>
                    <span style={{ fontSize: '1.1rem', fontWeight: 800, color: accentColor }}>
                      {parseInt(annonce.tarif_horaire_min).toLocaleString()} FCFA/h
                    </span>
                  </div>
                  <div>
                    <h3 style={{ margin: '0 0 0.4rem', fontSize: '1.1rem', fontWeight: 700 }}>{annonce.titre}</h3>
                    <p style={{ margin: 0, color: 'var(--text-secondary)', fontSize: '0.9rem', lineHeight: 1.5 }}>{annonce.description}</p>
                  </div>
                  <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.5rem' }}>
                    {annonce.competences.map((comp, i) => (
                      <span key={i} style={{ background: 'var(--bg)', padding: '4px 10px', borderRadius: '12px', fontSize: '0.8rem', fontWeight: 600 }}>
                        {comp}
                      </span>
                    ))}
                  </div>
                  <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem', fontSize: '0.85rem', color: 'var(--text-secondary)' }}>
                    <span style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
                      <IconMapPin /> {annonce.cantons_noms.join(', ')}
                    </span>
                    <span style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
                      <IconCalendar /> Dispo: {new Date(annonce.date_disponibilite_debut).toLocaleDateString()}
                      {annonce.date_disponibilite_fin && ` — ${new Date(annonce.date_disponibilite_fin).toLocaleDateString()}`}
                    </span>
                  </div>
                  {isExploitant && annonce.statut === 'ACTIVE' && (
                    <button onClick={() => window.location.href = '/messaging'}
                      style={{ padding: '0.75rem', borderRadius: '10px', border: 'none', background: accentColor, color: 'white', fontWeight: 700, cursor: 'pointer', fontSize: '0.95rem' }}>
                      Contacter
                    </button>
                  )}
                  {isOuvrier && (
                    <div style={{ display: 'flex', gap: '0.5rem', paddingTop: '0.5rem', borderTop: '1px solid var(--border)' }}>
                      <button onClick={() => annonce.statut === 'ACTIVE' ? desactiverAnnonceOuvrier(annonce.id).then(fetchData) : null}
                        style={{ flex: 1, padding: '0.5rem', borderRadius: '8px', border: '1px solid var(--border)', background: 'transparent', color: 'var(--text)', fontWeight: 600, cursor: 'pointer', fontSize: '0.85rem' }}>
                        {annonce.statut === 'ACTIVE' ? 'Désactiver' : 'Inactive'}
                      </button>
                    </div>
                  )}
                </motion.div>
              ))}
            </div>
          )
        ) : activeTab === 'contracts' ? (
          contrats.length === 0 ? (
            <div style={{ textAlign: 'center', padding: '4rem', color: 'var(--text-secondary)', background: 'var(--surface)', borderRadius: '16px', border: '1px solid var(--border)' }}>
              <p style={{ fontSize: '1.1rem', margin: 0 }}>Vous n'avez aucun contrat actif.</p>
            </div>
          ) : (
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(300px, 1fr))', gap: '1.5rem' }}>
              {contrats.map(contrat => (
                <motion.div key={contrat.id} layout initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }}
                  style={{ background: 'var(--surface)', border: '1px solid var(--border)', borderRadius: '16px', padding: '1.5rem' }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1rem' }}>
                    <span style={{ background: 'var(--bg)', padding: '4px 12px', borderRadius: '20px', fontSize: '0.78rem', fontWeight: 600 }}>#{contrat.id}</span>
                    <span style={{ color: contrat.statut === 'SIGNE' ? '#059669' : '#2563eb', fontWeight: 700, fontSize: '0.85rem' }}>{contrat.statut}</span>
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
        ) : (
          offres.length === 0 ? (
            <div style={{ textAlign: 'center', padding: '4rem', color: 'var(--text-secondary)', background: 'var(--surface)', borderRadius: '16px', border: '1px solid var(--border)' }}>
              <p style={{ fontSize: '1.1rem', margin: 0 }}>Aucune offre d'emploi disponible pour le moment.</p>
            </div>
          ) : (
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(300px, 1fr))', gap: '1.5rem' }}>
              {offres.map(offre => (
                <motion.div key={offre.id} layout initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }}
                  style={{ background: 'var(--surface)', border: '1px solid var(--border)', borderRadius: '16px', padding: '1.5rem', display: 'flex', flexDirection: 'column', gap: '1rem' }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
                    <div style={{ display: 'flex', gap: '0.5rem', flexWrap: 'wrap' }}>
                      <span style={{ background: `${accentColor}18`, color: accentColor, padding: '4px 12px', borderRadius: '20px', fontSize: '0.78rem', fontWeight: 700 }}>{offre.type_travail}</span>
                      {offre.est_collective && <span style={{ background: '#7c3aed18', color: '#7c3aed', padding: '4px 10px', borderRadius: '20px', fontSize: '0.72rem', fontWeight: 600 }}>Collective</span>}
                    </div>
                    <span style={{ fontSize: '1.1rem', fontWeight: 800, color: accentColor }}>{parseInt(offre.salaire_horaire).toLocaleString()} FCFA/h</span>
                  </div>
                  <div>
                    <h3 style={{ margin: '0 0 0.4rem', fontSize: '1.1rem', fontWeight: 700 }}>{offre.type_travail} à {offre.canton_nom}</h3>
                    <p style={{ margin: 0, color: 'var(--text-secondary)', fontSize: '0.9rem', lineHeight: 1.5 }}>{offre.description}</p>
                  </div>
                  <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem', fontSize: '0.85rem', color: 'var(--text-secondary)' }}>
                    <span style={{ display: 'flex', alignItems: 'center', gap: '6px' }}><IconMapPin /> {offre.canton_nom}</span>
                    <span style={{ display: 'flex', alignItems: 'center', gap: '6px' }}><IconCalendar /> {new Date(offre.date_debut).toLocaleDateString()} — {new Date(offre.date_fin).toLocaleDateString()}</span>
                    <span style={{ display: 'flex', alignItems: 'center', gap: '6px' }}><IconBriefcase /> {offre.nombre_postes - offre.postes_pourvus} postes restants sur {offre.nombre_postes}</span>
                  </div>
                  {isOuvrier && (
                    <button onClick={() => handlePostuler(offre.id)} disabled={offre.postes_pourvus >= offre.nombre_postes}
                      style={{ padding: '0.75rem', borderRadius: '10px', border: 'none', background: offre.postes_pourvus >= offre.nombre_postes ? 'var(--border)' : accentColor, color: 'white', fontWeight: 700, cursor: offre.postes_pourvus >= offre.nombre_postes ? 'not-allowed' : 'pointer', fontSize: '0.95rem' }}>
                      Postuler maintenant
                    </button>
                  )}
                  {isExploitant && (
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', fontSize: '0.8rem', paddingTop: '0.5rem', borderTop: '1px solid var(--border)' }}>
                      <span style={{ color: 'var(--text-secondary)' }}>Publié le {new Date(offre.created_at).toLocaleDateString()}</span>
                      <span style={{ fontWeight: 700, color: offre.statut === 'OUVERTE' ? '#059669' : '#dc2626' }}>{offre.statut}</span>
                    </div>
                  )}
                </motion.div>
              ))}
            </div>
          )
        )}

        {/* ─── Modals ─── */}
        <AnimatePresence>
          {showModal === 'offre' && (
            <div style={{ position: 'fixed', inset: 0, background: 'rgba(0,0,0,0.55)', display: 'flex', alignItems: 'center', justifyContent: 'center', zIndex: 1000, padding: '1rem' }}>
              <motion.div initial={{ scale: 0.92, opacity: 0 }} animate={{ scale: 1, opacity: 1 }} exit={{ scale: 0.92, opacity: 0 }}
                style={{ background: 'var(--surface)', padding: '2rem', borderRadius: '20px', width: '100%', maxWidth: '520px', boxShadow: '0 25px 60px rgba(0,0,0,0.25)', maxHeight: '90vh', overflowY: 'auto' }}>
                <h2 style={{ margin: '0 0 1.5rem', fontSize: '1.4rem', fontWeight: 800 }}>Publier une offre directe</h2>
                <form onSubmit={handleCreateOffre}>
                  <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
                    <div><label style={labelStyle}>Type de travail</label><select name="type_travail" required style={inputStyle}>{JOB_TYPES.map(t => <option key={t} value={t}>{t}</option>)}</select></div>
                    <div><label style={labelStyle}>Description</label><textarea name="description" placeholder="Décrivez les tâches, conditions, etc." required rows={3} style={{ ...inputStyle, resize: 'vertical' }} /></div>
                    <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem' }}>
                      <div><label style={labelStyle}>Date début</label><input name="date_debut" type="date" required style={inputStyle} /></div>
                      <div><label style={labelStyle}>Date fin</label><input name="date_fin" type="date" required style={inputStyle} /></div>
                    </div>
                    <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem' }}>
                      <div><label style={labelStyle}>Salaire horaire (FCFA)</label><input name="salaire_horaire" type="number" required style={inputStyle} /></div>
                      <div><label style={labelStyle}>Nombre de postes</label><input name="nombre_postes" type="number" required style={inputStyle} /></div>
                    </div>
                    <div>
                      <label style={labelStyle}>Canton</label>
                      <input name="canton" type="hidden" value={eligibilite?.canton_id ?? ''} />
                      <div style={{ ...inputStyle, background: 'var(--bg)', opacity: 0.85, cursor: 'default' }}>
                        {eligibilite?.canton_nom || 'Non renseigné dans votre profil'}
                      </div>
                    </div>
                    <div style={{ display: 'flex', gap: '1rem', marginTop: '0.5rem' }}>
                      <button type="button" onClick={() => setShowModal(null)} style={{ flex: 1, padding: '0.75rem', borderRadius: '10px', border: '1px solid var(--border)', background: 'transparent', color: 'var(--text)', fontWeight: 600, cursor: 'pointer' }}>Annuler</button>
                      <button type="submit" disabled={isSubmitting} style={{ flex: 1, padding: '0.75rem', borderRadius: '10px', border: 'none', background: accentColor, color: 'white', fontWeight: 700, cursor: 'pointer', opacity: isSubmitting ? 0.7 : 1 }}>{isSubmitting ? 'Publication...' : 'Publier'}</button>
                    </div>
                  </div>
                </form>
              </motion.div>
            </div>
          )}

          {showModal === 'annonce' && (
            <div style={{ position: 'fixed', inset: 0, background: 'rgba(0,0,0,0.55)', display: 'flex', alignItems: 'center', justifyContent: 'center', zIndex: 1000, padding: '1rem' }}>
              <motion.div initial={{ scale: 0.92, opacity: 0 }} animate={{ scale: 1, opacity: 1 }} exit={{ scale: 0.92, opacity: 0 }}
                style={{ background: 'var(--surface)', padding: '2rem', borderRadius: '20px', width: '100%', maxWidth: '520px', boxShadow: '0 25px 60px rgba(0,0,0,0.25)', maxHeight: '90vh', overflowY: 'auto' }}>
                <h2 style={{ margin: '0 0 0.5rem', fontSize: '1.4rem', fontWeight: 800 }}>Créer une annonce collective</h2>
                <p style={{ color: 'var(--text-secondary)', fontSize: '0.88rem', margin: '0 0 1.5rem', lineHeight: 1.5 }}>
                  Votre superficie ({eligibilite ? parseFloat(eligibilite.superficie).toFixed(1) : '?'} ha) sera ajoutée automatiquement.
                  Les exploitants de votre zone ont <span style={{ fontWeight: 700, color: '#7c3aed' }}>2 jours</span> pour rejoindre et atteindre le seuil de 10 ha.
                  Si le quota n'est pas atteint, l'annonce expire automatiquement.
                </p>
                <form onSubmit={handleCreateAnnonce}>
                  <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
                    <div><label style={labelStyle}>Type de travail</label><select name="type_travail" required style={inputStyle}>{JOB_TYPES.map(t => <option key={t} value={t}>{t}</option>)}</select></div>
                    <div><label style={labelStyle}>Description</label><textarea name="description" placeholder="Décrivez les travaux nécessaires..." required rows={3} style={{ ...inputStyle, resize: 'vertical' }} /></div>
                    <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem' }}>
                      <div><label style={labelStyle}>Date début</label><input name="date_debut" type="date" required style={inputStyle} /></div>
                      <div><label style={labelStyle}>Date fin</label><input name="date_fin" type="date" required style={inputStyle} /></div>
                    </div>
                    <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem' }}>
                      <div><label style={labelStyle}>Salaire horaire (FCFA)</label><input name="salaire_horaire" type="number" required style={inputStyle} /></div>
                      <div><label style={labelStyle}>Nombre de postes</label><input name="nombre_postes" type="number" required style={inputStyle} /></div>
                    </div>
                    <div>
                      <label style={labelStyle}>Canton</label>
                      <input name="canton" type="hidden" value={eligibilite?.canton_id ?? ''} />
                      <div style={{ ...inputStyle, background: 'var(--bg)', opacity: 0.85, cursor: 'default' }}>
                        {eligibilite?.canton_nom || 'Non renseigné dans votre profil'}
                      </div>
                    </div>
                    <div style={{ display: 'flex', gap: '1rem', marginTop: '0.5rem' }}>
                      <button type="button" onClick={() => setShowModal(null)} style={{ flex: 1, padding: '0.75rem', borderRadius: '10px', border: '1px solid var(--border)', background: 'transparent', color: 'var(--text)', fontWeight: 600, cursor: 'pointer' }}>Annuler</button>
                      <button type="submit" disabled={isSubmitting} style={{ flex: 1, padding: '0.75rem', borderRadius: '10px', border: 'none', background: '#7c3aed', color: 'white', fontWeight: 700, cursor: 'pointer', opacity: isSubmitting ? 0.7 : 1 }}>{isSubmitting ? 'Création...' : 'Créer l\'annonce'}</button>
                    </div>
                  </div>
                </form>
              </motion.div>
            </div>
          )}

          {showModal === 'annonce_ouvrier' && (
            <AnnonceOuvrierModal
              onClose={() => {
                setShowModal(null);
                setHasTeam(null);
                setSelectedCompetences([]);
                setSelectedRegion(null);
                setSelectedPrefecture(null);
                setSelectedCantons([]);
                setTeamMembers(Array(7).fill(null).map(() => ({ nom: '', prenom: '', telephone: '' })));
              }}
              onSubmit={handleCreateAnnonceOuvrier}
              isSubmitting={isSubmitting}
              accentColor={accentColor}
              regions={regions}
              prefectures={prefectures}
              cantons={cantons}
              selectedRegion={selectedRegion}
              setSelectedRegion={setSelectedRegion}
              selectedPrefecture={selectedPrefecture}
              setSelectedPrefecture={setSelectedPrefecture}
              selectedCompetences={selectedCompetences}
              setSelectedCompetences={setSelectedCompetences}
              selectedCantons={selectedCantons}
              setSelectedCantons={setSelectedCantons}
              hasTeam={hasTeam}
              setHasTeam={setHasTeam}
              teamMembers={teamMembers}
              setTeamMembers={setTeamMembers}
              typeAnnonce={typeAnnonce}
              setTypeAnnonce={setTypeAnnonce}
            />
          )}
        </AnimatePresence>
      </div>
    </div>
  );
}
