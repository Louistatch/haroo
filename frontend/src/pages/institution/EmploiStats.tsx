import React, { useEffect, useState } from "react";
import { motion } from "framer-motion";
import api from "../../api/auth";

const IconBriefcase = () => <svg width="24" height="24" viewBox="0 0 24 24" fill="none"><rect x="2" y="7" width="18" height="12" rx="2" stroke="currentColor" strokeWidth="1.5"/><path d="M7 7V5a2 2 0 012-2h4a2 2 0 012 2v2M2 11h18" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round"/></svg>;
const IconUsers = () => <svg width="24" height="24" viewBox="0 0 24 24" fill="none"><circle cx="9" cy="7" r="4" stroke="currentColor" strokeWidth="1.5"/><path d="M2 20c0-3.9 3.1-7 7-7s7 3.1 7 7" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round"/><path d="M15 7a4 4 0 100-8M19 20c0-2.2-1.3-4.1-3.2-5" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round"/></svg>;
const IconClock = () => <svg width="24" height="24" viewBox="0 0 24 24" fill="none"><circle cx="12" cy="12" r="9" stroke="currentColor" strokeWidth="1.5"/><path d="M12 6v6l4 2" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round"/></svg>;
const IconCheck = () => <svg width="24" height="24" viewBox="0 0 24 24" fill="none"><path d="M20 6L9 17l-5-5" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round"/></svg>;

export default function EmploiStats() {
  const [stats, setStats] = useState({
    offresActives: 0,
    offresTotal: 0,
    annoncesOuvriers: 0,
    tauxPourvoi: 0,
  });
  const [offres, setOffres] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    Promise.all([
      api.get("/jobs/offres/"),
      api.get("/jobs/annonces-ouvriers/"),
    ]).then(([offresResp, annoncesResp]) => {
      const offresData = offresResp.data.results || offresResp.data || [];
      const annoncesData = annoncesResp.data.results || annoncesResp.data || [];
      
      const offresActives = offresData.filter((o: any) => o.statut === 'OUVERTE').length;
      const offresPourvues = offresData.filter((o: any) => o.statut === 'POURVUE').length;
      const tauxPourvoi = offresData.length > 0 ? Math.round((offresPourvues / offresData.length) * 100) : 0;

      setStats({
        offresActives,
        offresTotal: offresData.length,
        annoncesOuvriers: annoncesData.length,
        tauxPourvoi,
      });
      setOffres(offresData.slice(0, 10)); // 10 dernières offres
      setLoading(false);
    }).catch(() => setLoading(false));
  }, []);

  const mainStats = [
    { label: "Offres d'emploi actives", value: loading ? "…" : stats.offresActives, icon: <IconBriefcase />, color: "#16a34a" },
    { label: "Total offres publiées", value: loading ? "…" : stats.offresTotal, icon: <IconClock />, color: "#2563eb" },
    { label: "Annonces ouvriers", value: loading ? "…" : stats.annoncesOuvriers, icon: <IconUsers />, color: "#f59e0b" },
    { label: "Taux de pourvoi", value: loading ? "…" : `${stats.tauxPourvoi}%`, icon: <IconCheck />, color: "#7c3aed" },
  ];

  const typeEmploi = [
    { type: "Travaux agricoles", count: stats.offresActives, color: "#16a34a" },
    { type: "Récolte", count: 0, color: "#f59e0b" },
    { type: "Post-récolte", count: 0, color: "#2563eb" },
    { type: "Entretien", count: 0, color: "#7c3aed" },
  ];

  return (
    <div style={{ minHeight: "100vh", background: "var(--bg)", paddingTop: "5rem" }}>
      <div style={{ maxWidth: 1200, margin: "0 auto", padding: "2rem 1.5rem" }}>
        
        {/* Header */}
        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }}>
          <div style={{ marginBottom: "0.5rem" }}>
            <a href="/dashboard" style={{ color: "var(--text-muted)", fontSize: "0.85rem", textDecoration: "none" }}>
              ← Retour au dashboard
            </a>
          </div>
          <h1 style={{ fontSize: "2rem", fontWeight: 800, color: "var(--text)", margin: "0 0 0.5rem", letterSpacing: "-0.02em" }}>
            Emploi Agricole
          </h1>
          <p style={{ color: "var(--text-muted)", fontSize: "0.95rem", margin: 0 }}>
            Suivi des offres d'emploi et des demandes de main-d'œuvre agricole
          </p>
        </motion.div>

        {/* Statistiques principales */}
        <motion.div initial={{ opacity: 0, y: 16 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.1 }}
          style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(260px, 1fr))", gap: "1rem", margin: "2rem 0" }}>
          {mainStats.map((s, i) => (
            <motion.div key={s.label}
              initial={{ opacity: 0, y: 12 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.12 + i * 0.05 }}
              style={{ background: "var(--surface)", border: "1px solid var(--border)", borderRadius: "16px", padding: "1.5rem" }}>
              <div style={{ display: "flex", alignItems: "center", gap: "1rem", marginBottom: "1rem" }}>
                <div style={{ width: 48, height: 48, borderRadius: "12px", background: `${s.color}15`, color: s.color, display: "flex", alignItems: "center", justifyContent: "center" }}>
                  {s.icon}
                </div>
                <div style={{ flex: 1 }}>
                  <div style={{ fontSize: "0.75rem", fontWeight: 600, color: "var(--text-muted)", textTransform: "uppercase", letterSpacing: "0.05em" }}>{s.label}</div>
                  <div style={{ fontWeight: 800, fontSize: "1.8rem", color: "var(--text)", letterSpacing: "-0.03em" }}>{s.value}</div>
                </div>
              </div>
            </motion.div>
          ))}
        </motion.div>

        {/* Répartition par type */}
        <motion.div initial={{ opacity: 0, y: 16 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.2 }}
          style={{ background: "var(--surface)", border: "1px solid var(--border)", borderRadius: "16px", padding: "1.5rem", marginBottom: "1.5rem" }}>
          <h2 style={{ fontSize: "1.1rem", fontWeight: 700, color: "var(--text)", margin: "0 0 1.5rem" }}>
            Répartition par type d'emploi
          </h2>
          <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fill, minmax(200px, 1fr))", gap: "1rem" }}>
            {typeEmploi.map((t, i) => (
              <motion.div key={t.type}
                initial={{ opacity: 0, scale: 0.9 }} animate={{ opacity: 1, scale: 1 }} transition={{ delay: 0.25 + i * 0.05 }}
                style={{ background: "var(--bg)", border: "1px solid var(--border)", borderRadius: "12px", padding: "1.2rem", textAlign: "center" }}>
                <div style={{ width: 12, height: 12, borderRadius: "50%", background: t.color, margin: "0 auto 0.75rem" }} />
                <div style={{ fontWeight: 700, fontSize: "1.5rem", color: "var(--text)", marginBottom: "0.25rem" }}>{t.count}</div>
                <div style={{ fontSize: "0.85rem", color: "var(--text-muted)" }}>{t.type}</div>
              </motion.div>
            ))}
          </div>
        </motion.div>

        {/* Dernières offres */}
        <motion.div initial={{ opacity: 0, y: 16 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.3 }}
          style={{ background: "var(--surface)", border: "1px solid var(--border)", borderRadius: "16px", padding: "1.5rem" }}>
          <h2 style={{ fontSize: "1.1rem", fontWeight: 700, color: "var(--text)", margin: "0 0 1.5rem" }}>
            Dernières offres d'emploi
          </h2>
          {offres.length === 0 ? (
            <div style={{ padding: "2rem", textAlign: "center", color: "var(--text-muted)" }}>
              Aucune offre d'emploi disponible pour le moment
            </div>
          ) : (
            <div style={{ display: "grid", gap: "1rem" }}>
              {offres.map((offre, i) => (
                <motion.div key={offre.id}
                  initial={{ opacity: 0, x: -20 }} animate={{ opacity: 1, x: 0 }} transition={{ delay: 0.35 + i * 0.05 }}
                  style={{ background: "var(--bg)", border: "1px solid var(--border)", borderRadius: "12px", padding: "1.2rem" }}>
                  <div style={{ display: "flex", justifyContent: "space-between", alignItems: "start", marginBottom: "0.75rem" }}>
                    <div>
                      <h3 style={{ fontSize: "1rem", fontWeight: 700, color: "var(--text)", margin: "0 0 0.25rem" }}>
                        {offre.titre}
                      </h3>
                      <div style={{ fontSize: "0.85rem", color: "var(--text-muted)" }}>
                        {offre.exploitant_nom || "Exploitant"} • {offre.canton_nom || "Canton"}
                      </div>
                    </div>
                    <span style={{ 
                      padding: "0.25rem 0.75rem", 
                      borderRadius: "100px", 
                      fontSize: "0.75rem", 
                      fontWeight: 600,
                      background: offre.statut === 'OUVERTE' ? '#dcfce7' : '#fef3c7',
                      color: offre.statut === 'OUVERTE' ? '#16a34a' : '#f59e0b'
                    }}>
                      {offre.statut === 'OUVERTE' ? 'Ouverte' : offre.statut}
                    </span>
                  </div>
                  <div style={{ display: "flex", gap: "1.5rem", fontSize: "0.85rem", color: "var(--text-muted)" }}>
                    <div>👥 {offre.nombre_ouvriers || 8} ouvriers</div>
                    <div>📅 {new Date(offre.date_debut).toLocaleDateString('fr-FR')}</div>
                    <div>💰 {offre.remuneration_proposee || 1000} FCFA/h</div>
                  </div>
                </motion.div>
              ))}
            </div>
          )}
        </motion.div>
      </div>
    </div>
  );
}
