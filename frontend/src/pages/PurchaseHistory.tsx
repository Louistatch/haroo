import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { motion, AnimatePresence } from "framer-motion";
import { fetchPurchaseHistory, regenerateDownloadLink, buildDownloadUrl, Purchase, PurchaseFilters } from "../api/purchases";
import { useDebounce } from "../hooks/useDebounce";

const IconDoc = () => <svg width="20" height="20" viewBox="0 0 20 20" fill="none"><path d="M4 2h8l4 4v12a1 1 0 01-1 1H4a1 1 0 01-1-1V3a1 1 0 011-1z" stroke="currentColor" strokeWidth="1.4"/><path d="M12 2v4h4M6 9h8M6 13h5" stroke="currentColor" strokeWidth="1.4" strokeLinecap="round"/></svg>;
const IconDownload = () => <svg width="16" height="16" viewBox="0 0 16 16" fill="none"><path d="M8 2v8M5 7l3 3 3-3" stroke="currentColor" strokeWidth="1.6" strokeLinecap="round" strokeLinejoin="round"/><path d="M2 13h12" stroke="currentColor" strokeWidth="1.6" strokeLinecap="round"/></svg>;
const IconRefresh = () => <svg width="16" height="16" viewBox="0 0 16 16" fill="none"><path d="M13.5 8a5.5 5.5 0 11-1.6-3.9" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round"/><path d="M14 3v4h-4" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round"/></svg>;
const IconPlant = () => <svg width="12" height="12" viewBox="0 0 12 12" fill="none"><path d="M6 10V6M6 6C6 6 4 4 2 5M6 6C6 6 8 4 10 5" stroke="currentColor" strokeWidth="1.1" strokeLinecap="round"/><circle cx="6" cy="3" r="1.5" stroke="currentColor" strokeWidth="1.1"/></svg>;
const IconPin = () => <svg width="12" height="12" viewBox="0 0 12 12" fill="none"><path d="M6 11S2 7.5 2 5a4 4 0 018 0c0 2.5-4 6-4 6z" stroke="currentColor" strokeWidth="1.1"/><circle cx="6" cy="5" r="1.2" stroke="currentColor" strokeWidth="1.1"/></svg>;
const IconFilter = () => <svg width="16" height="16" viewBox="0 0 16 16" fill="none"><path d="M2 4h12M4 8h8M6 12h4" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round"/></svg>;
const IconX = () => <svg width="14" height="14" viewBox="0 0 14 14" fill="none"><path d="M2 2l10 10M12 2L2 12" stroke="currentColor" strokeWidth="1.6" strokeLinecap="round"/></svg>;
const IconClock = () => <svg width="12" height="12" viewBox="0 0 12 12" fill="none"><circle cx="6" cy="6" r="5" stroke="currentColor" strokeWidth="1.1"/><path d="M6 3v3.5l2 1.5" stroke="currentColor" strokeWidth="1.1" strokeLinecap="round"/></svg>;
const IconEmpty = () => <svg width="40" height="40" viewBox="0 0 40 40" fill="none"><path d="M8 6h16l8 8v22H8V6z" stroke="var(--text-muted)" strokeWidth="1.5"/><path d="M24 6v8h8" stroke="var(--text-muted)" strokeWidth="1.5"/><path d="M14 20h12M14 26h8" stroke="var(--text-muted)" strokeWidth="1.5" strokeLinecap="round"/></svg>;

const STATUS_CONF: Record<string, { label: string; color: string; bg: string }> = {
  SUCCESS: { label: "Payé",       color: "#16a34a", bg: "#dcfce7" },
  PENDING: { label: "En attente", color: "#d97706", bg: "#fef3c7" },
  FAILED:  { label: "Échoué",     color: "#ef4444", bg: "#fee2e2" },
};

function formatDate(d: string) {
  return new Date(d).toLocaleDateString("fr-FR", { day: "2-digit", month: "short", year: "numeric", hour: "2-digit", minute: "2-digit" });
}

function SkeletonCard() {
  return (
    <div style={{ background: "var(--surface)", border: "1px solid var(--border)", borderRadius: "16px", padding: "1.5rem", animation: "pulse 1.5s ease-in-out infinite" }}>
      <div style={{ display: "flex", gap: "1rem", marginBottom: "1rem" }}>
        <div style={{ width: 44, height: 44, borderRadius: "12px", background: "var(--border)", flexShrink: 0 }} />
        <div style={{ flex: 1 }}>
          <div style={{ height: 16, background: "var(--border)", borderRadius: "6px", marginBottom: "0.5rem", width: "60%" }} />
          <div style={{ height: 12, background: "var(--border)", borderRadius: "4px", width: "30%" }} />
        </div>
      </div>
      <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "0.5rem" }}>
        {[1, 2, 3, 4].map(i => <div key={i} style={{ height: 12, background: "var(--border)", borderRadius: "4px" }} />)}
      </div>
      <style>{`@keyframes pulse { 0%,100%{opacity:1} 50%{opacity:0.6} }`}</style>
    </div>
  );
}

export default function PurchaseHistory() {
  const [purchases, setPurchases] = useState<Purchase[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [filters, setFilters] = useState<PurchaseFilters>({});
  const [totalCount, setTotalCount] = useState(0);
  const [currentPage, setCurrentPage] = useState(1);
  const [regeneratingId, setRegeneratingId] = useState<number | null>(null);
  const [successMsg, setSuccessMsg] = useState("");
  const [showFilters, setShowFilters] = useState(false);
  const navigate = useNavigate();

  const debouncedCulture = useDebounce(filters.culture, 300);

  useEffect(() => { load(); }, [debouncedCulture, filters.date_debut, filters.date_fin, filters.statut, filters.lien_expire, currentPage]);

  async function load() {
    const token = localStorage.getItem("access_token");
    if (!token) { navigate("/login"); return; }
    setLoading(true); setError(null);
    try {
      const data = await fetchPurchaseHistory({ ...filters, culture: debouncedCulture, page: currentPage, page_size: 12 }, token);
      setPurchases(data.results || []);
      setTotalCount(data.count || 0);
    } catch (err: any) {
      if (err.response?.status === 401) { navigate("/login"); return; }
      setError("Impossible de charger vos achats. Veuillez réessayer.");
    } finally { setLoading(false); }
  }

  async function handleRegenerate(id: number) {
    const token = localStorage.getItem("access_token");
    if (!token) { navigate("/login"); return; }
    setRegeneratingId(id);
    try {
      const res = await regenerateDownloadLink(id, token);
      setPurchases(prev => prev.map(p => p.id === id ? { ...p, lien_expire: false, expiration_lien: res.expiration } : p));
      setSuccessMsg("Lien régénéré avec succès");
      setTimeout(() => setSuccessMsg(""), 3000);
    } catch (err: any) {
      alert(err.response?.data?.error || "Impossible de régénérer le lien");
    } finally { setRegeneratingId(null); }
  }

  function handleDownload(p: Purchase) {
    window.open(buildDownloadUrl(p.document, p.lien_telechargement), "_blank");
  }

  const hasFilters = Object.values(filters).some(v => v !== undefined && v !== "" && v !== false);
  const totalPages = Math.ceil(totalCount / 12);

  return (
    <div style={{ minHeight: "100vh", background: "var(--bg)", paddingTop: "5rem" }}>
      <div style={{ maxWidth: 980, margin: "0 auto", padding: "2rem 1.5rem" }}>

        {/* Header */}
        <motion.div initial={{ opacity: 0, y: 16 }} animate={{ opacity: 1, y: 0 }} style={{ marginBottom: "1.75rem" }}>
          <button onClick={() => navigate("/documents")}
            style={{ display: "inline-flex", alignItems: "center", gap: "0.4rem", color: "var(--text-muted)", background: "none", border: "none", cursor: "pointer", fontSize: "0.85rem", fontWeight: 500, padding: "0 0 0.75rem", marginBottom: "0.25rem" }}>
            ← Retour aux documents
          </button>
          <div style={{ display: "flex", alignItems: "flex-start", justifyContent: "space-between", flexWrap: "wrap", gap: "1rem" }}>
            <div>
              <h1 style={{ margin: "0 0 0.35rem", fontSize: "clamp(1.4rem, 3vw, 2rem)", fontWeight: 800, color: "var(--text)", letterSpacing: "-0.03em" }}>
                Mes Achats
              </h1>
              <p style={{ margin: 0, color: "var(--text-muted)", fontSize: "0.9rem" }}>
                {loading ? "Chargement..." : `${totalCount} document${totalCount !== 1 ? "s" : ""} acheté${totalCount !== 1 ? "s" : ""}`}
              </p>
            </div>
            <button onClick={() => setShowFilters(v => !v)}
              style={{ display: "flex", alignItems: "center", gap: "0.5rem", padding: "0.65rem 1.1rem", background: showFilters ? "var(--primary)" : "var(--surface)", color: showFilters ? "white" : "var(--text)", border: "1.5px solid var(--border)", borderRadius: "10px", fontWeight: 600, fontSize: "0.85rem", cursor: "pointer" }}>
              <IconFilter /> Filtres {hasFilters && <span style={{ background: showFilters ? "rgba(255,255,255,0.3)" : "var(--primary)", color: showFilters ? "white" : "white", padding: "0.1rem 0.4rem", borderRadius: "100px", fontSize: "0.7rem" }}>!</span>}
            </button>
          </div>
        </motion.div>

        {/* success */}
        <AnimatePresence>
          {successMsg && (
            <motion.div initial={{ opacity: 0, y: -8 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0 }}
              style={{ display: "flex", alignItems: "center", gap: "0.5rem", padding: "0.75rem 1rem", background: "#f0fdf4", border: "1.5px solid #bbf7d0", borderRadius: "10px", color: "#16a34a", fontWeight: 600, fontSize: "0.88rem", marginBottom: "1rem" }}>
              {successMsg}
            </motion.div>
          )}
        </AnimatePresence>

        {/* Filters panel */}
        <AnimatePresence>
          {showFilters && (
            <motion.div initial={{ opacity: 0, height: 0 }} animate={{ opacity: 1, height: "auto" }} exit={{ opacity: 0, height: 0 }}
              style={{ background: "var(--surface)", border: "1px solid var(--border)", borderRadius: "16px", padding: "1.5rem", marginBottom: "1.5rem", overflow: "hidden" }}>
              <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fill, minmax(180px, 1fr))", gap: "1rem", marginBottom: "1rem" }}>
                {[
                  { label: "Date de début", key: "date_debut", type: "date" },
                  { label: "Date de fin", key: "date_fin", type: "date" },
                  { label: "Culture", key: "culture", type: "text", placeholder: "Ex: Maïs, Riz..." },
                ].map(({ label, key, type, placeholder }) => (
                  <div key={key}>
                    <label style={{ display: "block", fontSize: "0.72rem", fontWeight: 700, color: "var(--text-muted)", textTransform: "uppercase", letterSpacing: "0.05em", marginBottom: "0.4rem" }}>{label}</label>
                    <input type={type} placeholder={placeholder}
                      value={(filters as any)[key] || ""}
                      onChange={e => setFilters(f => ({ ...f, [key]: e.target.value || undefined }))}
                      style={{ width: "100%", padding: "0.6rem 0.8rem", border: "1.5px solid var(--border)", borderRadius: "8px", background: "var(--bg)", color: "var(--text)", fontSize: "0.88rem", outline: "none", boxSizing: "border-box" }} />
                  </div>
                ))}
                <div>
                  <label style={{ display: "block", fontSize: "0.72rem", fontWeight: 700, color: "var(--text-muted)", textTransform: "uppercase", letterSpacing: "0.05em", marginBottom: "0.4rem" }}>Statut</label>
                  <select value={filters.statut || ""} onChange={e => setFilters(f => ({ ...f, statut: e.target.value || undefined }))}
                    style={{ width: "100%", padding: "0.6rem 0.8rem", border: "1.5px solid var(--border)", borderRadius: "8px", background: "var(--bg)", color: "var(--text)", fontSize: "0.88rem", outline: "none", boxSizing: "border-box" }}>
                    <option value="">Tous les statuts</option>
                    <option value="SUCCESS">Payé</option>
                    <option value="PENDING">En attente</option>
                    <option value="FAILED">Échoué</option>
                  </select>
                </div>
              </div>
              <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between" }}>
                <label style={{ display: "flex", alignItems: "center", gap: "0.5rem", fontSize: "0.85rem", color: "var(--text)", cursor: "pointer", fontWeight: 500 }}>
                  <input type="checkbox" checked={filters.lien_expire || false} onChange={e => setFilters(f => ({ ...f, lien_expire: e.target.checked || undefined }))} style={{ accentColor: "var(--primary)" }} />
                  Liens expirés uniquement
                </label>
                {hasFilters && (
                  <button onClick={() => { setFilters({}); setCurrentPage(1); }}
                    style={{ display: "flex", alignItems: "center", gap: "0.35rem", color: "#ef4444", background: "none", border: "none", cursor: "pointer", fontSize: "0.82rem", fontWeight: 600 }}>
                    <IconX /> Réinitialiser
                  </button>
                )}
              </div>
            </motion.div>
          )}
        </AnimatePresence>

        {/* Error */}
        {!loading && error && (
          <div style={{ textAlign: "center", padding: "4rem 2rem", background: "var(--surface)", border: "1px solid var(--border)", borderRadius: "16px" }}>
            <div style={{ width: 56, height: 56, borderRadius: "16px", background: "rgba(239,68,68,0.06)", border: "1.5px solid rgba(239,68,68,0.15)", display: "flex", alignItems: "center", justifyContent: "center", margin: "0 auto 1rem" }}>
              <svg width="24" height="24" viewBox="0 0 24 24" fill="none"><path d="M12 9v4M12 17h.01" stroke="#ef4444" strokeWidth="1.8" strokeLinecap="round"/><path d="M10.29 3.86L1.82 18a2 2 0 001.71 3h16.94a2 2 0 001.71-3L13.71 3.86a2 2 0 00-3.42 0z" stroke="#ef4444" strokeWidth="1.5" strokeLinejoin="round"/></svg>
            </div>
            <p style={{ color: "var(--text-muted)", marginBottom: "1.25rem" }}>{error}</p>
            <button onClick={load} style={{ padding: "0.6rem 1.5rem", background: "var(--primary)", color: "white", border: "none", borderRadius: "10px", fontWeight: 600, cursor: "pointer" }}>Réessayer</button>
          </div>
        )}

        {/* Loading */}
        {loading && (
          <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fill, minmax(280px, 1fr))", gap: "1.25rem" }}>
            {[1, 2, 3, 4, 5, 6].map(i => <SkeletonCard key={i} />)}
          </div>
        )}

        {/* Empty */}
        {!loading && !error && purchases.length === 0 && (
          <motion.div initial={{ opacity: 0, scale: 0.96 }} animate={{ opacity: 1, scale: 1 }}
            style={{ textAlign: "center", padding: "5rem 2rem", background: "var(--surface)", border: "1px solid var(--border)", borderRadius: "16px" }}>
            <div style={{ display: "flex", justifyContent: "center", marginBottom: "1.25rem" }}><IconEmpty /></div>
            <h3 style={{ color: "var(--text)", marginBottom: "0.5rem", fontWeight: 700 }}>Aucun achat trouvé</h3>
            <p style={{ color: "var(--text-muted)", marginBottom: "1.5rem", fontSize: "0.9rem" }}>
              {hasFilters ? "Aucun résultat pour ces filtres." : "Vous n'avez pas encore acheté de documents."}
            </p>
            {hasFilters ? (
              <button onClick={() => setFilters({})} style={{ padding: "0.65rem 1.5rem", background: "var(--bg)", border: "1.5px solid var(--border)", borderRadius: "10px", fontWeight: 600, cursor: "pointer", color: "var(--text)", marginRight: "0.75rem" }}>Réinitialiser</button>
            ) : null}
            <button onClick={() => navigate("/documents")} style={{ padding: "0.65rem 1.5rem", background: "var(--primary)", color: "white", border: "none", borderRadius: "10px", fontWeight: 600, cursor: "pointer" }}>
              Parcourir le catalogue
            </button>
          </motion.div>
        )}

        {/* Cards grid */}
        {!loading && !error && purchases.length > 0 && (
          <>
            <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fill, minmax(280px, 1fr))", gap: "1.25rem" }}>
              <AnimatePresence>
                {purchases.map((p, i) => {
                  const statusConf = STATUS_CONF[p.transaction_statut] || { label: p.transaction_statut, color: "#6366f1", bg: "#ede9fe" };
                  return (
                    <motion.div key={p.id}
                      initial={{ opacity: 0, y: 12 }} animate={{ opacity: 1, y: 0 }}
                      transition={{ duration: 0.3, delay: i * 0.04 }}
                      style={{
                        background: "var(--surface)",
                        border: `1px solid ${p.lien_expire ? "rgba(239,68,68,0.25)" : "var(--border)"}`,
                        borderRadius: "16px", padding: "1.35rem",
                        display: "flex", flexDirection: "column",
                      }}>
                      {/* card header */}
                      <div style={{ display: "flex", gap: "0.85rem", marginBottom: "1rem" }}>
                        <div style={{ width: 44, height: 44, borderRadius: "12px", background: "var(--bg)", border: "1.5px solid var(--border)", display: "flex", alignItems: "center", justifyContent: "center", flexShrink: 0, color: "var(--text-muted)" }}>
                          <IconDoc />
                        </div>
                        <div style={{ flex: 1, minWidth: 0 }}>
                          <div style={{ fontWeight: 700, color: "var(--text)", fontSize: "0.9rem", lineHeight: 1.3, marginBottom: "0.4rem", overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap" }}>
                            {p.document_titre}
                          </div>
                          <div style={{ display: "flex", gap: "0.4rem", flexWrap: "wrap" }}>
                            <span style={{ padding: "0.15rem 0.55rem", borderRadius: "100px", fontSize: "0.72rem", fontWeight: 600, background: statusConf.bg, color: statusConf.color }}>
                              {statusConf.label}
                            </span>
                            {p.lien_expire && (
                              <span style={{ padding: "0.15rem 0.55rem", borderRadius: "100px", fontSize: "0.72rem", fontWeight: 600, background: "#fee2e2", color: "#ef4444" }}>
                                Expiré
                              </span>
                            )}
                          </div>
                        </div>
                      </div>

                      {/* details */}
                      <div style={{ display: "flex", flexDirection: "column", gap: "0.45rem", marginBottom: "1rem", flexGrow: 1 }}>
                        <div style={{ display: "flex", justifyContent: "space-between", fontSize: "0.82rem" }}>
                          <span style={{ display: "flex", alignItems: "center", gap: "4px", color: "var(--text-muted)" }}>
                            <IconPlant /> Culture
                          </span>
                          <span style={{ fontWeight: 600, color: "var(--text)" }}>{p.document_culture}</span>
                        </div>
                        <div style={{ display: "flex", justifyContent: "space-between", fontSize: "0.82rem" }}>
                          <span style={{ color: "var(--text-muted)" }}>Format</span>
                          <span style={{ fontWeight: 600, color: "var(--text)" }}>{p.format_fichier}</span>
                        </div>
                        <div style={{ display: "flex", justifyContent: "space-between", fontSize: "0.82rem" }}>
                          <span style={{ color: "var(--text-muted)" }}>Téléchargements</span>
                          <span style={{ fontWeight: 600, color: "var(--text)" }}>{p.nombre_telechargements}</span>
                        </div>
                        <div style={{ display: "flex", justifyContent: "space-between", fontSize: "0.82rem" }}>
                          <span style={{ color: "var(--text-muted)" }}>Prix</span>
                          <span style={{ fontWeight: 700, color: "var(--primary)", fontSize: "0.88rem" }}>
                            {parseInt(p.document_prix).toLocaleString("fr-FR")} FCFA
                          </span>
                        </div>
                        {p.expiration_lien && (
                          <div style={{ display: "flex", justifyContent: "space-between", fontSize: "0.78rem", marginTop: "0.2rem" }}>
                            <span style={{ display: "flex", alignItems: "center", gap: "4px", color: "var(--text-muted)" }}>
                              <IconClock /> Expiration
                            </span>
                            <span style={{ fontWeight: 500, color: p.lien_expire ? "#ef4444" : "var(--text)" }}>
                              {formatDate(p.expiration_lien)}
                            </span>
                          </div>
                        )}
                      </div>

                      {/* date footer */}
                      <div style={{ fontSize: "0.72rem", color: "var(--text-muted)", marginBottom: "0.85rem", borderTop: "1px solid var(--border)", paddingTop: "0.75rem" }}>
                        Acheté le {formatDate(p.created_at)}
                      </div>

                      {/* actions */}
                      <div style={{ display: "flex", gap: "0.5rem" }}>
                        {p.transaction_statut === "SUCCESS" && !p.lien_expire && (
                          <motion.button whileHover={{ scale: 1.02 }} whileTap={{ scale: 0.97 }}
                            onClick={() => handleDownload(p)}
                            style={{ flex: 1, display: "flex", alignItems: "center", justifyContent: "center", gap: "0.4rem", padding: "0.65rem", background: "var(--primary)", color: "white", border: "none", borderRadius: "10px", fontWeight: 600, fontSize: "0.82rem", cursor: "pointer" }}>
                            <IconDownload /> Télécharger
                          </motion.button>
                        )}
                        {p.lien_expire && p.peut_regenerer && (
                          <motion.button whileHover={{ scale: 1.02 }} whileTap={{ scale: 0.97 }}
                            onClick={() => handleRegenerate(p.id)}
                            disabled={regeneratingId === p.id}
                            style={{ flex: 1, display: "flex", alignItems: "center", justifyContent: "center", gap: "0.4rem", padding: "0.65rem", background: "rgba(99,102,241,0.1)", color: "#6366f1", border: "1.5px solid rgba(99,102,241,0.25)", borderRadius: "10px", fontWeight: 600, fontSize: "0.82rem", cursor: regeneratingId === p.id ? "not-allowed" : "pointer", opacity: regeneratingId === p.id ? 0.7 : 1 }}>
                            {regeneratingId === p.id ? (
                              <motion.div animate={{ rotate: 360 }} transition={{ duration: 0.7, repeat: Infinity, ease: "linear" }}
                                style={{ width: 14, height: 14, border: "2px solid rgba(99,102,241,0.3)", borderTop: "2px solid #6366f1", borderRadius: "50%" }} />
                            ) : <IconRefresh />}
                            {regeneratingId === p.id ? "Régénération..." : "Régénérer le lien"}
                          </motion.button>
                        )}
                        {p.transaction_statut !== "SUCCESS" && (
                          <div style={{ flex: 1, padding: "0.65rem", background: "var(--bg)", border: "1px solid var(--border)", borderRadius: "10px", color: "var(--text-muted)", fontSize: "0.82rem", textAlign: "center" }}>
                            {p.transaction_statut === "PENDING" ? "Paiement en attente" : "Paiement échoué"}
                          </div>
                        )}
                      </div>
                    </motion.div>
                  );
                })}
              </AnimatePresence>
            </div>

            {/* Pagination */}
            {totalPages > 1 && (
              <div style={{ display: "flex", justifyContent: "center", alignItems: "center", gap: "0.75rem", marginTop: "2rem" }}>
                <button onClick={() => setCurrentPage(p => Math.max(1, p - 1))} disabled={currentPage === 1}
                  style={{ padding: "0.6rem 1.1rem", background: "var(--surface)", border: "1.5px solid var(--border)", borderRadius: "10px", color: currentPage === 1 ? "var(--text-muted)" : "var(--text)", fontWeight: 600, fontSize: "0.88rem", cursor: currentPage === 1 ? "not-allowed" : "pointer" }}>
                  ← Précédent
                </button>
                <span style={{ color: "var(--text-muted)", fontSize: "0.88rem", fontWeight: 500 }}>
                  Page {currentPage} / {totalPages}
                </span>
                <button onClick={() => setCurrentPage(p => Math.min(totalPages, p + 1))} disabled={currentPage >= totalPages}
                  style={{ padding: "0.6rem 1.1rem", background: "var(--surface)", border: "1.5px solid var(--border)", borderRadius: "10px", color: currentPage >= totalPages ? "var(--text-muted)" : "var(--text)", fontWeight: 600, fontSize: "0.88rem", cursor: currentPage >= totalPages ? "not-allowed" : "pointer" }}>
                  Suivant →
                </button>
              </div>
            )}
          </>
        )}
      </div>
    </div>
  );
}
