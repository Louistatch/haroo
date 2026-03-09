import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { motion } from "framer-motion";
import { getOffres, getContrats, OffreEmploi, Contrat } from "../../api/jobs";

const C = "#d97706";

const IconSearch = () => <svg width="22" height="22" viewBox="0 0 22 22" fill="none"><circle cx="10" cy="10" r="7" stroke="currentColor" strokeWidth="1.5"/><path d="M15.5 15.5L20 20" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round"/></svg>;
const IconContract = () => <svg width="22" height="22" viewBox="0 0 22 22" fill="none"><path d="M4 3h9l5 5v11a2 2 0 01-2 2H4a2 2 0 01-2-2V5a2 2 0 012-2z" stroke="currentColor" strokeWidth="1.5"/><path d="M13 3v5h5M7 10h8M7 13h8M7 16h5" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round"/><path d="M14 15l1.5 1.5 3-3" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round"/></svg>;
const IconDoc = () => <svg width="22" height="22" viewBox="0 0 22 22" fill="none"><path d="M4 3h9l5 5v11a2 2 0 01-2 2H4a2 2 0 01-2-2V5a2 2 0 012-2z" stroke="currentColor" strokeWidth="1.5"/><path d="M13 3v5h5M7 11h8M7 15h5" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round"/></svg>;
const IconProfile = () => <svg width="22" height="22" viewBox="0 0 22 22" fill="none"><circle cx="11" cy="7" r="4" stroke="currentColor" strokeWidth="1.5"/><path d="M3 20c0-4.4 3.6-8 8-8s8 3.6 8 8" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round"/></svg>;
const IconLocation = () => <svg width="22" height="22" viewBox="0 0 22 22" fill="none"><path d="M11 2C7.7 2 5 4.7 5 8c0 4.5 6 12 6 12s6-7.5 6-12c0-3.3-2.7-6-6-6z" stroke="currentColor" strokeWidth="1.5" strokeLinejoin="round"/><circle cx="11" cy="8" r="2.5" stroke="currentColor" strokeWidth="1.5"/></svg>;
const IconSettings = () => <svg width="22" height="22" viewBox="0 0 22 22" fill="none"><circle cx="11" cy="11" r="3" stroke="currentColor" strokeWidth="1.5"/><path d="M11 2v2M11 18v2M2 11h2M18 11h2M4.9 4.9l1.4 1.4M15.7 15.7l1.4 1.4M4.9 17.1l1.4-1.4M15.7 6.3l1.4-1.4" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round"/></svg>;
const IconArrow = () => <svg width="14" height="14" viewBox="0 0 14 14" fill="none"><path d="M3 7h8M8 4l3 3-3 3" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round"/></svg>;

function getInitials(user: any) {
  return ((user.first_name?.[0] || "") + (user.last_name?.[0] || "")).toUpperCase() || user.username?.[0]?.toUpperCase() || "O";
}

export default function OuvrierDashboard({ user }: { user: any }) {
  const navigate = useNavigate();
  const [offres, setOffres] = useState<OffreEmploi[]>([]);
  const [contrats, setContrats] = useState<Contrat[]>([]);
  const [loading, setLoading] = useState(true);
  const memberDays = Math.floor((Date.now() - new Date(user.created_at).getTime()) / 86400000);

  useEffect(() => {
    Promise.all([
      getOffres().catch(() => [] as OffreEmploi[]),
      getContrats().catch(() => [] as Contrat[]),
    ]).then(([o, c]) => {
      setOffres(o.filter(x => x.statut === 'OUVERTE').slice(0, 5));
      setContrats(c);
    }).finally(() => setLoading(false));
  }, []);

  const contratsActifs = contrats.filter(c => ['SIGNE', 'EN_COURS'].includes(c.statut));

  const stats = [
    { label: "Offres disponibles", value: loading ? "…" : offres.length },
    { label: "Contrats actifs", value: loading ? "…" : contratsActifs.length },
    { label: "Contrats terminés", value: loading ? "…" : contrats.filter(c => c.statut === 'TERMINE').length },
    { label: "Jours membre", value: memberDays },
  ];

  const actions = [
    { label: "Offres d'emploi", desc: "Emplois agricoles disponibles", icon: <IconSearch />, to: "/jobs", color: C, bg: "#fef3c7" },
    { label: "Mes contrats", desc: "Suivi de vos missions", icon: <IconContract />, to: "/jobs", color: "#16a34a", bg: "#dcfce7" },
    { label: "Documents", desc: "Fiches et guides", icon: <IconDoc />, to: "/documents", color: "#0ea5e9", bg: "#e0f2fe" },
    { label: "Marchés proches", desc: "Prix dans votre zone", icon: <IconLocation />, to: "/markets", color: "#7c3aed", bg: "#ede9fe" },
    { label: "Mon profil", desc: "Compétences et disponibilités", icon: <IconProfile />, to: "/me", color: "#2563eb", bg: "#dbeafe" },
    { label: "Paramètres", desc: "Sécurité du compte", icon: <IconSettings />, to: "/security", color: "#6366f1", bg: "#eef2ff" },
  ];

  return (
    <div style={{ minHeight: "100vh", background: "var(--bg)", paddingTop: "5rem" }}>
      <div style={{ maxWidth: 1040, margin: "0 auto", padding: "2rem 1.5rem" }}>

        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.5 }}
          style={{ background: "linear-gradient(135deg, #78350f 0%, #b45309 60%, #d97706 100%)", borderRadius: "20px", padding: "2.5rem", marginBottom: "1.75rem", position: "relative", overflow: "hidden" }}>
          <div style={{ position: "absolute", inset: 0, backgroundImage: "url('/images/hero/harvest.jpg')", backgroundSize: "cover", backgroundPosition: "center", opacity: 0.1 }} />
          <div style={{ position: "absolute", inset: 0, background: "linear-gradient(135deg, rgba(120,53,15,0.92) 0%, rgba(180,83,9,0.88) 60%, rgba(217,119,6,0.85) 100%)" }} />
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

        <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "1.25rem" }}>
          {/* Offres récentes */}
          <motion.div initial={{ opacity: 0, y: 16 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.25 }}
            style={{ background: "var(--surface)", border: "1px solid var(--border)", borderRadius: "16px", padding: "1.5rem" }}>
            <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", marginBottom: "1.25rem" }}>
              <div style={{ fontWeight: 700, color: "var(--text)", fontSize: "0.95rem" }}>Offres récentes</div>
              <a href="/jobs" style={{ color: C, fontWeight: 600, fontSize: "0.8rem", textDecoration: "none", display: "flex", alignItems: "center", gap: 4 }}>Voir tout <IconArrow /></a>
            </div>
            {loading ? (
              <div style={{ color: "var(--text-muted)", fontSize: "0.85rem", textAlign: "center", padding: "1.5rem 0" }}>Chargement…</div>
            ) : offres.length === 0 ? (
              <div style={{ textAlign: "center", padding: "1.5rem 0" }}>
                <div style={{ color: "var(--text-muted)", fontSize: "0.85rem", marginBottom: "0.75rem" }}>Aucune offre disponible pour le moment</div>
                <button onClick={() => navigate("/jobs")} style={{ background: C, color: "white", border: "none", borderRadius: "10px", padding: "0.55rem 1.1rem", fontWeight: 600, fontSize: "0.85rem", cursor: "pointer" }}>
                  Parcourir les offres
                </button>
              </div>
            ) : (
              <div style={{ display: "flex", flexDirection: "column", gap: "0.6rem" }}>
                {offres.map(o => (
                  <div key={o.id} style={{ padding: "0.8rem", background: "var(--bg)", borderRadius: "10px", display: "flex", alignItems: "center", justifyContent: "space-between" }}>
                    <div>
                      <div style={{ fontWeight: 600, color: "var(--text)", fontSize: "0.85rem" }}>{o.type_travail} — {o.canton_nom}</div>
                      <div style={{ color: "var(--text-muted)", fontSize: "0.75rem" }}>{o.nombre_postes - o.postes_pourvus} postes · {parseInt(o.salaire_horaire).toLocaleString()} FCFA/h</div>
                    </div>
                    <span style={{ background: "#dcfce7", color: "#16a34a", padding: "0.2rem 0.55rem", borderRadius: "100px", fontSize: "0.7rem", fontWeight: 700 }}>Ouverte</span>
                  </div>
                ))}
              </div>
            )}
          </motion.div>

          {/* Mes contrats */}
          <motion.div initial={{ opacity: 0, y: 16 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.3 }}
            style={{ background: "var(--surface)", border: "1px solid var(--border)", borderRadius: "16px", padding: "1.5rem" }}>
            <div style={{ fontWeight: 700, color: "var(--text)", fontSize: "0.95rem", marginBottom: "1.25rem" }}>Mes contrats</div>
            {loading ? (
              <div style={{ color: "var(--text-muted)", fontSize: "0.85rem", textAlign: "center", padding: "1.5rem 0" }}>Chargement…</div>
            ) : contrats.length === 0 ? (
              <div style={{ textAlign: "center", padding: "1.5rem 0" }}>
                <div style={{ color: "var(--text-muted)", fontSize: "0.85rem", marginBottom: "0.5rem" }}>Aucun contrat pour l'instant</div>
                <div style={{ color: "var(--text-muted)", fontSize: "0.78rem" }}>Postulez à des offres pour obtenir des contrats.</div>
              </div>
            ) : (
              <div style={{ display: "flex", flexDirection: "column", gap: "0.6rem" }}>
                {contrats.slice(0, 4).map(c => (
                  <div key={c.id} style={{ padding: "0.8rem", background: "var(--bg)", borderRadius: "10px", display: "flex", alignItems: "center", justifyContent: "space-between" }}>
                    <div>
                      <div style={{ fontWeight: 600, color: "var(--text)", fontSize: "0.85rem" }}>Contrat #{c.id}</div>
                      <div style={{ color: "var(--text-muted)", fontSize: "0.75rem" }}>{parseInt(c.salaire_horaire).toLocaleString()} FCFA/h · {c.exploitant_nom}</div>
                    </div>
                    <span style={{ background: c.statut === 'SIGNE' ? "#dcfce7" : "#dbeafe", color: c.statut === 'SIGNE' ? "#16a34a" : "#2563eb", padding: "0.2rem 0.55rem", borderRadius: "100px", fontSize: "0.7rem", fontWeight: 700 }}>{c.statut}</span>
                  </div>
                ))}
              </div>
            )}
          </motion.div>
        </div>
      </div>
    </div>
  );
}
