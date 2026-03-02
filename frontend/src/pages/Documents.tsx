import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { useNavigate } from 'react-router-dom';
import { useToast } from '../hooks/useToast';
import Toast from '../components/Toast';
import PurchaseModal from '../components/PurchaseModal';
import { fetchPurchaseHistory, buildDownloadUrl } from '../api/purchases';
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
  is_purchased?: boolean;
  purchase_id?: number;
  download_token?: string;
}

export default function Documents() {
  const [documents, setDocuments] = useState<Document[]>([]);
  const [loading, setLoading] = useState(true);
  const [filters, setFilters] = useState({
    culture: '',
    region: '',
    search: ''
  });
  const [selectedDocument, setSelectedDocument] = useState<Document | null>(null);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [isProcessing, setIsProcessing] = useState(false);
  const [purchasedDocuments, setPurchasedDocuments] = useState<Set<number>>(new Set());
  
  const navigate = useNavigate();
  const { toasts, removeToast, success, error: showError, info } = useToast();

  useEffect(() => {
    loadData();
  }, [filters]);

  const loadData = async () => {
    try {
      setLoading(true);
      
      // First check purchased documents
      await checkPurchasedDocuments();
      
      // Then fetch documents
      await fetchDocuments();
    } catch (error) {
      console.error('Erreur lors du chargement:', error);
    } finally {
      setLoading(false);
    }
  };

  const checkPurchasedDocuments = async () => {
    try {
      const token = localStorage.getItem('access_token');
      if (!token) {
        setPurchasedDocuments(new Set());
        return;
      }

      const history = await fetchPurchaseHistory({ page_size: 1000 }, token);
      const purchasedIds = new Set(
        history.results
          .filter(p => p.transaction_statut === 'SUCCESS' && !p.lien_expire)
          .map(p => p.document)
      );
      setPurchasedDocuments(purchasedIds);
    } catch (error) {
      console.error('Erreur lors de la vérification des achats:', error);
      setPurchasedDocuments(new Set());
    }
  };

  const fetchDocuments = async () => {
    try {
      const params = new URLSearchParams();
      if (filters.culture) params.append('culture', filters.culture);
      if (filters.region) params.append('region', filters.region);
      if (filters.search) params.append('search', filters.search);

      const response = await axios.get(`http://localhost:8000/api/v1/documents/?${params}`);
      const docs = response.data.results || [];
      
      // Mark purchased documents
      const markedDocs = docs.map((doc: Document) => ({
        ...doc,
        is_purchased: purchasedDocuments.has(doc.id)
      }));
      
      setDocuments(markedDocs);
    } catch (error: any) {
      console.error('Erreur lors du chargement des documents:', error);
      
      // More specific error messages
      if (error.response?.status === 500) {
        showError('Erreur serveur', 'Le serveur rencontre des difficultés');
      } else if (error.code === 'ERR_NETWORK') {
        showError('Erreur réseau', 'Impossible de contacter le serveur');
      } else {
        showError('Erreur', 'Impossible de charger les documents');
      }
      
      setDocuments([]);
    }
  };

  const handlePurchaseClick = (doc: Document) => {
    const token = localStorage.getItem('access_token');
    if (!token) {
      info('Connexion requise', 'Veuillez vous connecter pour acheter un document');
      setTimeout(() => navigate('/login'), 2000);
      return;
    }

    if (doc.is_purchased) {
      handleDownload(doc);
    } else {
      setSelectedDocument(doc);
      setIsModalOpen(true);
    }
  };

  const handleConfirmPurchase = async () => {
    if (!selectedDocument) return;

    try {
      setIsProcessing(true);
      const token = localStorage.getItem('access_token');
      
      if (!token) {
        showError('Non authentifié', 'Veuillez vous connecter');
        navigate('/login');
        return;
      }

      const response = await axios.post(
        `http://localhost:8000/api/v1/documents/${selectedDocument.id}/purchase`,
        {},
        {
          headers: { Authorization: `Bearer ${token}` }
        }
      );
      
      if (response.data.already_purchased) {
        success('Déjà acheté', 'Vous possédez déjà ce document');
        setIsModalOpen(false);
        await checkPurchasedDocuments();
        await fetchDocuments();
      } else if (response.data.payment_url) {
        info('Redirection', 'Redirection vers la page de paiement...');
        setTimeout(() => {
          window.location.href = response.data.payment_url;
        }, 1000);
      }
    } catch (error: any) {
      console.error('Erreur lors de l\'achat:', error);
      
      if (error.response?.status === 401) {
        showError('Session expirée', 'Veuillez vous reconnecter');
        setTimeout(() => navigate('/login'), 2000);
      } else if (error.response?.status === 400) {
        showError('Erreur', error.response.data.error || 'Document non disponible');
      } else if (error.response?.status === 404) {
        showError('Introuvable', 'Document non trouvé');
      } else {
        showError('Erreur', 'Impossible de procéder à l\'achat');
      }
    } finally {
      setIsProcessing(false);
    }
  };

  const handleDownload = async (doc: Document) => {
    try {
      const token = localStorage.getItem('access_token');
      if (!token) {
        showError('Non authentifié', 'Veuillez vous connecter');
        navigate('/login');
        return;
      }

      // Get fresh purchase data
      const history = await fetchPurchaseHistory({ page_size: 1000 }, token);
      const purchase = history.results.find(
        p => p.document === doc.id && p.transaction_statut === 'SUCCESS'
      );

      if (purchase) {
        if (purchase.lien_expire) {
          showError('Lien expiré', 'Le lien de téléchargement a expiré');
          info('Astuce', 'Consultez votre historique pour régénérer le lien');
          setTimeout(() => navigate('/purchases'), 2000);
        } else {
          const downloadUrl = buildDownloadUrl(purchase.document, purchase.lien_telechargement);
          window.open(downloadUrl, '_blank');
          success('Téléchargement', 'Le document va s\'ouvrir dans un nouvel onglet');
        }
      } else {
        showError('Erreur', 'Impossible de trouver votre achat');
      }
    } catch (error) {
      console.error('Erreur lors du téléchargement:', error);
      showError('Erreur', 'Impossible de télécharger le document');
    }
  };

  const renderSkeletonCard = () => (
    <div className="document-card skeleton-card">
      <div className="skeleton skeleton-icon"></div>
      <div className="skeleton skeleton-title"></div>
      <div className="skeleton skeleton-description"></div>
      <div className="skeleton-meta">
        <div className="skeleton skeleton-badge"></div>
        <div className="skeleton skeleton-badge"></div>
      </div>
      <div className="skeleton-footer">
        <div className="skeleton skeleton-price"></div>
        <div className="skeleton skeleton-button"></div>
      </div>
    </div>
  );

  if (loading) {
    return (
      <>
        <div className="toast-container">
          {toasts.map(toast => (
            <Toast key={toast.id} {...toast} onClose={removeToast} />
          ))}
        </div>
        
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
              <div className="skeleton skeleton-filter"></div>
              <div className="skeleton skeleton-filter"></div>
              <div className="skeleton skeleton-filter"></div>
            </aside>

            <main className="documents-grid">
              {[1, 2, 3, 4, 5, 6].map(i => (
                <div key={i}>{renderSkeletonCard()}</div>
              ))}
            </main>
          </div>
        </div>
      </>
    );
  }

  return (
    <>
      <div className="toast-container">
        {toasts.map(toast => (
          <Toast key={toast.id} {...toast} onClose={removeToast} />
        ))}
      </div>

      <PurchaseModal
        document={selectedDocument}
        isOpen={isModalOpen}
        onClose={() => setIsModalOpen(false)}
        onConfirm={handleConfirmPurchase}
        isProcessing={isProcessing}
      />

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
              <div key={doc.id} className={`document-card ${doc.is_purchased ? 'purchased' : ''}`}>
                {doc.is_purchased && (
                  <div className="purchased-badge">
                    <span className="badge-icon">✓</span>
                    Acheté
                  </div>
                )}
                <div className="document-icon"><img src="/images/placeholder/document-default.jpg" alt="Document" className="inline-icon" style={{width: 24, height: 24, borderRadius: "50%", objectFit: "cover", marginRight: 8}} /></div>
                <h3>{doc.titre}</h3>
                <p className="document-description">{doc.description}</p>
                
                <div className="document-meta">
                  <span className="meta-item">
                    <span className="icon"><img src="/images/cultures/mais.jpg" alt="Culture" className="inline-icon" style={{width: 24, height: 24, borderRadius: "50%", objectFit: "cover", marginRight: 8}} /></span>
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
                    onClick={() => handlePurchaseClick(doc)}
                    className={`purchase-btn ${doc.is_purchased ? 'download-btn' : ''}`}
                  >
                    {doc.is_purchased ? '<img src="/images/hero/harvest.jpg" alt="Télécharger" className="inline-icon" style={{width: 20, height: 20, borderRadius: "50%", objectFit: "cover", marginRight: 8}} /> Télécharger' : '<img src="/images/hero/market.jpg" alt="Acheter" className="inline-icon" style={{width: 20, height: 20, borderRadius: "50%", objectFit: "cover", marginRight: 8}} /> Acheter'}
                  </button>
                </div>
              </div>
            ))
          )}
        </main>
      </div>
    </div>
    </>
  );
}
