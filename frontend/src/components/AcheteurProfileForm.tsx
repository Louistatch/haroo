import { useState, useEffect } from 'react';
import { getRegions, getPrefectures, getCantons, Region, Prefecture, Canton } from '../api/locations';

const PRODUITS_OPTIONS = [
  'Maïs', 'Riz', 'Sorgho', 'Mil', 'Arachide', 'Soja', 'Niébé', 
  'Manioc', 'Igname', 'Patate douce', 'Tomate', 'Oignon', 'Piment',
  'Coton', 'Café', 'Cacao', 'Karité', 'Anacarde'
];

const inputStyle: React.CSSProperties = {
  width: '100%', padding: '0.75rem', borderRadius: '10px',
  border: '1px solid var(--border)', background: 'var(--bg)',
  color: 'var(--text)', fontSize: '0.95rem', boxSizing: 'border-box',
};

const labelStyle: React.CSSProperties = {
  display: 'block', marginBottom: '0.4rem', fontSize: '0.875rem', fontWeight: 600, color: 'var(--text)',
};

interface Props {
  profile: any;
  onSave: (data: any) => void;
  isSaving: boolean;
  saveError?: string;
  saveSuccess?: string;
}

export default function AcheteurProfileForm({ profile, onSave, isSaving, saveError, saveSuccess }: Props) {
  const [isEditing, setIsEditing] = useState(!profile?.profil_complet);
  const [telephone, setTelephone] = useState(profile?.telephone || '');
  const [regions, setRegions] = useState<Region[]>([]);
  const [prefectures, setPrefectures] = useState<Prefecture[]>([]);
  const [cantons, setCantons] = useState<Canton[]>([]);
  const [selectedRegion, setSelectedRegion] = useState<number | null>(profile?.region || null);
  const [selectedPrefecture, setSelectedPrefecture] = useState<number | null>(profile?.prefecture || null);
  const [selectedCanton, setSelectedCanton] = useState<number | null>(profile?.canton || null);
  const [selectedProduits, setSelectedProduits] = useState<string[]>(profile?.produits_interesses || []);
  const [localSuccess, setLocalSuccess] = useState<string>('');

  useEffect(() => {
    if (profile) {
      setTelephone(profile.telephone || '');
      setSelectedRegion(profile.region || null);
      setSelectedPrefecture(profile.prefecture || null);
      setSelectedCanton(profile.canton || null);
      setSelectedProduits(profile.produits_interesses || []);
      if (profile.profil_complet) {
        setIsEditing(false);
      }
    }
  }, [profile]);

  useEffect(() => {
    if (saveSuccess) {
      setLocalSuccess(saveSuccess);
      const timer = setTimeout(() => setLocalSuccess(''), 5000);
      return () => clearTimeout(timer);
    }
  }, [saveSuccess]);

  useEffect(() => {
    getRegions().then(setRegions).catch(() => {});
  }, []);

  useEffect(() => {
    if (selectedRegion) {
      getPrefectures(selectedRegion).then(setPrefectures).catch(() => {});
    } else {
      setPrefectures([]);
      setCantons([]);
    }
  }, [selectedRegion]);

  useEffect(() => {
    if (selectedPrefecture) {
      getCantons(selectedPrefecture).then(setCantons).catch(() => {});
    } else {
      setCantons([]);
    }
  }, [selectedPrefecture]);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    onSave({
      telephone,
      region: selectedRegion,
      prefecture: selectedPrefecture,
      canton: selectedCanton,
      produits_interesses: selectedProduits,
    });
  };

  const handleCancel = () => {
    if (profile) {
      setTelephone(profile.telephone || '');
      setSelectedRegion(profile.region || null);
      setSelectedPrefecture(profile.prefecture || null);
      setSelectedCanton(profile.canton || null);
      setSelectedProduits(profile.produits_interesses || []);
    }
    setIsEditing(false);
  };

  const isComplete = telephone && selectedRegion && selectedPrefecture && selectedCanton && selectedProduits.length > 0;
  const regionNom = regions.find(r => r.id === selectedRegion)?.nom || profile?.region_nom || '—';
  const prefectureNom = prefectures.find(p => p.id === selectedPrefecture)?.nom || profile?.prefecture_nom || '—';
  const cantonNom = cantons.find(c => c.id === selectedCanton)?.nom || profile?.canton_nom || '—';

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
      {!isEditing && profile?.profil_complet && (
        <div style={{ display: 'flex', justifyContent: 'flex-end', marginBottom: '-0.5rem' }}>
          <button 
            type="button"
            onClick={() => setIsEditing(true)}
            style={{ padding: '0.5rem 1rem', borderRadius: '8px', border: '1px solid var(--border)', background: 'var(--primary)', color: 'white', fontWeight: 600, fontSize: '0.85rem', cursor: 'pointer' }}>
            Modifier
          </button>
        </div>
      )}

      {!profile?.profil_complet && (
        <div style={{ background: '#fef3c7', border: '1px solid #f59e0b', borderRadius: '12px', padding: '1rem' }}>
          <p style={{ margin: 0, fontSize: '0.9rem', color: '#92400e', lineHeight: 1.5 }}>
            ⚠️ Veuillez compléter votre profil pour accéder à toutes les fonctionnalités.
          </p>
        </div>
      )}

      {(localSuccess || saveSuccess) && (
        <div style={{ background: '#d1fae5', border: '1px solid #10b981', borderRadius: '12px', padding: '1rem' }}>
          <p style={{ margin: 0, fontSize: '0.9rem', color: '#065f46', lineHeight: 1.5, fontWeight: 600 }}>
            ✓ {localSuccess || saveSuccess}
          </p>
        </div>
      )}

      {saveError && (
        <div style={{ background: '#fee2e2', border: '1px solid #ef4444', borderRadius: '12px', padding: '1rem' }}>
          <p style={{ margin: 0, fontSize: '0.9rem', color: '#991b1b', lineHeight: 1.5 }}>
            ❌ {saveError}
          </p>
        </div>
      )}

      {!isEditing && profile?.profil_complet ? (
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '0.75rem' }}>
          <div style={{ padding: '0.75rem', background: 'var(--bg)', borderRadius: '10px' }}>
            <div style={{ fontSize: '0.7rem', fontWeight: 700, color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.05em', marginBottom: '0.25rem' }}>Téléphone</div>
            <div style={{ fontWeight: 600, color: 'var(--text)', fontSize: '0.88rem' }}>{telephone || '—'}</div>
          </div>
          <div style={{ padding: '0.75rem', background: 'var(--bg)', borderRadius: '10px' }}>
            <div style={{ fontSize: '0.7rem', fontWeight: 700, color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.05em', marginBottom: '0.25rem' }}>Région</div>
            <div style={{ fontWeight: 600, color: 'var(--text)', fontSize: '0.88rem' }}>{regionNom}</div>
          </div>
          <div style={{ padding: '0.75rem', background: 'var(--bg)', borderRadius: '10px' }}>
            <div style={{ fontSize: '0.7rem', fontWeight: 700, color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.05em', marginBottom: '0.25rem' }}>Préfecture</div>
            <div style={{ fontWeight: 600, color: 'var(--text)', fontSize: '0.88rem' }}>{prefectureNom}</div>
          </div>
          <div style={{ padding: '0.75rem', background: 'var(--bg)', borderRadius: '10px' }}>
            <div style={{ fontSize: '0.7rem', fontWeight: 700, color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.05em', marginBottom: '0.25rem' }}>Canton</div>
            <div style={{ fontWeight: 600, color: 'var(--text)', fontSize: '0.88rem' }}>{cantonNom}</div>
          </div>
          <div style={{ padding: '0.75rem', background: 'var(--bg)', borderRadius: '10px', gridColumn: '1 / -1' }}>
            <div style={{ fontSize: '0.7rem', fontWeight: 700, color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.05em', marginBottom: '0.25rem' }}>Produits d'intérêt</div>
            <div style={{ fontWeight: 600, color: 'var(--text)', fontSize: '0.88rem' }}>{selectedProduits.join(', ') || '—'}</div>
          </div>
        </div>
      ) : (
        <form onSubmit={handleSubmit} style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
          <div>
            <label style={labelStyle}>Numéro de téléphone *</label>
            <input 
              type="tel" 
              value={telephone}
              onChange={(e) => setTelephone(e.target.value)}
              required
              placeholder="Ex: +228 90 00 00 00"
              style={inputStyle} 
            />
          </div>

          <div>
            <label style={labelStyle}>Région *</label>
            {regions.length === 0 ? (
              <div style={{ ...inputStyle, color: 'var(--text-secondary)' }}>
                Chargement des régions...
              </div>
            ) : (
              <select 
                value={selectedRegion || ''} 
                onChange={(e) => setSelectedRegion(e.target.value ? Number(e.target.value) : null)}
                required
                style={inputStyle}>
                <option value="">Sélectionnez une région</option>
                {regions.map(r => <option key={r.id} value={r.id}>{r.nom}</option>)}
              </select>
            )}
          </div>

          {selectedRegion && (
            <div>
              <label style={labelStyle}>Préfecture *</label>
              {prefectures.length === 0 ? (
                <div style={{ ...inputStyle, color: 'var(--text-secondary)' }}>
                  Chargement des préfectures...
                </div>
              ) : (
                <select 
                  value={selectedPrefecture || ''} 
                  onChange={(e) => setSelectedPrefecture(e.target.value ? Number(e.target.value) : null)}
                  required
                  style={inputStyle}>
                  <option value="">Sélectionnez une préfecture</option>
                  {prefectures.map(p => <option key={p.id} value={p.id}>{p.nom}</option>)}
                </select>
              )}
            </div>
          )}

          {selectedPrefecture && cantons.length > 0 && (
            <div>
              <label style={labelStyle}>Canton *</label>
              <select 
                value={selectedCanton || ''} 
                onChange={(e) => setSelectedCanton(e.target.value ? Number(e.target.value) : null)}
                required
                style={inputStyle}>
                <option value="">Sélectionnez un canton</option>
                {cantons.map(c => <option key={c.id} value={c.id}>{c.nom}</option>)}
              </select>
            </div>
          )}

          <div>
            <label style={labelStyle}>Produits d'intérêt * (sélection multiple)</label>
            <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.5rem', padding: '0.75rem', borderRadius: '10px', border: '1px solid var(--border)', background: 'var(--bg)' }}>
              {PRODUITS_OPTIONS.map(produit => (
                <label key={produit} style={{ display: 'flex', alignItems: 'center', gap: '0.4rem', padding: '0.4rem 0.75rem', borderRadius: '8px', background: selectedProduits.includes(produit) ? '#0369a1' : 'var(--surface)', color: selectedProduits.includes(produit) ? 'white' : 'var(--text)', cursor: 'pointer', fontSize: '0.85rem', fontWeight: 600, border: '1px solid var(--border)', transition: 'all 0.2s' }}>
                  <input 
                    type="checkbox" 
                    checked={selectedProduits.includes(produit)}
                    onChange={(e) => {
                      if (e.target.checked) {
                        setSelectedProduits([...selectedProduits, produit]);
                      } else {
                        setSelectedProduits(selectedProduits.filter(p => p !== produit));
                      }
                    }}
                    style={{ display: 'none' }}
                  />
                  {produit}
                </label>
              ))}
            </div>
            {selectedProduits.length === 0 && (
              <p style={{ margin: '0.3rem 0 0', fontSize: '0.8rem', color: '#dc2626' }}>Sélectionnez au moins un produit</p>
            )}
          </div>

          <div style={{ display: 'flex', gap: '0.75rem' }}>
            <button 
              type="submit" 
              disabled={isSaving || !isComplete}
              style={{ flex: 1, padding: '0.75rem', borderRadius: '10px', border: 'none', background: '#0369a1', color: 'white', fontWeight: 700, cursor: 'pointer', fontSize: '0.95rem', opacity: (isSaving || !isComplete) ? 0.5 : 1 }}>
              {isSaving ? 'Enregistrement...' : 'Enregistrer'}
            </button>

            {profile?.profil_complet && (
              <button 
                type="button"
                onClick={handleCancel}
                disabled={isSaving}
                style={{ padding: '0.75rem 1.5rem', borderRadius: '10px', border: '1px solid var(--border)', background: 'var(--bg)', color: 'var(--text)', fontWeight: 600, cursor: 'pointer', fontSize: '0.95rem' }}>
                Annuler
              </button>
            )}
          </div>
        </form>
      )}
    </div>
  );
}
