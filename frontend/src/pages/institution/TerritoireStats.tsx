import React, { useEffect, useState } from "react";
import { motion } from "framer-motion";
import api from "../../api/auth";

const IconMap = () => <svg width="24" height="24" viewBox="0 0 24 24" fill="none"><path d="M1 5l6 2 8-4 6 3v14l-6-3-8 4-6-2V5z" stroke="currentColor" strokeWidth="1.5" strokeLinejoin="round"/><path d="M7 7v13M15 3v13" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round"/></svg>;
const IconPin = () => <svg width="24" height="24" viewBox="0 0 24 24" fill="none"><path d="M12 2C8.13 2 5 5.13 5 9c0 5.25 7 13 7 13s7-7.75 7-13c0-3.87-3.13-7-7-7z" stroke="currentColor" strokeWidth="1.5"/><circle cx="12" cy="9" r="2.5" stroke="currentColor" strokeWidth="1.5"/></svg>;
const IconUsers = () => <svg width="24" height="24" viewBox="0 0 24 24" fill="none"><circle cx="9" cy="7" r="4" stroke="currentColor" strokeWidth="1.5"/><path d="M2 20c0-3.9 3.1-7 7-7s7 3.1 7 7" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round"/><path d="M15 7a4 4 0 100-8M19 20c0-2.2-1.3-4.1-3.2-5" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round"/></svg>;
const IconCheck = () => <svg width="24" height="24" viewBox="0 0 24 24" fill="none"><path d="M20 6L9 17l-5-5" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round"/></svg>;

export default function TerritoireStats() {
  const [stats, setStats] = useState({
    regions: 5,
    prefectures: 38,
    cantons: 323,
    cantonsCouvert: 0,
  });
  const [regionData, setRegionData] = useState<any[]>([]);
  const [prefectureData, setPrefectureData] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    Promise.all([
      api.get("/regions/"),
      api.get("/prefectures/"),
      api.get("/cantons/"),
      api.get("/exploitants/"),
      api.get("/agronomists"),
    ]).then(([regResp, prefResp, cantResp, explResp, agroResp]) => {
      const regions = regResp.data.results || regResp.data || [];
      const prefectures = prefResp.data.results || prefResp.data || [];
      const cantons = cantResp.data.results || cantResp.data || [];
      const exploitants = explResp.data.results || explResp.data || [];
      const agronomes = agroResp.data.results || agroResp.data || [];

      // Compter les cantons couverts (avec au moins un exploitant ou agronome)
      const cantonsSet = new Set();
      exploitants.forEach((e: any) => {
        if (e.exploitant_profile?.canton_principal) {
          cantonsSet.add(e.exploitant_profile.canton_principal);
        }
      });
      agronomes.forEach((a: any) => {
        if (a.agronome_profile?.canton_rattachement) {
          cantonsSet.add(a.agronome_profile.canton_rattachement);
        }
      });

      // Statistiques par région
      const regData = regions.map((region: any) => {
        const prefsInRegion = prefectures.filter((p: any) => p.region === region.id);
        const exploitantsCount = exploitants.filter((e: any) => 
          e.exploitant_profile?.canton_principal_nom?.includes(region.nom)
        ).length;
        const agronomeCount = agronomes.filter((a: any) => 
          a.agronome_profile?.canton_rattachement_nom?.includes(region.nom)
        ).length;
        
        return {
          nom: region.nom,
          prefectures: prefsInRegion.length,
          exploitants: exploitantsCount,
          agronomes: agronomeCount,
          total: exploitantsCount + agronomeCount,
        };
      });

      // Top 10 préfectures
      const prefData = prefectures.map((pref: any) => {
        const exploitantsCount = exploitants.filter((e: any) => 
          e.exploitant_profile?.canton_principal_nom?.includes(pref.nom)
        ).length;
        const agronomeCount = agronomes.filter((a: any) => 
          a.agronome_profile?.canton_rattachement_nom?.includes(pref.nom)
        ).length;
        
        return {
          nom: pref.nom,
          exploitants: exploitantsCount,
          agronomes: agronomeCount,
          total: exploitantsCount + agronomeCount,
        };
      }).sort((a: any, b: any) => b.total - a.total).slice(0, 10);

      setStats({
        regions: regions.length,
        prefectures: prefectures.length,
        cantons: cantons.length,
        cantonsCouvert: cantonsSet.size,
      });
      setRegionData(regData);
      setPrefectureData(prefData);
      setLoading(false);
    }).catch(() => setLoading(false));
  }, []);

  const mainStats = [
    { label: "Régions", value: loading ? "…" : stats.regions, icon: <IconMap />, color: "#16a34a" },
    { label: "Préfectures", value: loading ? "…" : stats.prefectures, icon: <IconPin />, color: "#2563eb" },
    { label: "Cantons", value: loading ? "…" : stats.cantons, icon: <IconPin />, color: "#f59e0b" },
    { label: "Cantons couverts", value: loading ? "…" : stats.cantonsCouvert, icon: <IconCheck />, color: "#7c3aed" },
  ];

  const tauxCouverture = stats.cantons > 0 ? Math.round((stats.cantonsCouvert / stats.cantons) * 100) : 0;

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
            Couverture Territoriale
          </h1>
          <p style={{ color: "var(--text-muted)", fontSize: "0.95rem", margin: 0 }}>
            Répartition géographique des acteurs agricoles au Togo
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

        {/* Taux de couverture */}
        <motion.div initial={{ opacity: 0, y: 16 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.2 }}
          style={{ background: "var(--surface)", border: "1px solid var(--border)", borderRadius: "16px", padding: "1.5rem", marginBottom: "1.5rem" }}>
          <h2 style={{ fontSize: "1.1rem", fontWeight: 700, color: "var(--text)", margin: "0 0 1rem" }}>
            Taux de couverture nationale
          </h2>
          <div style={{ display: "flex", alignItems: "center", gap: "1.5rem" }}>
            <div style={{ flex: 1 }}>
              <div style={{ background: "var(--bg)", borderRadius: "12px", height: "48px", position: "relative", overflow: "hidden" }}>
                <motion.div
                  initial={{ width: 0 }}
                  animate={{ width: `${tauxCouverture}%` }}
                  transition={{ delay: 0.3, duration: 1 }}
                  style={{ height: "100%", background: "linear-gradient(90deg, #16a34a, #22c55e)", borderRadius: "12px" }}
                />
                <div style={{ position: "absolute", inset: 0, display: "flex", alignItems: "center", justifyContent: "center", fontSize: "1.2rem", fontWeight: 800, color: "var(--text)" }}>
                  {tauxCouverture}%
                </div>
              </div>
              <div style={{ marginTop: "0.75rem", fontSize: "0.85rem", color: "var(--text-muted)", textAlign: "center" }}>
                {stats.cantonsCouvert} cantons sur {stats.cantons} couverts
              </div>
            </div>
          </div>
        </motion.div>

        {/* Répartition par région */}
        <motion.div initial={{ opacity: 0, y: 16 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.3 }}
          style={{ background: "var(--surface)", border: "1px solid var(--border)", borderRadius: "16px", padding: "1.5rem", marginBottom: "1.5rem" }}>
          <h2 style={{ fontSize: "1.1rem", fontWeight: 700, color: "var(--text)", margin: "0 0 1.5rem" }}>
            Répartition par région
          </h2>
          <div style={{ display: "grid", gap: "1rem" }}>
            {regionData.map((region, i) => (
              <motion.div key={region.nom}
                initial={{ opacity: 0, x: -20 }} animate={{ opacity: 1, x: 0 }} transition={{ delay: 0.35 + i * 0.05 }}
                style={{ background: "var(--bg)", border: "1px solid var(--border)", borderRadius: "12px", padding: "1.2rem" }}>
                <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "0.75rem" }}>
                  <div>
                    <h3 style={{ fontSize: "1rem", fontWeight: 700, color: "var(--text)", margin: "0 0 0.25rem" }}>
                      {region.nom}
                    </h3>
                    <div style={{ fontSize: "0.85rem", color: "var(--text-muted)" }}>
                      {region.prefectures} préfectures
                    </div>
                  </div>
                  <div style={{ textAlign: "right" }}>
                    <div style={{ fontSize: "1.5rem", fontWeight: 800, color: "var(--text)" }}>{region.total}</div>
                    <div style={{ fontSize: "0.75rem", color: "var(--text-muted)" }}>acteurs</div>
                  </div>
                </div>
                <div style={{ display: "flex", gap: "1.5rem", fontSize: "0.85rem", color: "var(--text-muted)" }}>
                  <div>👨‍🌾 {region.exploitants} exploitants</div>
                  <div>👨‍🎓 {region.agronomes} agronomes</div>
                </div>
              </motion.div>
            ))}
          </div>
        </motion.div>

        {/* Top 10 préfectures */}
        <motion.div initial={{ opacity: 0, y: 16 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.4 }}
          style={{ background: "var(--surface)", border: "1px solid var(--border)", borderRadius: "16px", padding: "1.5rem" }}>
          <h2 style={{ fontSize: "1.1rem", fontWeight: 700, color: "var(--text)", margin: "0 0 1.5rem" }}>
            Top 10 préfectures les plus actives
          </h2>
          <div style={{ display: "grid", gap: "0.75rem" }}>
            {prefectureData.map((pref, i) => (
              <motion.div key={pref.nom}
                initial={{ opacity: 0, x: -20 }} animate={{ opacity: 1, x: 0 }} transition={{ delay: 0.45 + i * 0.03 }}
                style={{ display: "flex", alignItems: "center", gap: "1rem", background: "var(--bg)", border: "1px solid var(--border)", borderRadius: "10px", padding: "1rem" }}>
                <div style={{ width: 32, height: 32, borderRadius: "8px", background: "#16a34a15", color: "#16a34a", display: "flex", alignItems: "center", justifyContent: "center", fontWeight: 800, fontSize: "0.9rem" }}>
                  {i + 1}
                </div>
                <div style={{ flex: 1 }}>
                  <div style={{ fontWeight: 700, color: "var(--text)", fontSize: "0.9rem" }}>{pref.nom}</div>
                  <div style={{ fontSize: "0.75rem", color: "var(--text-muted)" }}>
                    {pref.exploitants} exploitants • {pref.agronomes} agronomes
                  </div>
                </div>
                <div style={{ fontWeight: 800, fontSize: "1.2rem", color: "var(--text)" }}>{pref.total}</div>
              </motion.div>
            ))}
          </div>
        </motion.div>
      </div>
    </div>
  );
}
