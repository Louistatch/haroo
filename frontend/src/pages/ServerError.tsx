import { Link } from "react-router-dom";

export default function ServerError() {
  return (
    <div style={{ minHeight: "80vh", display: "flex", flexDirection: "column", alignItems: "center", justifyContent: "center", padding: "2rem", textAlign: "center" }}>
      <div style={{ fontSize: "6rem", fontWeight: 700, color: "#ef4444", lineHeight: 1 }}>500</div>
      <h1 style={{ fontSize: "1.5rem", margin: "1rem 0 0.5rem", color: "var(--text)" }}>Erreur serveur</h1>
      <p style={{ color: "var(--text-secondary)", maxWidth: 400, marginBottom: "1.5rem" }}>
        Une erreur inattendue s'est produite. Veuillez réessayer plus tard.
      </p>
      <Link to="/" style={{ padding: "0.75rem 2rem", background: "var(--primary)", color: "#fff", borderRadius: 8, textDecoration: "none", fontWeight: 600 }}>
        Retour à l'accueil
      </Link>
    </div>
  );
}
