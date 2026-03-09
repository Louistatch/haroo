import React, { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { motion, AnimatePresence } from "framer-motion";
import { me, chooseProfile } from "../api/auth";

const IconExploitant = ({ color }: { color: string }) => (
  <svg width="28" height="28" viewBox="0 0 24 24" fill="none">
    <path d="M3 18c0-4 3.5-7 9-7s9 3 9 7" stroke={color} strokeWidth="1.5" strokeLinecap="round"/>
    <path d="M12 11V4M9 7l3-3 3 3" stroke={color} strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round"/>
    <path d="M5 18c1-2 3-3 5-3h4c2 0 4 1 5 3" stroke={color} strokeWidth="1.5" strokeLinecap="round"/>
  </svg>
);
const IconAgronome = ({ color }: { color: string }) => (
  <svg width="28" height="28" viewBox="0 0 24 24" fill="none">
    <circle cx="12" cy="7" r="4" stroke={color} strokeWidth="1.5"/>
    <path d="M4 20c0-4 3.6-7 8-7s8 3 8 7" stroke={color} strokeWidth="1.5" strokeLinecap="round"/>
    <rect x="15" y="1" width="5" height="3" rx="1" stroke={color} strokeWidth="1.2"/>
  </svg>
);
const IconOuvrier = ({ color }: { color: string }) => (
  <svg width="28" height="28" viewBox="0 0 24 24" fill="none">
    <circle cx="12" cy="7" r="4" stroke={color} strokeWidth="1.5"/>
    <path d="M4 20c0-4 3.6-7 8-7s8 3 8 7" stroke={color} strokeWidth="1.5" strokeLinecap="round"/>
    <path d="M8 10l-2 4h2l-1 3M16 10l2 4h-2l1 3" stroke={color} strokeWidth="1.3" strokeLinecap="round"/>
  </svg>
);
const IconAcheteur = ({ color }: { color: string }) => (
  <svg width="28" height="28" viewBox="0 0 24 24" fill="none">
    <path d="M6 2L3 6v14a2 2 0 002 2h14a2 2 0 002-2V6l-3-4z" stroke={color} strokeWidth="1.5" strokeLinejoin="round"/>
    <path d="M3 6h18M16 10a4 4 0 01-8 0" stroke={color} strokeWidth="1.5" strokeLinecap="round"/>
  </svg>
);
const IconInstitution = ({ color }: { color: string }) => (
  <svg width="28" height="28" viewBox="0 0 24 24" fill="none">
    <path d="M3 21h18M3 10h18M5 6l7-3 7 3M4 10v11M20 10v11M8 10v11M12 10v11M16 10v11" stroke={color} strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round"/>
  </svg>
);

const USER_TYPES = [
  { value: "EXPLOITANT", label: "Exploitant Agricole", desc: "Je cultive la terre et gère mon exploitation", icon: IconExploitant, color: "#16a34a" },
  { value: "AGRONOME", label: "Agronome", desc: "Je conseille et accompagne les agriculteurs", icon: IconAgronome, color: "#7c3aed" },
  { value: "OUVRIER", label: "Ouvrier Agricole", desc: "Je cherche du travail dans l'agriculture", icon: IconOuvrier, color: "#d97706" },
  { value: "ACHETEUR", label: "Acheteur", desc: "J'achète des produits agricoles", icon: IconAcheteur, color: "#0891b2" },
  { value: "INSTITUTION", label: "Institution", desc: "Organisation publique ou privée", icon: IconInstitution, color: "#dc2626" },
];

export default function ChooseProfile() {
  const [selected, setSelected] = useState("");
  const [loading, setLoading] = useState(false);
  const [checking, setChecking] = useState(true);
  const [error, setError] = useState("");
  const [userName, setUserName] = useState("");
  const navigate = useNavigate();

  useEffect(() => {
    me()
      .then((user) => {
        if (user.user_type) {
          navigate("/home", { replace: true });
          return;
        }
        setUserName(user.first_name || user.email?.split("@")[0] || "");
      })
      .catch(() => navigate("/login", { replace: true }))
      .finally(() => setChecking(false));
  }, [navigate]);

  async function handleConfirm() {
    if (!selected) return;
    setLoading(true);
    setError("");
    try {
      await chooseProfile(selected);
      navigate("/home", { replace: true });
    } catch (err: any) {
      const msg = err?.response?.data?.error || "Erreur lors du choix du profil.";
      setError(msg);
    } finally {
      setLoading(false);
    }
  }

  if (checking) {
    return (
      <div style={{ minHeight: "100vh", display: "flex", alignItems: "center", justifyContent: "center", background: "var(--bg)" }}>
        <motion.div animate={{ rotate: 360 }} transition={{ duration: 0.8, repeat: Infinity, ease: "linear" }}
          style={{ width: 32, height: 32, border: "3px solid var(--border)", borderTop: "3px solid var(--primary)", borderRadius: "50%" }} />
      </div>
    );
  }

  const accent = selected ? (USER_TYPES.find(t => t.value === selected)?.color || "#16a34a") : "#16a34a";

  return (
    <div style={{ minHeight: "100vh", display: "flex", alignItems: "center", justifyContent: "center", background: "var(--bg)", padding: "2rem" }}>
      <motion.div
        initial={{ opacity: 0, y: 30 }} animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5, ease: [0.22, 1, 0.36, 1] }}
        style={{ width: "100%", maxWidth: 560 }}>

        <div style={{ textAlign: "center", marginBottom: "2.5rem" }}>
          <div style={{ width: 56, height: 56, background: "rgba(22,163,74,0.1)", border: "2px solid rgba(22,163,74,0.2)", borderRadius: "16px", display: "inline-flex", alignItems: "center", justifyContent: "center", marginBottom: "1.2rem" }}>
            <svg width="28" height="28" viewBox="0 0 24 24" fill="none">
              <path d="M12 2C6 2 3 5 3 8c0 4.5 7 10 7 10s7-5.5 7-10c0-3-3-6-7-6z" fill="#16a34a" fillOpacity="0.8"/>
              <circle cx="12" cy="8" r="2.5" fill="white" fillOpacity="0.9"/>
            </svg>
          </div>
          <h1 style={{ fontSize: "1.8rem", fontWeight: 800, color: "var(--text)", margin: "0 0 0.5rem", letterSpacing: "-0.03em" }}>
            Bienvenue{userName ? ` ${userName}` : ""} 👋
          </h1>
          <p style={{ color: "var(--text-muted)", fontSize: "1rem", margin: 0, lineHeight: 1.6 }}>
            Choisissez votre profil pour personnaliser votre expérience sur Haroo.
          </p>
        </div>

        <AnimatePresence>
          {error && (
            <motion.div initial={{ opacity: 0, y: -8 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0, y: -8 }}
              style={{ display: "flex", alignItems: "center", gap: "0.75rem", padding: "0.85rem 1rem", background: "rgba(239,68,68,0.08)", border: "1.5px solid rgba(239,68,68,0.25)", borderRadius: "12px", marginBottom: "1.5rem" }}>
              <span style={{ color: "#ef4444", fontSize: "0.9rem", fontWeight: 500 }}>{error}</span>
            </motion.div>
          )}
        </AnimatePresence>

        <div style={{ display: "flex", flexDirection: "column", gap: "0.75rem" }}>
          {USER_TYPES.map((t, i) => {
            const Icon = t.icon;
            const isSelected = selected === t.value;
            return (
              <motion.button key={t.value} type="button"
                onClick={() => setSelected(t.value)}
                initial={{ opacity: 0, y: 15 }} animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.3, delay: i * 0.06 }}
                whileTap={{ scale: 0.98 }}
                style={{
                  display: "flex", alignItems: "center", gap: "1rem",
                  padding: "1.1rem 1.2rem",
                  border: isSelected ? `2px solid ${t.color}` : "1.5px solid var(--border)",
                  borderRadius: "14px",
                  background: isSelected ? `${t.color}0D` : "var(--card)",
                  cursor: "pointer", textAlign: "left",
                  transition: "all 0.2s",
                  boxShadow: isSelected ? `0 0 0 3px ${t.color}18` : "none",
                }}>
                <div style={{
                  width: 48, height: 48, borderRadius: "12px",
                  background: isSelected ? `${t.color}18` : "var(--bg)",
                  border: `1.5px solid ${isSelected ? `${t.color}40` : "var(--border)"}`,
                  display: "flex", alignItems: "center", justifyContent: "center", flexShrink: 0,
                  transition: "all 0.2s",
                }}>
                  <Icon color={isSelected ? t.color : "var(--text-muted)"} />
                </div>
                <div style={{ flex: 1 }}>
                  <div style={{ fontSize: "0.95rem", fontWeight: 700, color: "var(--text)", marginBottom: "0.15rem" }}>{t.label}</div>
                  <div style={{ fontSize: "0.8rem", color: "var(--text-muted)", lineHeight: 1.4 }}>{t.desc}</div>
                </div>
                <div style={{
                  width: 22, height: 22, borderRadius: "50%",
                  border: isSelected ? `2px solid ${t.color}` : "2px solid var(--border)",
                  background: isSelected ? t.color : "transparent",
                  display: "flex", alignItems: "center", justifyContent: "center",
                  transition: "all 0.2s", flexShrink: 0,
                }}>
                  {isSelected && (
                    <svg width="12" height="12" viewBox="0 0 12 12" fill="none">
                      <path d="M2 6l3 3 5-5" stroke="white" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
                    </svg>
                  )}
                </div>
              </motion.button>
            );
          })}
        </div>

        <motion.button
          type="button" onClick={handleConfirm}
          disabled={!selected || loading}
          whileTap={{ scale: 0.98 }}
          style={{
            width: "100%", padding: "0.95rem", marginTop: "1.8rem",
            background: selected ? accent : "var(--border)",
            color: "white", border: "none", borderRadius: "12px",
            fontSize: "1rem", fontWeight: 700,
            cursor: selected && !loading ? "pointer" : "not-allowed",
            transition: "all 0.3s",
            boxShadow: selected ? `0 4px 16px ${accent}40` : "none",
            opacity: loading ? 0.7 : 1,
          }}>
          {loading ? "Enregistrement..." : "Confirmer mon profil"}
        </motion.button>
      </motion.div>
    </div>
  );
}
