import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { 
  fetchPurchaseHistory, 
  regenerateDownloadLink, 
  buildDownloadUrl,
  Purchase,
  PurchaseFilters 
} from '../api/purchases';
import { useDebounce } from '../hooks/useDebounce';
import { useToast } from '../hooks/useToast';
import Toast from '../components/Toast';
import '../styles/purchase-history.css';

export default function PurchaseHistory() {
  const [purchases, setPurchases] = useState<Purchase[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [filters, setFilters] = useState<PurchaseFilters>({});
  const [totalCount, setTotalCount] = useState(0);
  const [currentPage, setCurrentPage] = useState(1);
  const [regeneratingId, setRegeneratingId] = useState<number | null>(null);
  const navigate = useNavigate();
  const { toasts, removeToast, success, error: showError, info } = useToast();

  // Debounce the culture filter to avoid excessive API calls
  const debouncedCulture = useDebounce(filters.culture, 300);

  useEffect(() => {
    loadPurchaseHistory();
  }, [debouncedCulture, filters.date_debut, filters.date_fin, filters.statut, filters.lien_expire, currentPage]);

  const loadPurchaseHistory = async () => {
    try {
      setLoading(true);
      setError(null);
      
      const token = localStorage.getItem('access_token');
      
      if (!token) {
        navigate('/login');
        return;
      }

      // Build filters with debounced culture value
      const apiFilters: PurchaseFilters = {
        ...filters,
        culture: debouncedCulture,
        page: currentPage,
        page_size: 20
      };

      const data = await fetchPurchaseHistory(apiFilters, token);

      setPurchases(data.results || []);
      setTotalCount(data.count || 0);
    } catch (err: any) {
      console.error('Erreur lors du chargement de l\'historique:', err);
      
      // Handle specific error cases
      if (err.response?.status === 401) {
        setError('Session expirée. Veuillez vous reconnecter.');
        showError('Session expirée', 'Veuillez vous reconnecter');
        setTimeout(() => navigate('/login'), 2000);
      } else if (err.response?.status === 403) {
        setError('Accès non autorisé.');
        showError('Accès refusé', 'Vous n\'avez pas les permissions nécessaires');
      } else if (err.response?.status === 500) {
        setError('Erreur serveur. Veuillez réessayer plus tard.');
        showError('Erreur serveur', 'Le serveur rencontre des difficultés');
      } else {
        setError('Impossible de charger l\'historique des achats.');
        showError('Erreur de chargement', 'Impossible de charger l\'historique');
      }
    } finally {
      setLoading(false);
    }
  };

  const handleRegenerateLink = async (purchaseId: number) => {
    try {
      setRegeneratingId(purchaseId);
      const token = localStorage.getItem('access_token');
      
      if (!token) {
        navigate('/login');
        return;
      }

      info('Régénération en cours...', 'Veuillez patienter');
      const result = await regenerateDownloadLink(purchaseId, token);

      // Update purchase in state
      setPurchases(prev => prev.map(p => 
        p.id === purchaseId 
          ? { ...p, lien_expire: false, expiration_lien: result.expiration }
          : p
      ));

      success('Lien régénéré', result.message);
    } catch (err: any) {
      console.error('Erreur lors de la régénération du lien:', err);
      
      if (err.response?.status === 400) {
        showError('Erreur', err.response.data.error || 'Impossible de régénérer le lien');
      } else if (err.response?.status === 403) {
        showError('Accès refusé', 'Vous n\'êtes pas autorisé à régénérer ce lien');
      } else if (err.response?.status === 404) {
        showError('Introuvable', 'Achat introuvable');
      } else {
        showError('Erreur', 'Erreur lors de la régénération du lien');
      }
    } finally {
      setRegeneratingId(null);
    }
  };

  const handleDownload = (purchase: Purchase) => {
    const downloadUrl = buildDownloadUrl(purchase.document, purchase.lien_telechargement);
    window.open(downloadUrl, '_blank');
    info('Téléchargement démarré', 'Le document va s\'ouvrir dans un nouvel onglet');
  };

  const resetFilters = () => {
    setFilters({});
    setCurrentPage(1);
  };

  const getStatusBadge = (status: string) => {
    const badges = {
      SUCCESS: { text: 'Payé', color: 'success' },
      PENDING: { text: 'En attente', color: 'warning' },
      FAILED: { text: 'Échoué', color: 'error' }
    };
    const badge = badges[status as keyof typeof badges] || { text: status, color: 'default' };
    return <span className={`status-badge status-${badge.color}`}>{badge.text}</span>;
  };

  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    return date.toLocaleDateString('fr-FR', {
      day: '2-digit',
      month: '2-digit',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  const formatPrice = (price: string) => {
    return parseInt(price).toLocaleString('fr-FR');
  };

  const getCardBorderClass = (purchase: Purchase) => {
    if (purchase.lien_expire) return 'expired';
    return '';
  };

  const renderSkeletonCard = () => (
    <div className="skeleton-card">
      <div className="skeleton-header">
        <div className="skeleton skeleton-icon"></div>
        <div className="skeleton-title">
          <div className="skeleton skeleton-text"></div>
          <div className="skeleton skeleton-text small"></div>
        </div>
      </div>
      <div className="skeleton-details">
        <div className="skeleton skeleton-detail"></div>
        <div className="skeleton skeleton-detail"></div>
        <div className="skeleton skeleton-detail"></div>
        <div className="skeleton skeleton-detail"></div>
      </div>
      <div className="skeleton-actions">
        <div className="skeleton skeleton-button"></div>
      </div>
    </div>
  );

  if (loading) {
    return (
      <div className="purchase-history-page">
        <div className="page-header">
          <h1>📚 Mes Achats de Documents</h1>
          <button 
            onClick={() => navigate('/documents')}
            className="back-btn"
          >
            ← Retour aux documents
          </button>
        </div>

        <div className="history-container">
          <aside className="filters-sidebar">
            <h3>🔍 Filtrer les achats</h3>
            <div className="skeleton skeleton-text" style={{ marginBottom: '1rem' }}></div>
            <div className="skeleton skeleton-text" style={{ marginBottom: '1rem' }}></div>
            <div className="skeleton skeleton-text" style={{ marginBottom: '1rem' }}></div>
          </aside>

          <main className="purchases-list">
            {[1, 2, 3].map(i => (
              <div key={i}>{renderSkeletonCard()}</div>
            ))}
          </main>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="error-container">
        <div className="error-icon"><img src="/images/hero/market.jpg" alt="Erreur" className="inline-icon" style={{width: 20, height: 20, borderRadius: "50%", objectFit: "cover", marginRight: 8}} /></div>
        <h2>Erreur</h2>
        <p>{error}</p>
        <button 
          onClick={() => loadPurchaseHistory()}
          className="retry-btn"
        >
          🔄 Réessayer
        </button>
      </div>
    );
  }

  return (
    <>
      <div className="toast-container">
        {toasts.map(toast => (
          <Toast
            key={toast.id}
            {...toast}
            onClose={removeToast}
          />
        ))}
      </div>

      <div className="purchase-history-page">
      <div className="page-header">
        <h1>📚 Mes Achats de Documents</h1>
        <p className="total-count">Total: {totalCount} achat{totalCount > 1 ? 's' : ''}</p>
        <button 
          onClick={() => navigate('/documents')}
          className="back-btn"
        >
          ← Retour aux documents
        </button>
      </div>

      <div className="history-container">
        <aside className="filters-sidebar">
          <h3>🔍 Filtrer les achats</h3>

          <div className="filter-group">
            <label>Date de début</label>
            <input
              type="date"
              value={filters.date_debut || ''}
              onChange={(e) => setFilters({ ...filters, date_debut: e.target.value })}
              className="filter-input"
            />
          </div>

          <div className="filter-group">
            <label>Date de fin</label>
            <input
              type="date"
              value={filters.date_fin || ''}
              onChange={(e) => setFilters({ ...filters, date_fin: e.target.value })}
              className="filter-input"
            />
          </div>

          <div className="filter-group">
            <label>Culture</label>
            <input
              type="text"
              placeholder="Ex: Maïs, Riz..."
              value={filters.culture || ''}
              onChange={(e) => setFilters({ ...filters, culture: e.target.value })}
              className="filter-input"
            />
          </div>

          <div className="filter-group">
            <label>Statut</label>
            <select
              value={filters.statut || ''}
              onChange={(e) => setFilters({ ...filters, statut: e.target.value })}
              className="filter-select"
            >
              <option value="">Tous les statuts</option>
              <option value="SUCCESS">Payé</option>
              <option value="PENDING">En attente</option>
              <option value="FAILED">Échoué</option>
            </select>
          </div>

          <div className="filter-group">
            <label className="checkbox-label">
              <input
                type="checkbox"
                checked={filters.lien_expire || false}
                onChange={(e) => setFilters({ ...filters, lien_expire: e.target.checked })}
              />
              Liens expirés uniquement
            </label>
          </div>

          <button 
            onClick={resetFilters}
            className="reset-filters-btn"
          >
            Réinitialiser les filtres
          </button>
        </aside>

        <main className="purchases-list">
          {purchases.length === 0 ? (
            <div className="no-purchases">
              <p>😔 Aucun achat trouvé</p>
              <p className="subtitle">Vous n'avez pas encore acheté de documents</p>
              <button 
                onClick={() => navigate('/documents')}
                className="browse-btn"
              >
                Parcourir les documents
              </button>
            </div>
          ) : (
            <>
              {purchases.map((purchase) => (
                <div 
                  key={purchase.id} 
                  className={`purchase-card ${getCardBorderClass(purchase)}`}
                  data-status={purchase.transaction_statut}
                >
                  <div className="purchase-header">
                    <div className="purchase-icon"><img src="/images/placeholder/document-default.jpg" alt="Document" className="inline-icon" style={{width: 24, height: 24, borderRadius: "50%", objectFit: "cover", marginRight: 8}} /></div>
                    <div className="purchase-title">
                      <h3>{purchase.document_titre}</h3>
                      {getStatusBadge(purchase.transaction_statut)}
                      {purchase.lien_expire && (
                        <span className="status-badge status-error">Expiré</span>
                      )}
                    </div>
                  </div>

                  <div className="purchase-details">
                    <div className="detail-row">
                      <span className="detail-label"><img src="/images/cultures/mais.jpg" alt="Culture" className="inline-icon" style={{width: 24, height: 24, borderRadius: "50%", objectFit: "cover", marginRight: 8}} /> Culture:</span>
                      <span className="detail-value">{purchase.document_culture}</span>
                    </div>
                    <div className="detail-row">
                      <span className="detail-label"><img src="/images/hero/market.jpg" alt="Prix" className="inline-icon" style={{width: 20, height: 20, borderRadius: "50%", objectFit: "cover", marginRight: 8}} /> Prix:</span>
                      <span className="detail-value">
                        {formatPrice(purchase.document_prix)} FCFA
                      </span>
                    </div>
                    <div className="detail-row">
                      <span className="detail-label">📋 Format:</span>
                      <span className="detail-value">{purchase.format_fichier}</span>
                    </div>
                    <div className="detail-row">
                      <span className="detail-label">📅 Date d'achat:</span>
                      <span className="detail-value">{formatDate(purchase.created_at)}</span>
                    </div>
                    <div className="detail-row">
                      <span className="detail-label"><img src="/images/hero/harvest.jpg" alt="Télécharger" className="inline-icon" style={{width: 20, height: 20, borderRadius: "50%", objectFit: "cover", marginRight: 8}} /> Téléchargements:</span>
                      <span className="detail-value">{purchase.nombre_telechargements}</span>
                    </div>
                    {purchase.expiration_lien && (
                      <div className="detail-row">
                        <span className="detail-label"><img src="/images/hero/farmer.jpg" alt="Temps" className="inline-icon" style={{width: 20, height: 20, borderRadius: "50%", objectFit: "cover", marginRight: 8}} /> Expiration:</span>
                        <span className={`detail-value ${purchase.lien_expire ? 'expired-text' : ''}`}>
                          {formatDate(purchase.expiration_lien)}
                          {purchase.lien_expire && ' (Expiré)'}
                        </span>
                      </div>
                    )}
                  </div>

                  <div className="purchase-actions">
                    {purchase.transaction_statut === 'SUCCESS' && !purchase.lien_expire && (
                      <button 
                        onClick={() => handleDownload(purchase)}
                        className="action-btn download-btn"
                      >
                        <img src="/images/hero/harvest.jpg" alt="Télécharger" className="inline-icon" style={{width: 20, height: 20, borderRadius: "50%", objectFit: "cover", marginRight: 8}} /> Télécharger
                      </button>
                    )}
                    {purchase.lien_expire && purchase.peut_regenerer && (
                      <button 
                        onClick={() => handleRegenerateLink(purchase.id)}
                        className="action-btn regenerate-btn"
                        disabled={regeneratingId === purchase.id}
                      >
                        {regeneratingId === purchase.id ? '<img src="/images/hero/farmer.jpg" alt="En attente" className="inline-icon" style={{width: 20, height: 20, borderRadius: "50%", objectFit: "cover", marginRight: 8}} /> Régénération...' : '🔄 Régénérer le lien'}
                      </button>
                    )}
                  </div>
                </div>
              ))}

              {totalCount > 20 && (
                <div className="pagination">
                  <button
                    onClick={() => setCurrentPage(prev => Math.max(1, prev - 1))}
                    disabled={currentPage === 1}
                    className="pagination-btn"
                  >
                    ← Précédent
                  </button>
                  <span className="page-info">
                    Page {currentPage} sur {Math.ceil(totalCount / 20)}
                  </span>
                  <button
                    onClick={() => setCurrentPage(prev => prev + 1)}
                    disabled={currentPage >= Math.ceil(totalCount / 20)}
                    className="pagination-btn"
                  >
                    Suivant →
                  </button>
                </div>
              )}
            </>
          )}
        </main>
      </div>
    </div>
    </>
  );
}
