import React from "react";
import { Link, useNavigate } from "react-router-dom";
import { Container } from "../components/Layout";

const services = [
  {
    icon: "📄",
    title: "Documents Techniques",
    desc: "Accédez à des comptes d'exploitation prévisionnels et itinéraires techniques adaptés à votre région et vos cultures.",
    btnLabel: "Explorer les documents",
    to: "/documents",
    public: true,
  },
  {
    icon: "🌿",
    title: "Annuaire des Agronomes",
    desc: "Trouvez des agronomes qualifiés et validés dans votre canton pour vous accompagner dans vos projets agricoles.",
    btnLabel: "Voir l'annuaire",
    to: "/agronomists",
    public: true,
  },
  {
    icon: "👥",
    title: "Recrutement",
    desc: "Recrutez des agronomes et ouvriers agricoles qualifiés pour vos missions et travaux saisonniers.",
    btnLabel: "Recruter maintenant",
    to: "/agronomists",
    public: true,
  },
  {
    icon: "🌾",
    title: "Préventes Agricoles",
    desc: "Sécurisez vos revenus en vendant votre production future avec un système d'acompte et de garantie.",
    btnLabel: "Créer une prévente",
    to: "/register",
    public: false,
  },
  {
    icon: "📈",
    title: "Analyses de Marché",
    desc: "Bénéficiez de prévisions de prix, analyses de demande et recommandations de marchés optimaux.",
    btnLabel: "Voir les analyses",
    to: "/register",
    public: false,
  },
  {
    icon: "🚚",
    title: "Optimisation Logistique",
    desc: "Optimisez vos itinéraires de transport et trouvez des transporteurs vérifiés au meilleur prix.",
    btnLabel: "Optimiser mes trajets",
    to: "/register",
    public: false,
  },
];

const features = [
  { icon: "🔒", title: "Sécurisé", desc: "Paiements sécurisés via Fedapay et protection de vos données" },
  { icon: "📍", title: "Géolocalisé", desc: "Services adaptés à votre région, préfecture et canton" },
  { icon: "⚡", title: "Rapide", desc: "Accès instantané aux services et transactions en temps réel" },
  { icon: "🤝", title: "Fiable", desc: "Professionnels vérifiés et système de notation transparent" },
];

const stats = [
  { value: "5", label: "Régions couvertes" },
  { value: "39", label: "Préfectures" },
  { value: "300+", label: "Cantons" },
  { value: "100%", label: "Togolais" },
];

export default function Landing() {
  const navigate = useNavigate();

  return (
    <div style={{ background: "#f8f9fa" }}>
      {/* Hero */}
      <div style={{
        background: "linear-gradient(135deg, #1b5e20 0%, #2e7d32 50%, #4caf50 100%)",
        color: "white",
        padding: "5rem 2rem",
        textAlign: "center",
      }}>
        <Container>
          <p style={{ fontSize: "1rem", letterSpacing: "3px", opacity: 0.8, marginBottom: "1rem", textTransform: "uppercase" }}>
            Plateforme Agricole
          </p>
          <h1 style={{ fontSize: "3.2rem", margin: "0 0 1.5rem 0", fontWeight: "800", lineHeight: 1.2 }}>
            Modernisez votre agriculture<br />au Togo
          </h1>
          <p style={{ fontSize: "1.25rem", margin: "0 0 2.5rem 0", opacity: 0.9, maxWidth: "700px", marginLeft: "auto", marginRight: "auto", lineHeight: 1.6 }}>
            Documents techniques, recrutement d'experts agronomes, préventes et analyses de marché — tout en un.
          </p>
          <div style={{ display: "flex", gap: "1rem", justifyContent: "center", flexWrap: "wrap" }}>
            <button onClick={() => navigate("/register")} style={{
              background: "white", color: "#2e7d32", padding: "1rem 2.5rem",
              border: "none", borderRadius: "8px", fontSize: "1.1rem",
              fontWeight: "700", cursor: "pointer", boxShadow: "0 4px 15px rgba(0,0,0,0.2)"
            }}>
              Créer un compte gratuit
            </button>
            <button onClick={() => navigate("/documents")} style={{
              background: "transparent", color: "white", padding: "1rem 2.5rem",
              border: "2px solid white", borderRadius: "8px", fontSize: "1.1rem",
              fontWeight: "600", cursor: "pointer"
            }}>
              Voir les documents
            </button>
          </div>
        </Container>
      </div>

      {/* Stats */}
      <div style={{ background: "#2e7d32", padding: "2rem" }}>
        <Container>
          <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(140px, 1fr))", gap: "1rem", textAlign: "center" }}>
            {stats.map((s) => (
              <div key={s.label}>
                <div style={{ fontSize: "2.2rem", fontWeight: "800", color: "white" }}>{s.value}</div>
                <div style={{ fontSize: "0.9rem", color: "rgba(255,255,255,0.8)" }}>{s.label}</div>
              </div>
            ))}
          </div>
        </Container>
      </div>

      {/* Services */}
      <Container>
        <div style={{ padding: "5rem 1rem" }}>
          <h2 style={{ textAlign: "center", fontSize: "2.5rem", marginBottom: "0.75rem", color: "#1b5e20" }}>
            Nos Services
          </h2>
          <p style={{ textAlign: "center", color: "#666", fontSize: "1.1rem", marginBottom: "3rem" }}>
            Des outils numériques conçus pour les agriculteurs togolais
          </p>
          <div style={{
            display: "grid",
            gridTemplateColumns: "repeat(auto-fit, minmax(300px, 1fr))",
            gap: "1.5rem",
          }}>
            {services.map((svc) => (
              <div key={svc.title} className="service-card">
                <div className="service-icon">{svc.icon}</div>
                <h3>{svc.title}</h3>
                <p>{svc.desc}</p>
                <Link to={svc.to} className={`service-btn${svc.public ? " public" : ""}`}>
                  {svc.btnLabel}
                </Link>
              </div>
            ))}
          </div>
        </div>
      </Container>

      {/* Pourquoi nous choisir */}
      <div style={{ background: "white", padding: "5rem 2rem" }}>
        <Container>
          <h2 style={{ textAlign: "center", fontSize: "2.5rem", marginBottom: "0.75rem", color: "#1b5e20" }}>
            Pourquoi nous choisir ?
          </h2>
          <p style={{ textAlign: "center", color: "#666", fontSize: "1.1rem", marginBottom: "3rem" }}>
            Une plateforme pensée pour le contexte agricole togolais
          </p>
          <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(220px, 1fr))", gap: "2rem" }}>
            {features.map((f) => (
              <div key={f.title} className="feature-box">
                <div style={{ fontSize: "3rem", marginBottom: "1rem" }}>{f.icon}</div>
                <h4>{f.title}</h4>
                <p>{f.desc}</p>
              </div>
            ))}
          </div>
        </Container>
      </div>

      {/* Comment ça marche */}
      <div style={{ background: "#f1f8e9", padding: "5rem 2rem" }}>
        <Container>
          <h2 style={{ textAlign: "center", fontSize: "2.5rem", marginBottom: "0.75rem", color: "#1b5e20" }}>
            Comment ça marche ?
          </h2>
          <p style={{ textAlign: "center", color: "#666", fontSize: "1.1rem", marginBottom: "3.5rem" }}>
            En 3 étapes simples
          </p>
          <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(250px, 1fr))", gap: "2rem" }}>
            {[
              { step: "1", title: "Créez votre compte", desc: "Inscrivez-vous avec votre numéro de téléphone togolais (+228) en moins de 2 minutes." },
              { step: "2", title: "Parcourez le catalogue", desc: "Accédez aux documents techniques, à l'annuaire des agronomes et aux services disponibles." },
              { step: "3", title: "Payez et téléchargez", desc: "Réglez via Mobile Money (Flooz, T-Money) et accédez instantanément à vos ressources." },
            ].map((item) => (
              <div key={item.step} style={{
                background: "white", borderRadius: "12px", padding: "2rem",
                textAlign: "center", boxShadow: "0 2px 8px rgba(0,0,0,0.07)"
              }}>
                <div style={{
                  width: "56px", height: "56px", borderRadius: "50%",
                  background: "linear-gradient(135deg, #2e7d32, #4caf50)",
                  color: "white", fontSize: "1.5rem", fontWeight: "800",
                  display: "flex", alignItems: "center", justifyContent: "center",
                  margin: "0 auto 1.25rem auto"
                }}>
                  {item.step}
                </div>
                <h4 style={{ color: "#1b5e20", fontSize: "1.2rem", marginBottom: "0.75rem" }}>{item.title}</h4>
                <p style={{ color: "#666", lineHeight: 1.6, margin: 0 }}>{item.desc}</p>
              </div>
            ))}
          </div>
        </Container>
      </div>

      {/* CTA */}
      <div style={{
        background: "linear-gradient(135deg, #1b5e20 0%, #2e7d32 100%)",
        color: "white", padding: "5rem 2rem", textAlign: "center"
      }}>
        <Container>
          <h2 style={{ fontSize: "2.5rem", marginBottom: "1rem", fontWeight: "800" }}>
            Prêt à moderniser votre agriculture ?
          </h2>
          <p style={{ fontSize: "1.2rem", marginBottom: "2.5rem", opacity: 0.9 }}>
            Rejoignez des centaines d'agriculteurs togolais sur la plateforme
          </p>
          <div style={{ display: "flex", gap: "1rem", justifyContent: "center", flexWrap: "wrap" }}>
            <button onClick={() => navigate("/register")} style={{
              background: "white", color: "#2e7d32", padding: "1rem 3rem",
              border: "none", borderRadius: "8px", fontSize: "1.2rem",
              fontWeight: "700", cursor: "pointer", boxShadow: "0 4px 15px rgba(0,0,0,0.2)"
            }}>
              Commencer gratuitement
            </button>
            <button onClick={() => navigate("/documents")} style={{
              background: "transparent", color: "white", padding: "1rem 3rem",
              border: "2px solid white", borderRadius: "8px", fontSize: "1.2rem",
              fontWeight: "600", cursor: "pointer"
            }}>
              Voir les documents
            </button>
          </div>
        </Container>
      </div>

      {/* Footer */}
      <div style={{ background: "#0a3d12", color: "white", padding: "2.5rem 2rem", textAlign: "center" }}>
        <Container>
          <p style={{ margin: "0 0 0.5rem 0", fontWeight: "700", fontSize: "1.1rem" }}>
            🌱 Plateforme Agricole Intelligente du Togo
          </p>
          <p style={{ margin: 0, opacity: 0.7, fontSize: "0.9rem" }}>
            © 2026 Haroo. Tous droits réservés. · Conçu pour les agriculteurs togolais
          </p>
        </Container>
      </div>

      <style>{`
        .service-card {
          background: white;
          padding: 2rem;
          border-radius: 16px;
          box-shadow: 0 2px 12px rgba(0,0,0,0.08);
          text-align: center;
          transition: transform 0.3s ease, box-shadow 0.3s ease;
          display: flex;
          flex-direction: column;
        }
        .service-card:hover {
          transform: translateY(-6px);
          box-shadow: 0 8px 24px rgba(0,0,0,0.13);
        }
        .service-icon {
          font-size: 3.5rem;
          margin-bottom: 1rem;
        }
        .service-card h3 {
          color: #1b5e20;
          margin: 0 0 0.75rem 0;
          font-size: 1.3rem;
        }
        .service-card p {
          color: #666;
          line-height: 1.6;
          margin-bottom: 1.5rem;
          flex: 1;
        }
        .service-btn {
          display: inline-block;
          background: #2e7d32;
          color: white;
          padding: 0.75rem 1.5rem;
          border: none;
          border-radius: 8px;
          font-size: 0.95rem;
          font-weight: 600;
          cursor: pointer;
          text-decoration: none;
          transition: background 0.3s ease;
          align-self: center;
        }
        .service-btn:hover {
          background: #1b5e20;
        }
        .service-btn.public {
          background: #388e3c;
        }
        .service-btn.public:hover {
          background: #2e7d32;
        }
        .feature-box {
          text-align: center;
          padding: 1.5rem;
          border-radius: 12px;
          transition: background 0.3s ease;
        }
        .feature-box:hover {
          background: #f1f8e9;
        }
        .feature-box h4 {
          color: #1b5e20;
          font-size: 1.2rem;
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
