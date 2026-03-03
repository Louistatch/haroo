import React, { useEffect, useState } from "react";
import { useNavigate, Link } from "react-router-dom";
import { motion } from "framer-motion";
import api from "../../api/auth";

const C = "#0e7490";

const IconReport = () => <svg width="22" height="22" viewBox="0 0 22 22" fill="none"><path d="M4 3h9l5 5v11a2 2 0 01-2 2H4a2 2 0 01-2-2V5a2 2 0 012-2z" stroke="currentColor" strokeWidth="1.5"/><path d="M13 3v5h5M7 10h8M7 13h6M7 16h3" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round"/></svg>;
const IconChart = () => <svg width="22" height="22" viewBox="0 0 22 22" fill="none"><path d="M3 17l5-5 4 4 7-8" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round"/><path d="M2 2v18h18" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round"/></svg>;
const IconAgro = () => <svg width="22" height="22" viewBox="0 0 22 22" fill="none"><circle cx="11" cy="7" r="4" stroke="currentColor" strokeWidth="1.5"/><path d="M3 20c0-4.4 3.6-8 8-8s8 3.6 8 8" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round"/><rect x="14" y="1" width="5" height="3" rx="1" stroke="currentColor" strokeWidth="1.2"/></svg>;
const IconDoc = () => <svg width="22" height="22" viewBox="0 0 22 22" fill="none"><path d="M4 3h9l5 5v11a2 2 0 01-2 2H4a2 2 0 01-2-2V5a2 2 0 012-2z" stroke="currentColor" strokeWidth="1.5"/><path d="M13 3v5h5M7 11h8M7 15h5" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round"/></svg>;
const IconShield = () => <svg width="22" height="22" viewBox="0 0 22 22" fill="none"><path d="M11 2L3 6v6c0 4.4 3.4 8.6 8 9.9 4.6-1.3 8-5.5 8-9.9V6l-8-4z" stroke="currentColor" strokeWidth="1.5" strokeLinejoin="round"/><path d="M8 11l2 2 4-4" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round"/></svg>;
const IconMap = () => <svg width="22" height="22" viewBox="0 0 22 22" fill="none"><path d="M1 5l6 2 8-4 6 3v14l-6-3-8 4-6-2V5z" stroke="currentColor" strokeWidth="1.5" strokeLinejoin="round"/><path d="M7 7v13M15 3v13" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round"/></svg>;
const IconSettings = () => <svg width="22" height="22" viewBox="0 0 22 22" fill="none"><circle cx="11" cy="11" r="3" stroke="currentColor" strokeWidth="1.5"/><path d="M11 2v2M11 18v2M2 11h2M18 11h2M4.9 4.9l1.4 1.4M15.7 15.7l1.4 1.4M4.9 17.1l1.4-1.4M15.7 6.3l1.4-1.4" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round"/></svg>;
const IconArrow = () => <svg width="14" height="14" viewBox="0 0 14 14" fill="none"><path d="M3 7h8M8 4l3 3-3 3" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round"/></svg>;
const IconLock = () => <svg width="16" height="16" viewBox="0 0 16 16" fill="none"><rect x="2" y="7" width="12" height="8" rx="1.5" stroke="currentColor" strokeWidth="1.3"/><path d="M5 7V5a3 3 0 016 0v2" stroke="currentColor" strokeWidth="1.3" strokeLinecap="round"/></svg>;

function getInitials(user: any) {
  return ((user.first_name?.[0] || "") + (user.last_name?.[0] || "")).toUpperCase() || user.username?.[0]?.toUpperCase() || "I";
}

export default function InstitutionDashboard({ user }: { user: any }) {
  const navigate = useNavigate();
  const [agronomeCount, setAgronomeCount] = useState<number | null>(null);
  const [docCount, setDocCount] = useState<number | null>(null);
  const memberDays = Math.floor((Date.now() - new Date(user.created_at).getTime()) / 86400000);

  useEffect(() => {
    api.get("/agronomists").then(r => setAgronomeCount(r.data?.count ?? r.data?.results?.length ?? 0)).catch(() => setAgronomeCount(0));
    api.get("/documents/").then(r => setDocCount(r.data?.count ?? r.data?.results?.length ?? 0)).catch(() => setDocCount(0));
  }, []);

  const stats = [
    { label: "Agronomes actifs", value: agronomeCount === null ? "…" : agronomeCount },
    { label: "Documents disponibles", value: docCount === null ? "…" : docCount },
    { label: "Jours membre", value: memberDays },
    { label: "Accès 2FA", value: user.two_factor_enabled ? "Activé" : "Requis" },
  ];

  const actions = [
    { label: "Rapports sectoriels", desc: "Vue d'ensemble du secteur", icon: <IconReport />, to: "/documents", color: C, bg: "#cffafe" },
    { label: "Analyses & KPIs", desc: "Indicateurs de performance", icon: <IconChart />, to: "/documents", color: "#2563eb", bg: "#dbeafe" },
    { label: "Annuaire agronomes", desc: "Professionnels certifiés", icon: <IconAgro />, to: "/agronomists", color: "#16a34a", bg: "#dcfce7" },
    { label: "Documents techniques", desc: "Catalogue réglementé", icon: <IconDoc />, to: "/documents", color: "#f59e0b", bg: "#fef3c7" },
    { label: "Couverture territoriale", desc: "Répartition géographique", icon: <IconMap />, to: "/agronomists", color: "#7c3aed", bg: "#ede9fe" },
    { label: "Sécurité & 2FA", desc: "Paramètres de sécurité avancés", icon: <IconSettings />, to: "/security", color: "#dc2626", bg: "#fee2e2" },
  ];

  const kpis = [
    { label: "Taux de validation agronomes", value: "—", desc: "Dossiers validés / soumis" },
    { label: "Volume transactions (mois)", value: "—", desc: "FCFA traités via FedaPay" },
    { label: "Missions accomplies", value: "—", desc: "Depuis le lancement" },
    { label: "Cantons couverts", value: "—", desc: "Sur 39 préfectures" },
  ];

  return (
    <div style={{ minHeight: "100vh", background: "var(--bg)", paddingTop: "5rem" }}>
      <div style={{ maxWidth: 1040, margin: "0 auto", padding: "2rem 1.5rem" }}>

        {!user.two_factor_enabled && (
          <motion.div initial={{ opacity: 0, y: -8 }} animate={{ opacity: 1, y: 0 }}
            style={{ display: "flex", alignItems: "center", gap: "0.75rem", padding: "0.9rem 1.25rem", background: "rgba(220,38,38,0.07)", border: "1.5px solid rgba(220,38,38,0.2)", borderRadius: "12px", marginBottom: "1.5rem" }}>
            <div style={{ color: "#dc2626", flexShrink: 0 }}><IconLock /></div>
            <div style={{ flex: 1 }}>
              <div style={{ fontWeight: 700, color: "#991b1b", fontSize: "0.88rem" }}>Authentification 2FA requise pour votre type de compte</div>
              <div style={{ color: "#b91c1c", fontSize: "0.78rem" }}>Activez la double authentification pour sécuriser l'accès institutionnel.</div>
            </div>
            <button onClick={() => navigate("/security")} style={{ background: "#dc2626", color: "white", border: "none", borderRadius: "8px", padding: "0.45rem 0.9rem", fontWeight: 700, fontSize: "0.78rem", cursor: "pointer", flexShrink: 0 }}>
              Activer 2FA
            </button>
          </motion.div>
        )}

        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.5 }}
          style={{ background: "linear-gradient(135deg, #083344 0%, #0e7490 60%, #0891b2 100%)", borderRadius: "20px", padding: "2.5rem", marginBottom: "1.75rem", position: "relative", overflow: "hidden" }}>
          <div style={{ position: "absolute", inset: 0, backgroundImage: "radial-gradient(circle at 75% 25%, rgba(255,255,255,0.07) 0%, transparent 55%)", pointerEvents: "none" }} />
          <div style={{ position: "absolute", right: 32, top: 32, opacity: 0.07 }}>
            <svg width="100" height="100" viewBox="0 0 100 100" fill="white"><path d="M50 5L15 25v25c0 22 14.5 42.5 35 50 20.5-7.5 35-28 35-50V25L50 5z"/></svg>
          </div>
          <div style={{ display: "flex", alignItems: "center", gap: "1.25rem", position: "relative" }}>
            <div style={{ width: 58, height: 58, borderRadius: "50%", background: "rgba(255,255,255,0.15)", border: "2px solid rgba(255,255,255,0.25)", display: "flex", alignItems: "center", justifyContent: "center", flexShrink: 0 }}>
              <span style={{ color: "white", fontWeight: 800, fontSize: "1.35rem" }}>{getInitials(user)}</span>
            </div>
            <div>
              <div style={{ color: "rgba(255,255,255,0.55)", fontSize: "0.78rem", fontWeight: 600, textTransform: "uppercase", letterSpacing: "0.07em", marginBottom: "0.2rem" }}>Accès Institutionnel</div>
              <h1 style={{ color: "white", fontSize: "clamp(1.3rem,3vw,1.9rem)", fontWeight: 800, margin: 0, letterSpacing: "-0.03em" }}>
                {user.first_name ? `${user.first_name} ${user.last_name}` : user.username}
              </h1>
              <div style={{ display: "flex", alignItems: "center", gap: "0.6rem", marginTop: "0.5rem", flexWrap: "wrap" }}>
                <span style={{ background: "rgba(255,255,255,0.15)", color: "white", padding: "0.18rem 0.6rem", borderRadius: "100px", fontSize: "0.75rem", fontWeight: 600 }}>Institution</span>
                <span style={{ display: "flex", alignItems: "center", gap: 4, background: user.two_factor_enabled ? "rgba(74,222,128,0.25)" : "rgba(248,113,113,0.25)", color: user.two_factor_enabled ? "#4ade80" : "#fca5a5", padding: "0.18rem 0.6rem", borderRadius: "100px", fontSize: "0.73rem", fontWeight: 600 }}>
                  <IconShield /> {user.two_factor_enabled ? "2FA activé" : "2FA requis"}
                </span>
              </div>
            </div>
          </div>
          <div style={{ display: "grid", gridTemplateColumns: "repeat(4, 1fr)", gap: "1rem", marginTop: "2rem", position: "relative" }}>
            {stats.map(s => (
              <div key={s.label} style={{ background: "rgba(255,255,255,0.08)", borderRadius: "12px", padding: "0.9rem 1rem" }}>
                <div style={{ color: "rgba(255,255,255,0.45)", fontSize: "0.68rem", fontWeight: 600, textTransform: "uppercase", letterSpacing: "0.05em", marginBottom: "0.25rem" }}>{s.label}</div>
                <div style={{ color: "white", fontWeight: 800, fontSize: "1.25rem", letterSpacing: "-0.02em" }}>{s.value}</div>
              </div>
            ))}
          </div>
        </motion.div>

        <motion.div initial={{ opacity: 0, y: 16 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.1 }}>
          <div style={{ fontSize: "0.72rem", fontWeight: 700, color: "var(--text-muted)", textTransform: "uppercase", letterSpacing: "0.08em", marginBottom: "1rem" }}>Actions rapides</div>
          <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fill, minmax(185px, 1fr))", gap: "0.85rem", marginBottom: "1.75rem" }}>
            {actions.map((a, i) => (
              <motion.div key={a.label}
                initial={{ opacity: 0, y: 12 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.14 + i * 0.05 }}
                whileHover={{ y: -3, boxShadow: "0 8px 24px rgba(0,0,0,0.09)" }}
                onClick={() => navigate(a.to)}
                style={{ background: "var(--surface)", border: "1px solid var(--border)", borderRadius: "16px", padding: "1.2rem", cursor: "pointer" }}>
                <div style={{ width: 42, height: 42, borderRadius: "11px", background: a.bg, color: a.color, display: "flex", alignItems: "center", justifyContent: "center", marginBottom: "0.8rem" }}>{a.icon}</div>
                <div style={{ fontWeight: 700, color: "var(--text)", fontSize: "0.9rem", marginBottom: "0.2rem" }}>{a.label}</div>
                <div style={{ color: "var(--text-muted)", fontSize: "0.75rem", lineHeight: 1.4 }}>{a.desc}</div>
              </motion.div>
            ))}
          </div>
        </motion.div>

        <motion.div initial={{ opacity: 0, y: 16 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.25 }}>
          <div style={{ fontSize: "0.72rem", fontWeight: 700, color: "var(--text-muted)", textTransform: "uppercase", letterSpacing: "0.08em", marginBottom: "1rem" }}>Indicateurs sectoriels (bêta)</div>
          <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fill, minmax(220px, 1fr))", gap: "1rem" }}>
            {kpis.map((k, i) => (
              <motion.div key={k.label}
                initial={{ opacity: 0, y: 12 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.28 + i * 0.05 }}
                style={{ background: "var(--surface)", border: "1px solid var(--border)", borderRadius: "14px", padding: "1.2rem" }}>
                <div style={{ fontSize: "0.72rem", fontWeight: 600, color: "var(--text-muted)", textTransform: "uppercase", letterSpacing: "0.05em", marginBottom: "0.5rem" }}>{k.label}</div>
                <div style={{ fontWeight: 800, fontSize: "1.6rem", color: "var(--text)", letterSpacing: "-0.03em", marginBottom: "0.25rem" }}>{k.value}</div>
                <div style={{ fontSize: "0.72rem", color: "var(--text-muted)" }}>{k.desc}</div>
              </motion.div>
            ))}
          </div>
        </motion.div>
      </div>
    </div>
  );
}
