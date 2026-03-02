import React from "react";
import { useNavigate } from "react-router-dom";
import { Container } from "../components/Layout";

export default function Landing() {
  const navigate = useNavigate();

  return (
    <div style={{ background: '#f8f9fa' }}>
      {/* Hero Section */}
      <div style={{
        background: 'linear-gradient(135deg, #2e7d32 0%, #4caf50 100%)',
        color: 'white',
        padding: '4rem 2rem',
        textAlign: 'center'
      }}>
        <Container>
          <h1 style={{ 
            fontSize: '3rem', 
            margin: '0 0 1rem 0',
            fontWeight: 'bold'
          }}>
            Plateforme Agricole Intelligente du Togo
          </h1>
          <p style={{ 
            fontSize: '1.3rem', 
            margin: '0 0 2rem 0',
            opacity: 0.95,
            maxWidth: '800px',
            marginLeft: 'auto',
            marginRight: 'auto'
          }}>
            Modernisez votre agriculture avec des outils numériques: 
            documents techniques, recrutement d'experts, préventes et analyses de marché
          </p>
          <div style={{ display: 'flex', gap: '1rem', justifyContent: 'center', flexWrap: 'wrap' }}>
            <button 
              onClick={() => navigate('/register')}
              style={{
                background: 'white',
                color: '#2e7d32',
                padding: '1rem 2rem',
                border: 'none',
                borderRadius: '8px',
                fontSize: '1.1rem',
                fontWeight: 'bold',
                cursor: 'pointer',
                boxShadow: '0 4px 6px rgba(0,0,0,0.1)'
              }}
            >
              Créer un compte
            </button>
            <button 
              onClick={() => navigate('/login')}
              style={{
                background: 'transparent',
                color: 'white',
                padding: '1rem 2rem',
                border: '2px solid white',
                borderRadius: '8px',
                fontSize: '1.1rem',
                fontWeight: 'bold',
                cursor: 'pointer'
              }}
            >
              Se connecter
            </button>
          </div>
        </Container>
      </div>

      {/* Services Section */}
      <Container>
        <div style={{ padding: '4rem 1rem' }}>
          <h2 style={{ 
            textAlign: 'center', 
            fontSize: '2.5rem',
            marginBottom: '3rem',
            color: '#333'
          }}>
            Nos Services
          </h2>

          <div style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))',
            gap: '2rem',
            marginBottom: '3rem'
          }}>
            {/* Service 1: Documents */}
            <div className="service-card">
              <div className="service-icon"><img src="/images/placeholder/document-default.jpg" alt="Document" className="inline-icon" style={{width: 24, height: 24, borderRadius: "50%", objectFit: "cover", marginRight: 8}} /></div>
              <h3>Documents Techniques</h3>
              <p>
                Accédez à des comptes d'exploitation prévisionnels et itinéraires 
                techniques adaptés à votre région et vos cultures.
              </p>
              <button 
                className="service-btn"
                onClick={() => {
                  alert('Connectez-vous pour accéder aux documents techniques');
                  navigate('/login');
                }}
              >
                Explorer les documents
              </button>
            </div>

            {/* Service 2: Annuaire */}
            <div className="service-card">
              <div className="service-icon"><img src="/images/cultures/mais.jpg" alt="Culture" className="inline-icon" style={{width: 24, height: 24, borderRadius: "50%", objectFit: "cover", marginRight: 8}} /></div>
              <h3>Annuaire des Agronomes</h3>
              <p>
                Trouvez des agronomes qualifiés et validés dans votre canton 
                pour vous accompagner dans vos projets agricoles.
              </p>
              <button 
                className="service-btn public"
                onClick={() => alert('Annuaire public - Fonctionnalité à venir')}
              >
                Voir l'annuaire
              </button>
            </div>

            {/* Service 3: Recrutement */}
            <div className="service-card">
              <div className="service-icon">👥</div>
              <h3>Recrutement</h3>
              <p>
                Recrutez des agronomes et ouvriers agricoles qualifiés 
                pour vos missions et travaux saisonniers.
              </p>
              <button 
                className="service-btn"
                onClick={() => {
                  alert('Connectez-vous pour recruter');
                  navigate('/login');
                }}
              >
                Recruter maintenant
              </button>
            </div>

            {/* Service 4: Préventes */}
            <div className="service-card">
              <div className="service-icon"><img src="/images/hero/agriculture.jpg" alt="Statistiques" className="inline-icon" style={{width: 24, height: 24, borderRadius: "50%", objectFit: "cover", marginRight: 8}} /></div>
              <h3>Préventes Agricoles</h3>
              <p>
                Sécurisez vos revenus en vendant votre production future 
                avec un système d'acompte et de garantie.
              </p>
              <button 
                className="service-btn"
                onClick={() => {
                  alert('Connectez-vous pour créer une prévente');
                  navigate('/login');
                }}
              >
                Créer une prévente
              </button>
            </div>

            {/* Service 5: Analyses */}
            <div className="service-card">
              <div className="service-icon">📈</div>
              <h3>Analyses de Marché</h3>
              <p>
                Bénéficiez de prévisions de prix, analyses de demande 
                et recommandations de marchés optimaux.
              </p>
              <button 
                className="service-btn"
                onClick={() => {
                  alert('Connectez-vous pour accéder aux analyses');
                  navigate('/login');
                }}
              >
                Voir les analyses
              </button>
            </div>

            {/* Service 6: Logistique */}
            <div className="service-card">
              <div className="service-icon">🚚</div>
              <h3>Optimisation Logistique</h3>
              <p>
                Optimisez vos itinéraires de transport et trouvez 
                des transporteurs vérifiés au meilleur prix.
              </p>
              <button 
                className="service-btn"
                onClick={() => {
                  alert('Connectez-vous pour optimiser votre logistique');
                  navigate('/login');
                }}
              >
                Optimiser mes trajets
              </button>
            </div>
          </div>
        </div>
      </Container>

      {/* Features Section */}
      <div style={{ background: 'white', padding: '4rem 2rem' }}>
        <Container>
          <h2 style={{ 
            textAlign: 'center', 
            fontSize: '2.5rem',
            marginBottom: '3rem',
            color: '#333'
          }}>
            Pourquoi nous choisir ?
          </h2>

          <div style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))',
            gap: '2rem'
          }}>
            <div className="feature-box">
              <div style={{ fontSize: '3rem', marginBottom: '1rem' }}>✓</div>
              <h4>Sécurisé</h4>
              <p>Paiements sécurisés via Fedapay et protection de vos données</p>
            </div>

            <div className="feature-box">
              <div style={{ fontSize: '3rem', marginBottom: '1rem' }}><img src="/images/hero/agriculture.jpg" alt="Objectif" className="inline-icon" style={{width: 48, height: 48, borderRadius: "50%", objectFit: "cover"}} /></div>
              <h4>Géolocalisé</h4>
              <p>Services adaptés à votre région, préfecture et canton</p>
            </div>

            <div className="feature-box">
              <div style={{ fontSize: '3rem', marginBottom: '1rem' }}>⚡</div>
              <h4>Rapide</h4>
              <p>Accès instantané aux services et transactions en temps réel</p>
            </div>

            <div className="feature-box">
              <div style={{ fontSize: '3rem', marginBottom: '1rem' }}>🤝</div>
              <h4>Fiable</h4>
              <p>Professionnels vérifiés et système de notation transparent</p>
            </div>
          </div>
        </Container>
      </div>

      {/* CTA Section */}
      <div style={{
        background: 'linear-gradient(135deg, #2e7d32 0%, #4caf50 100%)',
        color: 'white',
        padding: '4rem 2rem',
        textAlign: 'center'
      }}>
        <Container>
          <h2 style={{ fontSize: '2.5rem', marginBottom: '1rem' }}>
            Prêt à moderniser votre agriculture ?
          </h2>
          <p style={{ fontSize: '1.2rem', marginBottom: '2rem', opacity: 0.95 }}>
            Rejoignez des centaines d'agriculteurs togolais qui utilisent déjà notre plateforme
          </p>
          <button 
            onClick={() => navigate('/register')}
            style={{
              background: 'white',
              color: '#2e7d32',
              padding: '1rem 3rem',
              border: 'none',
              borderRadius: '8px',
              fontSize: '1.2rem',
              fontWeight: 'bold',
              cursor: 'pointer',
              boxShadow: '0 4px 6px rgba(0,0,0,0.1)'
            }}
          >
            Commencer gratuitement
          </button>
        </Container>
      </div>

      {/* Footer */}
      <div style={{ 
        background: '#1b5e20', 
        color: 'white', 
        padding: '2rem',
        textAlign: 'center'
      }}>
        <Container>
          <p style={{ margin: 0, opacity: 0.9 }}>
            © 2026 Plateforme Agricole Intelligente du Togo. Tous droits réservés.
          </p>
        </Container>
      </div>

      <style>{`
        .service-card {
          background: white;
          padding: 2rem;
          border-radius: 12px;
          box-shadow: 0 4px 6px rgba(0,0,0,0.1);
          text-align: center;
          transition: transform 0.3s ease;
        }
        .service-card:hover {
          transform: translateY(-8px);
          box-shadow: 0 8px 12px rgba(0,0,0,0.15);
        }
        .service-icon {
          font-size: 4rem;
          margin-bottom: 1rem;
        }
        .service-card h3 {
          color: #2e7d32;
          margin: 0 0 1rem 0;
          font-size: 1.5rem;
        }
        .service-card p {
          color: #666;
          line-height: 1.6;
          margin-bottom: 1.5rem;
        }
        .service-btn {
          background: #2e7d32;
          color: white;
          padding: 0.75rem 1.5rem;
          border: none;
          border-radius: 6px;
          font-size: 1rem;
          cursor: pointer;
          transition: background 0.3s ease;
        }
        .service-btn:hover {
          background: #1b5e20;
        }
        .service-btn.public {
          background: #4caf50;
        }
        .service-btn.public:hover {
          background: #388e3c;
        }
        .feature-box {
          text-align: center;
          padding: 2rem;
        }
        .feature-box h4 {
          color: #2e7d32;
          font-size: 1.3rem;
          margin: 0 0 0.5rem 0;
        }
        .feature-box p {
          color: #666;
          margin: 0;
          line-height: 1.5;
        }
      `}</style>
    </div>
  );
}
