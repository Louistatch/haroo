import React, { useState, useEffect } from 'react';
import axios from 'axios';
import '../styles/documents.css';

interface Document {
  id: number;
  titre: string;
  description: string;
  prix: string;
  culture: string;
  region: string;
  prefecture: string;
  canton: string;
}

export default function Documents() {
  const [documents, setDocuments] = useState<Document[]>([]);
  const [loading, setLoading] = useState(true);
  const [filters, setFilters] = useState({
    culture: '',
    region: '',
    search: ''
  });

  useEffect(() => {
    fetchDocuments();
  }, [filters]);

  const fetchDocuments = async () => {
    try {
      const params = new URLSearchParams();
      if (filters.culture) params.append('culture', filters.culture);
      if (filters.region) params.append('region', filters.region);
      if (filters.search) params.append('search', filters.search);

      const response = await axios.get(`http://localhost:8000/api/v1/documents/?${params}`);
      setDocuments(response.data.results || []);
    } catch (error) {
      console.error('Erreur lors du chargement des documents:', error);
    } finally {
      setLoading(false);
    }
  };

  const handlePurchase = async (documentId: number) => {
    try {
      const token = localStorage.getItem('access_token');
      const response = await axios.post(
        `http://localhost:8000/api/v1/documents/${documentId}/purchase`,
        {},
        {
          headers: { Authorization: `Bearer ${token}` }
        }
      );
      
      if (response.data.payment_url) {
        window.location.href = response.data.payment_url;
      }
    } catch (error) {
      console.error('Erreur lors de l\'achat:', error);
      alert('Erreur lors de l\'achat du document');
    }
  };

  if (loading) {
    return (
      <div className="loading-container">
        <div className="spinner"></div>
        <p>Chargement des documents...</p>
      </div>
    );
  }

  return (
    <div className="documents-page">
      <div className="documents-hero">
        <div className="hero-content">
          <h1>📚 Documents Techniques Agricoles</h1>
          <p>Accédez à des guides pratiques et comptes d'exploitation adaptés à votre région</p>
        </div>
      </div>

      <div className="documents-container">
        <aside className="filters-sidebar">
          <h3>🔍 Filtrer les documents</h3>
          
          <div className="filter-group">
            <label>Rechercher</label>
            <input
              type="text"
              placeholder="Nom du document..."
              value={filters.search}
              onChange={(e) => setFilters({ ...filters, search: e.target.value })}
              className="filter-input"
            />
          </div>

          <div className="filter-group">
            <label>Culture</label>
            <select
              value={filters.culture}
              onChange={(e) => setFilters({ ...filters, culture: e.target.value })}
              className="filter-select"
            >
              <option value="">Toutes les cultures</option>
              <option value="Maïs">Maïs</option>
              <option value="Riz">Riz</option>
              <option value="Manioc">Manioc</option>
              <option value="Tomate">Tomate</option>
              <option value="Oignon">Oignon</option>
              <option value="Arachide">Arachide</option>
            </select>
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

          <button 
            onClick={() => setFilters({ culture: '', region: '', search: '' })}
            className="reset-filters-btn"
          >
            Réinitialiser les filtres
          </button>
        </aside>

        <main className="documents-grid">
          {documents.length === 0 ? (
            <div className="no-documents">
              <p>😔 Aucun document trouvé</p>
              <p className="subtitle">Essayez de modifier vos filtres</p>
            </div>
          ) : (
            documents.map((doc) => (
              <div key={doc.id} className="document-card">
                <div className="document-icon">📄</div>
                <h3>{doc.titre}</h3>
                <p className="document-description">{doc.description}</p>
                
                <div className="document-meta">
                  <span className="meta-item">
                    <span className="icon">🌾</span>
                    {doc.culture}
                  </span>
                  <span className="meta-item">
                    <span className="icon">📍</span>
                    {doc.canton || doc.prefecture || doc.region}
                  </span>
                </div>

                <div className="document-footer">
                  <span className="document-price">{parseInt(doc.prix).toLocaleString()} FCFA</span>
                  <button 
                    onClick={() => handlePurchase(doc.id)}
                    className="purchase-btn"
                  >
                    Acheter
                  </button>
                </div>
              </div>
            ))
          )}
        </main>
      </div>
    </div>
  );
}
