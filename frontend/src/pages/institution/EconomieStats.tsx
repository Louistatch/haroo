import React, { useEffect, useState } from "react";
import { motion } from "framer-motion";
import api from "../../api/auth";

const IconCoin = () => <svg width="24" height="24" viewBox="0 0 24 24" fill="none"><circle cx="12" cy="12" r="9" stroke="currentColor" strokeWidth="1.5"/><path d="M12 7v10M9 9h6a2 2 0 000-4h-4a2 2 0 000 4h4a2 2 0 010 4H9" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round"/></svg>;
const IconTrending = () => <svg width="24" height="24" viewBox="0 0 24 24" fill="none"><path d="M2 12l4-4 3 3 7-7M16 4v5h-5" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round"/></svg>;
const IconCart = () => <svg width="24" height="24" viewBox="0 0 24 24" fill="none"><circle cx="9" cy="20" r="1" stroke="currentColor" strokeWidth="1.5"/><circle cx="18" cy="20" r="1" stroke="currentColor" strokeWidth="1.5"/><path d="M1 1h4l2.68 13.39a1 1 0 001 .78h9.72a1 1 0 001-.78L21 6H6" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round"/></svg>;
const IconDoc = () => <svg width="24" height="24" viewBox="0 0 24 24" fill="none"><path d="M4 3h9l5 5v11a2 2 0 01-2 2H4a2 2 0 01-2-2V5a2 2 0 012-2z" stroke="currentColor" strokeWidth="1.5"/><path d="M13 3v5h5M7 11h8M7 15h5" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round"/></svg>;

export default function EconomieStats() {
  const [stats, setStats] = useState({
    preventes: 0,
    volumePreventes: 0,
    documentsVendus: 0,
    revenusDocuments: 0,
  });
  const [preventes, setPreventes] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    Promise.all([
      api.get("/presales/preventes/"),
      api.get("/documents/"),
    ]).then(([preventesResp, docsResp]) => {
      const preventesData = preventesResp.data.results || preventesResp.data || [];
      const docsData = docsResp.data.results || docsResp.data || [];
      
      // Calculer le volume total des préventes
      const volumePreventes = preventesData.reduce((sum: number, p: any) => {
        return sum + (parseFloat(p.quantite_proposee) || 0);
      }, 0);

      setStats({
        preventes: preventesData.length,
        volumePreventes: Math.round(volumePreventes * 10) / 10,
        documentsVendus: 0, // À implémenter avec les achats
        revenusDocuments: 0, // À implémenter avec FedaPay
      });
      setPreventes(preventesData.slice(0, 10));
      setLoading(false);
    }).catch(() => setLoading(false));
  }, []);

  const mainStats = [
    { label: "Préventes actives", value: loading ? "…" : stats.preventes, icon: <IconCart />, color: "#16a34a" },
    { label: "Volume total (tonnes)", value: loading ? "…" : stats.volumePreventes, icon: <IconTrending />, color: "#2563eb" },
    { label: "Documents vendus", value: loading ? "…" : stats.documentsVendus, icon: <IconDoc />, color: "#f59e0b" },
    { label: "Revenus documents (FCFA)", value: loading ? "…" : stats.revenusDocuments, icon: <IconCoin />, color: "#7c3aed" },
  ];

  const produitsPopulaires = [
    { produit: "Maïs", volume: "—", valeur: "—", color: "#f59e0b" },
    { produit: "Riz", volume: "—", valeur: "—", color: "#16a34a" },
    { produit: "Soja", volume: "—", valeur: "—", color: "#2563eb" },
    { produit: "Arachide", volume: "—", valeur: "—", color: "#7c3aed" },
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
            Indicateurs Économiques
          </h1>
          <p style={{ color: "var(--text-muted)", fontSize: "0.95rem", margin: 0 }}>
            Suivi des transactions, préventes et revenus de la plateforme
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

        {/* Produits les plus échangés */}
        <motion.div initial={{ opacity: 0, y: 16 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.2 }}
          style={{ background: "var(--surface)", border: "1px solid var(--border)", borderRadius: "16px", padding: "1.5rem", marginBottom: "1.5rem" }}>
          <h2 style={{ fontSize: "1.1rem", fontWeight: 700, color: "var(--text)", margin: "0 0 1.5rem" }}>
            Produits les plus échangés
          </h2>
          <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fill, minmax(220px, 1fr))", gap: "1rem" }}>
            {produitsPopulaires.map((p, i) => (
              <motion.div key={p.produit}
                initial={{ opacity: 0, scale: 0.9 }} animate={{ opacity: 1, scale: 1 }} transition={{ delay: 0.25 + i * 0.05 }}
                style={{ background: "var(--bg)", border: "1px solid var(--border)", borderRadius: "12px", padding: "1.2rem" }}>
                <div style={{ display: "flex", alignItems: "center", gap: "0.5rem", marginBottom: "0.75rem" }}>
                  <div style={{ width: 10, height: 10, borderRadius: "50%", background: p.color }} />
                  <div style={{ fontWeight: 700, color: "var(--text)", fontSize: "0.95rem" }}>{p.produit}</div>
                </div>
                <div style={{ fontSize: "0.75rem", color: "var(--text-muted)", marginBottom: "0.25rem" }}>Volume: {p.volume}</div>
                <div style={{ fontSize: "0.75rem", color: "var(--text-muted)" }}>Valeur: {p.valeur}</div>
              </motion.div>
            ))}
          </div>
        </motion.div>

        {/* Dernières préventes */}
        <motion.div initial={{ opacity: 0, y: 16 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.3 }}
          style={{ background: "var(--surface)", border: "1px solid var(--border)", borderRadius: "16px", padding: "1.5rem" }}>
          <h2 style={{ fontSize: "1.1rem", fontWeight: 700, color: "var(--text)", margin: "0 0 1.5rem" }}>
            Dernières préventes
          </h2>
          {preventes.length === 0 ? (
            <div style={{ padding: "2rem", textAlign: "center", color: "var(--text-muted)" }}>
              Aucune prévente disponible pour le moment
            </div>
          ) : (
            <div style={{ display: "grid", gap: "1rem" }}>
              {preventes.map((prevente, i) => (
                <motion.div key={prevente.id}
                  initial={{ opacity: 0, x: -20 }} animate={{ opacity: 1, x: 0 }} transition={{ delay: 0.35 + i * 0.05 }}
                  style={{ background: "var(--bg)", border: "1px solid var(--border)", borderRadius: "12px", padding: "1.2rem" }}>
                  <div style={{ display: "flex", justifyContent: "space-between", alignItems: "start", marginBottom: "0.75rem" }}>
                    <div>
                      <h3 style={{ fontSize: "1rem", fontWeight: 700, color: "var(--text)", margin: "0 0 0.25rem" }}>
                        {prevente.produit}
                      </h3>
                      <div style={{ fontSize: "0.85rem", color: "var(--text-muted)" }}>
                        {prevente.exploitant_nom || "Exploitant"} • {prevente.canton_nom || "Canton"}
                      </div>
                    </div>
                    <span style={{ 
                      padding: "0.25rem 0.75rem", 
                      borderRadius: "100px", 
                      fontSize: "0.75rem", 
                      fontWeight: 600,
                      background: prevente.statut === 'DISPONIBLE' ? '#dcfce7' : '#fef3c7',
                      color: prevente.statut === 'DISPONIBLE' ? '#16a34a' : '#f59e0b'
                    }}>
                      {prevente.statut}
                    </span>
                  </div>
                  <div style={{ display: "flex", gap: "1.5rem", fontSize: "0.85rem", color: "var(--text-muted)" }}>
                    <div>📦 {prevente.quantite_proposee} tonnes</div>
                    <div>💰 {prevente.prix_unitaire} FCFA/kg</div>
                    <div>📅 {new Date(prevente.date_recolte_prevue).toLocaleDateString('fr-FR')}</div>
                  </div>
                </motion.div>
              ))}
            </div>
          )}
        </motion.div>

        {/* Note sur FedaPay */}
        <motion.div initial={{ opacity: 0, y: 16 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.4 }}
          style={{ marginTop: "1.5rem", padding: "1.2rem", background: "#dbeafe", border: "1px solid #2563eb", borderRadius: "12px" }}>
          <p style={{ margin: 0, fontSize: "0.85rem", color: "#1e40af" }}>
            ℹ️ Les données de transactions FedaPay seront disponibles une fois l'intégration de paiement activée.
          </p>
        </motion.div>
      </div>
    </div>
  );
}
