import { useState } from "react";
import { useUser, useUpdateProfile } from "../hooks/useAuth";
import { useNavigate } from "react-router-dom";

export default function Settings() {
  const { data: user, isLoading } = useUser();
  const updateProfile = useUpdateProfile();
  const navigate = useNavigate();
  const [saved, setSaved] = useState(false);

  if (isLoading) return <div style={{ padding: "2rem", textAlign: "center" }}>Chargement...</div>;
  if (!user) { navigate("/login"); return null; }

  const handleNotifToggle = async (key: string, value: boolean) => {
    await updateProfile.mutateAsync({ [key]: value });
    setSaved(true);
    setTimeout(() => setSaved(false), 2000);
  };

  const cardStyle: React.CSSProperties = {
    background: "var(--card-bg, #fff)", borderRadius: 12, padding: "1.5rem",
    border: "1px solid var(--border, #e5e7eb)", marginBottom: "1rem",
  };

  return (
    <div style={{ maxWidth: 600, margin: "0 auto", padding: "2rem 1rem" }}>
      <h1 style={{ fontSize: "1.5rem", fontWeight: 700, marginBottom: "1.5rem", color: "var(--text)" }}>Paramètres</h1>

      {saved && (
        <div style={{ padding: "0.75rem 1rem", background: "#dcfce7", color: "#166534", borderRadius: 8, marginBottom: "1rem", fontSize: "0.875rem" }}>
          Paramètres sauvegardés
        </div>
      )}

      <div style={cardStyle}>
        <h2 style={{ fontSize: "1.1rem", fontWeight: 600, marginBottom: "1rem" }}>Compte</h2>
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", padding: "0.5rem 0" }}>
          <span>Email</span>
          <span style={{ color: "var(--text-secondary)" }}>{user.email || "Non défini"}</span>
        </div>
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", padding: "0.5rem 0" }}>
          <span>Téléphone</span>
          <span style={{ color: "var(--text-secondary)" }}>{user.phone_number || "Non défini"}</span>
        </div>
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", padding: "0.5rem 0" }}>
          <span>Type de compte</span>
          <span style={{ color: "var(--text-secondary)" }}>{user.user_type || "Non défini"}</span>
        </div>
      </div>

      <div style={cardStyle}>
        <h2 style={{ fontSize: "1.1rem", fontWeight: 600, marginBottom: "1rem" }}>Sécurité</h2>
        <button onClick={() => navigate("/security")}
          style={{ width: "100%", padding: "0.75rem", background: "var(--primary)", color: "#fff", border: "none", borderRadius: 8, cursor: "pointer", fontWeight: 600 }}>
          Gérer la sécurité et le 2FA
        </button>
      </div>

      <div style={cardStyle}>
        <h2 style={{ fontSize: "1.1rem", fontWeight: 600, marginBottom: "1rem" }}>Langue</h2>
        <p style={{ color: "var(--text-secondary)", fontSize: "0.875rem" }}>Français (seule langue disponible pour le moment)</p>
      </div>
    </div>
  );
}
