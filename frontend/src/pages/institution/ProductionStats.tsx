import React, { useEffect, useState } from "react";
import { motion } from "framer-motion";
import api from "../../api/auth";

const IconTractor = () => <svg width="24" height="24" viewBox="0 0 24 24" fill="none"><circle cx="7" cy="18" r="3" stroke="currentColor" strokeWidth="1.5"/><circle cx="18" cy="18" r="2" stroke="currentColor" strokeWidth="1.5"/><path d="M10 18h6M4 18H2V9h8l3 3h6v6h-1" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round"/></svg>;
const IconMap = () => <svg width="24" height="24" viewBox="0 0 24 24" fill="none"><path d="M1 5l6 2 8-4 6 3v14l-6-3-8 4-6-2V5z" stroke="currentColor" strokeWidth="1.5" strokeLinejoin="round"/><path d="M7 7v13M15 3v13" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round"/></svg>;
const IconChart = () => <svg width="24" height="24" viewBox="0 0 24 24" fill="none"><path d="M3 17l5-5 4 4 7-8" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round"/><path d="M2 2v18h18" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round"/></svg>;
const IconLeaf = () => <svg width="24" height="24" viewBox="0 0 24 24" fill="none"><path d="M12 2C6.5 2 2 6.5 2 12s4.5 10 10 10 10-4.5 10-10S17.5 2 12 2z" stroke="currentColor" strokeWidth="1.5"/><path d="M12 6v12M8 12h8" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round"/></svg>;

export default function ProductionStats() {
  const [stats, setStats] = useState({
    exploitants: 0,
    superficieTotale: 0,
    exploitantsVerifies: 0,
    regionsActives: 5,
  });
  const [exploitantsByRegion, setExploitantsByRegion] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    Promise.all([
      api.get("/exploitants/"),
      api.get("/regions/"),
    ]).then(([explResp, regResp]) => {
      const exploitants = explResp.data.results || explResp.data || [];
      const regions = regResp.data.results || regResp.data || [];
      
      // Calculer les statistiques
      const superficieTotale = exploitants.reduce((sum: number, e: any) => {
        return sum + (parseFloat(e.exploitant_profile?.superficie_totale) || 0);
      }, 0);
      
      const exploitantsVerifies = exploitants.filter((e: any) => 
        e.exploitant_profile?.statut_verification === 'VERIFIE'
      ).length;

      // Grouper par région
      const byRegion = regions.map((region: any) => {
        const count = exploitants.filter((e: any) => 
          e.exploitant_profile?.canton_principal_nom?.includes(region.nom)
        ).length;
        return { region: region.nom, count };
      });

      setStats({
        exploitants: exploitants.length,
        superficieTotale: Math.round(superficieTotale * 10) / 10,
        exploitantsVerifies,
        regionsActives: byRegion.filter((r: any) => r.count > 0).length,
      });
      setExploitantsByRegion(byRegion);
      setLoading(false);
    }).catch(() => setLoading(false));
  }, []);

  const mainStats = [
    { label: "Exploitants enregistrés", value: loading ? "…" : stats.exploitants, icon: <IconTractor />, color: "#16a34a" },
    { label: "Superficie totale déclarée", value: loading ? "…" : `${stats.superficieTotale} ha`, icon: <IconLeaf />, color: "#f59e0b" },
    { label: "Exploitations vérifiées", value: loading ? "…" : stats.exploitantsVerifies, icon: <IconChart />, color: "#2563eb" },
    { label: "Régions actives", value: loading ? "…" : `${stats.regionsActives}/5`, icon: <IconMap />, color: "#7c3aed" },
  ];

  const cultures = [
    { nom: "Maïs", superficie: "—", production: "—", color: "#f59e0b" },
    { nom: "Riz", superficie: "—", production: "—", color: "#16a34a" },
    { nom: "Soja", superficie: "—", production: "—", color: "#2563eb" },
    { nom: "Manioc", superficie: "—", production: "—", color: "#7c3aed" },
    { nom: "Igname", superficie: "—", production: "—", color: "#dc2626" },
    { nom: "Arachide", superficie: "—", production: "—", color: "#0e7490" },
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
            Statistiques de Production
          </h1>
          <p style={{ color: "var(--text-muted)", fontSize: "0.95rem", margin: 0 }}>
            Vue d'ensemble de la production agricole par région et par culture
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

        {/* Répartition par région */}
        <motion.div initial={{ opacity: 0, y: 16 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.2 }}
          style={{ background: "var(--surface)", border: "1px solid var(--border)", borderRadius: "16px", padding: "1.5rem", marginBottom: "1.5rem" }}>
          <h2 style={{ fontSize: "1.1rem", fontWeight: 700, color: "var(--text)", margin: "0 0 1.5rem" }}>
            Répartition des exploitants par région
          </h2>
          <div style={{ display: "grid", gap: "1rem" }}>
            {exploitantsByRegion.map((item, i) => (
              <div key={item.region} style={{ display: "flex", alignItems: "center", gap: "1rem" }}>
                <div style={{ flex: 1, fontSize: "0.9rem", fontWeight: 600, color: "var(--text)" }}>{item.region}</div>
                <div style={{ flex: 2, background: "var(--bg)", borderRadius: "8px", height: "32px", position: "relative", overflow: "hidden" }}>
                  <motion.div
                    initial={{ width: 0 }}
                    animate={{ width: `${(item.count / stats.exploitants) * 100}%` }}
                    transition={{ delay: 0.3 + i * 0.1, duration: 0.6 }}
                    style={{ height: "100%", background: "linear-gradient(90deg, #16a34a, #22c55e)", borderRadius: "8px" }}
                  />
                  <div style={{ position: "absolute", inset: 0, display: "flex", alignItems: "center", paddingLeft: "0.75rem", fontSize: "0.85rem", fontWeight: 700, color: "var(--text)" }}>
                    {item.count} exploitants
                  </div>
                </div>
              </div>
            ))}
          </div>
        </motion.div>

        {/* Production par culture */}
        <motion.div initial={{ opacity: 0, y: 16 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.3 }}
          style={{ background: "var(--surface)", border: "1px solid var(--border)", borderRadius: "16px", padding: "1.5rem" }}>
          <h2 style={{ fontSize: "1.1rem", fontWeight: 700, color: "var(--text)", margin: "0 0 1.5rem" }}>
            Production par culture (données à venir)
          </h2>
          <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fill, minmax(200px, 1fr))", gap: "1rem" }}>
            {cultures.map((c, i) => (
              <motion.div key={c.nom}
                initial={{ opacity: 0, scale: 0.9 }} animate={{ opacity: 1, scale: 1 }} transition={{ delay: 0.35 + i * 0.05 }}
                style={{ background: "var(--bg)", border: "1px solid var(--border)", borderRadius: "12px", padding: "1.2rem" }}>
                <div style={{ display: "flex", alignItems: "center", gap: "0.5rem", marginBottom: "0.75rem" }}>
                  <div style={{ width: 8, height: 8, borderRadius: "50%", background: c.color }} />
                  <div style={{ fontWeight: 700, color: "var(--text)", fontSize: "0.95rem" }}>{c.nom}</div>
                </div>
                <div style={{ fontSize: "0.75rem", color: "var(--text-muted)", marginBottom: "0.25rem" }}>Superficie: {c.superficie}</div>
                <div style={{ fontSize: "0.75rem", color: "var(--text-muted)" }}>Production: {c.production}</div>
              </motion.div>
            ))}
          </div>
          <div style={{ marginTop: "1.5rem", padding: "1rem", background: "#fef3c7", border: "1px solid #f59e0b", borderRadius: "10px" }}>
            <p style={{ margin: 0, fontSize: "0.85rem", color: "#92400e" }}>
              ℹ️ Les données de production par culture seront disponibles une fois que les exploitants auront renseigné leurs cultures actuelles dans leur profil.
            </p>
          </div>
        </motion.div>
      </div>
    </div>
  );
}
