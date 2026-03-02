import React, { useState, useEffect } from 'react';
import axios from 'axios';
import '../styles/dashboard.css';

interface DashboardData {
  user: {
    first_name: string;
    last_name: string;
    user_type: string;
  };
  profile: {
    superficie_totale?: string;
    cultures_actuelles?: string[];
    statut_verification?: string;
    note_moyenne?: string;
    nombre_avis?: number;
  };
  stats: {
    missions_actives: number;
    missions_terminees: number;
    documents_achetes: number;
    montant_depense: string;
  };
}

export default function Dashboard() {
  const [data, setData] = useState<DashboardData | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchDashboardData();
  }, []);

  const fetchDashboardData = async () => {
    try {
      const token = localStorage.getItem('access_token');
      const response = await axios.get('http://localhost:8000/api/v1/users/me', {
        headers: { Authorization: `Bearer ${token}` }
      });
      setData(response.data);
    } catch (error) {
      console.error('Erreur lors du chargement du dashboard:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="loading-container">
        <div className="spinner"></div>
        <p>Chargement de votre tableau de bord...</p>
      </div>
    );
  }

  if (!data) {
    return <div className="error-message">Erreur lors du chargement des données</div>;
  }

  return (
    <div className="dashboard-page">
      <div className="dashboard-header">
        <div className="welcome-section">
          <h1>👋 Bienvenue, {data.user.first_name}!</h1>
          <p>Voici un aperçu de votre activité sur la plateforme</p>
        </div>
        
        {data.profile.statut_verification && (
          <div className={`verification-badge ${data.profile.statut_verification.toLowerCase()}`}>
            {data.profile.statut_verification === 'VERIFIE' ? '✓ Exploitant Vérifié' : 
             data.profile.statut_verification === 'EN_ATTENTE' ? '⏳ Vérification en cours' :
             '❌ Non vérifié'}
          </div>
        )}
      </div>

      <div className="dashboard-grid">
        {/* Statistiques rapides */}
        <div className="stats-row">
          <div className="stat-card green">
            <div className="stat-icon">📋</div>
            <div className="stat-content">
              <h3>{data.stats.missions_actives}</h3>
              <p>Missions actives</p>
            </div>
          </div>

          <div className="stat-card blue">
            <div className="stat-icon">✅</div>
            <div className="stat-content">
              <h3>{data.stats.missions_terminees}</h3>
              <p>Missions terminées</p>
            </div>
          </div>

          <div className="stat-card orange">
            <div className="stat-icon">📄</div>
            <div className="stat-content">
              <h3>{data.stats.documents_achetes}</h3>
              <p>Documents achetés</p>
            </div>
          </div>

          <div className="stat-card purple">
            <div className="stat-icon">💰</div>
            <div className="stat-content">
              <h3>{parseInt(data.stats.montant_depense).toLocaleString()} FCFA</h3>
              <p>Total dépensé</p>
            </div>
          </div>
        </div>

        {/* Informations du profil */}
        <div className="profile-section">
          <h2>📊 Votre Profil</h2>
          <div className="profile-details">
            {data.profile.superficie_totale && (
              <div className="detail-item">
                <span className="label">🌾 Superficie totale:</span>
                <span className="value">{data.profile.superficie_totale} hectares</span>
              </div>
            )}

            {data.profile.cultures_actuelles && data.profile.cultures_actuelles.length > 0 && (
              <div className="detail-item">
                <span className="label">🌱 Cultures actuelles:</span>
                <div className="cultures-list">
                  {data.profile.cultures_actuelles.map((culture, index) => (
                    <span key={index} className="culture-tag">{culture}</span>
                  ))}
                </div>
              </div>
            )}

            {data.profile.note_moyenne !== undefined && (
              <div className="detail-item">
                <span className="label">⭐ Note moyenne:</span>
                <span className="value">
                  {parseFloat(data.profile.note_moyenne).toFixed(1)} / 5.0
                  {data.profile.nombre_avis && ` (${data.profile.nombre_avis} avis)`}
                </span>
              </div>
            )}
          </div>
        </div>

        {/* Actions rapides */}
        <div className="quick-actions">
          <h2>⚡ Actions rapides</h2>
          <div className="actions-grid">
            <a href="/documents" className="action-card">
              <div className="action-icon">📚</div>
              <h3>Documents</h3>
              <p>Parcourir le catalogue</p>
            </a>

            <a href="/agronomists" className="action-card">
              <div className="action-icon">👨‍🌾</div>
              <h3>Agronomes</h3>
              <p>Trouver un expert</p>
            </a>

            <a href="/missions" className="action-card">
              <div className="action-icon">📋</div>
              <h3>Missions</h3>
              <p>Gérer vos missions</p>
            </a>

            <a href="/me" className="action-card">
              <div className="action-icon">⚙️</div>
              <h3>Profil</h3>
              <p>Modifier vos infos</p>
            </a>
          </div>
        </div>

        {/* Activité récente */}
        <div className="recent-activity">
          <h2>📅 Activité récente</h2>
          <div className="activity-list">
            <div className="activity-item">
              <div className="activity-icon">📄</div>
              <div className="activity-content">
                <p className="activity-title">Document acheté</p>
                <p className="activity-date">Il y a 2 jours</p>
              </div>
            </div>

            <div className="activity-item">
              <div className="activity-icon">✅</div>
              <div className="activity-content">
                <p className="activity-title">Mission terminée</p>
                <p className="activity-date">Il y a 5 jours</p>
              </div>
            </div>

            <div className="activity-item">
              <div className="activity-icon">⭐</div>
              <div className="activity-content">
                <p className="activity-title">Nouvel avis reçu</p>
                <p className="activity-date">Il y a 1 semaine</p>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
