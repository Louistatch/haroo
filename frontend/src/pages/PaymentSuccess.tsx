import { useState, useEffect } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import { verifyPaymentCallback } from '../api/payments';
import { fetchPurchaseHistory, buildDownloadUrl } from '../api/purchases';
import '../styles/payment-success.css';

export default function PaymentSuccess() {
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();
  
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [paymentData, setPaymentData] = useState<any>(null);
  const [purchaseData, setPurchaseData] = useState<any>(null);

  useEffect(() => {
    verifyPayment();
  }, []);

  const verifyPayment = async () => {
    try {
      setLoading(true);
      setError(null);

      // Extract transaction_id from URL params
      const fedapayTransactionId = searchParams.get('transaction_id');
      
      if (!fedapayTransactionId) {
        setError('ID de transaction manquant');
        setTimeout(() => navigate('/documents'), 3000);
        return;
      }

      // Verify payment with backend
      const result = await verifyPaymentCallback(fedapayTransactionId);
      
      if (!result.success) {
        setError(result.message || 'Erreur lors de la vérification du paiement');
        return;
      }

      setPaymentData(result);

      // If payment is successful, fetch purchase details
      if (result.statut === 'SUCCESS') {
        await fetchPurchaseDetails();
      }
    } catch (err: any) {
      console.error('Erreur lors de la vérification du paiement:', err);
      
      if (err.response?.status === 404) {
        setError('Transaction introuvable');
      } else if (err.response?.status === 400) {
        setError('Requête invalide');
      } else {
        setError('Erreur lors de la vérification du paiement');
      }
    } finally {
      setLoading(false);
    }
  };

  const fetchPurchaseDetails = async () => {
    try {
      const token = localStorage.getItem('access_token');
      
      if (!token) {
        return; // User not logged in, skip purchase details
      }

      // Fetch recent purchases to get the latest one
      const history = await fetchPurchaseHistory({ page: 1, page_size: 1 }, token);
      
      if (history.results && history.results.length > 0) {
        setPurchaseData(history.results[0]);
      }
    } catch (err) {
      console.error('Erreur lors de la récupération des détails d\'achat:', err);
      // Don't show error, purchase details are optional
    }
  };

  const handleDownload = () => {
    if (purchaseData) {
      const downloadUrl = buildDownloadUrl(
        purchaseData.document,
        purchaseData.lien_telechargement
      );
      window.open(downloadUrl, '_blank');
    }
  };

  const calculateExpirationDate = () => {
    if (purchaseData?.expiration_lien) {
      return new Date(purchaseData.expiration_lien).toLocaleString('fr-FR', {
        day: '2-digit',
        month: 'long',
        year: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
      });
    }
    
    // Default: 48 hours from now
    const expiration = new Date();
    expiration.setHours(expiration.getHours() + 48);
    return expiration.toLocaleString('fr-FR', {
      day: '2-digit',
      month: 'long',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  const formatPrice = (price: string) => {
    return parseInt(price).toLocaleString('fr-FR');
  };

  // Loading State
  if (loading) {
    return (
      <div className="payment-success-page">
        <div className="success-container">
          <div className="loading-state">
            <div className="loading-spinner"></div>
            <h2>Vérification du paiement</h2>
            <p>Veuillez patienter...</p>
          </div>
        </div>
      </div>
    );
  }

  // Error State
  if (error || !paymentData) {
    return (
      <div className="payment-success-page">
        <div className="success-container">
          <div className="error-state">
            <div className="error-icon"><img src="/images/hero/market.jpg" alt="Erreur" className="inline-icon" style={{width: 20, height: 20, borderRadius: "50%", objectFit: "cover", marginRight: 8}} /></div>
            <h2>Erreur</h2>
            <p>{error || 'Une erreur est survenue'}</p>
            <div className="error-actions">
              <button onClick={() => verifyPayment()} className="retry-btn">
                🔄 Réessayer
              </button>
              <button onClick={() => navigate('/documents')} className="home-btn">
                📚 Retour aux documents
              </button>
            </div>
          </div>
        </div>
      </div>
    );
  }

  // Failed Payment State
  if (paymentData.statut === 'FAILED') {
    return (
      <div className="payment-success-page">
        <div className="success-container">
          <div className="error-state">
            <div className="error-icon">💳</div>
            <h2>Paiement échoué</h2>
            <p>Votre paiement n'a pas pu être traité. Veuillez réessayer.</p>
            <div className="error-actions">
              <button onClick={() => navigate('/documents')} className="retry-btn">
                🔄 Réessayer le paiement
              </button>
              <button onClick={() => navigate('/home')} className="home-btn">
                🏠 Retour à l'accueil
              </button>
            </div>
          </div>
        </div>
      </div>
    );
  }

  // Pending Payment State
  if (paymentData.statut === 'PENDING') {
    return (
      <div className="payment-success-page">
        <div className="success-container">
          <div className="pending-state">
            <div className="pending-icon"><img src="/images/hero/farmer.jpg" alt="En attente" className="inline-icon" style={{width: 20, height: 20, borderRadius: "50%", objectFit: "cover", marginRight: 8}} /></div>
            <h2>Paiement en cours</h2>
            <p>Votre paiement est en cours de traitement. Cela peut prendre quelques minutes.</p>
            <div className="error-actions">
              <button onClick={() => verifyPayment()} className="retry-btn">
                🔄 Vérifier à nouveau
              </button>
              <button onClick={() => navigate('/purchases')} className="secondary-btn">
                📋 Voir mes achats
              </button>
            </div>
          </div>
        </div>
      </div>
    );
  }

  // Success State
  return (
    <div className="payment-success-page">
      <div className="success-container">
        <div className="success-animation">
          <div className="checkmark-circle">
            <div className="checkmark">✓</div>
          </div>
        </div>

        <h1 className="success-title">Paiement réussi !</h1>
        <p className="success-subtitle">
          Votre document est maintenant disponible au téléchargement
        </p>

        {purchaseData && (
          <>
            <div className="document-details">
              <h3><img src="/images/placeholder/document-default.jpg" alt="Document" className="inline-icon" style={{width: 24, height: 24, borderRadius: "50%", objectFit: "cover", marginRight: 8}} /> Détails du document</h3>
              <div className="detail-item">
                <span className="detail-label">
                  📝 Titre
                </span>
                <span className="detail-value">{purchaseData.document_titre}</span>
              </div>
              <div className="detail-item">
                <span className="detail-label">
                  <img src="/images/cultures/mais.jpg" alt="Culture" className="inline-icon" style={{width: 24, height: 24, borderRadius: "50%", objectFit: "cover", marginRight: 8}} /> Culture
                </span>
                <span className="detail-value">{purchaseData.document_culture}</span>
              </div>
              <div className="detail-item">
                <span className="detail-label">
                  📋 Format
                </span>
                <span className="detail-value">{purchaseData.format_fichier}</span>
              </div>
              <div className="detail-item">
                <span className="detail-label">
                  <img src="/images/hero/market.jpg" alt="Prix" className="inline-icon" style={{width: 20, height: 20, borderRadius: "50%", objectFit: "cover", marginRight: 8}} /> Montant payé
                </span>
                <span className="detail-value highlight">
                  {formatPrice(purchaseData.document_prix)} FCFA
                </span>
              </div>
            </div>

            <div className="expiration-notice">
              <div className="icon"><img src="/images/hero/farmer.jpg" alt="Temps" className="inline-icon" style={{width: 20, height: 20, borderRadius: "50%", objectFit: "cover", marginRight: 8}} /></div>
              <div className="text">
                <strong>Lien de téléchargement valide pendant 48h</strong>
                <span>Expire le {calculateExpirationDate()}</span>
              </div>
            </div>

            <div className="action-buttons">
              <button onClick={handleDownload} className="download-btn">
                <img src="/images/hero/harvest.jpg" alt="Télécharger" className="inline-icon" style={{width: 20, height: 20, borderRadius: "50%", objectFit: "cover", marginRight: 8}} /> Télécharger maintenant
              </button>
              <button 
                onClick={() => navigate('/purchases')} 
                className="secondary-btn"
              >
                📋 Voir mes achats
              </button>
            </div>
          </>
        )}

        {!purchaseData && (
          <div className="action-buttons">
            <button 
              onClick={() => navigate('/purchases')} 
              className="download-btn"
            >
              📋 Voir mes achats
            </button>
            <button 
              onClick={() => navigate('/documents')} 
              className="secondary-btn"
            >
              📚 Parcourir les documents
            </button>
          </div>
        )}
      </div>
    </div>
  );
}
