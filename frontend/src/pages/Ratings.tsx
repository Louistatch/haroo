import React, { useState, useEffect, useCallback } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { getRatings, createRating, reportRating, Rating, ReportPayload } from "../api/ratings";
import { getMissions, Mission } from "../api/missions";

function getMyId(): number {
  try {
    const token = localStorage.getItem("access_token");
    if (!token) return 0;
    return JSON.parse(atob(token.split(".")[1])).user_id || 0;
  } catch { return 0; }
}

function formatDate(d: string) {
  return new Date(d).toLocaleDateString("fr-FR", { day: "2-digit", month: "long", year: "numeric" });
}

function StarRow({ value, max = 5, size = 18 }: { value: number; max?: number; size?: number }) {
  return (
    <span style={{ display: "inline-flex", gap: 2 }}>
      {Array.from({ length: max }).map((_, i) => (
        <svg key={i} width={size} height={size} viewBox="0 0 24 24" fill={i < value ? "#f59e0b" : "none"} stroke="#f59e0b" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
          <polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2" />
        </svg>
      ))}
    </span>
  );
}

function StarSelector({ value, onChange }: { value: number; onChange: (v: number) => void }) {
  const [hover, setHover] = useState(0);
  const labels = ["", "Mauvais", "Passable", "Bien", "Très bien", "Excellent"];
  return (
    <div>
      <div style={{ display: "flex", gap: 6, justifyContent: "center", marginBottom: 8 }}>
        {[1, 2, 3, 4, 5].map((star) => (
          <motion.button
            key={star}
            whileHover={{ scale: 1.2 }}
            whileTap={{ scale: 0.9 }}
            onMouseEnter={() => setHover(star)}
            onMouseLeave={() => setHover(0)}
            onClick={() => onChange(star)}
            style={{ background: "none", border: "none", cursor: "pointer", padding: 2 }}
          >
            <svg width={32} height={32} viewBox="0 0 24 24"
              fill={(hover || value) >= star ? "#f59e0b" : "none"}
              stroke="#f59e0b" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round"
              style={{ transition: "fill 0.15s" }}
            >
              <polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2" />
            </svg>
          </motion.button>
        ))}
      </div>
      {(hover || value) > 0 && (
        <p style={{ textAlign: "center", fontSize: 13, color: "#f59e0b", fontWeight: 600, margin: 0, minHeight: 20 }}>
          {labels[hover || value]}
        </p>
      )}
    </div>
  );
}

function DistributionBar({ ratings }: { ratings: Rating[] }) {
  const total = ratings.length;
  if (total === 0) return null;
  const avg = ratings.reduce((s, r) => s + r.note_valeur, 0) / total;
  const counts = [5, 4, 3, 2, 1].map((star) => ({
    star,
    count: ratings.filter((r) => r.note_valeur === star).length,
  }));

  return (
    <div style={{
      background: "var(--card)",
      border: "1px solid var(--border)",
      borderRadius: 16,
      padding: "1.5rem",
      marginBottom: "1.75rem",
      display: "flex",
      gap: "2rem",
      alignItems: "center",
      flexWrap: "wrap",
    }}>
      {/* Average */}
      <div style={{ textAlign: "center", minWidth: 100 }}>
        <p style={{ margin: 0, fontSize: 48, fontWeight: 800, color: "var(--text)", lineHeight: 1 }}>
          {avg.toFixed(1)}
        </p>
        <StarRow value={Math.round(avg)} size={16} />
        <p style={{ margin: "6px 0 0", fontSize: 13, color: "var(--muted)" }}>
          {total} avis
        </p>
      </div>

      {/* Distribution */}
      <div style={{ flex: 1, minWidth: 200 }}>
        {counts.map(({ star, count }) => {
          const pct = total > 0 ? (count / total) * 100 : 0;
          return (
            <div key={star} style={{ display: "flex", alignItems: "center", gap: 8, marginBottom: 5 }}>
              <span style={{ fontSize: 12, color: "var(--muted)", minWidth: 20, textAlign: "right" }}>{star}</span>
              <svg width="12" height="12" viewBox="0 0 24 24" fill="#f59e0b" stroke="none"><polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2" /></svg>
              <div style={{ flex: 1, height: 8, borderRadius: 4, background: "var(--border)", overflow: "hidden" }}>
                <motion.div
                  initial={{ width: 0 }}
                  animate={{ width: `${pct}%` }}
                  transition={{ duration: 0.6, delay: (5 - star) * 0.06 }}
                  style={{ height: "100%", background: "#f59e0b", borderRadius: 4 }}
                />
              </div>
              <span style={{ fontSize: 12, color: "var(--muted)", minWidth: 18 }}>{count}</span>
            </div>
          );
        })}
      </div>
    </div>
  );
}

function RatingCard({ rating, myId, onReport }: { rating: Rating; myId: number; onReport: (r: Rating) => void }) {
  const isFromMe = rating.notateur.id === myId;
  const person = isFromMe ? rating.note : rating.notateur;
  return (
    <motion.div
      layout
      initial={{ opacity: 0, y: 12 }}
      animate={{ opacity: 1, y: 0 }}
      exit={{ opacity: 0, y: -8 }}
      style={{
        background: "var(--card)",
        border: "1px solid var(--border)",
        borderRadius: 14,
        padding: "1.25rem 1.5rem",
      }}
    >
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", gap: 12 }}>
        <div style={{ flex: 1 }}>
          <div style={{ display: "flex", alignItems: "center", gap: 10, marginBottom: 8 }}>
            <div style={{
              width: 36, height: 36, borderRadius: "50%",
              background: "var(--primary)", display: "flex", alignItems: "center",
              justifyContent: "center", color: "#fff", fontWeight: 700, fontSize: 14, flexShrink: 0,
            }}>
              {person.first_name?.[0]?.toUpperCase() || "?"}
            </div>
            <div>
              <p style={{ margin: 0, fontWeight: 600, fontSize: 14, color: "var(--text)" }}>
                {person.first_name} {person.last_name}
              </p>
              <p style={{ margin: 0, fontSize: 12, color: "var(--muted)" }}>{formatDate(rating.created_at)}</p>
            </div>
          </div>

          <StarRow value={rating.note_valeur} size={15} />

          <p style={{
            margin: "8px 0 0",
            color: "var(--text)",
            fontSize: 14,
            lineHeight: 1.7,
            fontStyle: "italic",
          }}>
            "{rating.commentaire}"
          </p>
        </div>

        {!isFromMe && (
          <button
            onClick={() => onReport(rating)}
            title="Signaler cet avis"
            style={{
              background: "none", border: "none", cursor: "pointer",
              color: "var(--muted)", padding: "4px", borderRadius: 6,
              opacity: 0.6,
            }}
          >
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <circle cx="12" cy="12" r="10" />
              <line x1="12" y1="8" x2="12" y2="12" />
              <line x1="12" y1="16" x2="12.01" y2="16" />
            </svg>
          </button>
        )}
      </div>
    </motion.div>
  );
}

function EmptyState({ icon, title, desc, action }: { icon: string; title: string; desc: string; action?: React.ReactNode }) {
  return (
    <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} style={{ textAlign: "center", padding: "3rem 0" }}>
      <div style={{
        width: 64, height: 64, borderRadius: "50%",
        background: "var(--bg)", border: "1px solid var(--border)",
        display: "flex", alignItems: "center", justifyContent: "center",
        margin: "0 auto 14px", fontSize: 28,
      }}>{icon}</div>
      <h3 style={{ color: "var(--text)", fontWeight: 600, margin: "0 0 6px" }}>{title}</h3>
      <p style={{ color: "var(--muted)", fontSize: 14, maxWidth: 340, margin: "0 auto 16px", lineHeight: 1.6 }}>{desc}</p>
      {action}
    </motion.div>
  );
}

function CreateRatingModal({ mission, onClose, onCreated }: {
  mission: Mission;
  onClose: () => void;
  onCreated: () => void;
}) {
  const [stars, setStars] = useState(0);
  const [comment, setComment] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const MIN_CHARS = 20;

  async function handleSubmit() {
    if (stars === 0) { setError("Sélectionnez une note."); return; }
    if (comment.trim().length < MIN_CHARS) { setError(`Le commentaire doit contenir au moins ${MIN_CHARS} caractères.`); return; }
    setError("");
    setLoading(true);
    try {
      await createRating({ note_valeur: stars, commentaire: comment.trim(), mission: mission.id });
      onCreated();
      onClose();
    } catch (e: unknown) {
      const err = e as { response?: { data?: Record<string, string[]> | { detail?: string } } };
      const data = err?.response?.data;
      if (data) {
        const msgs = Object.values(data).flat().join(" ");
        setError(msgs || "Erreur lors de la soumission.");
      } else {
        setError("Impossible de soumettre l'avis.");
      }
    } finally {
      setLoading(false);
    }
  }

  return (
    <div style={{
      position: "fixed", inset: 0, zIndex: 300,
      background: "rgba(0,0,0,0.45)", backdropFilter: "blur(4px)",
      display: "flex", alignItems: "center", justifyContent: "center", padding: "1rem",
    }}>
      <motion.div
        initial={{ opacity: 0, scale: 0.95, y: 20 }}
        animate={{ opacity: 1, scale: 1, y: 0 }}
        exit={{ opacity: 0, scale: 0.95, y: 20 }}
        transition={{ duration: 0.2 }}
        style={{
          background: "var(--card)", borderRadius: 18, padding: "2rem",
          width: "100%", maxWidth: 480,
          boxShadow: "0 24px 80px rgba(0,0,0,0.2)",
        }}
      >
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", marginBottom: "1.5rem" }}>
          <div>
            <h2 style={{ margin: 0, fontSize: "1.15rem", fontWeight: 700, color: "var(--text)" }}>Laisser un avis</h2>
            <p style={{ margin: "4px 0 0", fontSize: 13, color: "var(--muted)" }}>
              Mission #{mission.id} · {mission.agronome_nom}
            </p>
          </div>
          <button onClick={onClose} style={{ background: "none", border: "none", cursor: "pointer", color: "var(--muted)", fontSize: 22 }}>×</button>
        </div>

        <div style={{ marginBottom: "1.5rem" }}>
          <p style={{ fontSize: 13, fontWeight: 600, color: "var(--text)", marginBottom: 12, textAlign: "center" }}>
            Votre note globale
          </p>
          <StarSelector value={stars} onChange={setStars} />
        </div>

        <div style={{ marginBottom: "1.25rem" }}>
          <label style={{ display: "block", fontSize: 13, fontWeight: 600, color: "var(--text)", marginBottom: 6 }}>
            Votre commentaire
          </label>
          <textarea
            rows={4}
            placeholder="Partagez votre expérience de cette mission avec l'agronome..."
            value={comment}
            onChange={(e) => setComment(e.target.value)}
            style={{
              width: "100%", padding: "10px 12px", borderRadius: 10,
              border: `1px solid ${comment.length > 0 && comment.length < MIN_CHARS ? "#f59e0b" : "var(--border)"}`,
              background: "var(--bg)", color: "var(--text)", fontSize: 14,
              resize: "vertical", fontFamily: "inherit",
              boxSizing: "border-box", outline: "none",
            }}
          />
          <div style={{ display: "flex", justifyContent: "space-between", marginTop: 4 }}>
            <span style={{ fontSize: 12, color: comment.length < MIN_CHARS ? "#f59e0b" : "#16a34a" }}>
              {comment.length < MIN_CHARS ? `Minimum ${MIN_CHARS - comment.length} caractère(s) manquant(s)` : "Longueur suffisante"}
            </span>
            <span style={{ fontSize: 12, color: "var(--muted)" }}>{comment.length} / 500</span>
          </div>
        </div>

        {error && <p style={{ color: "#dc2626", fontSize: 13, marginBottom: "1rem" }}>{error}</p>}

        <div style={{ display: "flex", gap: 8 }}>
          <button onClick={onClose} style={{ padding: "12px 20px", borderRadius: 10, border: "1px solid var(--border)", background: "none", color: "var(--text)", fontWeight: 500, cursor: "pointer" }}>
            Annuler
          </button>
          <button
            disabled={loading || stars === 0 || comment.trim().length < MIN_CHARS}
            onClick={handleSubmit}
            style={{
              flex: 1, padding: "12px", borderRadius: 10, border: "none",
              background: stars > 0 && comment.trim().length >= MIN_CHARS ? "var(--primary)" : "var(--border)",
              color: stars > 0 && comment.trim().length >= MIN_CHARS ? "#fff" : "var(--muted)",
              fontWeight: 600, fontSize: 15,
              cursor: loading ? "wait" : "pointer",
              opacity: loading ? 0.7 : 1, transition: "all 0.2s",
            }}
          >
            {loading ? "Envoi..." : "Publier l'avis"}
          </button>
        </div>
      </motion.div>
    </div>
  );
}

function ReportModal({ rating, onClose, onReported }: {
  rating: Rating;
  onClose: () => void;
  onReported: () => void;
}) {
  const [motif, setMotif] = useState<ReportPayload["motif"]>("INAPPROPRIE");
  const [description, setDescription] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const MOTIFS: { value: ReportPayload["motif"]; label: string }[] = [
    { value: "INAPPROPRIE", label: "Contenu inapproprié" },
    { value: "FAUX", label: "Information fausse" },
    { value: "SPAM", label: "Spam" },
    { value: "HARCÈLEMENT", label: "Harcèlement" },
    { value: "AUTRE", label: "Autre" },
  ];

  async function handleSubmit() {
    setLoading(true);
    try {
      await reportRating(rating.id, { motif, description });
      onReported();
      onClose();
    } catch {
      setError("Impossible d'envoyer le signalement.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div style={{
      position: "fixed", inset: 0, zIndex: 310,
      background: "rgba(0,0,0,0.5)", backdropFilter: "blur(4px)",
      display: "flex", alignItems: "center", justifyContent: "center", padding: "1rem",
    }}>
      <motion.div
        initial={{ opacity: 0, scale: 0.95 }}
        animate={{ opacity: 1, scale: 1 }}
        style={{ background: "var(--card)", borderRadius: 16, padding: "1.75rem", width: "100%", maxWidth: 420, boxShadow: "0 24px 80px rgba(0,0,0,0.2)" }}
      >
        <div style={{ display: "flex", justifyContent: "space-between", marginBottom: "1.25rem" }}>
          <h3 style={{ margin: 0, fontWeight: 700, color: "var(--text)" }}>Signaler cet avis</h3>
          <button onClick={onClose} style={{ background: "none", border: "none", cursor: "pointer", color: "var(--muted)", fontSize: 20 }}>×</button>
        </div>

        <div style={{ marginBottom: "1rem" }}>
          <label style={{ fontSize: 13, fontWeight: 600, color: "var(--text)", display: "block", marginBottom: 8 }}>Motif</label>
          <div style={{ display: "flex", flexDirection: "column", gap: 6 }}>
            {MOTIFS.map((m) => (
              <button
                key={m.value}
                onClick={() => setMotif(m.value)}
                style={{
                  padding: "9px 12px", borderRadius: 8, textAlign: "left",
                  border: motif === m.value ? "2px solid var(--primary)" : "1px solid var(--border)",
                  background: motif === m.value ? "rgba(var(--primary-rgb),0.05)" : "none",
                  color: "var(--text)", fontSize: 14, cursor: "pointer",
                }}
              >
                {m.label}
              </button>
            ))}
          </div>
        </div>

        <div style={{ marginBottom: "1.25rem" }}>
          <label style={{ fontSize: 13, fontWeight: 600, color: "var(--text)", display: "block", marginBottom: 6 }}>
            Précisions (optionnel)
          </label>
          <textarea
            rows={3}
            value={description}
            onChange={(e) => setDescription(e.target.value)}
            placeholder="Expliquez brièvement..."
            style={{
              width: "100%", padding: "10px 12px", borderRadius: 8,
              border: "1px solid var(--border)", background: "var(--bg)",
              color: "var(--text)", fontSize: 14, fontFamily: "inherit",
              boxSizing: "border-box", resize: "none", outline: "none",
            }}
          />
        </div>

        {error && <p style={{ color: "#dc2626", fontSize: 13, marginBottom: "1rem" }}>{error}</p>}

        <div style={{ display: "flex", gap: 8 }}>
          <button onClick={onClose} style={{ padding: "10px 18px", borderRadius: 8, border: "1px solid var(--border)", background: "none", color: "var(--text)", cursor: "pointer", fontWeight: 500 }}>
            Annuler
          </button>
          <button disabled={loading} onClick={handleSubmit} style={{ flex: 1, padding: "10px", borderRadius: 8, border: "none", background: "#dc2626", color: "#fff", fontWeight: 600, cursor: "pointer", opacity: loading ? 0.7 : 1 }}>
            {loading ? "Envoi..." : "Signaler"}
          </button>
        </div>
      </motion.div>
    </div>
  );
}

type Tab = "received" | "given" | "pending";

export default function Ratings() {
  const myId = getMyId();
  const [tab, setTab] = useState<Tab>("received");
  const [received, setReceived] = useState<Rating[]>([]);
  const [given, setGiven] = useState<Rating[]>([]);
  const [missions, setMissions] = useState<Mission[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [createFor, setCreateFor] = useState<Mission | null>(null);
  const [reportTarget, setReportTarget] = useState<Rating | null>(null);
  const [toast, setToast] = useState("");

  const load = useCallback(async () => {
    setLoading(true);
    setError("");
    try {
      const [recv, all, missionList] = await Promise.all([
        getRatings({ user_id: myId }),
        getRatings(),
        getMissions(),
      ]);
      setReceived(recv);
      setGiven(all.filter((r) => r.notateur.id === myId));
      setMissions(missionList);
    } catch {
      setError("Impossible de charger les avis.");
    } finally {
      setLoading(false);
    }
  }, [myId]);

  useEffect(() => { load(); }, [load]);

  function showToast(msg: string) {
    setToast(msg);
    setTimeout(() => setToast(""), 3500);
  }

  const givenMissionIds = new Set(given.filter((r) => r.mission !== null).map((r) => r.mission));
  const pendingMissions = missions.filter(
    (m) => m.statut === "TERMINEE" && !givenMissionIds.has(m.id)
  );

  const TABS: { key: Tab; label: string; count: number }[] = [
    { key: "received", label: "Avis reçus", count: received.length },
    { key: "given", label: "Avis donnés", count: given.length },
    { key: "pending", label: "À noter", count: pendingMissions.length },
  ];

  return (
    <div style={{ maxWidth: 800, margin: "0 auto", padding: "2.5rem 1.5rem 5rem" }}>
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
              boxShadow: "0 8px 24px rgba(0,0,0,0.2)", whiteSpace: "nowrap",
            }}
          >
            {toast}
          </motion.div>
        )}
      </AnimatePresence>

      {/* Header */}
      <div style={{ marginBottom: "1.75rem" }}>
        <h1 style={{ margin: 0, fontSize: "1.75rem", fontWeight: 800, color: "var(--text)" }}>
          Avis & Notations
        </h1>
        <p style={{ margin: "6px 0 0", color: "var(--muted)", fontSize: 15 }}>
          Consultez vos avis reçus et notez vos collaborations passées
        </p>
      </div>

      {loading && (
        <div style={{ textAlign: "center", padding: "5rem 0" }}>
          <div style={{ width: 32, height: 32, borderRadius: "50%", border: "3px solid var(--border)", borderTopColor: "var(--primary)", margin: "0 auto 12px", animation: "spin 0.8s linear infinite" }} />
          <p style={{ color: "var(--muted)", fontSize: 14 }}>Chargement...</p>
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

      {!loading && !error && (
        <>
          {/* Star distribution (only shown on "received" tab if ratings exist) */}
          {tab === "received" && received.length > 0 && (
            <DistributionBar ratings={received} />
          )}

          {/* Tabs */}
          <div style={{ display: "flex", gap: 4, marginBottom: "1.5rem", borderBottom: "1px solid var(--border)", paddingBottom: 0 }}>
            {TABS.map((t) => (
              <button
                key={t.key}
                onClick={() => setTab(t.key)}
                style={{
                  padding: "10px 16px",
                  borderRadius: "8px 8px 0 0",
                  border: "none",
                  borderBottom: tab === t.key ? "2px solid var(--primary)" : "2px solid transparent",
                  background: "none",
                  color: tab === t.key ? "var(--primary)" : "var(--muted)",
                  fontWeight: tab === t.key ? 700 : 400,
                  fontSize: 14,
                  cursor: "pointer",
                  transition: "all 0.15s",
                  display: "flex",
                  alignItems: "center",
                  gap: 6,
                }}
              >
                {t.label}
                {t.count > 0 && (
                  <span style={{
                    padding: "1px 7px", borderRadius: 10, fontSize: 11, fontWeight: 700,
                    background: tab === t.key ? "var(--primary)" : "var(--border)",
                    color: tab === t.key ? "#fff" : "var(--text)",
                  }}>
                    {t.count}
                  </span>
                )}
              </button>
            ))}
          </div>

          {/* Tab content */}
          <AnimatePresence mode="wait">
            {tab === "received" && (
              <motion.div key="recv" initial={{ opacity: 0, y: 8 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0 }}>
                {received.length === 0 ? (
                  <EmptyState
                    icon="⭐"
                    title="Aucun avis reçu"
                    desc="Les avis que d'autres utilisateurs vous laissent après vos collaborations apparaîtront ici."
                  />
                ) : (
                  <div style={{ display: "flex", flexDirection: "column", gap: 12 }}>
                    {received.map((r) => (
                      <RatingCard key={r.id} rating={r} myId={myId} onReport={setReportTarget} />
                    ))}
                  </div>
                )}
              </motion.div>
            )}

            {tab === "given" && (
              <motion.div key="given" initial={{ opacity: 0, y: 8 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0 }}>
                {given.length === 0 ? (
                  <EmptyState
                    icon="✍️"
                    title="Aucun avis publié"
                    desc="Vous n'avez pas encore laissé d'avis. Notez vos missions terminées depuis l'onglet À noter."
                    action={
                      pendingMissions.length > 0 ? (
                        <button onClick={() => setTab("pending")} style={{ padding: "9px 20px", borderRadius: 8, border: "none", background: "var(--primary)", color: "#fff", fontWeight: 600, cursor: "pointer", fontSize: 14 }}>
                          Voir les missions à noter ({pendingMissions.length})
                        </button>
                      ) : undefined
                    }
                  />
                ) : (
                  <div style={{ display: "flex", flexDirection: "column", gap: 12 }}>
                    {given.map((r) => (
                      <RatingCard key={r.id} rating={r} myId={myId} onReport={setReportTarget} />
                    ))}
                  </div>
                )}
              </motion.div>
            )}

            {tab === "pending" && (
              <motion.div key="pend" initial={{ opacity: 0, y: 8 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0 }}>
                {pendingMissions.length === 0 ? (
                  <EmptyState
                    icon="🌿"
                    title="Aucune mission à noter"
                    desc="Les missions terminées pour lesquelles vous n'avez pas encore laissé d'avis apparaîtront ici."
                  />
                ) : (
                  <div style={{ display: "flex", flexDirection: "column", gap: 10 }}>
                    {pendingMissions.map((m) => (
                      <motion.div
                        key={m.id}
                        layout
                        initial={{ opacity: 0, y: 10 }}
                        animate={{ opacity: 1, y: 0 }}
                        style={{
                          background: "var(--card)",
                          border: "1px solid var(--border)",
                          borderRadius: 14,
                          padding: "1.1rem 1.4rem",
                          display: "flex",
                          alignItems: "center",
                          justifyContent: "space-between",
                          gap: 12,
                        }}
                      >
                        <div>
                          <p style={{ margin: "0 0 4px", fontWeight: 600, fontSize: 14, color: "var(--text)" }}>
                            Mission #{m.id} — {m.agronome_nom}
                          </p>
                          <p style={{
                            margin: 0, fontSize: 13, color: "var(--muted)",
                            overflow: "hidden", textOverflow: "ellipsis",
                            display: "-webkit-box", WebkitLineClamp: 1, WebkitBoxOrient: "vertical" as const,
                            maxWidth: 380,
                          }}>
                            {m.description}
                          </p>
                        </div>
                        <button
                          onClick={() => setCreateFor(m)}
                          style={{
                            padding: "8px 16px", borderRadius: 8, border: "none",
                            background: "var(--primary)", color: "#fff",
                            fontWeight: 600, fontSize: 13, cursor: "pointer", whiteSpace: "nowrap",
                          }}
                        >
                          Laisser un avis
                        </button>
                      </motion.div>
                    ))}
                  </div>
                )}
              </motion.div>
            )}
          </AnimatePresence>
        </>
      )}

      {/* Create rating modal */}
      <AnimatePresence>
        {createFor && (
          <CreateRatingModal
            mission={createFor}
            onClose={() => setCreateFor(null)}
            onCreated={() => {
              load();
              showToast("Votre avis a été publié.");
              setTab("given");
            }}
          />
        )}
      </AnimatePresence>

      {/* Report modal */}
      <AnimatePresence>
        {reportTarget && (
          <ReportModal
            rating={reportTarget}
            onClose={() => setReportTarget(null)}
            onReported={() => showToast("Avis signalé. Notre équipe va l'examiner.")}
          />
        )}
      </AnimatePresence>

      <style>{`@keyframes spin { to { transform: rotate(360deg); } }`}</style>
    </div>
  );
}
