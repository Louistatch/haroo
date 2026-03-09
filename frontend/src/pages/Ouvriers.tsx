import { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { getAnnoncesOuvriers, AnnonceOuvrier } from '../api/jobs';
import { useToast } from '../hooks/useToast';
import Toast from '../components/Toast';

const IconUsers = () => (
  <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <path d="M17 21v-2a4 4 0 00-4-4H5a4 4 0 00-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M23 21v-2a4 4 0 00-3-3.87"/><path d="M16 3.13a4 4 0 010 7.75"/>
  </svg>
);

const IconCalendar = () => (
  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <rect x="3" y="4" width="18" height="18" rx="2" ry="2"/><line x1="16" y1="2" x2="16" y2="6"/><line x1="8" y1="2" x2="8" y2="6"/><line x1="3" y1="10" x2="21" y2="10"/>
  </svg>
);

const IconMapPin = () => (
  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
    <path d="M21 10c0 7-9 13-9 13s-9-6-9-13a9 9 0 0118 0z"/><circle cx="12" cy="10" r="3"/>
  </svg>
);

export default function Ouvriers() {
  const [annonces, setAnnonces] = useState<AnnonceOuvrier[]>([]);
  const [loading, setLoading] = useState(true);
  const [filterCompetence, setFilterCompetence] = useState('');
  const { toasts, removeToast, error: showError } = useToast();

  useEffect(() => {
    fetchAnnonces();
  }, []);

  const fetchAnnonces = async () => {
    setLoading(true);
    try {
      const data = await getAnnoncesOuvriers();
      // Filtrer uniquement les ouvriers avec compétences en récolte ou post-récolte
      const filtered = data.filter(a => 
        a.competences.some(c => 
          c.toLowerCase().includes('récolte') || 
          c.toLowerCase().includes('recolte')
        ) && (a.statut === 'ACTIVE' || a.statut === 'VALIDEE')
      );
      setAnnonces(filtered);
    } catch {
      showError('Erreur', 'Impossible de charger les annonces d\'ouvriers');
    } finally {
      setLoading(false);
    }
  };

  const filteredAnnonces = filterCompetence
    ? annonces.filter(a => a.competences.some(c => c.toLowerCase().includes(filterCompetence.toLowerCase())))
    : annonces;

  return (
    <div style={{ minHeight: '100vh', background: 'var(--bg)', paddingTop: '80px' }}>
      {toasts.map(toast => (
        <Toast key={toast.id} {...toast} onClose={() => removeToast(toast.id)} />
      ))}
      
      {/* Hero */}
      <div style={{ background: 'linear-gradient(135deg, #0369a1 0%, #0284c7 100%)', padding: '3rem 1.5rem', color: 'white' }}>
        <div style={{ maxWidth: '1200px', margin: '0 auto' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '1rem', marginBottom: '1rem' }}>
            <IconUsers />
            <h1 style={{ margin: 0, fontSize: '2rem', fontWeight: 800 }}>Ouvriers Disponibles</h1>
          </div>
          <p style={{ margin: 0, fontSize: '1.05rem', opacity: 0.95, maxWidth: '700px' }}>
            Trouvez des ouvriers qualifiés pour vos besoins en récolte et post-récolte.
          </p>
        </div>
      </div>

      {/* Contenu */}
      <div style={{ maxWidth: '1200px', margin: '0 auto', padding: '2rem 1.5rem' }}>
        {/* Filtres */}
        <div style={{ marginBottom: '2rem' }}>
          <label style={{ display: 'block', marginBottom: '0.5rem', fontSize: '0.9rem', fontWeight: 600, color: 'var(--text)' }}>
            Filtrer par compétence
          </label>
          <select 
            value={filterCompetence}
            onChange={(e) => setFilterCompetence(e.target.value)}
            style={{ padding: '0.75rem', borderRadius: '10px', border: '1px solid var(--border)', background: 'var(--surface)', color: 'var(--text)', fontSize: '0.95rem', minWidth: '250px' }}>
            <option value="">Toutes les compétences</option>
            <option value="récolte">Récolte</option>
            <option value="post">Post-récolte</option>
          </select>
        </div>

        {/* Liste des annonces */}
        {loading ? (
          <div style={{ textAlign: 'center', padding: '3rem', color: 'var(--text-secondary)' }}>
            Chargement...
          </div>
        ) : filteredAnnonces.length === 0 ? (
          <div style={{ textAlign: 'center', padding: '3rem' }}>
            <p style={{ color: 'var(--text-secondary)', fontSize: '1.05rem' }}>
              Aucun ouvrier disponible pour le moment.
            </p>
          </div>
        ) : (
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(350px, 1fr))', gap: '1.5rem' }}>
            {filteredAnnonces.map(annonce => (
              <motion.div
                key={annonce.id}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                style={{ background: 'var(--surface)', border: '1px solid var(--border)', borderRadius: '16px', padding: '1.5rem', display: 'flex', flexDirection: 'column', gap: '1rem' }}>
                
                {/* En-tête */}
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
                  <div>
                    <h3 style={{ margin: '0 0 0.3rem', fontSize: '1.1rem', fontWeight: 700 }}>
                      {annonce.titre}
                    </h3>
                    <p style={{ margin: 0, color: 'var(--text-secondary)', fontSize: '0.88rem' }}>
                      {annonce.ouvrier_nom}
                    </p>
                  </div>
                  {annonce.type_annonce === 'COLLECTIVE' && (
                    <span style={{ background: '#7c3aed18', color: '#7c3aed', padding: '4px 12px', borderRadius: '20px', fontSize: '0.75rem', fontWeight: 700 }}>
                      Équipe {annonce.nb_membres_actuels}/8
                    </span>
                  )}
                  {annonce.equipe_complete && (
                    <span style={{ background: '#dcfce7', color: '#16a34a', padding: '4px 12px', borderRadius: '20px', fontSize: '0.75rem', fontWeight: 700 }}>
                      ✓ Équipe complète
                    </span>
                  )}
                </div>

                {/* Description */}
                <p style={{ margin: 0, color: 'var(--text-secondary)', fontSize: '0.9rem', lineHeight: 1.5 }}>
                  {annonce.description}
                </p>

                {/* Compétences */}
                <div>
                  <p style={{ margin: '0 0 0.5rem', fontSize: '0.85rem', fontWeight: 600, color: 'var(--text-secondary)' }}>
                    Compétences :
                  </p>
                  <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.5rem' }}>
                    {annonce.competences.map((comp, idx) => (
                      <span key={idx} style={{ background: 'var(--bg)', padding: '4px 10px', borderRadius: '8px', fontSize: '0.8rem', fontWeight: 600, color: 'var(--text)' }}>
                        {comp}
                      </span>
                    ))}
                  </div>
                </div>

                {/* Infos */}
                <div style={{ display: 'flex', flexDirection: 'column', gap: '0.4rem', fontSize: '0.85rem', color: 'var(--text-secondary)' }}>
                  <span style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
                    <IconMapPin /> {annonce.cantons_noms.join(', ')}
                  </span>
                  <span style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
                    <IconCalendar /> Disponible du {new Date(annonce.date_disponibilite_debut).toLocaleDateString()}
                    {annonce.date_disponibilite_fin && ` au ${new Date(annonce.date_disponibilite_fin).toLocaleDateString()}`}
                  </span>
                  <span style={{ fontWeight: 700, color: '#0369a1' }}>
                    {parseInt(annonce.tarif_horaire_min).toLocaleString()} FCFA/h
                  </span>
                </div>

                {/* Bouton contact */}
                <button
                  onClick={() => window.location.href = `/messages?contact=${annonce.ouvrier}`}
                  style={{ padding: '0.75rem', borderRadius: '10px', border: 'none', background: '#0369a1', color: 'white', fontWeight: 700, cursor: 'pointer', fontSize: '0.95rem', marginTop: '0.5rem' }}>
                  Contacter
                </button>
              </motion.div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
