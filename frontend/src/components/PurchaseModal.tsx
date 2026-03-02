import React from 'react';

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

interface PurchaseModalProps {
  document: Document | null;
  isOpen: boolean;
  onClose: () => void;
  onConfirm: () => void;
  isProcessing: boolean;
}

export default function PurchaseModal({ 
  document, 
  isOpen, 
  onClose, 
  onConfirm, 
  isProcessing 
}: PurchaseModalProps) {
  if (!isOpen || !document) return null;

  const formatPrice = (price: string) => {
    return parseInt(price).toLocaleString('fr-FR');
  };

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal-content" onClick={(e) => e.stopPropagation()}>
        <button className="modal-close" onClick={onClose} aria-label="Fermer">
          ×
        </button>

        <div className="modal-header">
          <div className="modal-icon"><img src="/images/hero/market.jpg" alt="Acheter" className="inline-icon" style={{width: 20, height: 20, borderRadius: "50%", objectFit: "cover", marginRight: 8}} /></div>
          <h2>Confirmer l'achat</h2>
        </div>

        <div className="modal-body">
          <div className="document-preview">
            <div className="preview-icon"><img src="/images/placeholder/document-default.jpg" alt="Document" className="inline-icon" style={{width: 24, height: 24, borderRadius: "50%", objectFit: "cover", marginRight: 8}} /></div>
            <div className="preview-details">
              <h3>{document.titre}</h3>
              <p className="preview-description">{document.description}</p>
            </div>
          </div>

          <div className="purchase-details">
            <div className="detail-row">
              <span className="label"><img src="/images/cultures/mais.jpg" alt="Culture" className="inline-icon" style={{width: 24, height: 24, borderRadius: "50%", objectFit: "cover", marginRight: 8}} /> Culture</span>
              <span className="value">{document.culture}</span>
            </div>
            <div className="detail-row">
              <span className="label">📍 Localisation</span>
              <span className="value">
                {document.canton || document.prefecture || document.region}
              </span>
            </div>
            <div className="detail-row highlight">
              <span className="label"><img src="/images/hero/market.jpg" alt="Prix" className="inline-icon" style={{width: 20, height: 20, borderRadius: "50%", objectFit: "cover", marginRight: 8}} /> Prix</span>
              <span className="value price">{formatPrice(document.prix)} FCFA</span>
            </div>
          </div>

          <div className="purchase-info">
            <div className="info-item">
              <span className="info-icon">✓</span>
              <span>Accès immédiat après paiement</span>
            </div>
            <div className="info-item">
              <span className="info-icon">✓</span>
              <span>Lien de téléchargement valide 48h</span>
            </div>
            <div className="info-item">
              <span className="info-icon">✓</span>
              <span>Paiement sécurisé via Fedapay</span>
            </div>
          </div>
        </div>

        <div className="modal-footer">
          <button 
            onClick={onClose} 
            className="btn-cancel"
            disabled={isProcessing}
          >
            Annuler
          </button>
          <button 
            onClick={onConfirm} 
            className="btn-confirm"
            disabled={isProcessing}
          >
            {isProcessing ? (
              <>
                <span className="btn-spinner"></span>
                Traitement...
              </>
            ) : (
              <>
                💳 Procéder au paiement
              </>
            )}
          </button>
        </div>
      </div>
    </div>
  );
}
