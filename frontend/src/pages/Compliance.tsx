import React, { useState, useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";
import {
  getCGU,
  getPrivacyPolicy,
  acceptCGU,
  requestDataExport,
  requestAccountDeletion,
} from "../api/compliance";

const ShieldIcon = () => (
  <svg width="20" height="20" viewBox="0 0 20 20" fill="none">
    <path d="M10 2l6 3v4c0 4.5-2.5 7.5-6 9-3.5-1.5-6-4.5-6-9V5l6-3z" stroke="currentColor" strokeWidth="1.5" strokeLinejoin="round" />
    <path d="M7.5 10l2 2 3.5-3.5" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" />
  </svg>
);

type Tab = "cgu" | "privacy" | "data";

export default function Compliance() {
  const [activeTab, setActiveTab] = useState<Tab>("cgu");
  const [cguContent, setCguContent] = useState("");
  const [privacyContent, setPrivacyContent] = useState("");
  const [loading, setLoading] = useState(false);
  const [actionLoading, setActionLoading] = useState(false);
  const [toast, setToast] = useState("");
  const [showDeleteConfirm, setShowDeleteConfirm] = useState(false);
  const [deleteReason, setDeleteReason] = useState("");

  function showToast(msg: string) {
    setToast(msg);
    setTimeout(() => setToast(""), 4000);
  }

  useEffect(() => {
    if (activeTab === "cgu" && !cguContent) {
      setLoading(true);
      getCGU().then(c => setCguContent(typeof c === "string" ? c : JSON.stringify(c)))
        .catch(() => setCguContent("Impossible de charger les CGU."))
        .finally(() => setLoading(false));
    }
    if (activeTab === "privacy" && !privacyContent) {
      setLoading(true);
      getPrivacyPolicy().then(c => setPrivacyContent(typeof c === "string" ? c : JSON.stringify(c)))
        .catch(() => setPrivacyContent("Impossible de charger la politique de confidentialité."))
        .finally(() => setLoading(false));
    }
  }, [activeTab, cguContent, privacyContent]);

  async function handleAcceptCGU() {
    setActionLoading(true);
    try {
      await acceptCGU("1.0");
      showToast("CGU acceptées avec succès.");
    } catch {
      showToast("Erreur lors de l'acceptation des CGU.");
    } finally {
      setActionLoading(false);
    }
  }

  async function handleExportData() {
    setActionLoading(true);
    try {
      await requestDataExport();
      showToast("Demande d'export envoyée. Vous recevrez un lien par email.");
    } catch {
      showToast("Erreur lors de la demande d'export.");
    } finally {
      setActionLoading(false);
    }
  }

  async function handleDeleteAccount() {
    setActionLoading(true);
    try {
      await requestAccountDeletion(deleteReason || undefined);
      showToast("Demande de suppression envoyée. Vous serez contacté sous 48h.");
      setShowDeleteConfirm(false);
      setDeleteReason("");
    } catch {
      showToast("Erreur lors de la demande de suppression.");
    } finally {
      setActionLoading(false);
    }
  }

  const tabs = [
    { key: "cgu" as const, label: "Conditions Générales", icon: "📜" },
    { key: "privacy" as const, label: "Confidentialité", icon: "🔒" },
    { key: "data" as const, label: "Mes Données", icon: "📦" },
  ];

  return (
    <div style={{ maxWidth: 900, margin: "0 auto", padding: "2.5rem 1.5rem 4rem" }}>
      {/* Toast */}
      <AnimatePresence>
        {toast && (
          <motion.div initial={{ opacity: 0, y: -20 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0, y: -20 }}
            style={{ position: "fixed", top: 80, left: "50%", transform: "translateX(-50%)", background: "#1a1a1a", color: "#fff", padding: "10px 20px", borderRadius: 10, fontSize: 14, fontWeight: 500, zIndex: 500, boxShadow: "0 8px 24px rgba(0,0,0,0.2)" }}>
            {toast}
          </motion.div>
        )}
      </AnimatePresence>

      {/* Header */}
      <div style={{ marginBottom: "2rem" }}>
        <motion.div initial={{ opacity: 0, y: -10 }} animate={{ opacity: 1, y: 0 }}
          style={{ display: "inline-flex", alignItems: "center", gap: 8, background: "rgba(22,163,74,0.1)", border: "1px solid rgba(22,163,74,0.2)", borderRadius: 100, padding: "6px 16px", marginBottom: "1rem" }}>
          <ShieldIcon />
          <span style={{ fontSize: "0.85rem", fontWeight: 600, color: "var(--primary)" }}>CONFORMITÉ</span>
        </motion.div>
        <h1 style={{ margin: 0, fontSize: "1.75rem", fontWeight: 800, color: "var(--text)" }}>
          Conformité & Données Personnelles
        </h1>
        <p style={{ margin: "6px 0 0", color: "var(--text-secondary)", fontSize: 15 }}>
          Consultez les CGU, la politique de confidentialité et gérez vos données
        </p>
      </div>

      {/* Tabs */}
      <div style={{ display: "flex", gap: 4, marginBottom: "1.5rem", flexWrap: "wrap" }}>
        {tabs.map(tab => {
          const active = activeTab === tab.key;
          return (
            <button key={tab.key} onClick={() => setActiveTab(tab.key)}
              style={{ padding: "8px 16px", borderRadius: 8, border: "1px solid", borderColor: active ? "var(--primary)" : "var(--border)", background: active ? "var(--primary)" : "none", color: active ? "#fff" : "var(--text-secondary)", fontSize: 13, fontWeight: active ? 600 : 400, cursor: "pointer", transition: "all 0.15s", display: "flex", alignItems: "center", gap: 6 }}>
              <span>{tab.icon}</span> {tab.label}
            </button>
          );
        })}
      </div>

      {/* Loading */}
      {loading && (
        <div style={{ textAlign: "center", padding: "4rem 0", color: "var(--text-secondary)" }}>
          <div style={{ width: 32, height: 32, borderRadius: "50%", border: "3px solid var(--border)", borderTopColor: "var(--primary)", margin: "0 auto 12px", animation: "spin 0.8s linear infinite" }} />
          Chargement...
        </div>
      )}

      {/* CGU */}
      {!loading && activeTab === "cgu" && (
        <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }}
          style={{ background: "var(--surface)", border: "1px solid var(--border)", borderRadius: 14, padding: "2rem" }}>
          <div style={{ whiteSpace: "pre-wrap", lineHeight: 1.8, color: "var(--text)", fontSize: 14, maxHeight: 500, overflowY: "auto", marginBottom: "1.5rem" }}>
            {cguContent || "Contenu non disponible."}
          </div>
          <button onClick={handleAcceptCGU} disabled={actionLoading}
            style={{ padding: "10px 24px", borderRadius: 10, border: "none", background: "var(--primary)", color: "#fff", fontWeight: 600, fontSize: 14, cursor: actionLoading ? "wait" : "pointer", opacity: actionLoading ? 0.7 : 1 }}>
            {actionLoading ? "Envoi..." : "✓ Accepter les CGU"}
          </button>
        </motion.div>
      )}

      {/* Privacy */}
      {!loading && activeTab === "privacy" && (
        <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }}
          style={{ background: "var(--surface)", border: "1px solid var(--border)", borderRadius: 14, padding: "2rem" }}>
          <div style={{ whiteSpace: "pre-wrap", lineHeight: 1.8, color: "var(--text)", fontSize: 14, maxHeight: 500, overflowY: "auto" }}>
            {privacyContent || "Contenu non disponible."}
          </div>
        </motion.div>
      )}

      {/* Data management */}
      {!loading && activeTab === "data" && (
        <div style={{ display: "flex", flexDirection: "column", gap: 16 }}>
          {/* Export */}
          <motion.div initial={{ opacity: 0, y: 12 }} animate={{ opacity: 1, y: 0 }}
            style={{ background: "var(--surface)", border: "1px solid var(--border)", borderRadius: 14, padding: "1.5rem" }}>
            <h3 style={{ margin: "0 0 8px", fontSize: "1.05rem", fontWeight: 700, color: "var(--text)" }}>📦 Exporter mes données</h3>
            <p style={{ margin: "0 0 1rem", color: "var(--text-secondary)", fontSize: 14, lineHeight: 1.6 }}>
              Conformément au RGPD, vous pouvez demander une copie de toutes vos données personnelles. Le fichier sera envoyé à votre adresse email.
            </p>
            <button onClick={handleExportData} disabled={actionLoading}
              style={{ padding: "10px 20px", borderRadius: 10, border: "1px solid var(--border)", background: "var(--surface)", color: "var(--text)", fontWeight: 600, fontSize: 13, cursor: actionLoading ? "wait" : "pointer" }}>
              {actionLoading ? "Envoi..." : "Demander l'export"}
            </button>
          </motion.div>

          {/* Delete account */}
          <motion.div initial={{ opacity: 0, y: 12 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.1 }}
            style={{ background: "var(--surface)", border: "1px solid #fecaca", borderRadius: 14, padding: "1.5rem" }}>
            <h3 style={{ margin: "0 0 8px", fontSize: "1.05rem", fontWeight: 700, color: "#dc2626" }}>⚠️ Supprimer mon compte</h3>
            <p style={{ margin: "0 0 1rem", color: "var(--text-secondary)", fontSize: 14, lineHeight: 1.6 }}>
              Cette action est irréversible. Toutes vos données seront supprimées conformément à notre politique de rétention.
            </p>
            {!showDeleteConfirm ? (
              <button onClick={() => setShowDeleteConfirm(true)}
                style={{ padding: "10px 20px", borderRadius: 10, border: "1px solid #fecaca", background: "none", color: "#dc2626", fontWeight: 600, fontSize: 13, cursor: "pointer" }}>
                Supprimer mon compte
              </button>
            ) : (
              <div style={{ display: "flex", flexDirection: "column", gap: 10 }}>
                <textarea rows={3} placeholder="Raison de la suppression (optionnel)..." value={deleteReason}
                  onChange={e => setDeleteReason(e.target.value)}
                  style={{ width: "100%", padding: "10px 12px", borderRadius: 10, border: "1px solid var(--border)", background: "var(--bg)", color: "var(--text)", fontSize: 14, resize: "vertical", fontFamily: "inherit", boxSizing: "border-box", outline: "none" }} />
                <div style={{ display: "flex", gap: 8 }}>
                  <button onClick={() => setShowDeleteConfirm(false)}
                    style={{ padding: "10px 18px", borderRadius: 10, border: "1px solid var(--border)", background: "none", color: "var(--text)", fontWeight: 500, fontSize: 13, cursor: "pointer" }}>
                    Annuler
                  </button>
                  <button onClick={handleDeleteAccount} disabled={actionLoading}
                    style={{ padding: "10px 18px", borderRadius: 10, border: "none", background: "#dc2626", color: "#fff", fontWeight: 600, fontSize: 13, cursor: actionLoading ? "wait" : "pointer", opacity: actionLoading ? 0.7 : 1 }}>
                    {actionLoading ? "Envoi..." : "Confirmer la suppression"}
                  </button>
                </div>
              </div>
            )}
          </motion.div>
        </div>
      )}

      <style>{`
        @keyframes spin { to { transform: rotate(360deg); } }
      `}</style>
    </div>
  );
}
