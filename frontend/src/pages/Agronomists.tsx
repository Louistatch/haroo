import React, { useState, useEffect } from 'react';
import axios from 'axios';
import '../styles/agronomists.css';

interface Agronomist {
  id: number;
  user: {
    id: number;
    first_name: string;
    last_name: string;
    phone_number: string;
  };
  specialisations: string[];
  canton_rattachement: {
    nom: string;
    prefecture: {
      nom: string;
      region: {
        nom: string;
      };
    };
  };
  note_moyenne: string;
  nombre_avis: number;
  badge_valide: boolean;
}

export default function Agronomists() {
  const [agronomists, setAgronomists] = useState<Agronomist[]>([]);
  const [loading, setLoading] = useState(true);
  const [filters, setFilters] = useState({
    region: '',
    specialisation: '',
    search: ''
  });
  const [selectedAgronomist, setSelectedAgronomist] = useState<Agronomist | null>(null);

  useEffect(() => {
    fetchAgronomists();
  }, [filters]);

  const fetchAgronomists = async () => {
    try {
      const params = new URLSearchParams();
      if (filters.region) params.append('region', filters.region);
      if (filters.specialisation) params.append('specialisation', filters.specialisation);
      if (filters.search) params.append('search', filters.search);

      const response = await axios.get(`http://localhost:8000/api/v1/agronomists/?${params}`);
      setAgronomists(response.data.results || []);
    } catch (error) {
      console.error('Erreur lors du chargement des agronomes:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleContact = (agronomist: Agronomist) => {
    setSelectedAgronomist(agronomist);
  };

  const renderStars = (rating: string) => {
    const stars = [];
    const ratingNum = parseFloat(rating);
    for (let i = 1; i <= 5; i++) {
      if (i <= ratingNum) {
        stars.push(<span key={i} className="star filled">★</span>);
      } else if (i - 0.5 <= ratingNum) {
        stars.push(<span key={i} className="star half">★</span>);
      } else {
        stars.push(<span key={i} className="star">☆</span>);
      }
    }
    return stars;
  };

  if (loading) {
    return (
      <div className="loading-container">
        <div className="spinner"></div>
        <p>Chargement des agronomes...</p>
      </div>
    );
  }

  return (
    <div className="agronomists-page">
      <div className="agronomists-hero">
        <div className="hero-content">
          <h1>👨‍🌾 Annuaire des Agronomes Validés</h1>
          <p>Trouvez des experts agricoles qualifiés près de chez vous</p>
        </div>
      </div>

      <div className="agronomists-container">
        <aside className="filters-sidebar">
          <h3>🔍 Rechercher un agronome</h3>
          
          <div className="filter-group">
            <label>Nom ou téléphone</label>
            <input
              type="text"
              placeholder="Rechercher..."
              value={filters.search}
              onChange={(e) => setFilters({ ...filters, search: e.target.value })}
              className="filter-input"
            />
          </div>

          <div className="filter-group">
            <label>Région</label>
            <select
              value={filters.region}
              onChange={(e) => setFilters({ ...filters, region: e.target.value })}
              className="filter-select"
            >
              <option value="">Toutes les régions</option>
              <option value="Maritime">Maritime</option>
              <option value="Plateaux">Plateaux</option>
              <option value="Centrale">Centrale</option>
              <option value="Kara">Kara</option>
              <option value="Savanes">Savanes</option>
            </select>
          </div>

          <div className="filter-group">
            <label>Spécialisation</label>
            <select
              value={filters.specialisation}
              onChange={(e) => setFilters({ ...filters, specialisation: e.target.value })}
              className="filter-select"
            >
              <option value="">Toutes</option>
              <option value="Maraîchage">Maraîchage</option>
              <option value="Céréaliculture">Céréaliculture</option>
              <option value="Arboriculture">Arboriculture</option>
              <option value="Élevage">Élevage</option>
              <option value="Irrigation">Irrigation</option>
              <option value="Agroforesterie">Agroforesterie</option>
            </select>
          </div>

          <button 
            onClick={() => setFilters({ region: '', specialisation: '', search: '' })}
            className="reset-filters-btn"
          >
            Réinitialiser
          </button>
        </aside>

        <main className="agronomists-grid">
          {agronomists.length === 0 ? (
            <div className="no-agronomists">
              <p>😔 Aucun agronome trouvé</p>
              <p className="subtitle">Essayez de modifier vos critères de recherche</p>
            </div>
          ) : (
            agronomists.map((agro) => (
              <div key={agro.id} className="agronomist-card">
                <div className="card-header">
                  <div className="avatar">
                    <span className="avatar-icon">👨‍🌾</span>
                  </div>
                  {agro.badge_valide && (
                    <span className="badge-verified">✓ Validé</span>
                  )}
                </div>

                <h3>{agro.user.first_name} {agro.user.last_name}</h3>
                
                <div className="rating">
                  <div className="stars">
                    {renderStars(agro.note_moyenne)}
                  </div>
                  <span className="rating-text">
                    {parseFloat(agro.note_moyenne).toFixed(1)} ({agro.nombre_avis} avis)
                  </span>
                </div>

                <div className="location">
                  <span className="icon">📍</span>
                  <span>{agro.canton_rattachement.nom}, {agro.canton_rattachement.prefecture.nom}</span>
                </div>

                <div className="specialisations">
                  {agro.specialisations.map((spec, index) => (
                    <span key={index} className="spec-tag">{spec}</span>
                  ))}
                </div>

                <button 
                  onClick={() => handleContact(agro)}
                  className="contact-btn"
                >
                  📞 Contacter
                </button>
              </div>
            ))
          )}
        </main>
      </div>

      {selectedAgronomist && (
        <div className="modal-overlay" onClick={() => setSelectedAgronomist(null)}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()}>
            <button className="modal-close" onClick={() => setSelectedAgronomist(null)}>×</button>
            
            <div className="modal-header">
              <div className="avatar-large">👨‍🌾</div>
              <h2>{selectedAgronomist.user.first_name} {selectedAgronomist.user.last_name}</h2>
              {selectedAgronomist.badge_valide && (
                <span className="badge-verified">✓ Agronome Validé</span>
              )}
            </div>

            <div className="modal-body">
              <div className="info-section">
                <h4>📞 Contact</h4>
                <p className="phone-number">{selectedAgronomist.user.phone_number}</p>
              </div>

              <div className="info-section">
                <h4>📍 Localisation</h4>
                <p>
                  {selectedAgronomist.canton_rattachement.nom}<br/>
                  {selectedAgronomist.canton_rattachement.prefecture.nom}<br/>
                  Région {selectedAgronomist.canton_rattachement.prefecture.region.nom}
                </p>
              </div>

              <div className="info-section">
                <h4>🎓 Spécialisations</h4>
                <div className="specialisations">
                  {selectedAgronomist.specialisations.map((spec, index) => (
                    <span key={index} className="spec-tag">{spec}</span>
                  ))}
                </div>
              </div>

              <div className="info-section">
                <h4>⭐ Évaluation</h4>
                <div className="rating-large">
                  <div className="stars">
                    {renderStars(selectedAgronomist.note_moyenne)}
                  </div>
                  <p className="rating-text">
                    {parseFloat(selectedAgronomist.note_moyenne).toFixed(2)} / 5.00
                    <br/>
                    <small>Basé sur {selectedAgronomist.nombre_avis} avis</small>
                  </p>
                </div>
              </div>
            </div>

            <div className="modal-footer">
              <button className="btn-primary">Créer une mission</button>
              <button className="btn-secondary" onClick={() => setSelectedAgronomist(null)}>
                Fermer
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
