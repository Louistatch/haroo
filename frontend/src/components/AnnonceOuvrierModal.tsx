import { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { Region, Prefecture, Canton } from '../api/locations';
import { MembreEquipe } from '../api/jobs';

const COMPETENCES_OPTIONS = ['Récolte', 'Semis', 'Désherbage', 'Irrigation', 'Taille', 'Entretien', 'Labour', 'Traitement', 'Autre'];

const inputStyle: React.CSSProperties = {
  width: '100%', padding: '0.75rem', borderRadius: '10px',
  border: '1px solid var(--border)', background: 'var(--bg)',
  color: 'var(--text)', fontSize: '0.95rem', boxSizing: 'border-box',
};

const labelStyle: React.CSSProperties = {
  display: 'block', marginBottom: '0.4rem', fontSize: '0.875rem', fontWeight: 600, color: 'var(--text)',
};

interface Props {
  onClose: () => void;
  onSubmit: (e: React.FormEvent<HTMLFormElement>) => void;
  isSubmitting: boolean;
  accentColor: string;
  regions: Region[];
  prefectures: Prefecture[];
  cantons: Canton[];
  selectedRegion: number | null;
  setSelectedRegion: (id: number | null) => void;
  selectedPrefecture: number | null;
  setSelectedPrefecture: (id: number | null) => void;
  selectedCompetences: string[];
  setSelectedCompetences: (comps: string[]) => void;
  selectedCantons: number[];
  setSelectedCantons: (cantons: number[]) => void;
  hasTeam: boolean | null;
  setHasTeam: (has: boolean | null) => void;
  teamMembers: MembreEquipe[];
  setTeamMembers: (members: MembreEquipe[]) => void;
  typeAnnonce: 'INDIVIDUELLE' | 'COLLECTIVE';
  setTypeAnnonce: (type: 'INDIVIDUELLE' | 'COLLECTIVE') => void;
}

export default function AnnonceOuvrierModal({
  onClose, onSubmit, isSubmitting, accentColor,
  regions, prefectures, cantons,
  selectedRegion, setSelectedRegion,
  selectedPrefecture, setSelectedPrefecture,
  selectedCompetences, setSelectedCompetences,
  selectedCantons, setSelectedCantons,
  hasTeam, setHasTeam,
  teamMembers, setTeamMembers,
  typeAnnonce, setTypeAnnonce
}: Props) {
  const [showTeamAlert, setShowTeamAlert] = useState(false);

  const updateTeamMember = (index: number, field: keyof MembreEquipe, value: string) => {
    const newMembers = [...teamMembers];
    newMembers[index] = { ...newMembers[index], [field]: value };
    setTeamMembers(newMembers);
  };

  const isTeamComplete = teamMembers.every(m => m.nom && m.prenom && m.telephone);
  const canSubmit = selectedCompetences.length > 0 && selectedCantons.length > 0 && selectedRegion && selectedPrefecture &&
    (hasTeam === null || (hasTeam === false) || (hasTeam === true && isTeamComplete));

  useEffect(() => {
    if (hasTeam === true) {
      setTypeAnnonce('INDIVIDUELLE');
    } else if (hasTeam === false) {
      setTypeAnnonce('COLLECTIVE');
    }
  }, [hasTeam, setTypeAnnonce]);

  return (
    <div style={{ position: 'fixed', inset: 0, background: 'rgba(0,0,0,0.55)', display: 'flex', alignItems: 'center', justifyContent: 'center', zIndex: 1000, padding: '1rem' }}>
      <motion.div initial={{ scale: 0.92, opacity: 0 }} animate={{ scale: 1, opacity: 1 }} exit={{ scale: 0.92, opacity: 0 }}
        style={{ background: 'var(--surface)', padding: '2rem', borderRadius: '20px', width: '100%', maxWidth: '700px', boxShadow: '0 25px 60px rgba(0,0,0,0.25)', maxHeight: '90vh', overflowY: 'auto' }}>
        <h2 style={{ margin: '0 0 0.5rem', fontSize: '1.4rem', fontWeight: 800 }}>Proposer ma disponibilité</h2>
        <p style={{ color: 'var(--text-secondary)', fontSize: '0.88rem', margin: '0 0 1.5rem', lineHeight: 1.5 }}>
          Créez une annonce pour proposer vos services aux exploitants de votre zone.
        </p>

        {/* Alerte équipe de 8 personnes */}
        {showTeamAlert && (
          <div style={{ background: '#fef3c7', border: '1px solid #fbbf24', borderRadius: '12px', padding: '1rem', marginBottom: '1.5rem' }}>
            <h3 style={{ margin: '0 0 0.5rem', fontSize: '1rem', fontWeight: 700, color: '#92400e' }}>
              ⚠️ Information importante
            </h3>
            <p style={{ margin: '0 0 0.5rem', fontSize: '0.88rem', color: '#78350f', lineHeight: 1.5 }}>
              Pour travailler 1 hectare, vous devez former une équipe de <strong>8 personnes</strong> (vous + 7 autres ouvriers).
            </p>
            <ul style={{ margin: '0.5rem 0 0', paddingLeft: '1.5rem', fontSize: '0.85rem', color: '#78350f', lineHeight: 1.6 }}>
              <li>Durée de travail : <strong>8 heures</strong></li>
              <li>Tarif : <strong>1000 FCFA/heure</strong></li>
              <li>Commission plateforme : <strong>20%</strong></li>
              <li>Rémunération par personne : <strong>{((1000 * 0.8 * 8) / 8).toLocaleString()} FCFA/jour</strong></li>
              <li>Vous travaillerez sous la supervision d'un guide</li>
            </ul>
            <button 
              type="button"
              onClick={() => setShowTeamAlert(false)}
              style={{ marginTop: '0.75rem', padding: '0.5rem 1rem', borderRadius: '8px', border: 'none', background: '#fbbf24', color: '#78350f', fontWeight: 600, cursor: 'pointer', fontSize: '0.85rem' }}>
              J'ai compris
            </button>
          </div>
        )}

        <form onSubmit={onSubmit}>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
            <div>
              <label style={labelStyle}>Titre de l'annonce</label>
              <input name="titre" type="text" required placeholder="Ex: Ouvrier expérimenté disponible" style={inputStyle} />
            </div>

            <div>
              <label style={labelStyle}>Description</label>
              <textarea name="description" placeholder="Décrivez votre expérience et vos compétences..." required rows={3} style={{ ...inputStyle, resize: 'vertical' }} />
            </div>

            <div>
              <label style={labelStyle}>Compétences (sélection multiple)</label>
              <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.5rem', padding: '0.75rem', borderRadius: '10px', border: '1px solid var(--border)', background: 'var(--bg)' }}>
                {COMPETENCES_OPTIONS.map(comp => (
                  <label key={comp} style={{ display: 'flex', alignItems: 'center', gap: '0.4rem', padding: '0.4rem 0.75rem', borderRadius: '8px', background: selectedCompetences.includes(comp) ? accentColor : 'var(--surface)', color: selectedCompetences.includes(comp) ? 'white' : 'var(--text)', cursor: 'pointer', fontSize: '0.85rem', fontWeight: 600, border: '1px solid var(--border)', transition: 'all 0.2s' }}>
                    <input 
                      type="checkbox" 
                      checked={selectedCompetences.includes(comp)}
                      onChange={(e) => {
                        if (e.target.checked) {
                          setSelectedCompetences([...selectedCompetences, comp]);
                        } else {
                          setSelectedCompetences(selectedCompetences.filter(c => c !== comp));
                        }
                      }}
                      style={{ display: 'none' }}
                    />
                    {comp}
                  </label>
                ))}
              </div>
              {selectedCompetences.length === 0 && (
                <p style={{ margin: '0.3rem 0 0', fontSize: '0.8rem', color: '#dc2626' }}>Sélectionnez au moins une compétence</p>
              )}
            </div>

            <div>
              <label style={labelStyle}>Région</label>
              <select 
                value={selectedRegion || ''} 
                onChange={(e) => setSelectedRegion(e.target.value ? Number(e.target.value) : null)}
                required
                style={inputStyle}>
                <option value="">Sélectionnez une région</option>
                {regions.map(r => <option key={r.id} value={r.id}>{r.nom}</option>)}
              </select>
            </div>

            {selectedRegion && (
              <div>
                <label style={labelStyle}>Préfecture</label>
                <select 
                  value={selectedPrefecture || ''} 
                  onChange={(e) => setSelectedPrefecture(e.target.value ? Number(e.target.value) : null)}
                  required
                  style={inputStyle}>
                  <option value="">Sélectionnez une préfecture</option>
                  {prefectures.map(p => <option key={p.id} value={p.id}>{p.nom}</option>)}
                </select>
              </div>
            )}

            {selectedPrefecture && cantons.length > 0 && (
              <div>
                <label style={labelStyle}>Cantons disponibles (sélection multiple)</label>
                <div style={{ maxHeight: '150px', overflowY: 'auto', padding: '0.75rem', borderRadius: '10px', border: '1px solid var(--border)', background: 'var(--bg)' }}>
                  {cantons.map(canton => (
                    <label key={canton.id} style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', padding: '0.5rem', cursor: 'pointer', borderRadius: '6px', transition: 'background 0.2s' }}>
                      <input 
                        type="checkbox" 
                        checked={selectedCantons.includes(canton.id)}
                        onChange={(e) => {
                          if (e.target.checked) {
                            setSelectedCantons([...selectedCantons, canton.id]);
                          } else {
                            setSelectedCantons(selectedCantons.filter(c => c !== canton.id));
                          }
                        }}
                        style={{ width: '16px', height: '16px', cursor: 'pointer' }}
                      />
                      <span style={{ fontSize: '0.9rem' }}>{canton.nom}</span>
                    </label>
                  ))}
                </div>
                {selectedCantons.length === 0 && (
                  <p style={{ margin: '0.3rem 0 0', fontSize: '0.8rem', color: '#dc2626' }}>Sélectionnez au moins un canton</p>
                )}
              </div>
            )}

            {/* Question sur l'équipe */}
            {selectedCantons.length > 0 && hasTeam === null && (
              <div style={{ background: '#eff6ff', border: '1px solid #3b82f6', borderRadius: '12px', padding: '1.5rem' }}>
                <h3 style={{ margin: '0 0 0.75rem', fontSize: '1rem', fontWeight: 700, color: '#1e40af' }}>
                  Avez-vous déjà une équipe de 7 autres ouvriers ?
                </h3>
                <p style={{ margin: '0 0 1rem', fontSize: '0.85rem', color: '#1e3a8a', lineHeight: 1.5 }}>
                  Pour travailler 1 hectare, vous devez être 8 personnes au total.
                </p>
                <div style={{ display: 'flex', gap: '1rem' }}>
                  <button 
                    type="button"
                    onClick={() => setHasTeam(true)}
                    style={{ flex: 1, padding: '0.75rem', borderRadius: '10px', border: '1px solid #3b82f6', background: '#3b82f6', color: 'white', fontWeight: 700, cursor: 'pointer' }}>
                    Oui, j'ai mon équipe
                  </button>
                  <button 
                    type="button"
                    onClick={() => setHasTeam(false)}
                    style={{ flex: 1, padding: '0.75rem', borderRadius: '10px', border: '1px solid #3b82f6', background: 'white', color: '#3b82f6', fontWeight: 700, cursor: 'pointer' }}>
                    Non, je cherche une équipe
                  </button>
                </div>
              </div>
            )}

            {/* Formulaire des 7 membres */}
            {hasTeam === true && (
              <div style={{ background: '#f0fdf4', border: '1px solid #16a34a', borderRadius: '12px', padding: '1.5rem' }}>
                <h3 style={{ margin: '0 0 0.5rem', fontSize: '1rem', fontWeight: 700, color: '#15803d' }}>
                  Informations des 7 membres de votre équipe
                </h3>
                <p style={{ margin: '0 0 1rem', fontSize: '0.85rem', color: '#166534', lineHeight: 1.5 }}>
                  Renseignez le nom, prénom et téléphone de chaque membre.
                </p>
                <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
                  {teamMembers.map((membre, idx) => (
                    <div key={idx} style={{ background: 'white', padding: '1rem', borderRadius: '10px', border: '1px solid #bbf7d0' }}>
                      <h4 style={{ margin: '0 0 0.75rem', fontSize: '0.9rem', fontWeight: 700, color: '#15803d' }}>Membre {idx + 1}</h4>
                      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr 1fr', gap: '0.75rem' }}>
                        <input 
                          type="text" 
                          placeholder="Nom" 
                          value={membre.nom}
                          onChange={(e) => updateTeamMember(idx, 'nom', e.target.value)}
                          required
                          style={{ ...inputStyle, fontSize: '0.85rem', padding: '0.6rem' }} 
                        />
                        <input 
                          type="text" 
                          placeholder="Prénom" 
                          value={membre.prenom}
                          onChange={(e) => updateTeamMember(idx, 'prenom', e.target.value)}
                          required
                          style={{ ...inputStyle, fontSize: '0.85rem', padding: '0.6rem' }} 
                        />
                        <input 
                          type="tel" 
                          placeholder="Téléphone" 
                          value={membre.telephone}
                          onChange={(e) => updateTeamMember(idx, 'telephone', e.target.value)}
                          required
                          style={{ ...inputStyle, fontSize: '0.85rem', padding: '0.6rem' }} 
                        />
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Annonce collective */}
            {hasTeam === false && (
              <div style={{ background: '#fef3c7', border: '1px solid #f59e0b', borderRadius: '12px', padding: '1.5rem' }}>
                <h3 style={{ margin: '0 0 0.5rem', fontSize: '1rem', fontWeight: 700, color: '#92400e' }}>
                  Annonce collective de recrutement
                </h3>
                <p style={{ margin: '0', fontSize: '0.85rem', color: '#78350f', lineHeight: 1.5 }}>
                  Votre annonce sera publiée comme une <strong>annonce collective</strong>. Les autres ouvriers auront <strong>2 jours</strong> pour rejoindre votre équipe. 
                  Une fois 8 personnes réunies, l'annonce sera visible par les exploitants, agronomes et institutions.
                </p>
              </div>
            )}

            <div>
              <label style={labelStyle}>Tarif horaire</label>
              <div style={{ ...inputStyle, background: 'var(--bg)', opacity: 0.85, cursor: 'default', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <span>1000 FCFA/heure</span>
                <span style={{ fontSize: '0.8rem', color: 'var(--text-secondary)' }}>(Commission 20% déduite)</span>
              </div>
              <p style={{ margin: '0.5rem 0 0', fontSize: '0.82rem', color: 'var(--text-secondary)', lineHeight: 1.5 }}>
                💡 Tarif fixe : 1000 FCFA/h. Après commission (20%), vous recevrez <strong>800 FCFA/h</strong>. 
                En équipe de 8 pour 8h de travail, chaque personne gagne <strong>{((1000 * 0.8 * 8) / 8).toLocaleString()} FCFA/jour</strong>.
              </p>
              <button 
                type="button"
                onClick={() => setShowTeamAlert(true)}
                style={{ marginTop: '0.5rem', padding: '0.5rem 1rem', borderRadius: '8px', border: '1px solid var(--border)', background: 'transparent', color: accentColor, fontWeight: 600, cursor: 'pointer', fontSize: '0.85rem' }}>
                ℹ️ Voir les détails de l'équipe
              </button>
            </div>

            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem' }}>
              <div>
                <label style={labelStyle}>Disponible à partir du</label>
                <input name="date_disponibilite_debut" type="date" required style={inputStyle} />
              </div>
              <div>
                <label style={labelStyle}>Jusqu'au (optionnel)</label>
                <input name="date_disponibilite_fin" type="date" style={inputStyle} />
              </div>
            </div>

            <div style={{ display: 'flex', gap: '1rem', marginTop: '0.5rem' }}>
              <button type="button" onClick={onClose} style={{ flex: 1, padding: '0.75rem', borderRadius: '10px', border: '1px solid var(--border)', background: 'transparent', color: 'var(--text)', fontWeight: 600, cursor: 'pointer' }}>Annuler</button>
              <button 
                type="submit" 
                disabled={isSubmitting || !canSubmit} 
                style={{ flex: 1, padding: '0.75rem', borderRadius: '10px', border: 'none', background: accentColor, color: 'white', fontWeight: 700, cursor: 'pointer', opacity: (isSubmitting || !canSubmit) ? 0.5 : 1 }}>
                {isSubmitting ? 'Création...' : 'Publier'}
              </button>
            </div>
          </div>
        </form>
      </motion.div>
    </div>
  );
}
