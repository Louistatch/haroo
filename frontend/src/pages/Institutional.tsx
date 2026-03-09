import React, { useState, useEffect } from "react";
import { motion } from "framer-motion";
import {
  getDashboard,
  exportReport,
  InstitutionalDashboard,
} from "../api/institutional";

function formatNumber(n: number) {
  return n.toLocaleString("fr-FR");
}

function formatCurrency(n: number) {
  return n.toLocaleString("fr-FR") + " FCFA";
}

const STAT_ICONS: Record<string, string> = {
  total_utilisateurs: "👥",
  total_exploitants: "🌾",
  total_agronomes: "🔬",
  total_ouvriers: "👷",
  total_missions: "📋",
  total_transactions: "💳",
  volume_transactions: "💰",
};

const STAT_LABELS: Record<string, string> = {
  total_utilisateurs: "Utilisateurs",
  total_exploitants: "Exploitants",
  total_agronomes: "Agronomes",
  total_ouvriers: "Ouvriers",
  total_missions: "Missions",
  total_transactions: "Transactions",
  volume_transactions: "Volume total",
};

function StatCard({ label, value, icon, index }: { label: string; value: string; icon: string; index: number }) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 16 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: index * 0.05, duration: 0.3 }}
      style={{
        background: "var(--surface)", border: "1px solid var(--border)", borderRadius: 14,
        padding: "1.25rem", display: "flex", alignItems: "center", gap: 14,
      }}
    >
      <div style={{ width: 48, height: 48, borderRadius: 12, background: "var(--bg)", display: "flex", alignItems: "center", justifyContent: "center", fontSize: 24, flexShrink: 0 }}>
        {icon}
      </div>
      <div>
        <div style={{ fontSize: "1.4rem", fontWeight: 800, color: "var(--text)" }}>{value}</div>
        <div style={{ fontSize: 13, color: "var(--text-secondary)", fontWeight: 500 }}>{label}</div>
      </div>
    </motion.div>
  );
}

export default function Institutional() {
  const [data, setData] = useState<InstitutionalDashboard | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [exporting, setExporting] = useState(false);
  const [activeTab, setActiveTab] = useState<"overview" | "prefectures" | "trends">("overview");

  useEffect(() => {
    setLoading(true);
    getDashboard()
      .then(setData)
      .catch(() => setError("Impossible de charger le dashboard institutionnel."))
      .finally(() => setLoading(false));
  }, []);

  async function handleExport(format: "excel" | "pdf") {
    setExporting(true);
    try {
      const blob = await exportReport(format);
      const url = URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = `rapport-haroo.${format === "excel" ? "xlsx" : "pdf"}`;
      a.click();
      URL.revokeObjectURL(url);
    } catch {
      alert("Erreur lors de l'export du rapport.");
    } finally {
      setExporting(false);
    }
  }

  const tabs = [
    { key: "overview" as const, label: "Vue d'ensemble" },
    { key: "prefectures" as const, label: "Par préfecture" },
    { key: "trends" as const, label: "Tendances" },
  ];

  return (
    <div style={{ maxWidth: 1100, margin: "0 auto", padding: "2.5rem 1.5rem 4rem" }}>
      {/* Header */}
      <div style={{ display: "flex", alignItems: "flex-start", justifyContent: "space-between", gap: 16, marginBottom: "2rem", flexWrap: "wrap" }}>
        <div>
          <motion.div initial={{ opacity: 0, y: -10 }} animate={{ opacity: 1, y: 0 }}
            style={{ display: "inline-flex", alignItems: "center", gap: 8, background: "rgba(99,102,241,0.1)", border: "1px solid rgba(99,102,241,0.2)", borderRadius: 100, padding: "6px 16px", marginBottom: "1rem" }}>
            <span style={{ fontSize: "0.85rem", fontWeight: 600, color: "#6366f1" }}>🏛️ DASHBOARD INSTITUTIONNEL</span>
          </motion.div>
          <h1 style={{ margin: 0, fontSize: "1.75rem", fontWeight: 800, color: "var(--text)" }}>
            Statistiques Nationales
          </h1>
          <p style={{ margin: "6px 0 0", color: "var(--text-secondary)", fontSize: 15 }}>
            Indicateurs agrégés et anonymisés de la plateforme Haroo
          </p>
        </div>
        <div style={{ display: "flex", gap: 8 }}>
          <button onClick={() => handleExport("excel")} disabled={exporting || loading}
            style={{ padding: "10px 18px", borderRadius: 10, border: "1px solid var(--border)", background: "var(--surface)", color: "var(--text)", fontWeight: 600, fontSize: 13, cursor: exporting ? "wait" : "pointer" }}>
            📊 Export Excel
          </button>
          <button onClick={() => handleExport("pdf")} disabled={exporting || loading}
            style={{ padding: "10px 18px", borderRadius: 10, border: "none", background: "#6366f1", color: "#fff", fontWeight: 600, fontSize: 13, cursor: exporting ? "wait" : "pointer" }}>
            📄 Export PDF
          </button>
        </div>
      </div>

      {/* Loading */}
      {loading && (
        <div style={{ textAlign: "center", padding: "4rem 0", color: "var(--text-secondary)" }}>
          <div style={{ width: 32, height: 32, borderRadius: "50%", border: "3px solid var(--border)", borderTopColor: "#6366f1", margin: "0 auto 12px", animation: "spin 0.8s linear infinite" }} />
          Chargement des données...
        </div>
      )}

      {/* Error */}
      {!loading && error && (
        <div style={{ textAlign: "center", padding: "3rem 0", color: "#dc2626" }}>{error}</div>
      )}

      {/* Content */}
      {!loading && !error && data && (
        <>
          {/* Tabs */}
          <div style={{ display: "flex", gap: 4, marginBottom: "1.5rem", flexWrap: "wrap" }}>
            {tabs.map(tab => {
              const active = activeTab === tab.key;
              return (
                <button key={tab.key} onClick={() => setActiveTab(tab.key)}
                  style={{ padding: "8px 16px", borderRadius: 8, border: "1px solid", borderColor: active ? "#6366f1" : "var(--border)", background: active ? "#6366f1" : "none", color: active ? "#fff" : "var(--text-secondary)", fontSize: 13, fontWeight: active ? 600 : 400, cursor: "pointer", transition: "all 0.15s" }}>
                  {tab.label}
                </button>
              );
            })}
          </div>

          {/* Overview */}
          {activeTab === "overview" && (
            <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fill, minmax(240px, 1fr))", gap: 12 }}>
              {Object.entries(data.aggregated).map(([key, value], i) => (
                <StatCard key={key} label={STAT_LABELS[key] || key} icon={STAT_ICONS[key] || "📊"}
                  value={key === "volume_transactions" ? formatCurrency(value) : formatNumber(value)} index={i} />
              ))}
            </div>
          )}

          {/* By Prefecture */}
          {activeTab === "prefectures" && (
            <div style={{ background: "var(--surface)", border: "1px solid var(--border)", borderRadius: 14, overflow: "hidden" }}>
              <div style={{ overflowX: "auto" }}>
                <table style={{ width: "100%", borderCollapse: "collapse", fontSize: 14 }}>
                  <thead>
                    <tr style={{ borderBottom: "1px solid var(--border)" }}>
                      {["Préfecture", "Exploitants", "Agronomes", "Missions", "Volume"].map(h => (
                        <th key={h} style={{ padding: "12px 16px", textAlign: "left", fontWeight: 600, color: "var(--text-secondary)", fontSize: 12, textTransform: "uppercase", letterSpacing: "0.05em" }}>{h}</th>
                      ))}
                    </tr>
                  </thead>
                  <tbody>
                    {data.by_prefecture.map((row, i) => (
                      <motion.tr key={row.prefecture} initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ delay: i * 0.03 }}
                        style={{ borderBottom: "1px solid var(--border)" }}>
                        <td style={{ padding: "12px 16px", fontWeight: 600, color: "var(--text)" }}>{row.prefecture}</td>
                        <td style={{ padding: "12px 16px", color: "var(--text)" }}>{formatNumber(row.exploitants)}</td>
                        <td style={{ padding: "12px 16px", color: "var(--text)" }}>{formatNumber(row.agronomes)}</td>
                        <td style={{ padding: "12px 16px", color: "var(--text)" }}>{formatNumber(row.missions)}</td>
                        <td style={{ padding: "12px 16px", color: "var(--primary)", fontWeight: 600 }}>{formatCurrency(row.volume_transactions)}</td>
                      </motion.tr>
                    ))}
                    {data.by_prefecture.length === 0 && (
                      <tr><td colSpan={5} style={{ padding: "2rem", textAlign: "center", color: "var(--text-secondary)" }}>Aucune donnée disponible</td></tr>
                    )}
                  </tbody>
                </table>
              </div>
            </div>
          )}

          {/* Trends */}
          {activeTab === "trends" && (
            <div style={{ display: "flex", flexDirection: "column", gap: 12 }}>
              {data.monthly_trends.length === 0 ? (
                <div style={{ textAlign: "center", padding: "3rem 0", color: "var(--text-secondary)" }}>Aucune tendance disponible</div>
              ) : (
                <div style={{ background: "var(--surface)", border: "1px solid var(--border)", borderRadius: 14, overflow: "hidden" }}>
                  <div style={{ overflowX: "auto" }}>
                    <table style={{ width: "100%", borderCollapse: "collapse", fontSize: 14 }}>
                      <thead>
                        <tr style={{ borderBottom: "1px solid var(--border)" }}>
                          {["Mois", "Inscriptions", "Missions", "Transactions"].map(h => (
                            <th key={h} style={{ padding: "12px 16px", textAlign: "left", fontWeight: 600, color: "var(--text-secondary)", fontSize: 12, textTransform: "uppercase", letterSpacing: "0.05em" }}>{h}</th>
                          ))}
                        </tr>
                      </thead>
                      <tbody>
                        {data.monthly_trends.map((row, i) => (
                          <motion.tr key={row.mois} initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ delay: i * 0.03 }}
                            style={{ borderBottom: "1px solid var(--border)" }}>
                            <td style={{ padding: "12px 16px", fontWeight: 600, color: "var(--text)" }}>{row.mois}</td>
                            <td style={{ padding: "12px 16px", color: "var(--text)" }}>{formatNumber(row.inscriptions)}</td>
                            <td style={{ padding: "12px 16px", color: "var(--text)" }}>{formatNumber(row.missions)}</td>
                            <td style={{ padding: "12px 16px", color: "var(--primary)", fontWeight: 600 }}>{formatNumber(row.transactions)}</td>
                          </motion.tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                </div>
              )}
            </div>
          )}
        </>
      )}

      <style>{`
        @keyframes spin { to { transform: rotate(360deg); } }
      `}</style>
    </div>
  );
}
