import React, { useState, useEffect, useCallback } from "react";
import { motion, AnimatePresence } from "framer-motion";
import {
  getMissions,
  createMission,
  acceptMission,
  refuseMission,
  cancelMission,
  startMission,
  completeMission,
  Mission,
  MissionCreatePayload,
} from "../api/missions";
import { getAgronomists } from "../api/auth";

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
  DEMANDE:  { label: "En attente",  color: "#b45309", bg: "#fef3c7" },
  ACCEPTEE: { label: "Acceptée",   color: "#1d4ed8", bg: "#dbeafe" },
  REFUSEE:  { label: "Refusée",    color: "#dc2626", bg: "#fee2e2" },
  EN_COURS: { label: "En cours",   color: "#6d28d9", bg: "#ede9fe" },
  TERMINEE: { label: "Terminée",   color: "#16a34a", bg: "#dcfce7" },
  ANNULEE:  { label: "Annulée",    color: "#64748b", bg: "#f1f5f9" },
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
      letterSpacing: 0.3,
      color: s.color,
      background: s.bg,
    }}>
      {s.label}
    </span>
  );
}

function MissionCard({
  mission,
  userType,
  onAccept,
  onComplete,
  onSelect,
  loading,
}: {
  mission: Mission;
  userType: string;
  onAccept: (id: number) => void;
  onComplete: (id: number) => void;
  onSelect: (m: Mission) => void;
  loading: number | null;
}) {
  const isLoading = loading === mission.id;
  return (
    <motion.div
      layout
      initial={{ opacity: 0, y: 16 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: -8 }}
      transition={{ duration: 0.25 }}
      style={{
        background: "var(--card)",
        border: "1px solid var(--border)",
        borderRadius: 14,
        padding: "1.25rem 1.5rem",
        cursor: "pointer",
        transition: "box-shadow 0.2s, border-color 0.2s",
      }}
      whileHover={{ boxShadow: "0 4px 24px rgba(0,0,0,0.08)", borderColor: "var(--primary)" }}
      onClick={() => onSelect(mission)}
    >
      <div style={{ display: "flex", alignItems: "flex-start", justifyContent: "space-between", gap: 12 }}>
        <div style={{ flex: 1, minWidth: 0 }}>
          <div style={{ display: "flex", alignItems: "center", gap: 8, marginBottom: 6 }}>
            <StatusBadge statut={mission.statut} />
            <span style={{ color: "var(--muted)", fontSize: 12 }}>#{mission.id}</span>
          </div>
          <p style={{
            margin: "0 0 8px",
            color: "var(--text)",
            fontWeight: 500,
            overflow: "hidden",
            textOverflow: "ellipsis",
            display: "-webkit-box",
            WebkitLineClamp: 2,
            WebkitBoxOrient: "vertical" as const,
          }}>
            {mission.description}
          </p>
          <div style={{ display: "flex", flexWrap: "wrap", gap: "6px 16px", fontSize: 13, color: "var(--muted)" }}>
            {userType === "EXPLOITANT" ? (
              <span>Agronome : <strong style={{ color: "var(--text)" }}>{mission.agronome_nom}</strong></span>
            ) : (
              <span>Exploitant : <strong style={{ color: "var(--text)" }}>{mission.exploitant_nom}</strong></span>
            )}
            <span>Budget : <strong style={{ color: "var(--primary)" }}>{formatAmount(mission.budget_propose)}</strong></span>
            {mission.date_debut && <span>Du {formatDate(mission.date_debut)} au {formatDate(mission.date_fin)}</span>}
          </div>
        </div>
      </div>

      {/* Actions */}
      {userType === "AGRONOME" && mission.statut === "DEMANDE" && (
        <div
          style={{ display: "flex", gap: 8, marginTop: 14 }}
          onClick={(e) => e.stopPropagation()}
        >
          <button
            disabled={isLoading}
            onClick={() => onAccept(mission.id)}
            style={{
              flex: 1,
              padding: "8px 0",
              borderRadius: 8,
              border: "none",
              background: "var(--primary)",
              color: "#fff",
              fontWeight: 600,
              fontSize: 13,
              cursor: isLoading ? "wait" : "pointer",
              opacity: isLoading ? 0.7 : 1,
            }}
          >
            {isLoading ? "..." : "Accepter"}
          </button>
        </div>
      )}

      {mission.statut === "ACCEPTEE" && (
        <div
          style={{ display: "flex", gap: 8, marginTop: 14 }}
          onClick={(e) => e.stopPropagation()}
        >
          <button
            disabled={isLoading}
            onClick={() => onComplete(mission.id)}
            style={{
              flex: 1,
              padding: "8px 0",
              borderRadius: 8,
              border: "none",
              background: "#16a34a",
              color: "#fff",
              fontWeight: 600,
              fontSize: 13,
              cursor: isLoading ? "wait" : "pointer",
              opacity: isLoading ? 0.7 : 1,
            }}
          >
            {isLoading ? "..." : "Marquer comme terminée"}
          </button>
        </div>
      )}
    </motion.div>
  );
}

function MissionDetailPanel({ mission, userType, onClose, onAction }: { mission: Mission; userType: string; onClose: () => void; onAction: () => void }) {
  const [actionLoading, setActionLoading] = useState("");

  async function doAction(action: string) {
    setActionLoading(action);
    try {
      if (action === "accept") await acceptMission(mission.id);
      else if (action === "refuse") await refuseMission(mission.id);
      else if (action === "cancel") await cancelMission(mission.id);
      else if (action === "start") await startMission(mission.id);
      else if (action === "complete") await completeMission(mission.id);
      onAction();
      onClose();
    } catch {
      // silently fail — toast handled by parent
    } finally {
      setActionLoading("");
    }
  }

  const isExploitant = userType === "EXPLOITANT";
  const isAgronome = userType === "AGRONOME";

  return (
    <motion.div
      initial={{ opacity: 0, x: 40 }}
      animate={{ opacity: 1, x: 0 }}
      exit={{ opacity: 0, x: 40 }}
      transition={{ duration: 0.25 }}
      style={{
        position: "fixed", right: 0, top: 0, height: "100%",
        width: "min(420px, 100vw)", background: "var(--card)",
        borderLeft: "1px solid var(--border)", zIndex: 200,
        overflowY: "auto", padding: "2rem 1.75rem",
        boxShadow: "-8px 0 40px rgba(0,0,0,0.1)",
      }}
    >
      <button onClick={onClose} style={{ position: "absolute", top: 16, right: 16, background: "none", border: "none", cursor: "pointer", color: "var(--muted)", fontSize: 22, lineHeight: 1 }}>×</button>

      <div style={{ marginBottom: "1.5rem" }}>
        <StatusBadge statut={mission.statut} />
        <h2 style={{ margin: "12px 0 4px", fontSize: "1.15rem", fontWeight: 700, color: "var(--text)" }}>
          Mission #{mission.id}
        </h2>
        <p style={{ color: "var(--muted)", fontSize: 13, margin: 0 }}>
          Créée le {formatDate(mission.created_at)}
        </p>
      </div>

      <div style={{ display: "flex", flexDirection: "column", gap: "1.25rem" }}>
        <Section label="Description">
          <p style={{ color: "var(--text)", margin: 0, lineHeight: 1.7, whiteSpace: "pre-line" }}>{mission.description}</p>
        </Section>
        <Section label="Parties">
          <Row label="Exploitant" value={mission.exploitant_nom} />
          <Row label="Agronome" value={mission.agronome_nom} />
        </Section>
        <Section label="Financier">
          <Row label="Budget proposé" value={formatAmount(mission.budget_propose)} highlight />
          <Row label="Commission (10%)" value={formatAmount(Number(mission.budget_propose) * 0.1)} />
          <Row label="Net agronome" value={formatAmount(Number(mission.budget_propose) * 0.9)} highlight />
        </Section>
        {(mission.date_debut || mission.date_fin) && (
          <Section label="Planning">
            <Row label="Début" value={formatDate(mission.date_debut)} />
            <Row label="Fin" value={formatDate(mission.date_fin)} />
          </Section>
        )}
        <Section label="Référence">
          <Row label="ID mission" value={String(mission.id)} />
          <Row label="Modifié le" value={formatDate(mission.updated_at)} />
        </Section>
      </div>

      {/* Action buttons */}
      <div style={{ display: "flex", flexDirection: "column", gap: 8, marginTop: "1.5rem" }}>
        {/* Agronome: Accepter / Refuser une demande */}
        {isAgronome && mission.statut === "DEMANDE" && (
          <>
            <button onClick={() => doAction("accept")} disabled={!!actionLoading}
              style={{ width: "100%", padding: "12px", borderRadius: 12, border: "none", background: "var(--primary)", color: "#fff", fontWeight: 700, fontSize: 14, cursor: "pointer", opacity: actionLoading ? 0.6 : 1 }}>
              {actionLoading === "accept" ? "..." : "✅ Accepter la mission"}
            </button>
            <button onClick={() => doAction("refuse")} disabled={!!actionLoading}
              style={{ width: "100%", padding: "12px", borderRadius: 12, border: "1.5px solid #dc2626", background: "none", color: "#dc2626", fontWeight: 600, fontSize: 14, cursor: "pointer", opacity: actionLoading ? 0.6 : 1 }}>
              {actionLoading === "refuse" ? "..." : "Refuser"}
            </button>
          </>
        )}

        {/* Exploitant/Agronome: Démarrer une mission acceptée */}
        {mission.statut === "ACCEPTEE" && (
          <button onClick={() => doAction("start")} disabled={!!actionLoading}
            style={{ width: "100%", padding: "12px", borderRadius: 12, border: "none", background: "#7c3aed", color: "#fff", fontWeight: 700, fontSize: 14, cursor: "pointer", opacity: actionLoading ? 0.6 : 1 }}>
            {actionLoading === "start" ? "..." : "🚀 Démarrer la mission"}
          </button>
        )}

        {/* Exploitant: Terminer une mission en cours */}
        {isExploitant && mission.statut === "EN_COURS" && (
          <button onClick={() => doAction("complete")} disabled={!!actionLoading}
            style={{ width: "100%", padding: "12px", borderRadius: 12, border: "none", background: "var(--primary)", color: "#fff", fontWeight: 700, fontSize: 14, cursor: "pointer", opacity: actionLoading ? 0.6 : 1 }}>
            {actionLoading === "complete" ? "..." : "✅ Marquer comme terminée"}
          </button>
        )}

        {/* Exploitant: Annuler (avant démarrage) */}
        {isExploitant && ["DEMANDE", "ACCEPTEE"].includes(mission.statut) && (
          <button onClick={() => doAction("cancel")} disabled={!!actionLoading}
            style={{ width: "100%", padding: "12px", borderRadius: 12, border: "1.5px solid var(--border)", background: "none", color: "var(--muted)", fontWeight: 500, fontSize: 14, cursor: "pointer", opacity: actionLoading ? 0.6 : 1 }}>
            {actionLoading === "cancel" ? "..." : "Annuler la mission"}
          </button>
        )}
      </div>
    </motion.div>
  );
}

function Section({ label, children }: { label: string; children: React.ReactNode }) {
  return (
    <div>
      <p style={{ fontSize: 11, fontWeight: 700, letterSpacing: 1, color: "var(--muted)", textTransform: "uppercase", margin: "0 0 8px" }}>
        {label}
      </p>
      <div style={{ background: "var(--bg)", borderRadius: 10, padding: "12px 14px", display: "flex", flexDirection: "column", gap: 8 }}>
        {children}
      </div>
    </div>
  );
}

function Row({ label, value, highlight }: { label: string; value: string; highlight?: boolean }) {
  return (
    <div style={{ display: "flex", justifyContent: "space-between", gap: 8, fontSize: 14 }}>
      <span style={{ color: "var(--muted)" }}>{label}</span>
      <span style={{ color: highlight ? "var(--primary)" : "var(--text)", fontWeight: highlight ? 600 : 500 }}>{value}</span>
    </div>
  );
}

interface AgronomeOption { id: number; user_id?: number; first_name?: string; last_name?: string; nom_complet?: string; agronome_profile?: { specialite?: string }; specialisations?: string[] }

function getAgronomeDisplayName(a: AgronomeOption): string {
  if (a.nom_complet) return a.nom_complet;
  return [a.first_name, a.last_name].filter(Boolean).join(" ") || `Agronome #${a.id}`;
}

function getAgronomeInitial(a: AgronomeOption): string {
  const name = getAgronomeDisplayName(a);
  return name[0]?.toUpperCase() || "A";
}

function getAgronomeSpec(a: AgronomeOption): string {
  if (a.agronome_profile?.specialite) return a.agronome_profile.specialite;
  if (a.specialisations?.length) return a.specialisations.join(", ");
  return "";
}

function CreateMissionModal({ onClose, onCreated }: { onClose: () => void; onCreated: () => void }) {
  const [step, setStep] = useState<1 | 2>(1);
  const [agronomes, setAgronomes] = useState<AgronomeOption[]>([]);
  const [search, setSearch] = useState("");
  const [selected, setSelected] = useState<AgronomeOption | null>(null);
  const [description, setDescription] = useState("");
  const [budget, setBudget] = useState("");
  const [dateDebut, setDateDebut] = useState("");
  const [dateFin, setDateFin] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  useEffect(() => {
    getAgronomists({ statut_validation: "VALIDE" })
      .then((d) => setAgronomes(d.results ?? d))
      .catch(() => setAgronomes([]));
  }, []);

  const filtered = agronomes.filter((a) => {
    const name = getAgronomeDisplayName(a).toLowerCase();
    return name.includes(search.toLowerCase());
  });

  async function handleSubmit() {
    if (!selected) return;
    if (!description.trim()) { setError("Décrivez la mission."); return; }
    if (!budget || Number(budget) <= 0) { setError("Entrez un budget valide."); return; }
    setError("");
    setLoading(true);
    try {
      const payload: MissionCreatePayload = {
        agronome: selected.user_id ?? selected.id,
        description: description.trim(),
        budget_propose: Number(budget),
      };
      if (dateDebut) payload.date_debut = dateDebut;
      if (dateFin) payload.date_fin = dateFin;
      await createMission(payload);
      onCreated();
      onClose();
    } catch (e: unknown) {
      const err = e as { response?: { data?: Record<string, string[]> } };
      const data = err?.response?.data;
      if (data) {
        const msgs = Object.values(data).flat().join(" ");
        setError(msgs || "Une erreur est survenue.");
      } else {
        setError("Impossible de créer la mission.");
      }
    } finally {
      setLoading(false);
    }
  }

  return (
    <div style={{
      position: "fixed", inset: 0, zIndex: 300,
      background: "rgba(0,0,0,0.45)", backdropFilter: "blur(4px)",
      display: "flex", alignItems: "center", justifyContent: "center",
      padding: "1rem",
    }}>
      <motion.div
        initial={{ opacity: 0, scale: 0.95, y: 20 }}
        animate={{ opacity: 1, scale: 1, y: 0 }}
        exit={{ opacity: 0, scale: 0.95, y: 20 }}
        transition={{ duration: 0.2 }}
        style={{
          background: "var(--card)",
          borderRadius: 18,
          padding: "2rem",
          width: "100%",
          maxWidth: 520,
          maxHeight: "90vh",
          overflowY: "auto",
          boxShadow: "0 24px 80px rgba(0,0,0,0.2)",
        }}
      >
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "1.5rem" }}>
          <div>
            <h2 style={{ margin: 0, fontSize: "1.2rem", fontWeight: 700, color: "var(--text)" }}>
              Nouvelle mission
            </h2>
            <p style={{ margin: "4px 0 0", fontSize: 13, color: "var(--muted)" }}>
              Étape {step} sur 2
            </p>
          </div>
          <button onClick={onClose} style={{ background: "none", border: "none", cursor: "pointer", color: "var(--muted)", fontSize: 22 }}>×</button>
        </div>

        {/* Progress */}
        <div style={{ display: "flex", gap: 4, marginBottom: "1.75rem" }}>
          {[1, 2].map((s) => (
            <div key={s} style={{
              flex: 1, height: 4, borderRadius: 4,
              background: s <= step ? "var(--primary)" : "var(--border)",
              transition: "background 0.3s",
            }} />
          ))}
        </div>

        <AnimatePresence mode="wait">
          {step === 1 && (
            <motion.div key="step1" initial={{ opacity: 0, x: -16 }} animate={{ opacity: 1, x: 0 }} exit={{ opacity: 0, x: 16 }}>
              <p style={{ margin: "0 0 12px", fontWeight: 600, color: "var(--text)" }}>
                Sélectionnez un agronome
              </p>
              <input
                placeholder="Rechercher par nom..."
                value={search}
                onChange={(e) => setSearch(e.target.value)}
                style={{
                  width: "100%", padding: "10px 12px", borderRadius: 10,
                  border: "1px solid var(--border)", background: "var(--bg)",
                  color: "var(--text)", fontSize: 14, marginBottom: 10,
                  boxSizing: "border-box", outline: "none",
                }}
              />
              <div style={{ display: "flex", flexDirection: "column", gap: 6, maxHeight: 280, overflowY: "auto" }}>
                {filtered.length === 0 && (
                  <p style={{ color: "var(--muted)", fontSize: 13, textAlign: "center", padding: "1rem 0" }}>
                    Aucun agronome trouvé
                  </p>
                )}
                {filtered.map((a) => (
                  <button
                    key={a.id}
                    onClick={() => setSelected(a)}
                    style={{
                      display: "flex", alignItems: "center", gap: 12,
                      padding: "10px 12px", borderRadius: 10, textAlign: "left",
                      border: selected?.id === a.id ? "2px solid var(--primary)" : "1px solid var(--border)",
                      background: selected?.id === a.id ? "rgba(var(--primary-rgb), 0.06)" : "var(--bg)",
                      cursor: "pointer", transition: "all 0.15s",
                    }}
                  >
                    <div style={{
                      width: 36, height: 36, borderRadius: "50%",
                      background: "var(--primary)", display: "flex", alignItems: "center", justifyContent: "center",
                      color: "#fff", fontWeight: 700, fontSize: 14, flexShrink: 0,
                    }}>
                      {getAgronomeInitial(a)}
                    </div>
                    <div>
                      <p style={{ margin: 0, fontWeight: 600, fontSize: 14, color: "var(--text)" }}>
                        {getAgronomeDisplayName(a)}
                      </p>
                      {getAgronomeSpec(a) && (
                        <p style={{ margin: 0, fontSize: 12, color: "var(--muted)" }}>
                          {getAgronomeSpec(a)}
                        </p>
                      )}
                    </div>
                  </button>
                ))}
              </div>
              <button
                disabled={!selected}
                onClick={() => setStep(2)}
                style={{
                  marginTop: "1.25rem", width: "100%", padding: "12px",
                  borderRadius: 10, border: "none",
                  background: selected ? "var(--primary)" : "var(--border)",
                  color: selected ? "#fff" : "var(--muted)",
                  fontWeight: 600, fontSize: 15, cursor: selected ? "pointer" : "not-allowed",
                  transition: "all 0.2s",
                }}
              >
                Continuer {selected ? `avec ${getAgronomeDisplayName(selected)}` : ""}
              </button>
            </motion.div>
          )}

          {step === 2 && (
            <motion.div key="step2" initial={{ opacity: 0, x: 16 }} animate={{ opacity: 1, x: 0 }} exit={{ opacity: 0, x: -16 }}>
              {selected && (
                <div style={{
                  display: "flex", alignItems: "center", gap: 10,
                  padding: "10px 12px", borderRadius: 10,
                  background: "var(--bg)", border: "1px solid var(--border)",
                  marginBottom: "1.25rem",
                }}>
                  <div style={{
                    width: 32, height: 32, borderRadius: "50%",
                    background: "var(--primary)", display: "flex", alignItems: "center",
                    justifyContent: "center", color: "#fff", fontWeight: 700, fontSize: 13,
                  }}>
                    {getAgronomeInitial(selected)}
                  </div>
                  <div>
                    <p style={{ margin: 0, fontSize: 13, fontWeight: 600, color: "var(--text)" }}>
                      {getAgronomeDisplayName(selected)}
                    </p>
                    <button onClick={() => setStep(1)} style={{ background: "none", border: "none", padding: 0, fontSize: 12, color: "var(--primary)", cursor: "pointer" }}>
                      Changer
                    </button>
                  </div>
                </div>
              )}

              <div style={{ display: "flex", flexDirection: "column", gap: "1rem" }}>
                <Field label="Description de la mission *">
                  <textarea
                    rows={4}
                    placeholder="Décrivez précisément la mission attendue..."
                    value={description}
                    onChange={(e) => setDescription(e.target.value)}
                    style={{
                      width: "100%", padding: "10px 12px", borderRadius: 10,
                      border: "1px solid var(--border)", background: "var(--bg)",
                      color: "var(--text)", fontSize: 14, resize: "vertical",
                      fontFamily: "inherit", boxSizing: "border-box", outline: "none",
                    }}
                  />
                </Field>

                <Field label="Budget proposé (FCFA) *">
                  <input
                    type="number"
                    min={0}
                    placeholder="ex : 50000"
                    value={budget}
                    onChange={(e) => setBudget(e.target.value)}
                    style={inputStyle}
                  />
                </Field>

                <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 10 }}>
                  <Field label="Date de début">
                    <input type="date" value={dateDebut} onChange={(e) => setDateDebut(e.target.value)} style={inputStyle} />
                  </Field>
                  <Field label="Date de fin">
                    <input type="date" value={dateFin} onChange={(e) => setDateFin(e.target.value)} style={inputStyle} />
                  </Field>
                </div>
              </div>

              {error && (
                <p style={{ color: "#dc2626", fontSize: 13, marginTop: 12, marginBottom: 0 }}>{error}</p>
              )}

              <div style={{ display: "flex", gap: 8, marginTop: "1.5rem" }}>
                <button
                  onClick={() => setStep(1)}
                  style={{
                    padding: "12px 20px", borderRadius: 10,
                    border: "1px solid var(--border)", background: "none",
                    color: "var(--text)", fontWeight: 500, fontSize: 14, cursor: "pointer",
                  }}
                >
                  Retour
                </button>
                <button
                  disabled={loading}
                  onClick={handleSubmit}
                  style={{
                    flex: 1, padding: "12px", borderRadius: 10, border: "none",
                    background: "var(--primary)", color: "#fff",
                    fontWeight: 600, fontSize: 15, cursor: loading ? "wait" : "pointer",
                    opacity: loading ? 0.7 : 1,
                  }}
                >
                  {loading ? "Envoi..." : "Envoyer la demande"}
                </button>
              </div>
            </motion.div>
          )}
        </AnimatePresence>
      </motion.div>
    </div>
  );
}

const inputStyle: React.CSSProperties = {
  width: "100%", padding: "10px 14px", borderRadius: 12,
  border: "1.5px solid var(--border)", background: "var(--bg)",
  color: "var(--text)", fontSize: 14, boxSizing: "border-box", outline: "none",
};

function Field({ label, children }: { label: string; children: React.ReactNode }) {
  return (
    <div>
      <label style={{ display: "block", fontSize: 13, fontWeight: 600, color: "var(--text)", marginBottom: 6 }}>
        {label}
      </label>
      {children}
    </div>
  );
}

const FILTER_TABS: { key: string; label: string }[] = [
  { key: "all",      label: "Toutes" },
  { key: "DEMANDE",  label: "En attente" },
  { key: "ACCEPTEE", label: "Acceptées" },
  { key: "EN_COURS", label: "En cours" },
  { key: "TERMINEE", label: "Terminées" },
  { key: "REFUSEE",  label: "Refusées" },
  { key: "ANNULEE",  label: "Annulées" },
];

export default function Missions() {
  const userType = getUserType();
  const [missions, setMissions] = useState<Mission[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [filter, setFilter] = useState("all");
  const [selected, setSelected] = useState<Mission | null>(null);
  const [actionLoading, setActionLoading] = useState<number | null>(null);
  const [showCreate, setShowCreate] = useState(false);
  const [toast, setToast] = useState("");

  const load = useCallback(async () => {
    setLoading(true);
    setError("");
    try {
      const data = await getMissions();
      setMissions(data);
    } catch {
      setError("Impossible de charger les missions.");
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => { load(); }, [load]);

  function showToast(msg: string) {
    setToast(msg);
    setTimeout(() => setToast(""), 3500);
  }

  async function handleAccept(id: number) {
    setActionLoading(id);
    try {
      await acceptMission(id);
      showToast("Mission acceptée avec succès.");
      await load();
      setSelected(null);
    } catch {
      showToast("Impossible d'accepter la mission.");
    } finally {
      setActionLoading(null);
    }
  }

  async function handleComplete(id: number) {
    setActionLoading(id);
    try {
      await completeMission(id);
      showToast("Mission marquée comme terminée.");
      await load();
      setSelected(null);
    } catch {
      showToast("Impossible de terminer la mission.");
    } finally {
      setActionLoading(null);
    }
  }

  const filtered = filter === "all" ? missions : missions.filter((m) => m.statut === filter);

  const counts = FILTER_TABS.reduce<Record<string, number>>((acc, t) => {
    acc[t.key] = t.key === "all" ? missions.length : missions.filter((m) => m.statut === t.key).length;
    return acc;
  }, {});

  if (!userType || !["EXPLOITANT", "AGRONOME"].includes(userType)) {
    return (
      <div style={{ maxWidth: 600, margin: "6rem auto", textAlign: "center", padding: "0 1.5rem" }}>
        <div style={{ fontSize: 56, marginBottom: "1rem" }}>🌾</div>
        <h2 style={{ color: "var(--text)", fontWeight: 700, fontSize: "1.5rem" }}>
          Page réservée
        </h2>
        <p style={{ color: "var(--muted)", lineHeight: 1.7 }}>
          La page Missions est réservée aux exploitants agricoles et aux agronomes.
        </p>
      </div>
    );
  }

  const title = userType === "EXPLOITANT" ? "Mes missions" : "Demandes reçues";
  const subtitle = userType === "EXPLOITANT"
    ? "Suivez et gérez vos demandes d'intervention auprès d'agronomes"
    : "Consultez et acceptez les missions que des exploitants vous ont proposées";

  return (
    <div style={{ maxWidth: 900, margin: "0 auto", padding: "2.5rem 1.5rem 4rem" }}>
      {/* Toast */}
      <AnimatePresence>
        {toast && (
          <motion.div
            initial={{ opacity: 0, y: -20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -20 }}
            style={{
              position: "fixed", top: 80, left: "50%", transform: "translateX(-50%)",
              background: "#1a1a1a", color: "#fff", padding: "10px 20px",
              borderRadius: 10, fontSize: 14, fontWeight: 500, zIndex: 500,
              boxShadow: "0 8px 24px rgba(0,0,0,0.2)",
            }}
          >
            {toast}
          </motion.div>
        )}
      </AnimatePresence>

      {/* Header */}
      <div style={{ display: "flex", alignItems: "flex-start", justifyContent: "space-between", gap: 16, marginBottom: "2rem", flexWrap: "wrap" }}>
        <div>
          <h1 style={{ margin: 0, fontSize: "1.75rem", fontWeight: 800, color: "var(--text)" }}>
            {title}
          </h1>
          <p style={{ margin: "6px 0 0", color: "var(--muted)", fontSize: 15, maxWidth: 480 }}>
            {subtitle}
          </p>
        </div>
        {userType === "EXPLOITANT" && (
          <button
            onClick={() => setShowCreate(true)}
            style={{
              padding: "10px 20px", borderRadius: 10, border: "none",
              background: "var(--primary)", color: "#fff",
              fontWeight: 600, fontSize: 14, cursor: "pointer",
              whiteSpace: "nowrap",
            }}
          >
            + Nouvelle mission
          </button>
        )}
      </div>

      {/* Filter tabs */}
      <div style={{ display: "flex", gap: 4, marginBottom: "1.5rem", flexWrap: "wrap" }}>
        {FILTER_TABS.map((tab) => {
          const active = filter === tab.key;
          return (
            <button
              key={tab.key}
              onClick={() => setFilter(tab.key)}
              style={{
                padding: "7px 14px", borderRadius: 8,
                border: "1px solid",
                borderColor: active ? "var(--primary)" : "var(--border)",
                background: active ? "var(--primary)" : "none",
                color: active ? "#fff" : "var(--muted)",
                fontSize: 13, fontWeight: active ? 600 : 400,
                cursor: "pointer", transition: "all 0.15s",
              }}
            >
              {tab.label}
              {counts[tab.key] > 0 && (
                <span style={{
                  marginLeft: 6, padding: "1px 6px",
                  borderRadius: 10, fontSize: 11, fontWeight: 700,
                  background: active ? "rgba(255,255,255,0.25)" : "var(--border)",
                  color: active ? "#fff" : "var(--text)",
                }}>
                  {counts[tab.key]}
                </span>
              )}
            </button>
          );
        })}
      </div>

      {/* Content */}
      {loading && (
        <div style={{ textAlign: "center", padding: "4rem 0", color: "var(--muted)" }}>
          <div style={{ width: 32, height: 32, borderRadius: "50%", border: "3px solid var(--border)", borderTopColor: "var(--primary)", margin: "0 auto 12px", animation: "spin 0.8s linear infinite" }} />
          Chargement...
        </div>
      )}

      {!loading && error && (
        <div style={{ textAlign: "center", padding: "3rem 0" }}>
          <p style={{ color: "#dc2626", marginBottom: "1rem" }}>{error}</p>
          <button onClick={load} style={{ padding: "8px 18px", borderRadius: 8, border: "1px solid var(--border)", background: "none", color: "var(--text)", cursor: "pointer" }}>
            Réessayer
          </button>
        </div>
      )}

      {!loading && !error && filtered.length === 0 && (
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          style={{ textAlign: "center", padding: "4rem 0" }}
        >
          <div style={{
            width: 72, height: 72, borderRadius: "50%",
            background: "var(--bg)", border: "1px solid var(--border)",
            display: "flex", alignItems: "center", justifyContent: "center",
            margin: "0 auto 16px", fontSize: 30,
          }}>
            🌿
          </div>
          <h3 style={{ color: "var(--text)", fontWeight: 600, marginBottom: 8 }}>
            {filter === "all" ? "Aucune mission pour l'instant" : "Aucune mission dans cette catégorie"}
          </h3>
          <p style={{ color: "var(--muted)", fontSize: 14, maxWidth: 360, margin: "0 auto" }}>
            {userType === "EXPLOITANT" && filter === "all"
              ? "Créez votre première mission pour solliciter l'expertise d'un agronome."
              : "Les missions apparaîtront ici dès qu'elles seront créées."}
          </p>
          {userType === "EXPLOITANT" && filter === "all" && (
            <button
              onClick={() => setShowCreate(true)}
              style={{
                marginTop: "1.5rem", padding: "10px 22px", borderRadius: 10,
                border: "none", background: "var(--primary)", color: "#fff",
                fontWeight: 600, cursor: "pointer",
              }}
            >
              Créer une mission
            </button>
          )}
        </motion.div>
      )}

      {!loading && !error && filtered.length > 0 && (
        <div style={{ display: "flex", flexDirection: "column", gap: 12 }}>
          <AnimatePresence>
            {filtered.map((m) => (
              <MissionCard
                key={m.id}
                mission={m}
                userType={userType}
                onAccept={handleAccept}
                onComplete={handleComplete}
                onSelect={setSelected}
                loading={actionLoading}
              />
            ))}
          </AnimatePresence>
        </div>
      )}

      {/* Detail panel */}
      <AnimatePresence>
        {selected && (
          <>
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              onClick={() => setSelected(null)}
              style={{ position: "fixed", inset: 0, background: "rgba(0,0,0,0.2)", zIndex: 199 }}
            />
            <MissionDetailPanel mission={selected} userType={userType} onClose={() => setSelected(null)} onAction={load} />
          </>
        )}
      </AnimatePresence>

      {/* Create modal */}
      <AnimatePresence>
        {showCreate && (
          <CreateMissionModal
            onClose={() => setShowCreate(false)}
            onCreated={() => { load(); showToast("Mission créée avec succès."); }}
          />
        )}
      </AnimatePresence>

      <style>{`
        @keyframes spin { to { transform: rotate(360deg); } }
      `}</style>
    </div>
  );
}
