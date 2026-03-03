import React, { useEffect, useState } from "react";
import { useNavigate, Link } from "react-router-dom";
import { motion } from "framer-motion";

const C = "#d97706";

const IconSearch = () => <svg width="22" height="22" viewBox="0 0 22 22" fill="none"><circle cx="10" cy="10" r="7" stroke="currentColor" strokeWidth="1.5"/><path d="M15.5 15.5L20 20" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round"/></svg>;
const IconContract = () => <svg width="22" height="22" viewBox="0 0 22 22" fill="none"><path d="M4 3h9l5 5v11a2 2 0 01-2 2H4a2 2 0 01-2-2V5a2 2 0 012-2z" stroke="currentColor" strokeWidth="1.5"/><path d="M13 3v5h5M7 10h8M7 13h8M7 16h5" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round"/><path d="M14 15l1.5 1.5 3-3" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round"/></svg>;
const IconClock = () => <svg width="22" height="22" viewBox="0 0 22 22" fill="none"><circle cx="11" cy="11" r="9" stroke="currentColor" strokeWidth="1.5"/><path d="M11 7v4l2.5 2.5" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round"/></svg>;
const IconProfile = () => <svg width="22" height="22" viewBox="0 0 22 22" fill="none"><circle cx="11" cy="7" r="4" stroke="currentColor" strokeWidth="1.5"/><path d="M3 20c0-4.4 3.6-8 8-8s8 3.6 8 8" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round"/></svg>;
const IconLocation = () => <svg width="22" height="22" viewBox="0 0 22 22" fill="none"><path d="M11 2C7.7 2 5 4.7 5 8c0 4.5 6 12 6 12s6-7.5 6-12c0-3.3-2.7-6-6-6z" stroke="currentColor" strokeWidth="1.5" strokeLinejoin="round"/><circle cx="11" cy="8" r="2.5" stroke="currentColor" strokeWidth="1.5"/></svg>;
const IconBag = () => <svg width="22" height="22" viewBox="0 0 22 22" fill="none"><path d="M3 6h16l-1.5 12H4.5L3 6z" stroke="currentColor" strokeWidth="1.5" strokeLinejoin="round"/><path d="M8 6V4a3 3 0 016 0v2" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round"/></svg>;
const IconSettings = () => <svg width="22" height="22" viewBox="0 0 22 22" fill="none"><circle cx="11" cy="11" r="3" stroke="currentColor" strokeWidth="1.5"/><path d="M11 2v2M11 18v2M2 11h2M18 11h2M4.9 4.9l1.4 1.4M15.7 15.7l1.4 1.4M4.9 17.1l1.4-1.4M15.7 6.3l1.4-1.4" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round"/></svg>;
const IconArrow = () => <svg width="14" height="14" viewBox="0 0 14 14" fill="none"><path d="M3 7h8M8 4l3 3-3 3" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round"/></svg>;

function getInitials(user: any) {
  return ((user.first_name?.[0] || "") + (user.last_name?.[0] || "")).toUpperCase() || user.username?.[0]?.toUpperCase() || "O";
}

export default function OuvrierDashboard({ user }: { user: any }) {
  const navigate = useNavigate();
  const memberDays = Math.floor((Date.now() - new Date(user.created_at).getTime()) / 86400000);

  const stats = [
    { label: "Offres disponibles", value: "—" },
    { label: "Contrats actifs", value: "0" },
    { label: "Heures ce mois", value: "0 h" },
    { label: "Jours membre", value: memberDays },
  ];

  const actions = [
    { label: "Chercher des offres", desc: "Emplois agricoles disponibles", icon: <IconSearch />, to: "/missions", color: C, bg: "#fef3c7" },
    { label: "Mes contrats", desc: "Suivi de vos missions", icon: <IconContract />, to: "/missions", color: "#16a34a", bg: "#dcfce7" },
    { label: "Pointer mes heures", desc: "Enregistrer le temps travaillé", icon: <IconClock />, to: "/missions", color: "#2563eb", bg: "#dbeafe" },
    { label: "Ma zone", desc: "Cantons où vous intervenez", icon: <IconLocation />, to: "/me", color: "#7c3aed", bg: "#ede9fe" },
    { label: "Mon profil", desc: "Compétences et disponibilités", icon: <IconProfile />, to: "/me", color: "#0ea5e9", bg: "#e0f2fe" },
    { label: "Paramètres", desc: "Sécurité du compte", icon: <IconSettings />, to: "/security", color: "#6366f1", bg: "#eef2ff" },
  ];

  const tips = [
    { title: "Complétez votre profil", desc: "Un profil complet attire plus d'employeurs — ajoutez vos compétences et disponibilités.", cta: "Mon profil", to: "/me" },
    { title: "Définissez votre zone", desc: "Indiquez les cantons où vous êtes disponibles pour recevoir des offres correspondantes.", cta: "Configurer", to: "/me" },
    { title: "Parcourez les offres", desc: "Des exploitants cherchent activement des ouvriers agricoles dans votre région.", cta: "Voir les offres", to: "/missions" },
  ];

  return (
    <div style={{ minHeight: "100vh", background: "var(--bg)", paddingTop: "5rem" }}>
      <div style={{ maxWidth: 1040, margin: "0 auto", padding: "2rem 1.5rem" }}>

        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.5 }}
          style={{ background: "linear-gradient(135deg, #78350f 0%, #b45309 60%, #d97706 100%)", borderRadius: "20px", padding: "2.5rem", marginBottom: "1.75rem", position: "relative", overflow: "hidden" }}>
          <div style={{ position: "absolute", inset: 0, backgroundImage: "radial-gradient(circle at 78% 22%, rgba(255,255,255,0.07) 0%, transparent 55%)", pointerEvents: "none" }} />
          <div style={{ display: "flex", alignItems: "center", gap: "1.25rem", position: "relative" }}>
            <div style={{ width: 58, height: 58, borderRadius: "50%", background: "rgba(255,255,255,0.15)", border: "2px solid rgba(255,255,255,0.25)", display: "flex", alignItems: "center", justifyContent: "center", flexShrink: 0 }}>
              <span style={{ color: "white", fontWeight: 800, fontSize: "1.35rem" }}>{getInitials(user)}</span>
            </div>
            <div>
              <div style={{ color: "rgba(255,255,255,0.55)", fontSize: "0.78rem", fontWeight: 600, textTransform: "uppercase", letterSpacing: "0.07em", marginBottom: "0.2rem" }}>Tableau de bord</div>
              <h1 style={{ color: "white", fontSize: "clamp(1.3rem,3vw,1.9rem)", fontWeight: 800, margin: 0, letterSpacing: "-0.03em" }}>
                {user.first_name ? `${user.first_name} ${user.last_name}` : user.username}
              </h1>
              <div style={{ marginTop: "0.5rem" }}>
                <span style={{ background: "rgba(255,255,255,0.15)", color: "white", padding: "0.18rem 0.6rem", borderRadius: "100px", fontSize: "0.75rem", fontWeight: 600 }}>Ouvrier Agricole</span>
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
          <div style={{ fontSize: "0.72rem", fontWeight: 700, color: "var(--text-muted)", textTransform: "uppercase", letterSpacing: "0.08em", marginBottom: "1rem" }}>Premiers pas sur Haroo</div>
          <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fill, minmax(280px, 1fr))", gap: "1rem" }}>
            {tips.map((tip, i) => (
              <motion.div key={tip.title}
                initial={{ opacity: 0, y: 12 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.28 + i * 0.06 }}
                style={{ background: "var(--surface)", border: "1px solid var(--border)", borderRadius: "16px", padding: "1.35rem" }}>
                <div style={{ display: "flex", alignItems: "center", gap: 8, marginBottom: "0.5rem" }}>
                  <div style={{ width: 22, height: 22, borderRadius: "50%", background: `${C}20`, color: C, display: "flex", alignItems: "center", justifyContent: "center", fontSize: "0.75rem", fontWeight: 800 }}>{i + 1}</div>
                  <div style={{ fontWeight: 700, color: "var(--text)", fontSize: "0.9rem" }}>{tip.title}</div>
                </div>
                <div style={{ color: "var(--text-muted)", fontSize: "0.8rem", lineHeight: 1.55, marginBottom: "1rem" }}>{tip.desc}</div>
                <button onClick={() => navigate(tip.to)} style={{ background: `${C}15`, color: C, border: `1.5px solid ${C}30`, borderRadius: "8px", padding: "0.5rem 0.9rem", fontWeight: 700, fontSize: "0.8rem", cursor: "pointer", display: "flex", alignItems: "center", gap: 6 }}>
                  {tip.cta} <IconArrow />
                </button>
              </motion.div>
            ))}
          </div>
        </motion.div>
      </div>
    </div>
  );
}
