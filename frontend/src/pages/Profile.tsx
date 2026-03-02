import React, { useEffect, useState } from "react";
import { me } from "../api/auth";
import { Container } from "../components/Layout";

export default function Profile() {
  const [user, setUser] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    me()
      .then(setUser)
      .catch(() => {
        localStorage.removeItem("access_token");
        localStorage.removeItem("refresh_token");
        window.location.href = "/login";
      })
      .finally(() => setLoading(false));
  }, []);

  if (loading) return (
    <Container>
      <div style={{ textAlign: 'center', padding: '2rem' }}>
        Chargement...
      </div>
    </Container>
  );

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
      <div className="profile-card" style={{ maxWidth: '800px', margin: '2rem auto' }}>
        <h2 style={{ marginBottom: '2rem', color: 'var(--primary)' }}>Mon Profil</h2>
        
        <div style={{ display: 'grid', gap: '1.5rem' }}>
          {/* Informations de base */}
          <section>
            <h3 style={{ fontSize: '1.1rem', marginBottom: '1rem', color: '#333' }}>
              Informations personnelles
            </h3>
            <div style={{ display: 'grid', gap: '0.75rem' }}>
              <div className="info-row">
                <strong>Nom complet:</strong>
                <span>{user.first_name} {user.last_name}</span>
              </div>
              <div className="info-row">
                <strong>Nom d'utilisateur:</strong>
                <span>{user.username}</span>
              </div>
              <div className="info-row">
                <strong>Email:</strong>
                <span>{user.email || 'Non renseigné'}</span>
              </div>
              <div className="info-row">
                <strong>Téléphone:</strong>
                <span>{user.phone_number}</span>
              </div>
              <div className="info-row">
                <strong>Type de compte:</strong>
                <span style={{ 
                  background: 'var(--primary)', 
                  color: 'white', 
                  padding: '0.25rem 0.75rem', 
                  borderRadius: '4px',
                  fontSize: '0.9rem'
                }}>
                  {getUserTypeLabel(user.user_type)}
                </span>
              </div>
            </div>
          </section>

          {/* Sécurité */}
          <section>
            <h3 style={{ fontSize: '1.1rem', marginBottom: '1rem', color: '#333' }}>
              Sécurité
            </h3>
            <div style={{ display: 'grid', gap: '0.75rem' }}>
              <div className="info-row">
                <strong>Téléphone vérifié:</strong>
                <span style={{ color: user.phone_verified ? 'green' : 'orange' }}>
                  {user.phone_verified ? '✓ Vérifié' : '⚠ Non vérifié'}
                </span>
              </div>
              <div className="info-row">
                <strong>Authentification 2FA:</strong>
                <span style={{ color: user.two_factor_enabled ? 'green' : '#666' }}>
                  {user.two_factor_enabled ? '✓ Activée' : 'Désactivée'}
                </span>
              </div>
            </div>
          </section>

          {/* Dates */}
          <section>
            <h3 style={{ fontSize: '1.1rem', marginBottom: '1rem', color: '#333' }}>
              Informations du compte
            </h3>
            <div style={{ display: 'grid', gap: '0.75rem' }}>
              <div className="info-row">
                <strong>Membre depuis:</strong>
                <span>{new Date(user.created_at).toLocaleDateString('fr-FR', {
                  day: '2-digit',
                  month: 'long',
                  year: 'numeric'
                })}</span>
              </div>
              <div className="info-row">
                <strong>Dernière mise à jour:</strong>
                <span>{new Date(user.updated_at).toLocaleDateString('fr-FR', {
                  day: '2-digit',
                  month: 'long',
                  year: 'numeric'
                })}</span>
              </div>
            </div>
          </section>

          {/* Actions */}
          <section style={{ marginTop: '1rem' }}>
            <button 
              style={{
                background: 'var(--primary)',
                color: 'white',
                padding: '0.75rem 1.5rem',
                border: 'none',
                borderRadius: '8px',
                cursor: 'pointer',
                fontSize: '1rem',
                marginRight: '1rem'
              }}
              onClick={() => alert('Fonctionnalité de modification à venir')}
            >
              Modifier le profil
            </button>
            <button 
              style={{
                background: '#dc3545',
                color: 'white',
                padding: '0.75rem 1.5rem',
                border: 'none',
                borderRadius: '8px',
                cursor: 'pointer',
                fontSize: '1rem'
              }}
              onClick={() => {
                localStorage.removeItem("access_token");
                localStorage.removeItem("refresh_token");
                window.location.href = "/login";
              }}
            >
              Se déconnecter
            </button>
          </section>
        </div>
      </div>

      <style>{`
        .info-row {
          display: flex;
          justify-content: space-between;
          align-items: center;
          padding: 0.75rem;
          background: #f8f9fa;
          border-radius: 6px;
        }
        .info-row strong {
          color: #555;
          font-weight: 500;
        }
        .profile-card section {
          padding: 1.5rem;
          background: white;
          border-radius: 8px;
          box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
      `}</style>
    </Container>
  );
}
