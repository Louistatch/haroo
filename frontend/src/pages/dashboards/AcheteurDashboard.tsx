import React, { useEffect, useState } from "react";
import { useNavigate, Link } from "react-router-dom";
import { motion } from "framer-motion";
import { fetchPurchaseHistory, Purchase } from "../../api/purchases";

const C = "#7c3aed";

const IconDoc = () => <svg width="22" height="22" viewBox="0 0 22 22" fill="none"><path d="M4 3h9l5 5v11a2 2 0 01-2 2H4a2 2 0 01-2-2V5a2 2 0 012-2z" stroke="currentColor" strokeWidth="1.5"/><path d="M13 3v5h5M7 11h8M7 15h5" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round"/></svg>;
const IconBag = () => <svg width="22" height="22" viewBox="0 0 22 22" fill="none"><path d="M3 6h16l-1.5 12H4.5L3 6z" stroke="currentColor" strokeWidth="1.5" strokeLinejoin="round"/><path d="M8 6V4a3 3 0 016 0v2" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round"/></svg>;
const IconPresale = () => <svg width="22" height="22" viewBox="0 0 22 22" fill="none"><path d="M3 18c0-4 3.5-7 8-7s8 3 8 7" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round"/><path d="M11 11V5M8 8l3-3 3 3" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round"/><path d="M16 12l4 4M20 12l-4 4" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round"/></svg>;
const IconMarket = () => <svg width="22" height="22" viewBox="0 0 22 22" fill="none"><path d="M3 17l5-5 4 4 7-8" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round"/><path d="M2 2v18h18" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round"/></svg>;
const IconDownload = () => <svg width="22" height="22" viewBox="0 0 22 22" fill="none"><path d="M11 3v12M7 11l4 4 4-4" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round"/><path d="M3 18h16" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round"/></svg>;
const IconSettings = () => <svg width="22" height="22" viewBox="0 0 22 22" fill="none"><circle cx="11" cy="11" r="3" stroke="currentColor" strokeWidth="1.5"/><path d="M11 2v2M11 18v2M2 11h2M18 11h2M4.9 4.9l1.4 1.4M15.7 15.7l1.4 1.4M4.9 17.1l1.4-1.4M15.7 6.3l1.4-1.4" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round"/></svg>;
const IconArrow = () => <svg width="14" height="14" viewBox="0 0 14 14" fill="none"><path d="M3 7h8M8 4l3 3-3 3" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round"/></svg>;

function getInitials(user: any) {
  return ((user.first_name?.[0] || "") + (user.last_name?.[0] || "")).toUpperCase() || user.username?.[0]?.toUpperCase() || "A";
}

export default function AcheteurDashboard({ user }: { user: any }) {
  const navigate = useNavigate();
  const [purchases, setPurchases] = useState<Purchase[]>([]);
  const [purchaseCount, setPurchaseCount] = useState<number | null>(null);
  const [totalSpent, setTotalSpent] = useState(0);
  const [loading, setLoading] = useState(true);
  const memberDays = Math.floor((Date.now() - new Date(user.created_at).getTime()) / 86400000);

  useEffect(() => {
    const token = localStorage.getItem("access_token") || "";
    fetchPurchaseHistory({ page_size: 5 }, token)
      .then(data => {
        const items = data.results ?? [];
        setPurchases(items);
        setPurchaseCount(data.count ?? items.length);
        setTotalSpent(items.reduce((sum: number, p: any) => sum + Number(p.montant_paye || 0), 0));
      })
      .catch(() => { setPurchaseCount(0); })
      .finally(() => setLoading(false));
  }, []);

  const stats = [
    { label: "Préventes engagées", value: "—" },
    { label: "Dépenses totales", value: loading ? "…" : `${totalSpent.toLocaleString("fr-FR")} F` },
    { label: "Jours membre", value: memberDays },
  ];

  const actions = [
    { label: "Ouvriers disponibles", desc: "Récolte et post-récolte", icon: <IconBag />, to: "/ouvriers", color: "#d97706", bg: "#fef3c7" },
    { label: "Préventes agricoles", desc: "Engager des productions", icon: <IconPresale />, to: "/presales", color: "#16a34a", bg: "#dcfce7" },
    { label: "Marchés & tendances", desc: "Prix et analyses locales", icon: <IconMarket />, to: "/markets", color: "#0ea5e9", bg: "#e0f2fe" },
    { label: "Mes achats", desc: "Historique des achats", icon: <IconBag />, to: "/purchases", color: C, bg: "#ede9fe" },
    { label: "Paramètres", desc: "Sécurité du compte", icon: <IconSettings />, to: "/security", color: "#6366f1", bg: "#eef2ff" },
  ];

  return (
    <div style={{ minHeight: "100vh", background: "var(--bg)", paddingTop: "5rem" }}>
      <div style={{ maxWidth: 1040, margin: "0 auto", padding: "2rem 1.5rem" }}>

        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.5 }}
          style={{ background: "linear-gradient(135deg, #3b0764 0%, #6d28d9 60%, #8b5cf6 100%)", borderRadius: "20px", padding: "2.5rem", marginBottom: "1.75rem", position: "relative", overflow: "hidden" }}>
          <div style={{ position: "absolute", inset: 0, backgroundImage: "url('/images/hero/market.jpg')", backgroundSize: "cover", backgroundPosition: "center", opacity: 0.1 }} />
          <div style={{ position: "absolute", inset: 0, background: "linear-gradient(135deg, rgba(59,7,100,0.92) 0%, rgba(109,40,217,0.88) 60%, rgba(139,92,246,0.85) 100%)" }} />
          <div style={{ position: "absolute", inset: 0, backgroundImage: "radial-gradient(circle at 75% 25%, rgba(255,255,255,0.07) 0%, transparent 55%)", pointerEvents: "none" }} />
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
                <span style={{ background: "rgba(255,255,255,0.15)", color: "white", padding: "0.18rem 0.6rem", borderRadius: "100px", fontSize: "0.75rem", fontWeight: 600 }}>Acheteur</span>
              </div>
            </div>
          </div>
          <div style={{ display: "grid", gridTemplateColumns: "repeat(3, 1fr)", gap: "1rem", marginTop: "2rem", position: "relative" }}>
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
              <div style={{ fontWeight: 700, color: "var(--text)", fontSize: "0.95rem" }}>Achats récents</div>
              <Link to="/purchases" style={{ color: C, fontWeight: 600, fontSize: "0.8rem", textDecoration: "none", display: "flex", alignItems: "center", gap: 4 }}>Voir tout <IconArrow /></Link>
            </div>
            {loading ? (
              <div style={{ color: "var(--text-muted)", fontSize: "0.85rem", textAlign: "center", padding: "1.5rem 0" }}>Chargement…</div>
            ) : purchases.length === 0 ? (
              <div style={{ textAlign: "center", padding: "1.5rem 0" }}>
                <div style={{ color: "var(--text-muted)", fontSize: "0.85rem", marginBottom: "0.75rem" }}>Aucun achat pour l'instant</div>
                <button onClick={() => navigate("/presales")} style={{ background: C, color: "white", border: "none", borderRadius: "10px", padding: "0.55rem 1.1rem", fontWeight: 600, fontSize: "0.85rem", cursor: "pointer" }}>
                  Voir les préventes
                </button>
              </div>
            ) : (
              <div style={{ display: "flex", flexDirection: "column", gap: "0.6rem" }}>
                {purchases.map((p: any) => (
                  <div key={p.id} style={{ padding: "0.8rem", background: "var(--bg)", borderRadius: "10px", display: "flex", alignItems: "center", justifyContent: "space-between" }}>
                    <div>
                      <div style={{ fontWeight: 600, color: "var(--text)", fontSize: "0.85rem" }}>{p.document_titre || "Document"}</div>
                      <div style={{ color: "var(--text-muted)", fontSize: "0.75rem" }}>{new Date(p.created_at).toLocaleDateString("fr-FR")}</div>
                    </div>
                    <span style={{ fontWeight: 700, color: C, fontSize: "0.85rem" }}>{Number(p.montant_paye || 0).toLocaleString("fr-FR")} F</span>
                  </div>
                ))}
              </div>
            )}
          </motion.div>

          <motion.div initial={{ opacity: 0, y: 16 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.3 }}
            style={{ background: "var(--surface)", border: "1px solid var(--border)", borderRadius: "16px", padding: "1.5rem" }}>
            <div style={{ fontWeight: 700, color: "var(--text)", fontSize: "0.95rem", marginBottom: "1.25rem" }}>Mon compte</div>
            <div style={{ display: "flex", flexDirection: "column", gap: "0.6rem" }}>
              {[
                ["Nom", `${user.first_name || ""} ${user.last_name || ""}`.trim() || user.username],
                ["Email", user.email || "—"],
                ["Téléphone", user.phone_number || "Non renseigné"],
                ["Membre depuis", new Date(user.created_at).toLocaleDateString("fr-FR", { month: "long", year: "numeric" })],
              ].map(([k, v]) => (
                <div key={k} style={{ padding: "0.7rem", background: "var(--bg)", borderRadius: "10px", display: "flex", justifyContent: "space-between", alignItems: "center" }}>
                  <span style={{ fontSize: "0.75rem", fontWeight: 600, color: "var(--text-muted)", textTransform: "uppercase", letterSpacing: "0.04em" }}>{k}</span>
                  <span style={{ fontWeight: 600, color: "var(--text)", fontSize: "0.85rem" }}>{v}</span>
                </div>
              ))}
              <Link to="/me" style={{ display: "flex", alignItems: "center", justifyContent: "center", gap: 6, background: `${C}15`, color: C, border: `1.5px solid ${C}30`, borderRadius: "10px", padding: "0.65rem", fontWeight: 700, fontSize: "0.85rem", textDecoration: "none", marginTop: "0.25rem" }}>
                Modifier mon profil <IconArrow />
              </Link>
            </div>
          </motion.div>
        </div>
      </div>
    </div>
  );
}
