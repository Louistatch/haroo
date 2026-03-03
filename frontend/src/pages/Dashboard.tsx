import React, { useState, useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { me } from '../api/auth';
import '../styles/dashboard.css';

export default function Dashboard() {
  const [user, setUser] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const navigate = useNavigate();

  useEffect(() => {
    me()
      .then(setUser)
      .catch(() => navigate('/login'))
      .finally(() => setLoading(false));
  }, [navigate]);

  if (loading) {
    return (
      <div className="loading-container">
        <div className="spinner"></div>
        <p>Chargement de votre tableau de bord...</p>
      </div>
    );
  }

  if (!user) return null;

  const getUserTypeLabel = (type: string) => {
    const types: Record<string, string> = {
      EXPLOITANT: 'Exploitant Agricole',
      AGRONOME: 'Agronome',
      OUVRIER: 'Ouvrier Agricole',
      ACHETEUR: 'Acheteur',
      INSTITUTION: 'Institution',
      ADMIN: 'Administrateur',
    };
    return types[type] || type;
  };

  const profile = user.exploitant_profile || user.agronome_profile || user.ouvrier_profile || null;

  return (
    <div className="dashboard-page">
      <div className="dashboard-header">
        <div className="welcome-section">
          <h1>Bienvenue, {user.first_name || user.username}!</h1>
          <p>Voici un aperçu de votre activité sur la plateforme</p>
        </div>
        <div className="user-badge">
          <span className="badge-type">{getUserTypeLabel(user.user_type)}</span>
          {user.phone_verified && <span className="badge-verified">✓ Téléphone vérifié</span>}
        </div>
      </div>

      <div className="dashboard-grid">
        <div className="stats-row">
          <div className="stat-card green">
            <div className="stat-icon">📋</div>
            <div className="stat-content">
              <h3>0</h3>
              <p>Missions actives</p>
            </div>
          </div>
          <div className="stat-card blue">
            <div className="stat-icon">✅</div>
            <div className="stat-content">
              <h3>0</h3>
              <p>Missions terminées</p>
            </div>
          </div>
          <div className="stat-card orange">
            <div className="stat-icon">📄</div>
            <div className="stat-content">
              <h3>0</h3>
              <p>Documents achetés</p>
            </div>
          </div>
          <div className="stat-card purple">
            <div className="stat-icon">💰</div>
            <div className="stat-content">
              <h3>0 FCFA</h3>
              <p>Total dépensé</p>
            </div>
          </div>
        </div>

        <div className="profile-section">
          <h2>👤 Votre Profil</h2>
          <div className="profile-details">
            <div className="detail-item">
              <span className="label">Nom complet:</span>
              <span className="value">{user.first_name} {user.last_name}</span>
            </div>
            <div className="detail-item">
              <span className="label">Téléphone:</span>
              <span className="value">{user.phone_number}</span>
            </div>
            <div className="detail-item">
              <span className="label">Type de compte:</span>
              <span className="value">{getUserTypeLabel(user.user_type)}</span>
            </div>
            {profile?.superficie_totale && (
              <div className="detail-item">
                <span className="label">Superficie totale:</span>
                <span className="value">{profile.superficie_totale} hectares</span>
              </div>
            )}
            {profile?.note_moyenne !== undefined && (
              <div className="detail-item">
                <span className="label">Note moyenne:</span>
                <span className="value">
                  {parseFloat(profile.note_moyenne).toFixed(1)} / 5.0
                  {profile.nombre_avis > 0 && ` (${profile.nombre_avis} avis)`}
                </span>
              </div>
            )}
          </div>
        </div>

        <div className="quick-actions">
          <h2>⚡ Actions rapides</h2>
          <div className="actions-grid">
            <Link to="/documents" className="action-card">
              <div className="action-icon">📚</div>
              <h3>Documents</h3>
              <p>Parcourir le catalogue</p>
            </Link>
            <Link to="/agronomists" className="action-card">
              <div className="action-icon">🌿</div>
              <h3>Agronomes</h3>
              <p>Trouver un expert</p>
            </Link>
            <Link to="/purchases" className="action-card">
              <div className="action-icon">🛍️</div>
              <h3>Mes Achats</h3>
              <p>Historique des achats</p>
            </Link>
            <Link to="/me" className="action-card">
              <div className="action-icon">⚙️</div>
              <h3>Profil</h3>
              <p>Modifier vos infos</p>
            </Link>
          </div>
        </div>

        <div className="security-section">
          <h2>🔒 Sécurité</h2>
          <div className="security-items">
            <div className="security-item">
              <span className="security-label">Téléphone vérifié:</span>
              <span className={user.phone_verified ? 'status-ok' : 'status-warn'}>
                {user.phone_verified ? '✓ Vérifié' : '⚠ Non vérifié'}
              </span>
            </div>
            <div className="security-item">
              <span className="security-label">Authentification 2FA:</span>
              <span className={user.two_factor_enabled ? 'status-ok' : 'status-muted'}>
                {user.two_factor_enabled ? '✓ Activée' : 'Désactivée'}
              </span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
