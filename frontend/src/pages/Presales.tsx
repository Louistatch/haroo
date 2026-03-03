import React, { useState, useEffect, useCallback } from "react";
import { motion, AnimatePresence } from "framer-motion";
import {
  getPreventes,
  createPrevente,
  engagerPrevente,
  getMesEngagements,
  Prevente,
  Engagement,
} from "../api/presales";

const ACCENT_COLOR = "#7c3aed";

function getUserType(): string {
  try {
    const token = localStorage.getItem("access_token");
    if (!token) return "";
    const payload = JSON.parse(atob(token.split(".")[1]));
    return payload.user_type || "";
  } catch {
    return "";
  }
}

function formatDate(d: string | null) {
  if (!d) return "—";
  return new Date(d).toLocaleDateString("fr-FR", {
    day: "2-digit",
    month: "short",
    year: "numeric",
  });
}

function formatAmount(v: string | number) {
  return Number(v).toLocaleString("fr-FR") + " FCFA";
}

const STATUS_MAP: Record<string, { label: string; color: string; bg: string }> = {
  DISPONIBLE: { label: "Disponible", color: "#16a34a", bg: "#dcfce7" },
  ENGAGEE: { label: "Engagée", color: "#ea580c", bg: "#ffedd5" },
  LIVREE: { label: "Livrée", color: "#64748b", bg: "#f1f5f9" },
  ANNULEE: { label: "Annulée", color: "#dc2626", bg: "#fee2e2" },
};

function StatusBadge({ statut }: { statut: string }) {
  const s = STATUS_MAP[statut] || { label: statut, color: "#64748b", bg: "#f1f5f9" };
  return (
    <span style={{
      display: "inline-block",
      padding: "3px 10px",
      borderRadius: 20,
      fontSize: 12,
      fontWeight: 600,
      color: s.color,
      background: s.bg,
    }}>
      {s.label}
    </span>
  );
}

function PreventeCard({ 
  prevente, 
  userType, 
  onEngage 
}: { 
  prevente: Prevente; 
  userType: string;
  onEngage: (p: Prevente) => void;
}) {
  return (
    <motion.div
      layout
      initial={{ opacity: 0, y: 16 }}
      animate={{ opacity: 1, y: 0 }}
      style={{
        background: "var(--card)",
        border: "1px solid var(--border)",
        borderRadius: 14,
        padding: "1.25rem",
        display: "flex",
        flexDirection: "column",
        gap: "1rem",
      }}
    >
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start" }}>
        <div>
          <h3 style={{ margin: 0, fontSize: "1.1rem", fontWeight: 700, color: "var(--text)" }}>{prevente.culture}</h3>
          <p style={{ margin: "2px 0 0", fontSize: 13, color: "var(--muted)" }}>{prevente.canton_nom}</p>
        </div>
        <StatusBadge statut={prevente.statut} />
      </div>

      <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "0.75rem", fontSize: 13 }}>
        <div>
          <p style={{ margin: 0, color: "var(--muted)" }}>Quantité</p>
          <p style={{ margin: 0, fontWeight: 600 }}>{prevente.quantite_estimee} Tonnes</p>
        </div>
        <div>
          <p style={{ margin: 0, color: "var(--muted)" }}>Prix / Tonne</p>
          <p style={{ margin: 0, fontWeight: 600 }}>{formatAmount(prevente.prix_par_tonne)}</p>
        </div>
        <div>
          <p style={{ margin: 0, color: "var(--muted)" }}>Total estimé</p>
          <p style={{ margin: 0, fontWeight: 600, color: ACCENT_COLOR }}>{formatAmount(prevente.montant_total)}</p>
        </div>
        <div>
          <p style={{ margin: 0, color: "var(--muted)" }}>Récolte prévue</p>
          <p style={{ margin: 0, fontWeight: 600 }}>{formatDate(prevente.date_recolte_prevue)}</p>
        </div>
      </div>

      {prevente.description && (
        <p style={{ margin: 0, fontSize: 13, color: "var(--text)", opacity: 0.8, lineHeight: 1.5 }}>
          {prevente.description}
        </p>
      )}

      {userType === "ACHETEUR" && prevente.statut === "DISPONIBLE" && (
        <button
          onClick={() => onEngage(prevente)}
          style={{
            marginTop: "0.5rem",
            padding: "10px",
            borderRadius: 10,
            border: "none",
            background: ACCENT_COLOR,
            color: "#fff",
            fontWeight: 600,
            cursor: "pointer",
          }}
        >
          S'engager
        </button>
      )}
    </motion.div>
  );
}

function EngagementCard({ engagement }: { engagement: Engagement }) {
  return (
    <div style={{
      background: "var(--bg)",
      border: "1px solid var(--border)",
      borderRadius: 12,
      padding: "1rem",
      display: "flex",
      flexDirection: "column",
      gap: "0.5rem",
    }}>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
        <h4 style={{ margin: 0, fontWeight: 700 }}>{engagement.prevente_detail?.culture || `Prévente #${engagement.prevente}`}</h4>
        <span style={{ fontSize: 12, fontWeight: 600, color: ACCENT_COLOR }}>{engagement.statut}</span>
      </div>
      <div style={{ display: "grid", gridTemplateColumns: "1fr 1.5fr", gap: "0.5rem", fontSize: 13 }}>
        <span style={{ color: "var(--muted)" }}>Quantité :</span>
        <span style={{ fontWeight: 600 }}>{engagement.quantite_engagee} Tonnes</span>
        <span style={{ color: "var(--muted)" }}>Acompte (20%) :</span>
        <span style={{ fontWeight: 600, color: "#16a34a" }}>{formatAmount(engagement.acompte_20)}</span>
        <span style={{ color: "var(--muted)" }}>Total :</span>
        <span style={{ fontWeight: 600 }}>{formatAmount(engagement.montant_total)}</span>
      </div>
    </div>
  );
}

function CreatePreventeModal({ onClose, onCreated }: { onClose: () => void; onCreated: () => void }) {
  const [formData, setFormData] = useState({
    culture: "",
    quantite_estimee: "",
    prix_par_tonne: "",
    date_recolte_prevue: "",
    canton: "",
    description: "",
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setLoading(true);
    setError("");
    try {
      await createPrevente(formData);
      onCreated();
      onClose();
    } catch (err: any) {
      setError("Erreur lors de la création de la prévente.");
    } finally {
      setLoading(false);
    }
  }

  const inputStyle = {
    width: "100%", padding: "10px", borderRadius: 8, border: "1px solid var(--border)",
    background: "var(--bg)", color: "var(--text)", boxSizing: "border-box" as const, marginBottom: "1rem"
  };

  return (
    <div style={{ position: "fixed", inset: 0, zIndex: 300, background: "rgba(0,0,0,0.5)", display: "flex", alignItems: "center", justifyContent: "center", padding: "1rem" }}>
      <motion.div initial={{ opacity: 0, scale: 0.95 }} animate={{ opacity: 1, scale: 1 }} style={{ background: "var(--card)", padding: "2rem", borderRadius: 16, width: "100%", maxWidth: 500 }}>
        <h2 style={{ margin: "0 0 1.5rem" }}>Nouvelle prévente</h2>
        <form onSubmit={handleSubmit}>
          <label style={{ fontSize: 13, fontWeight: 600, display: "block", marginBottom: 4 }}>Culture</label>
          <input required style={inputStyle} value={formData.culture} onChange={e => setFormData({...formData, culture: e.target.value})} placeholder="ex: Maïs, Soja..." />
          
          <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "1rem" }}>
            <div>
              <label style={{ fontSize: 13, fontWeight: 600, display: "block", marginBottom: 4 }}>Quantité (Tonnes)</label>
              <input required type="number" step="0.01" style={inputStyle} value={formData.quantite_estimee} onChange={e => setFormData({...formData, quantite_estimee: e.target.value})} />
            </div>
            <div>
              <label style={{ fontSize: 13, fontWeight: 600, display: "block", marginBottom: 4 }}>Prix / Tonne (FCFA)</label>
              <input required type="number" style={inputStyle} value={formData.prix_par_tonne} onChange={e => setFormData({...formData, prix_par_tonne: e.target.value})} />
            </div>
          </div>

          <label style={{ fontSize: 13, fontWeight: 600, display: "block", marginBottom: 4 }}>Date de récolte prévue</label>
          <input required type="date" style={inputStyle} value={formData.date_recolte_prevue} onChange={e => setFormData({...formData, date_recolte_prevue: e.target.value})} />

          <label style={{ fontSize: 13, fontWeight: 600, display: "block", marginBottom: 4 }}>Canton (ID)</label>
          <input required type="number" style={inputStyle} value={formData.canton} onChange={e => setFormData({...formData, canton: e.target.value})} placeholder="ID du canton" />

          <label style={{ fontSize: 13, fontWeight: 600, display: "block", marginBottom: 4 }}>Description</label>
          <textarea style={{ ...inputStyle, height: 80 }} value={formData.description} onChange={e => setFormData({...formData, description: e.target.value})} />

          {error && <p style={{ color: "red", fontSize: 13 }}>{error}</p>}
          <div style={{ display: "flex", gap: "1rem", marginTop: "1rem" }}>
            <button type="button" onClick={onClose} style={{ flex: 1, padding: "12px", borderRadius: 8, border: "1px solid var(--border)", background: "none", cursor: "pointer" }}>Annuler</button>
            <button type="submit" disabled={loading} style={{ flex: 1, padding: "12px", borderRadius: 8, border: "none", background: "#16a34a", color: "white", fontWeight: 600, cursor: "pointer" }}>
              {loading ? "Création..." : "Créer"}
            </button>
          </div>
        </form>
      </motion.div>
    </div>
  );
}

function EngagementModal({ prevente, onClose, onEngaged }: { prevente: Prevente; onClose: () => void; onEngaged: () => void }) {
  const [quantite, setQuantite] = useState(prevente.quantite_estimee);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const total = Number(quantite) * Number(prevente.prix_par_tonne);
  const acompte = total * 0.2;

  async function handleEngage() {
    setLoading(true);
    setError("");
    try {
      await engagerPrevente(prevente.id, Number(quantite));
      onEngaged();
      onClose();
    } catch (err: any) {
      setError("Erreur lors de l'engagement.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div style={{ position: "fixed", inset: 0, zIndex: 300, background: "rgba(0,0,0,0.5)", display: "flex", alignItems: "center", justifyContent: "center", padding: "1rem" }}>
      <motion.div initial={{ opacity: 0, scale: 0.95 }} animate={{ opacity: 1, scale: 1 }} style={{ background: "var(--card)", padding: "2rem", borderRadius: 16, width: "100%", maxWidth: 450 }}>
        <h2 style={{ margin: "0 0 1rem" }}>S'engager sur : {prevente.culture}</h2>
        <p style={{ fontSize: 14, color: "var(--muted)", marginBottom: "1.5rem" }}>
          Un acompte de 20% est requis pour valider l'engagement.
        </p>

        <label style={{ fontSize: 13, fontWeight: 600, display: "block", marginBottom: 4 }}>Quantité à engager (Tonnes)</label>
        <input 
          type="number" 
          max={prevente.quantite_estimee} 
          step="0.01" 
          style={{ width: "100%", padding: "12px", borderRadius: 8, border: "1px solid var(--border)", background: "var(--bg)", color: "var(--text)", boxSizing: "border-box", marginBottom: "1.5rem" }}
          value={quantite}
          onChange={e => setQuantite(e.target.value)}
        />

        <div style={{ background: "var(--bg)", padding: "1rem", borderRadius: 10, marginBottom: "1.5rem", fontSize: 14 }}>
          <div style={{ display: "flex", justifyContent: "space-between", marginBottom: 8 }}>
            <span>Total estimé :</span>
            <span style={{ fontWeight: 600 }}>{formatAmount(total)}</span>
          </div>
          <div style={{ display: "flex", justifyContent: "space-between", color: "#16a34a" }}>
            <span style={{ fontWeight: 600 }}>Acompte à payer (20%) :</span>
            <span style={{ fontWeight: 800 }}>{formatAmount(acompte)}</span>
          </div>
        </div>

        {error && <p style={{ color: "red", fontSize: 13 }}>{error}</p>}

        <div style={{ display: "flex", gap: "1rem" }}>
          <button onClick={onClose} style={{ flex: 1, padding: "12px", borderRadius: 8, border: "1px solid var(--border)", background: "none", cursor: "pointer" }}>Annuler</button>
          <button onClick={handleEngage} disabled={loading} style={{ flex: 1, padding: "12px", borderRadius: 8, border: "none", background: ACCENT_COLOR, color: "white", fontWeight: 600, cursor: "pointer" }}>
            {loading ? "Traitement..." : "Confirmer l'engagement"}
          </button>
        </div>
      </motion.div>
    </div>
  );
}

export default function Presales() {
  const userType = getUserType();
  const [activeTab, setActiveTab] = useState<"available" | "mine">(userType === "ACHETEUR" ? "available" : "mine");
  const [preventes, setPreventes] = useState<Prevente[]>([]);
  const [engagements, setEngagements] = useState<Engagement[]>([]);
  const [loading, setLoading] = useState(true);
  const [showCreate, setShowCreate] = useState(false);
  const [selectedForEngage, setSelectedForEngage] = useState<Prevente | null>(null);

  const loadData = useCallback(async () => {
    setLoading(true);
    try {
      if (activeTab === "available") {
        const data = await getPreventes({ statut: "DISPONIBLE" });
        setPreventes(data);
      } else {
        if (userType === "ACHETEUR") {
          const data = await getMesEngagements();
          setEngagements(data);
        } else {
          const data = await getPreventes();
          setPreventes(data.filter(p => p.exploitant_nom)); // Just placeholder filtering, backend should filter by exploitant
        }
      }
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  }, [activeTab, userType]);

  useEffect(() => { loadData(); }, [loadData]);

  return (
    <div style={{ minHeight: "100vh", background: "var(--bg)", paddingTop: "2rem" }}>
      <div style={{ maxWidth: 1000, margin: "0 auto", padding: "0 1.5rem" }}>
        
        {/* Header Section */}
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-end", marginBottom: "2rem" }}>
          <div>
            <h1 style={{ margin: 0, fontSize: "2rem", fontWeight: 800 }}>Préventes Agricoles</h1>
            <p style={{ color: "var(--muted)", margin: "0.5rem 0 0" }}>Sécurisez vos récoltes et vos approvisionnements</p>
          </div>
          {userType === "EXPLOITANT" && (
            <button 
              onClick={() => setShowCreate(true)}
              style={{ padding: "12px 24px", borderRadius: 12, border: "none", background: "#16a34a", color: "white", fontWeight: 700, cursor: "pointer", display: "flex", alignItems: "center", gap: 8 }}
            >
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5"><line x1="12" y1="5" x2="12" y2="19"></line><line x1="5" y1="12" x2="19" y2="12"></line></svg>
              Créer une prévente
            </button>
          )}
        </div>

        {/* Tabs */}
        <div style={{ display: "flex", gap: "2rem", borderBottom: "1px solid var(--border)", marginBottom: "2rem" }}>
          <button 
            onClick={() => setActiveTab("available")}
            style={{ 
              padding: "1rem 0.5rem", background: "none", border: "none", cursor: "pointer", 
              fontSize: 15, fontWeight: 700, color: activeTab === "available" ? ACCENT_COLOR : "var(--muted)",
              borderBottom: activeTab === "available" ? `3px solid ${ACCENT_COLOR}` : "3px solid transparent",
              transition: "all 0.2s"
            }}
          >
            Préventes disponibles
          </button>
          <button 
            onClick={() => setActiveTab("mine")}
            style={{ 
              padding: "1rem 0.5rem", background: "none", border: "none", cursor: "pointer", 
              fontSize: 15, fontWeight: 700, color: activeTab === "mine" ? ACCENT_COLOR : "var(--muted)",
              borderBottom: activeTab === "mine" ? `3px solid ${ACCENT_COLOR}` : "3px solid transparent",
              transition: "all 0.2s"
            }}
          >
            {userType === "ACHETEUR" ? "Mes engagements" : "Mes préventes"}
          </button>
        </div>

        {/* Content */}
        {loading ? (
          <div style={{ textAlign: "center", padding: "4rem" }}>Chargement...</div>
        ) : (
          <>
            {activeTab === "available" ? (
              <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fill, minmax(300px, 1fr))", gap: "1.5rem" }}>
                {preventes.length === 0 ? (
                  <div style={{ gridColumn: "1/-1", textAlign: "center", padding: "4rem", color: "var(--muted)" }}>Aucune prévente disponible pour le moment.</div>
                ) : (
                  preventes.map(p => <PreventeCard key={p.id} prevente={p} userType={userType} onEngage={setSelectedForEngage} />)
                )}
              </div>
            ) : (
              <div style={{ display: "flex", flexDirection: "column", gap: "1rem" }}>
                {userType === "ACHETEUR" ? (
                  engagements.length === 0 ? (
                    <div style={{ textAlign: "center", padding: "4rem", color: "var(--muted)" }}>Vous n'avez pas encore d'engagements.</div>
                  ) : (
                    <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fill, minmax(320px, 1fr))", gap: "1rem" }}>
                      {engagements.map(e => <EngagementCard key={e.id} engagement={e} />)}
                    </div>
                  )
                ) : (
                  <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fill, minmax(300px, 1fr))", gap: "1.5rem" }}>
                    {preventes.length === 0 ? (
                      <div style={{ gridColumn: "1/-1", textAlign: "center", padding: "4rem", color: "var(--muted)" }}>Vous n'avez pas encore créé de préventes.</div>
                    ) : (
                      preventes.map(p => <PreventeCard key={p.id} prevente={p} userType={userType} onEngage={() => {}} />)
                    )}
                  </div>
                )}
              </div>
            )}
          </>
        )}
      </div>

      {/* Modals */}
      <AnimatePresence>
        {showCreate && <CreatePreventeModal onClose={() => setShowCreate(false)} onCreated={loadData} />}
        {selectedForEngage && <EngagementModal prevente={selectedForEngage} onClose={() => setSelectedForEngage(null)} onEngaged={loadData} />}
      </AnimatePresence>
    </div>
  );
}
