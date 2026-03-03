import React, { useEffect, useState } from "react";
import { useNavigate, Link } from "react-router-dom";
import { motion } from "framer-motion";
import { me } from "../api/auth";
import { fetchPurchaseHistory } from "../api/purchases";

const IconDoc = () => <svg width="22" height="22" viewBox="0 0 22 22" fill="none"><path d="M4 3h9l5 5v11a2 2 0 01-2 2H4a2 2 0 01-2-2V5a2 2 0 012-2z" stroke="currentColor" strokeWidth="1.5"/><path d="M13 3v5h5M7 11h8M7 15h5" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round"/></svg>;
const IconUser = () => <svg width="22" height="22" viewBox="0 0 22 22" fill="none"><circle cx="11" cy="7" r="4" stroke="currentColor" strokeWidth="1.5"/><path d="M3 20c0-4.4 3.6-8 8-8s8 3.6 8 8" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round"/></svg>;
const IconBag = () => <svg width="22" height="22" viewBox="0 0 22 22" fill="none"><path d="M3 6h16l-1.5 12H4.5L3 6z" stroke="currentColor" strokeWidth="1.5" strokeLinejoin="round"/><path d="M8 6V4a3 3 0 016 0v2" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round"/></svg>;
const IconSettings = () => <svg width="22" height="22" viewBox="0 0 22 22" fill="none"><circle cx="11" cy="11" r="3" stroke="currentColor" strokeWidth="1.5"/><path d="M11 2v2M11 18v2M2 11h2M18 11h2M4.9 4.9l1.4 1.4M15.7 15.7l1.4 1.4M4.9 17.1l1.4-1.4M15.7 6.3l1.4-1.4" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round"/></svg>;
const IconBriefcase = () => <svg width="22" height="22" viewBox="0 0 22 22" fill="none"><rect x="2" y="7" width="18" height="13" rx="2" stroke="currentColor" strokeWidth="1.5"/><path d="M7 7V5a2 2 0 012-2h4a2 2 0 012 2v2M11 12v4M9 14h4" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round"/></svg>;
const IconChart = () => <svg width="22" height="22" viewBox="0 0 22 22" fill="none"><path d="M3 17l5-5 4 4 7-8" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round"/><path d="M2 2v18h18" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round"/></svg>;
const IconWarning = () => <svg width="18" height="18" viewBox="0 0 18 18" fill="none"><path d="M9 7v4M9 13h.01" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round"/><path d="M7.9 2.6L1.4 14A1.5 1.5 0 002.7 16h12.6a1.5 1.5 0 001.3-2.2L10.1 2.6a1.3 1.3 0 00-2.2 0z" stroke="currentColor" strokeWidth="1.5" strokeLinejoin="round"/></svg>;
const IconCheck = () => <svg width="14" height="14" viewBox="0 0 14 14" fill="none"><path d="M2 7l3.5 3.5L12 3" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/></svg>;

const USER_TYPE_CONFIG: Record<string, { label: string; color: string; bg: string }> = {
  EXPLOITANT: { label: "Exploitant Agricole", color: "#16a34a", bg: "#dcfce7" },
  AGRONOME:   { label: "Agronome",            color: "#2563eb", bg: "#dbeafe" },
  OUVRIER:    { label: "Ouvrier Agricole",    color: "#d97706", bg: "#fef3c7" },
  ACHETEUR:   { label: "Acheteur",            color: "#7c3aed", bg: "#ede9fe" },
  INSTITUTION:{ label: "Institution",         color: "#0e7490", bg: "#cffafe" },
};

function getInitials(user: any) {
  const f = user.first_name?.[0] || "";
  const l = user.last_name?.[0] || "";
  return (f + l).toUpperCase() || user.username?.[0]?.toUpperCase() || "?";
}

export default function Home() {
  const [user, setUser] = useState<any>(null);
  const [purchaseCount, setPurchaseCount] = useState<number | null>(null);
  const [loading, setLoading] = useState(true);
  const navigate = useNavigate();

  useEffect(() => {
    me()
      .then(async (u) => {
        setUser(u);
        try {
          const token = localStorage.getItem("access_token") || "";
          const hist = await fetchPurchaseHistory({ page_size: 1 }, token);
          setPurchaseCount(hist.count);
        } catch { setPurchaseCount(0); }
      })
      .catch(() => navigate("/login"))
      .finally(() => setLoading(false));
  }, [navigate]);

  if (loading) {
    return (
      <div style={{ minHeight: "100vh", display: "flex", alignItems: "center", justifyContent: "center", background: "var(--bg)" }}>
        <motion.div animate={{ rotate: 360 }} transition={{ duration: 0.8, repeat: Infinity, ease: "linear" }}
          style={{ width: 32, height: 32, border: "3px solid var(--border)", borderTop: "3px solid var(--primary)", borderRadius: "50%" }} />
      </div>
    );
  }

  if (!user) return null;

  const typeConf = USER_TYPE_CONFIG[user.user_type] || { label: user.user_type, color: "#6366f1", bg: "#ede9fe" };

  const actions = [
    { label: "Documents", desc: "Parcourir le catalogue technique", icon: <IconDoc />, to: "/documents", color: "#f59e0b", bg: "#fffbeb" },
    { label: "Agronomes", desc: "Contacter un expert certifié", icon: <IconUser />, to: "/agronomists", color: "#16a34a", bg: "#f0fdf4" },
    { label: "Mes Achats", desc: `${purchaseCount ?? "—"} document${purchaseCount !== 1 ? "s" : ""} acheté${purchaseCount !== 1 ? "s" : ""}`, icon: <IconBag />, to: "/purchases", color: "#7c3aed", bg: "#faf5ff" },
    { label: "Mon Profil", desc: "Modifier vos informations", icon: <IconSettings />, to: "/me", color: "#0e7490", bg: "#ecfeff" },
    ...(user.user_type === "AGRONOME" ? [{ label: "Mes Missions", desc: "Gérer vos missions", icon: <IconBriefcase />, to: "/dashboard", color: "#6366f1", bg: "#eef2ff" }] : []),
    ...(user.user_type === "EXPLOITANT" ? [{ label: "Statistiques", desc: "Analyses de marché", icon: <IconChart />, to: "/dashboard", color: "#0ea5e9", bg: "#f0f9ff" }] : []),
  ];

  const memberDays = Math.floor((Date.now() - new Date(user.created_at).getTime()) / 86400000);

  return (
    <div style={{ minHeight: "100vh", background: "var(--bg)", paddingTop: "5rem" }}>
      <div style={{ maxWidth: 960, margin: "0 auto", padding: "2rem 1.5rem" }}>

        {/* phone not verified banner */}
        {!user.phone_verified && (
          <motion.div initial={{ opacity: 0, y: -8 }} animate={{ opacity: 1, y: 0 }}
            style={{ display: "flex", alignItems: "center", gap: "0.75rem", padding: "0.9rem 1.25rem", background: "rgba(245,158,11,0.08)", border: "1.5px solid rgba(245,158,11,0.25)", borderRadius: "12px", marginBottom: "1.5rem" }}>
            <div style={{ color: "#d97706", flexShrink: 0 }}><IconWarning /></div>
            <div>
              <div style={{ fontWeight: 700, color: "#92400e", fontSize: "0.9rem" }}>Téléphone non vérifié</div>
              <div style={{ color: "#b45309", fontSize: "0.82rem" }}>Vérifiez votre numéro pour accéder à toutes les fonctionnalités.</div>
            </div>
          </motion.div>
        )}

        {/* hero welcome */}
        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.5 }}
          style={{ background: "linear-gradient(135deg, #14532d 0%, #15803d 60%, #16a34a 100%)", borderRadius: "20px", padding: "2.5rem 2.5rem 2rem", marginBottom: "1.75rem", position: "relative", overflow: "hidden" }}>
          <div style={{ position: "absolute", inset: 0, backgroundImage: "radial-gradient(circle at 80% 20%, rgba(255,255,255,0.07) 0%, transparent 50%)", pointerEvents: "none" }} />
          <div style={{ display: "flex", alignItems: "center", gap: "1.25rem" }}>
            <div style={{ width: 60, height: 60, borderRadius: "50%", background: "rgba(255,255,255,0.15)", border: "2px solid rgba(255,255,255,0.3)", display: "flex", alignItems: "center", justifyContent: "center", flexShrink: 0 }}>
              <span style={{ color: "white", fontWeight: 800, fontSize: "1.4rem", letterSpacing: "-0.02em" }}>{getInitials(user)}</span>
            </div>
            <div>
              <div style={{ color: "rgba(255,255,255,0.65)", fontSize: "0.82rem", fontWeight: 600, marginBottom: "0.25rem", textTransform: "uppercase", letterSpacing: "0.06em" }}>
                Bienvenue
              </div>
              <h1 style={{ color: "white", fontSize: "clamp(1.4rem, 3vw, 2rem)", fontWeight: 800, margin: 0, letterSpacing: "-0.03em" }}>
                {user.first_name ? `${user.first_name} ${user.last_name}` : user.username}
              </h1>
              <div style={{ display: "flex", alignItems: "center", gap: "0.75rem", marginTop: "0.5rem", flexWrap: "wrap" }}>
                <span style={{ background: "rgba(255,255,255,0.15)", color: "white", padding: "0.2rem 0.65rem", borderRadius: "100px", fontSize: "0.78rem", fontWeight: 600 }}>
                  {typeConf.label}
                </span>
                {user.phone_verified && (
                  <span style={{ display: "flex", alignItems: "center", gap: "4px", color: "rgba(255,255,255,0.8)", fontSize: "0.78rem", fontWeight: 500 }}>
                    <span style={{ width: 16, height: 16, background: "rgba(74,222,128,0.3)", borderRadius: "50%", display: "flex", alignItems: "center", justifyContent: "center" }}><IconCheck /></span>
                    Vérifié
                  </span>
                )}
              </div>
            </div>
          </div>

          {/* stats row */}
          <div style={{ display: "grid", gridTemplateColumns: "repeat(3, 1fr)", gap: "1rem", marginTop: "2rem" }}>
            {[
              { label: "Documents achetés", value: purchaseCount ?? "—" },
              { label: "Jours membre", value: memberDays },
              { label: "Statut compte", value: user.phone_verified ? "Vérifié" : "En attente" },
            ].map((s) => (
              <div key={s.label} style={{ background: "rgba(255,255,255,0.08)", borderRadius: "12px", padding: "0.9rem 1rem" }}>
                <div style={{ color: "rgba(255,255,255,0.5)", fontSize: "0.72rem", fontWeight: 600, textTransform: "uppercase", letterSpacing: "0.05em", marginBottom: "0.3rem" }}>{s.label}</div>
                <div style={{ color: "white", fontWeight: 800, fontSize: "1.3rem", letterSpacing: "-0.02em" }}>{s.value}</div>
              </div>
            ))}
          </div>
        </motion.div>

        {/* actions grid */}
        <motion.div initial={{ opacity: 0, y: 16 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.45, delay: 0.1 }}>
          <div style={{ fontSize: "0.75rem", fontWeight: 700, color: "var(--text-muted)", textTransform: "uppercase", letterSpacing: "0.08em", marginBottom: "1rem" }}>
            Accès rapide
          </div>
          <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fill, minmax(200px, 1fr))", gap: "0.85rem" }}>
            {actions.map((a, i) => (
              <motion.div key={a.label}
                initial={{ opacity: 0, y: 12 }} animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.35, delay: 0.12 + i * 0.06 }}
                whileHover={{ y: -3, boxShadow: "0 8px 24px rgba(0,0,0,0.1)" }}
                onClick={() => navigate(a.to)}
                style={{ background: "var(--surface)", border: "1px solid var(--border)", borderRadius: "16px", padding: "1.35rem", cursor: "pointer", transition: "box-shadow 0.25s" }}>
                <div style={{ width: 44, height: 44, borderRadius: "12px", background: a.bg, color: a.color, display: "flex", alignItems: "center", justifyContent: "center", marginBottom: "0.85rem" }}>
                  {a.icon}
                </div>
                <div style={{ fontWeight: 700, color: "var(--text)", fontSize: "0.95rem", marginBottom: "0.25rem" }}>{a.label}</div>
                <div style={{ color: "var(--text-muted)", fontSize: "0.78rem", lineHeight: 1.4 }}>{a.desc}</div>
              </motion.div>
            ))}
          </div>
        </motion.div>

        {/* profile snapshot */}
        <motion.div initial={{ opacity: 0, y: 16 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.45, delay: 0.3 }}
          style={{ marginTop: "1.75rem", background: "var(--surface)", border: "1px solid var(--border)", borderRadius: "16px", padding: "1.5rem" }}>
          <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", marginBottom: "1.25rem" }}>
            <div style={{ fontWeight: 700, color: "var(--text)", fontSize: "0.95rem" }}>Informations du compte</div>
            <Link to="/me" style={{ color: "var(--primary)", fontWeight: 600, fontSize: "0.82rem", textDecoration: "none" }}>Modifier →</Link>
          </div>
          <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "0.75rem" }}>
            {[
              ["Téléphone", user.phone_number],
              ["Type de compte", typeConf.label],
              ["Nom d'utilisateur", user.username],
              ["Membre depuis", new Date(user.created_at).toLocaleDateString("fr-FR", { month: "long", year: "numeric" })],
            ].map(([k, v]) => (
              <div key={k} style={{ padding: "0.75rem", background: "var(--bg)", borderRadius: "10px" }}>
                <div style={{ fontSize: "0.72rem", fontWeight: 600, color: "var(--text-muted)", textTransform: "uppercase", letterSpacing: "0.05em", marginBottom: "0.25rem" }}>{k}</div>
                <div style={{ fontWeight: 600, color: "var(--text)", fontSize: "0.88rem" }}>{v}</div>
              </div>
            ))}
          </div>
        </motion.div>
      </div>
    </div>
  );
}
