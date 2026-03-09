import React, { useEffect, useState } from "react";
import { useNavigate, Link } from "react-router-dom";
import { motion } from "framer-motion";
import { getMissions, Mission } from "../../api/missions";

const C = "#2563eb";

const IconMission = () => <svg width="22" height="22" viewBox="0 0 22 22" fill="none"><rect x="2" y="7" width="18" height="13" rx="2" stroke="currentColor" strokeWidth="1.5"/><path d="M7 7V5a2 2 0 012-2h4a2 2 0 012 2v2" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round"/><path d="M7 13h8M7 16h5" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round"/></svg>;
const IconProfile = () => <svg width="22" height="22" viewBox="0 0 22 22" fill="none"><circle cx="11" cy="7" r="4" stroke="currentColor" strokeWidth="1.5"/><path d="M3 20c0-4.4 3.6-8 8-8s8 3.6 8 8" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round"/><rect x="14" y="1" width="5" height="3" rx="1" stroke="currentColor" strokeWidth="1.2"/></svg>;
const IconCalendar = () => <svg width="22" height="22" viewBox="0 0 22 22" fill="none"><rect x="2" y="4" width="18" height="17" rx="2" stroke="currentColor" strokeWidth="1.5"/><path d="M7 2v3M15 2v3M2 9h18" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round"/><rect x="6" y="13" width="2" height="2" rx="0.5" fill="currentColor"/><rect x="10" y="13" width="2" height="2" rx="0.5" fill="currentColor"/></svg>;
const IconStar = () => <svg width="22" height="22" viewBox="0 0 22 22" fill="none"><path d="M11 2l2.4 6.9H20l-5.7 4.1 2.2 6.7L11 16l-5.5 3.7 2.2-6.7L2 9l6.6-.1z" stroke="currentColor" strokeWidth="1.5" strokeLinejoin="round"/></svg>;
const IconSettings = () => <svg width="22" height="22" viewBox="0 0 22 22" fill="none"><circle cx="11" cy="11" r="3" stroke="currentColor" strokeWidth="1.5"/><path d="M11 2v2M11 18v2M2 11h2M18 11h2M4.9 4.9l1.4 1.4M15.7 15.7l1.4 1.4M4.9 17.1l1.4-1.4M15.7 6.3l1.4-1.4" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round"/></svg>;
const IconBadge = () => <svg width="22" height="22" viewBox="0 0 22 22" fill="none"><path d="M11 2l2 4 4.5.65-3.25 3.17.77 4.48L11 12l-4.02 2.3.77-4.48L4.5 6.65 9 6z" stroke="currentColor" strokeWidth="1.5" strokeLinejoin="round"/><path d="M7 17l-2 3M15 17l2 3" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round"/></svg>;
const IconDoc = () => <svg width="22" height="22" viewBox="0 0 22 22" fill="none"><path d="M4 3h9l5 5v11a2 2 0 01-2 2H4a2 2 0 01-2-2V5a2 2 0 012-2z" stroke="currentColor" strokeWidth="1.5"/><path d="M13 3v5h5M7 11h8M7 15h5" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round"/></svg>;
const IconCheck = () => <svg width="13" height="13" viewBox="0 0 13 13" fill="none"><path d="M2 6.5l3 3 6-6" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/></svg>;
const IconArrow = () => <svg width="14" height="14" viewBox="0 0 14 14" fill="none"><path d="M3 7h8M8 4l3 3-3 3" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round"/></svg>;

const STATUS_CONFIG: Record<string, { label: string; color: string; bg: string }> = {
  DEMANDE:  { label: "Nouvelle",  color: "#d97706", bg: "#fef3c7" },
  ACCEPTEE: { label: "Acceptée", color: "#16a34a", bg: "#dcfce7" },
  EN_COURS: { label: "En cours", color: "#2563eb", bg: "#dbeafe" },
  TERMINEE: { label: "Terminée", color: "#6b7280", bg: "#f3f4f6" },
  REFUSEE:  { label: "Refusée",  color: "#dc2626", bg: "#fee2e2" },
  ANNULEE:  { label: "Annulée",  color: "#6b7280", bg: "#f3f4f6" },
};

function getInitials(user: any) {
  return ((user.first_name?.[0] || "") + (user.last_name?.[0] || "")).toUpperCase() || user.username?.[0]?.toUpperCase() || "A";
}

export default function AgronomeDashboard({ user }: { user: any }) {
  const navigate = useNavigate();
  const [missions, setMissions] = useState<Mission[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    getMissions().catch(() => [] as Mission[]).then(ms => { setMissions(ms); setLoading(false); });
  }, []);

  const active = missions.filter(m => ["DEMANDE", "ACCEPTEE", "EN_COURS"].includes(m.statut));
  const done = missions.filter(m => m.statut === "TERMINEE");
  const memberDays = Math.floor((Date.now() - new Date(user.created_at).getTime()) / 86400000);
  const totalRevenue = done.reduce((sum, m) => sum + Number(m.budget_propose), 0);

  const stats = [
    { label: "Missions actives", value: loading ? "…" : active.length },
    { label: "Missions terminées", value: loading ? "…" : done.length },
    { label: "Revenus confirmés", value: loading ? "…" : `${totalRevenue.toLocaleString("fr-FR")} F` },
    { label: "Jours membre", value: memberDays },
  ];

  const actions = [
    { label: "Mes missions", desc: "Gérer vos demandes", icon: <IconMission />, to: "/missions", color: C, bg: "#dbeafe" },
    { label: "Mon profil public", desc: "Visibilité dans l'annuaire", icon: <IconProfile />, to: "/me", color: "#16a34a", bg: "#dcfce7" },
    { label: "Mon planning", desc: "Calendrier des interventions", icon: <IconCalendar />, to: "/missions", color: "#7c3aed", bg: "#ede9fe" },
    { label: "Mes notations", desc: "Avis des exploitants", icon: <IconStar />, to: "/ratings", color: "#f59e0b", bg: "#fef3c7" },
    { label: "Documents techniques", desc: "Accéder au catalogue", icon: <IconDoc />, to: "/documents", color: "#0ea5e9", bg: "#e0f2fe" },
    { label: "Marchés de proximité", desc: "Prix et tendances locales", icon: <IconCalendar />, to: "/markets", color: "#d97706", bg: "#fef3c7" },
    { label: "Sécurité", desc: "Paramètres du compte", icon: <IconSettings />, to: "/security", color: "#6366f1", bg: "#eef2ff" },
  ];

  return (
    <div style={{ minHeight: "100vh", background: "var(--bg)", paddingTop: "5rem" }}>
      <div style={{ maxWidth: 1040, margin: "0 auto", padding: "2rem 1.5rem" }}>

        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.5 }}
          style={{ background: "linear-gradient(135deg, #1e3a8a 0%, #1d4ed8 60%, #3b82f6 100%)", borderRadius: "20px", padding: "2.5rem", marginBottom: "1.75rem", position: "relative", overflow: "hidden" }}>
          <div style={{ position: "absolute", inset: 0, backgroundImage: "url('/images/hero/farmer.jpg')", backgroundSize: "cover", backgroundPosition: "center", opacity: 0.1 }} />
          <div style={{ position: "absolute", inset: 0, background: "linear-gradient(135deg, rgba(30,58,138,0.92) 0%, rgba(29,78,216,0.88) 60%, rgba(59,130,246,0.85) 100%)" }} />
          <div style={{ position: "absolute", inset: 0, backgroundImage: "radial-gradient(circle at 75% 25%, rgba(255,255,255,0.07) 0%, transparent 50%)", pointerEvents: "none" }} />
          <div style={{ position: "absolute", right: 32, top: 32, opacity: 0.06 }}>
            <IconBadge />
          </div>
          <div style={{ display: "flex", alignItems: "center", gap: "1.25rem", position: "relative" }}>
            <div style={{ width: 58, height: 58, borderRadius: "50%", background: "rgba(255,255,255,0.15)", border: "2px solid rgba(255,255,255,0.25)", display: "flex", alignItems: "center", justifyContent: "center", flexShrink: 0 }}>
              <span style={{ color: "white", fontWeight: 800, fontSize: "1.35rem" }}>{getInitials(user)}</span>
            </div>
            <div>
              <div style={{ color: "rgba(255,255,255,0.55)", fontSize: "0.78rem", fontWeight: 600, textTransform: "uppercase", letterSpacing: "0.07em", marginBottom: "0.2rem" }}>Tableau de bord Agronome</div>
              <h1 style={{ color: "white", fontSize: "clamp(1.3rem,3vw,1.9rem)", fontWeight: 800, margin: 0, letterSpacing: "-0.03em" }}>
                {user.first_name ? `${user.first_name} ${user.last_name}` : user.username}
              </h1>
              <div style={{ display: "flex", alignItems: "center", gap: "0.6rem", marginTop: "0.5rem", flexWrap: "wrap" }}>
                <span style={{ background: "rgba(255,255,255,0.15)", color: "white", padding: "0.18rem 0.6rem", borderRadius: "100px", fontSize: "0.75rem", fontWeight: 600 }}>Agronome</span>
                <span style={{ display: "flex", alignItems: "center", gap: 4, color: "rgba(255,255,255,0.8)", fontSize: "0.75rem", fontWeight: 500 }}>
                  <span style={{ width: 16, height: 16, background: "rgba(74,222,128,0.3)", borderRadius: "50%", display: "flex", alignItems: "center", justifyContent: "center" }}><IconCheck /></span>
                  Profil actif
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

        <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "1.25rem" }}>
          <motion.div initial={{ opacity: 0, y: 16 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.25 }}
            style={{ background: "var(--surface)", border: "1px solid var(--border)", borderRadius: "16px", padding: "1.5rem" }}>
            <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", marginBottom: "1.25rem" }}>
              <div style={{ fontWeight: 700, color: "var(--text)", fontSize: "0.95rem" }}>Mes missions</div>
              <Link to="/missions" style={{ color: C, fontWeight: 600, fontSize: "0.8rem", textDecoration: "none", display: "flex", alignItems: "center", gap: 4 }}>Voir tout <IconArrow /></Link>
            </div>
            {loading ? (
              <div style={{ color: "var(--text-muted)", fontSize: "0.85rem", textAlign: "center", padding: "1.5rem 0" }}>Chargement…</div>
            ) : missions.length === 0 ? (
              <div style={{ color: "var(--text-muted)", fontSize: "0.85rem", textAlign: "center", padding: "1.5rem 0" }}>
                Votre profil est visible dans l'annuaire. Les exploitants peuvent vous contacter.
              </div>
            ) : (
              <div style={{ display: "flex", flexDirection: "column", gap: "0.6rem" }}>
                {missions.slice(0, 4).map(m => {
                  const sc = STATUS_CONFIG[m.statut] || { label: m.statut, color: "#6b7280", bg: "#f3f4f6" };
                  return (
                    <div key={m.id} style={{ padding: "0.8rem", background: "var(--bg)", borderRadius: "10px", display: "flex", alignItems: "center", justifyContent: "space-between" }}>
                      <div>
                        <div style={{ fontWeight: 600, color: "var(--text)", fontSize: "0.85rem" }}>{m.exploitant_nom}</div>
                        <div style={{ color: "var(--text-muted)", fontSize: "0.75rem" }}>{Number(m.budget_propose).toLocaleString("fr-FR")} FCFA</div>
                      </div>
                      <span style={{ background: sc.bg, color: sc.color, padding: "0.2rem 0.55rem", borderRadius: "100px", fontSize: "0.7rem", fontWeight: 700 }}>{sc.label}</span>
                    </div>
                  );
                })}
              </div>
            )}
          </motion.div>

          <motion.div initial={{ opacity: 0, y: 16 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.3 }}
            style={{ background: "var(--surface)", border: "1px solid var(--border)", borderRadius: "16px", padding: "1.5rem" }}>
            <div style={{ fontWeight: 700, color: "var(--text)", fontSize: "0.95rem", marginBottom: "1.25rem" }}>Mon dossier professionnel</div>
            <div style={{ display: "flex", flexDirection: "column", gap: "0.75rem" }}>
              {(() => {
                const ap = user.agronome_profile;
                const verif = ap?.statut_validation === 'VALIDE' ? { v: "Validé", c: "#16a34a" } : ap?.statut_validation === 'EN_ATTENTE' ? { v: "En attente", c: "#d97706" } : { v: ap?.statut_validation || "Non renseigné", c: "var(--text)" };
                return [
                  { label: "Statut dossier", value: verif.v, color: verif.c },
                  { label: "Spécialisations", value: ap?.specialisations?.length ? ap.specialisations.join(", ") : "Non renseignées" },
                  { label: "Canton d'intervention", value: ap?.canton_rattachement_nom || "Non renseigné" },
                  { label: "Note moyenne", value: ap?.note_moyenne && parseFloat(ap.note_moyenne) > 0 ? `${parseFloat(ap.note_moyenne).toFixed(1)} / 5 (${ap.nombre_avis} avis)` : "Pas encore noté" },
                ];
              })().map(row => (
                <div key={row.label} style={{ padding: "0.7rem", background: "var(--bg)", borderRadius: "10px", display: "flex", justifyContent: "space-between", alignItems: "center" }}>
                  <span style={{ fontSize: "0.75rem", fontWeight: 600, color: "var(--text-muted)", textTransform: "uppercase", letterSpacing: "0.04em" }}>{row.label}</span>
                  <span style={{ fontWeight: 700, color: row.color || "var(--text)", fontSize: "0.85rem" }}>{row.value}</span>
                </div>
              ))}
              <Link to="/me" style={{ display: "flex", alignItems: "center", justifyContent: "center", gap: 6, background: `${C}15`, color: C, border: `1.5px solid ${C}30`, borderRadius: "10px", padding: "0.65rem", fontWeight: 700, fontSize: "0.85rem", textDecoration: "none", marginTop: "0.25rem" }}>
                Compléter mon profil <IconArrow />
              </Link>
            </div>
          </motion.div>
        </div>
      </div>
    </div>
  );
}
