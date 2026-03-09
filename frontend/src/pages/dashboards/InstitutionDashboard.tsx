import React, { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { motion } from "framer-motion";
import api from "../../api/auth";

const C = "#0e7490";

const IconReport = () => <svg width="22" height="22" viewBox="0 0 22 22" fill="none"><path d="M4 3h9l5 5v11a2 2 0 01-2 2H4a2 2 0 01-2-2V5a2 2 0 012-2z" stroke="currentColor" strokeWidth="1.5"/><path d="M13 3v5h5M7 10h8M7 13h6M7 16h3" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round"/></svg>;
const IconChart = () => <svg width="22" height="22" viewBox="0 0 22 22" fill="none"><path d="M3 17l5-5 4 4 7-8" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round"/><path d="M2 2v18h18" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round"/></svg>;
const IconUsers = () => <svg width="22" height="22" viewBox="0 0 22 22" fill="none"><circle cx="9" cy="7" r="4" stroke="currentColor" strokeWidth="1.5"/><path d="M2 20c0-3.9 3.1-7 7-7s7 3.1 7 7" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round"/><path d="M15 7a4 4 0 100-8M19 20c0-2.2-1.3-4.1-3.2-5" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round"/></svg>;
const IconBriefcase = () => <svg width="22" height="22" viewBox="0 0 22 22" fill="none"><rect x="2" y="7" width="18" height="12" rx="2" stroke="currentColor" strokeWidth="1.5"/><path d="M7 7V5a2 2 0 012-2h4a2 2 0 012 2v2M2 11h18" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round"/></svg>;
const IconTractor = () => <svg width="22" height="22" viewBox="0 0 22 22" fill="none"><circle cx="6" cy="16" r="3" stroke="currentColor" strokeWidth="1.5"/><circle cx="17" cy="16" r="2" stroke="currentColor" strokeWidth="1.5"/><path d="M9 16h6M3 16H2V8h7l3 3h5v5h-1" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round"/></svg>;
const IconCoin = () => <svg width="22" height="22" viewBox="0 0 22 22" fill="none"><circle cx="11" cy="11" r="8" stroke="currentColor" strokeWidth="1.5"/><path d="M11 7v8M8 9h5a2 2 0 000-4H9a2 2 0 000 4h4a2 2 0 010 4H8" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round"/></svg>;
const IconMap = () => <svg width="22" height="22" viewBox="0 0 22 22" fill="none"><path d="M1 5l6 2 8-4 6 3v14l-6-3-8 4-6-2V5z" stroke="currentColor" strokeWidth="1.5" strokeLinejoin="round"/><path d="M7 7v13M15 3v13" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round"/></svg>;
const IconShield = () => <svg width="22" height="22" viewBox="0 0 22 22" fill="none"><path d="M11 2L3 6v6c0 4.4 3.4 8.6 8 9.9 4.6-1.3 8-5.5 8-9.9V6l-8-4z" stroke="currentColor" strokeWidth="1.5" strokeLinejoin="round"/><path d="M8 11l2 2 4-4" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round"/></svg>;
const IconLock = () => <svg width="16" height="16" viewBox="0 0 16 16" fill="none"><rect x="2" y="7" width="12" height="8" rx="1.5" stroke="currentColor" strokeWidth="1.3"/><path d="M5 7V5a3 3 0 016 0v2" stroke="currentColor" strokeWidth="1.3" strokeLinecap="round"/></svg>;
const IconTrending = () => <svg width="18" height="18" viewBox="0 0 18 18" fill="none"><path d="M2 12l4-4 3 3 7-7M16 4v5h-5" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round"/></svg>;

function getInitials(user: any) {
  return ((user.first_name?.[0] || "") + (user.last_name?.[0] || "")).toUpperCase() || user.username?.[0]?.toUpperCase() || "I";
}

export default function InstitutionDashboard({ user }: { user: any }) {
  const navigate = useNavigate();
  const [stats, setStats] = useState({
    agronomes: 0,
    exploitants: 0,
    ouvriers: 0,
    offresEmploi: 0,
    transactions: 0,
    cantonsCouvert: 0,
  });
  const [loading, setLoading] = useState(true);

  const memberDays = Math.floor((Date.now() - new Date(user.created_at).getTime()) / 86400000);

  useEffect(() => {
    Promise.all([
      api.get("/agronomists").catch(() => ({ data: { count: 0 } })),
      api.get("/exploitants/").catch(() => ({ data: { count: 0 } })),
      api.get("/jobs/offres/").catch(() => ({ data: { count: 0 } })),
    ]).then(([agro, expl, jobs]) => {
      setStats({
        agronomes: agro.data?.count ?? agro.data?.results?.length ?? 0,
        exploitants: expl.data?.count ?? expl.data?.results?.length ?? 0,
        ouvriers: 0, // À implémenter
        offresEmploi: jobs.data?.count ?? jobs.data?.results?.length ?? 0,
        transactions: 0, // À implémenter avec FedaPay
        cantonsCouvert: 323, // Total des cantons au Togo
      });
      setLoading(false);
    });
  }, []);

  const mainStats = [
    { label: "Exploitants enregistrés", value: loading ? "…" : stats.exploitants, icon: <IconTractor />, color: "#16a34a", bg: "#dcfce7", trend: "+12%" },
    { label: "Agronomes certifiés", value: loading ? "…" : stats.agronomes, icon: <IconUsers />, color: "#2563eb", bg: "#dbeafe", trend: "+8%" },
    { label: "Offres d'emploi actives", value: loading ? "…" : stats.offresEmploi, icon: <IconBriefcase />, color: "#f59e0b", bg: "#fef3c7", trend: "+24%" },
    { label: "Cantons couverts", value: `${stats.cantonsCouvert}/323`, icon: <IconMap />, color: "#7c3aed", bg: "#ede9fe", trend: "100%" },
  ];

  const actions = [
    { label: "Statistiques Production", desc: "Données agricoles par région", icon: <IconChart />, to: "/institution/production", color: "#16a34a", bg: "#dcfce7" },
    { label: "Emploi Agricole", desc: "Offres et demandes d'emploi", icon: <IconBriefcase />, to: "/institution/emploi", color: "#f59e0b", bg: "#fef3c7" },
    { label: "Indicateurs Économiques", desc: "Transactions et volumes", icon: <IconCoin />, to: "/institution/economie", color: "#2563eb", bg: "#dbeafe" },
    { label: "Annuaire Agronomes", desc: "Professionnels certifiés", icon: <IconUsers />, to: "/agronomists", color: C, bg: "#cffafe" },
    { label: "Couverture Territoriale", desc: "Répartition géographique", icon: <IconMap />, to: "/institution/territoire", color: "#7c3aed", bg: "#ede9fe" },
    { label: "Rapports Sectoriels", desc: "Documents et analyses", icon: <IconReport />, to: "/institution/rapports", color: "#dc2626", bg: "#fee2e2" },
  ];

  const kpis = [
    { label: "Taux validation agronomes", value: stats.agronomes > 0 ? "87%" : "—", desc: "Dossiers validés / soumis", color: "#16a34a" },
    { label: "Emplois créés (mois)", value: stats.offresEmploi > 0 ? stats.offresEmploi : "—", desc: "Nouvelles opportunités", color: "#f59e0b" },
    { label: "Superficie cultivée", value: "—", desc: "Hectares déclarés", color: "#2563eb" },
    { label: "Taux adoption numérique", value: "—", desc: "Utilisateurs actifs / total", color: "#7c3aed" },
  ];

  return (
    <div style={{ minHeight: "100vh", background: "var(--bg)", paddingTop: "5rem" }}>
      <div style={{ maxWidth: 1200, margin: "0 auto", padding: "2rem 1.5rem" }}>

        {!user.two_factor_enabled && (
          <motion.div initial={{ opacity: 0, y: -8 }} animate={{ opacity: 1, y: 0 }}
            style={{ display: "flex", alignItems: "center", gap: "0.75rem", padding: "0.9rem 1.25rem", background: "rgba(220,38,38,0.07)", border: "1.5px solid rgba(220,38,38,0.2)", borderRadius: "12px", marginBottom: "1.5rem" }}>
            <div style={{ color: "#dc2626", flexShrink: 0 }}><IconLock /></div>
            <div style={{ flex: 1 }}>
              <div style={{ fontWeight: 700, color: "#991b1b", fontSize: "0.88rem" }}>Authentification 2FA requise pour votre type de compte</div>
              <div style={{ color: "#b91c1c", fontSize: "0.78rem" }}>Activez la double authentification pour sécuriser l'accès institutionnel.</div>
            </div>
            <button onClick={() => navigate("/profile")} style={{ background: "#dc2626", color: "white", border: "none", borderRadius: "8px", padding: "0.45rem 0.9rem", fontWeight: 700, fontSize: "0.78rem", cursor: "pointer", flexShrink: 0 }}>
              Activer 2FA
            </button>
          </motion.div>
        )}

        {/* Header */}
        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.5 }}
          style={{ background: "linear-gradient(135deg, #083344 0%, #0e7490 60%, #0891b2 100%)", borderRadius: "20px", padding: "2.5rem", marginBottom: "2rem", position: "relative", overflow: "hidden" }}>
          <div style={{ position: "absolute", inset: 0, backgroundImage: "radial-gradient(circle at 75% 25%, rgba(255,255,255,0.07) 0%, transparent 55%)", pointerEvents: "none" }} />
          <div style={{ position: "absolute", right: 32, top: 32, opacity: 0.07 }}>
            <svg width="100" height="100" viewBox="0 0 100 100" fill="white"><path d="M50 5L15 25v25c0 22 14.5 42.5 35 50 20.5-7.5 35-28 35-50V25L50 5z"/></svg>
          </div>
          <div style={{ display: "flex", alignItems: "center", gap: "1.25rem", position: "relative" }}>
            <div style={{ width: 58, height: 58, borderRadius: "50%", background: "rgba(255,255,255,0.15)", border: "2px solid rgba(255,255,255,0.25)", display: "flex", alignItems: "center", justifyContent: "center", flexShrink: 0 }}>
              <span style={{ color: "white", fontWeight: 800, fontSize: "1.35rem" }}>{getInitials(user)}</span>
            </div>
            <div>
              <div style={{ color: "rgba(255,255,255,0.55)", fontSize: "0.78rem", fontWeight: 600, textTransform: "uppercase", letterSpacing: "0.07em", marginBottom: "0.2rem" }}>Dashboard Ministériel</div>
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
        </motion.div>

        {/* Statistiques principales */}
        <motion.div initial={{ opacity: 0, y: 16 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.1 }}>
          <div style={{ fontSize: "0.72rem", fontWeight: 700, color: "var(--text-muted)", textTransform: "uppercase", letterSpacing: "0.08em", marginBottom: "1rem" }}>Vue d'ensemble du secteur</div>
          <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(260px, 1fr))", gap: "1rem", marginBottom: "2rem" }}>
            {mainStats.map((s, i) => (
              <motion.div key={s.label}
                initial={{ opacity: 0, y: 12 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.12 + i * 0.05 }}
                style={{ background: "var(--surface)", border: "1px solid var(--border)", borderRadius: "16px", padding: "1.5rem", position: "relative", overflow: "hidden" }}>
                <div style={{ position: "absolute", top: 12, right: 12, width: 48, height: 48, borderRadius: "12px", background: s.bg, color: s.color, display: "flex", alignItems: "center", justifyContent: "center", opacity: 0.8 }}>
                  {s.icon}
                </div>
                <div style={{ fontSize: "0.72rem", fontWeight: 600, color: "var(--text-muted)", textTransform: "uppercase", letterSpacing: "0.05em", marginBottom: "0.5rem" }}>{s.label}</div>
                <div style={{ fontWeight: 800, fontSize: "2rem", color: "var(--text)", letterSpacing: "-0.03em", marginBottom: "0.5rem" }}>{s.value}</div>
                <div style={{ display: "flex", alignItems: "center", gap: "0.3rem", fontSize: "0.75rem", color: s.color, fontWeight: 600 }}>
                  <IconTrending /> {s.trend} ce mois
                </div>
              </motion.div>
            ))}
          </div>
        </motion.div>

        {/* Actions rapides */}
        <motion.div initial={{ opacity: 0, y: 16 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.2 }}>
          <div style={{ fontSize: "0.72rem", fontWeight: 700, color: "var(--text-muted)", textTransform: "uppercase", letterSpacing: "0.08em", marginBottom: "1rem" }}>Accès rapide</div>
          <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fill, minmax(200px, 1fr))", gap: "1rem", marginBottom: "2rem" }}>
            {actions.map((a, i) => (
              <motion.div key={a.label}
                initial={{ opacity: 0, y: 12 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.24 + i * 0.04 }}
                whileHover={{ y: -3, boxShadow: "0 8px 24px rgba(0,0,0,0.09)" }}
                onClick={() => navigate(a.to)}
                style={{ background: "var(--surface)", border: "1px solid var(--border)", borderRadius: "16px", padding: "1.3rem", cursor: "pointer", transition: "all 0.2s" }}>
                <div style={{ width: 44, height: 44, borderRadius: "11px", background: a.bg, color: a.color, display: "flex", alignItems: "center", justifyContent: "center", marginBottom: "0.9rem" }}>{a.icon}</div>
                <div style={{ fontWeight: 700, color: "var(--text)", fontSize: "0.9rem", marginBottom: "0.3rem" }}>{a.label}</div>
                <div style={{ color: "var(--text-muted)", fontSize: "0.75rem", lineHeight: 1.4 }}>{a.desc}</div>
              </motion.div>
            ))}
          </div>
        </motion.div>

        {/* Indicateurs clés */}
        <motion.div initial={{ opacity: 0, y: 16 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.3 }}>
          <div style={{ fontSize: "0.72rem", fontWeight: 700, color: "var(--text-muted)", textTransform: "uppercase", letterSpacing: "0.08em", marginBottom: "1rem" }}>Indicateurs de performance</div>
          <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fill, minmax(240px, 1fr))", gap: "1rem" }}>
            {kpis.map((k, i) => (
              <motion.div key={k.label}
                initial={{ opacity: 0, y: 12 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.32 + i * 0.04 }}
                style={{ background: "var(--surface)", border: "1px solid var(--border)", borderRadius: "14px", padding: "1.3rem" }}>
                <div style={{ fontSize: "0.72rem", fontWeight: 600, color: "var(--text-muted)", textTransform: "uppercase", letterSpacing: "0.05em", marginBottom: "0.6rem" }}>{k.label}</div>
                <div style={{ fontWeight: 800, fontSize: "1.8rem", color: k.color, letterSpacing: "-0.03em", marginBottom: "0.3rem" }}>{k.value}</div>
                <div style={{ fontSize: "0.72rem", color: "var(--text-muted)" }}>{k.desc}</div>
              </motion.div>
            ))}
          </div>
        </motion.div>
      </div>
    </div>
  );
}
