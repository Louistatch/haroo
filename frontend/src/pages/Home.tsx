import React, { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { me } from "../api/auth";
import { Container } from "../components/Layout";

export default function Home() {
  const [user, setUser] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const navigate = useNavigate();

  useEffect(() => {
    me()
      .then(setUser)
      .catch(() => {
        navigate("/login");
      })
      .finally(() => setLoading(false));
  }, [navigate]);

  if (loading) {
    return (
      <Container>
        <div style={{ textAlign: 'center', padding: '3rem' }}>
          <div className="spinner"></div>
          <p>Chargement...</p>
        </div>
      </Container>
    );
  }

  if (!user) return null;

  const getUserTypeLabel = (type: string) => {
    const types: Record<string, string> = {
      'EXPLOITANT': 'Exploitant Agricole',
      'AGRONOME': 'Agronome',
      'OUVRIER': 'Ouvrier Agricole',
      'ACHETEUR': 'Acheteur',
      'INSTITUTION': 'Institution'
    };
    return types[type] || type;
  };

  return (
    <Container>
      <div style={{ maxWidth: '1200px', margin: '0 auto', padding: '2rem 1rem' }}>
        {/* En-tête de bienvenue */}
        <div style={{ 
          background: 'linear-gradient(135deg, #2e7d32 0%, #4caf50 100%)',
          color: 'white',
          padding: '2rem',
          borderRadius: '12px',
          marginBottom: '2rem',
          boxShadow: '0 4px 6px rgba(0,0,0,0.1)'
        }}>
          <h1 style={{ margin: 0, fontSize: '2rem', marginBottom: '0.5rem' }}>
            Bienvenue, {user.first_name} {user.last_name}!
          </h1>
          <p style={{ margin: 0, opacity: 0.9, fontSize: '1.1rem' }}>
            {getUserTypeLabel(user.user_type)} • {user.phone_number}
          </p>
        </div>

        {/* Cartes de fonctionnalités */}
        <div style={{ 
          display: 'grid', 
          gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))',
          gap: '1.5rem',
          marginBottom: '2rem'
        }}>
          {/* Carte Profil */}
          <div className="feature-card" onClick={() => navigate('/me')}>
            <div className="feature-icon" style={{ background: '#2196f3' }}>
              👤
            </div>
            <h3>Mon Profil</h3>
            <p>Gérer vos informations personnelles et paramètres de sécurité</p>
          </div>

          {/* Carte Annuaire des Agronomes */}
          {(user.user_type === 'EXPLOITANT' || user.user_type === 'ACHETEUR') && (
            <div className="feature-card" onClick={() => navigate('/agronomists')}>
              <div className="feature-icon" style={{ background: '#4caf50' }}>
                <img src="/images/cultures/mais.jpg" alt="Culture" className="inline-icon" style={{width: 24, height: 24, borderRadius: "50%", objectFit: "cover", marginRight: 8}} />
              </div>
              <h3>Annuaire des Agronomes</h3>
              <p>Trouver et recruter des agronomes qualifiés dans votre région</p>
            </div>
          )}

          {/* Carte Documents Techniques */}
          <div className="feature-card" onClick={() => navigate('/documents')}>
            <div className="feature-icon" style={{ background: '#ff9800' }}>
              <img src="/images/placeholder/document-default.jpg" alt="Document" className="inline-icon" style={{width: 24, height: 24, borderRadius: "50%", objectFit: "cover", marginRight: 8}} />
            </div>
            <h3>Documents Techniques</h3>
            <p>Accéder aux comptes d'exploitation et itinéraires techniques</p>
          </div>

          {/* Carte Missions (pour agronomes) */}
          {user.user_type === 'AGRONOME' && (
            <div className="feature-card" onClick={() => alert('Mes missions - À venir')}>
              <div className="feature-icon" style={{ background: '#9c27b0' }}>
                💼
              </div>
              <h3>Mes Missions</h3>
              <p>Consulter et gérer vos missions en cours et historique</p>
            </div>
          )}

          {/* Carte Recrutement (pour exploitants) */}
          {user.user_type === 'EXPLOITANT' && (
            <div className="feature-card" onClick={() => alert('Recrutement - À venir')}>
              <div className="feature-icon" style={{ background: '#f44336' }}>
                👥
              </div>
              <h3>Recrutement</h3>
              <p>Recruter des agronomes et ouvriers agricoles</p>
            </div>
          )}

          {/* Carte Préventes (pour exploitants vérifiés) */}
          {user.user_type === 'EXPLOITANT' && (
            <div className="feature-card" onClick={() => alert('Préventes - À venir')}>
              <div className="feature-icon" style={{ background: '#00bcd4' }}>
                <img src="/images/hero/agriculture.jpg" alt="Statistiques" className="inline-icon" style={{width: 24, height: 24, borderRadius: "50%", objectFit: "cover", marginRight: 8}} />
              </div>
              <h3>Préventes Agricoles</h3>
              <p>Créer et gérer vos préventes de production</p>
            </div>
          )}
        </div>

        {/* Statistiques rapides */}
        <div style={{
          background: 'white',
          padding: '2rem',
          borderRadius: '12px',
          boxShadow: '0 2px 4px rgba(0,0,0,0.1)'
        }}>
          <h2 style={{ marginTop: 0, marginBottom: '1.5rem', color: '#333' }}>
            Statistiques
          </h2>
          <div style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))',
            gap: '1.5rem'
          }}>
            <div className="stat-box">
              <div className="stat-value">0</div>
              <div className="stat-label">Missions actives</div>
            </div>
            <div className="stat-box" onClick={() => navigate('/purchases')} style={{ cursor: 'pointer' }}>
              <div className="stat-value">0</div>
              <div className="stat-label">Documents achetés</div>
            </div>
            <div className="stat-box">
              <div className="stat-value">
                {user.phone_verified ? '✓' : '⚠'}
              </div>
              <div className="stat-label">Compte vérifié</div>
            </div>
            <div className="stat-box">
              <div className="stat-value">
                {new Date(user.created_at).toLocaleDateString('fr-FR', { month: 'short', year: 'numeric' })}
              </div>
              <div className="stat-label">Membre depuis</div>
            </div>
          </div>
        </div>

        {/* Informations importantes */}
        {!user.phone_verified && (
          <div style={{
            background: '#fff3cd',
            border: '1px solid #ffc107',
            padding: '1rem 1.5rem',
            borderRadius: '8px',
            marginTop: '2rem',
            display: 'flex',
            alignItems: 'center',
            gap: '1rem'
          }}>
            <span style={{ fontSize: '1.5rem' }}><img src="/images/hero/market.jpg" alt="Attention" className="inline-icon" style={{width: 20, height: 20, borderRadius: "50%", objectFit: "cover", marginRight: 8}} /></span>
            <div>
              <strong>Vérification requise</strong>
              <p style={{ margin: '0.25rem 0 0 0', fontSize: '0.9rem' }}>
                Veuillez vérifier votre numéro de téléphone pour accéder à toutes les fonctionnalités.
              </p>
            </div>
          </div>
        )}
      </div>

      <style>{`
        .feature-card {
          background: white;
          padding: 1.5rem;
          border-radius: 12px;
          box-shadow: 0 2px 8px rgba(0,0,0,0.1);
          cursor: pointer;
          transition: all 0.3s ease;
          text-align: center;
        }
        .feature-card:hover {
          transform: translateY(-4px);
          box-shadow: 0 4px 12px rgba(0,0,0,0.15);
        }
        .feature-icon {
          width: 60px;
          height: 60px;
          margin: 0 auto 1rem;
          border-radius: 50%;
          display: flex;
          align-items: center;
          justify-content: center;
          font-size: 2rem;
        }
        .feature-card h3 {
          margin: 0 0 0.5rem 0;
          color: #333;
          font-size: 1.2rem;
        }
        .feature-card p {
          margin: 0;
          color: #666;
          font-size: 0.9rem;
          line-height: 1.4;
        }
        .stat-box {
          text-align: center;
          padding: 1rem;
          background: #f8f9fa;
          border-radius: 8px;
        }
        .stat-value {
          font-size: 2rem;
          font-weight: bold;
          color: var(--primary);
          margin-bottom: 0.5rem;
        }
        .stat-label {
          font-size: 0.9rem;
          color: #666;
        }
        .spinner {
          border: 3px solid #f3f3f3;
          border-top: 3px solid var(--primary);
          border-radius: 50%;
          width: 40px;
          height: 40px;
          animation: spin 1s linear infinite;
          margin: 0 auto 1rem;
        }
        @keyframes spin {
          0% { transform: rotate(0deg); }
          100% { transform: rotate(360deg); }
        }
      `}</style>
    </Container>
  );
}
