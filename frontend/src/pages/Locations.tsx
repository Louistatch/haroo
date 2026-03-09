import React, { useState, useEffect, useCallback } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { getRegions, getPrefectures, getCantons, Region, Prefecture, Canton } from "../api/locations";

const MapIcon = () => (
  <svg width="20" height="20" viewBox="0 0 20 20" fill="none">
    <path d="M10 17s-6-4.35-6-8.5a6 6 0 0112 0C16 12.65 10 17 10 17z" stroke="currentColor" strokeWidth="1.5" />
    <circle cx="10" cy="8.5" r="2" stroke="currentColor" strokeWidth="1.5" />
  </svg>
);

const ChevronIcon = ({ open }: { open: boolean }) => (
  <svg width="16" height="16" viewBox="0 0 16 16" fill="none" style={{ transform: open ? "rotate(90deg)" : "rotate(0)", transition: "transform 0.2s" }}>
    <path d="M6 4l4 4-4 4" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" />
  </svg>
);

export default function Locations() {
  const [regions, setRegions] = useState<Region[]>([]);
  const [prefectures, setPrefectures] = useState<Record<number, Prefecture[]>>({});
  const [cantons, setCantons] = useState<Record<number, Canton[]>>({});
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [expandedRegion, setExpandedRegion] = useState<number | null>(null);
  const [expandedPrefecture, setExpandedPrefecture] = useState<number | null>(null);
  const [search, setSearch] = useState("");

  useEffect(() => {
    setLoading(true);
    getRegions()
      .then(setRegions)
      .catch(() => setError("Impossible de charger les régions."))
      .finally(() => setLoading(false));
  }, []);

  const toggleRegion = useCallback(async (regionId: number) => {
    if (expandedRegion === regionId) { setExpandedRegion(null); return; }
    setExpandedRegion(regionId);
    setExpandedPrefecture(null);
    if (!prefectures[regionId]) {
      try {
        const data = await getPrefectures({ region: regionId });
        setPrefectures(prev => ({ ...prev, [regionId]: data }));
      } catch { /* silently fail */ }
    }
  }, [expandedRegion, prefectures]);

  const togglePrefecture = useCallback(async (prefId: number) => {
    if (expandedPrefecture === prefId) { setExpandedPrefecture(null); return; }
    setExpandedPrefecture(prefId);
    if (!cantons[prefId]) {
      try {
        const data = await getCantons({ prefecture: prefId });
        setCantons(prev => ({ ...prev, [prefId]: data }));
      } catch { /* silently fail */ }
    }
  }, [expandedPrefecture, cantons]);

  const filteredRegions = search
    ? regions.filter(r => r.nom.toLowerCase().includes(search.toLowerCase()))
    : regions;

  return (
    <div style={{ maxWidth: 900, margin: "0 auto", padding: "2.5rem 1.5rem 4rem" }}>
      {/* Header */}
      <div style={{ marginBottom: "2rem" }}>
        <motion.div initial={{ opacity: 0, y: -10 }} animate={{ opacity: 1, y: 0 }}
          style={{ display: "inline-flex", alignItems: "center", gap: 8, background: "rgba(22,163,74,0.1)", border: "1px solid rgba(22,163,74,0.2)", borderRadius: 100, padding: "6px 16px", marginBottom: "1rem" }}>
          <MapIcon />
          <span style={{ fontSize: "0.85rem", fontWeight: 600, color: "var(--primary)" }}>DÉCOUPAGE ADMINISTRATIF</span>
        </motion.div>
        <h1 style={{ margin: 0, fontSize: "1.75rem", fontWeight: 800, color: "var(--text)" }}>
          Régions du Togo
        </h1>
        <p style={{ margin: "6px 0 0", color: "var(--text-secondary)", fontSize: 15 }}>
          Explorez les régions, préfectures et cantons du Togo
        </p>
      </div>

      {/* Search */}
      <div style={{ marginBottom: "1.5rem" }}>
        <input type="text" placeholder="Rechercher une région..." value={search}
          onChange={e => setSearch(e.target.value)}
          style={{ width: "100%", maxWidth: 400, padding: "10px 14px", borderRadius: 10, border: "1.5px solid var(--border)", background: "var(--surface)", color: "var(--text)", fontSize: 14, outline: "none", boxSizing: "border-box" }}
          onFocus={e => (e.target.style.borderColor = "var(--primary)")}
          onBlur={e => (e.target.style.borderColor = "var(--border)")} />
      </div>

      {/* Loading */}
      {loading && (
        <div style={{ textAlign: "center", padding: "4rem 0", color: "var(--text-secondary)" }}>
          <div style={{ width: 32, height: 32, borderRadius: "50%", border: "3px solid var(--border)", borderTopColor: "var(--primary)", margin: "0 auto 12px", animation: "spin 0.8s linear infinite" }} />
          Chargement...
        </div>
      )}

      {/* Error */}
      {!loading && error && (
        <div style={{ textAlign: "center", padding: "3rem 0", color: "#dc2626" }}>{error}</div>
      )}

      {/* Regions list */}
      {!loading && !error && (
        <div style={{ display: "flex", flexDirection: "column", gap: 10 }}>
          {filteredRegions.length === 0 && (
            <div style={{ textAlign: "center", padding: "3rem 0", color: "var(--text-secondary)" }}>
              Aucune région trouvée
            </div>
          )}
          {filteredRegions.map(region => (
            <div key={region.id} style={{ background: "var(--surface)", border: "1px solid var(--border)", borderRadius: 14, overflow: "hidden" }}>
              {/* Region header */}
              <button onClick={() => toggleRegion(region.id)}
                style={{ width: "100%", display: "flex", alignItems: "center", gap: 12, padding: "1rem 1.25rem", background: "none", border: "none", cursor: "pointer", color: "var(--text)", textAlign: "left" }}>
                <div style={{ width: 40, height: 40, borderRadius: 10, background: "rgba(22,163,74,0.1)", display: "flex", alignItems: "center", justifyContent: "center", color: "var(--primary)", flexShrink: 0 }}>
                  <MapIcon />
                </div>
                <div style={{ flex: 1 }}>
                  <div style={{ fontWeight: 700, fontSize: "1.05rem" }}>{region.nom}</div>
                  {region.nombre_prefectures !== undefined && (
                    <div style={{ fontSize: 13, color: "var(--text-secondary)", marginTop: 2 }}>
                      {region.nombre_prefectures} préfecture{region.nombre_prefectures !== 1 ? "s" : ""}
                    </div>
                  )}
                </div>
                <ChevronIcon open={expandedRegion === region.id} />
              </button>

              {/* Prefectures */}
              <AnimatePresence>
                {expandedRegion === region.id && (
                  <motion.div initial={{ height: 0, opacity: 0 }} animate={{ height: "auto", opacity: 1 }} exit={{ height: 0, opacity: 0 }} transition={{ duration: 0.25 }}
                    style={{ overflow: "hidden", borderTop: "1px solid var(--border)" }}>
                    <div style={{ padding: "0.5rem 1rem 1rem", paddingLeft: "3.5rem" }}>
                      {!prefectures[region.id] ? (
                        <div style={{ padding: "0.75rem 0", color: "var(--text-secondary)", fontSize: 13 }}>Chargement...</div>
                      ) : prefectures[region.id].length === 0 ? (
                        <div style={{ padding: "0.75rem 0", color: "var(--text-secondary)", fontSize: 13 }}>Aucune préfecture</div>
                      ) : (
                        <div style={{ display: "flex", flexDirection: "column", gap: 4 }}>
                          {prefectures[region.id].map(pref => (
                            <div key={pref.id}>
                              <button onClick={() => togglePrefecture(pref.id)}
                                style={{ width: "100%", display: "flex", alignItems: "center", gap: 10, padding: "8px 10px", background: expandedPrefecture === pref.id ? "var(--bg)" : "none", border: "none", borderRadius: 8, cursor: "pointer", color: "var(--text)", textAlign: "left", transition: "background 0.15s" }}>
                                <ChevronIcon open={expandedPrefecture === pref.id} />
                                <span style={{ fontWeight: 600, fontSize: 14 }}>{pref.nom}</span>
                                {pref.nombre_cantons !== undefined && (
                                  <span style={{ fontSize: 12, color: "var(--text-secondary)", marginLeft: "auto" }}>
                                    {pref.nombre_cantons} canton{pref.nombre_cantons !== 1 ? "s" : ""}
                                  </span>
                                )}
                              </button>

                              {/* Cantons */}
                              <AnimatePresence>
                                {expandedPrefecture === pref.id && (
                                  <motion.div initial={{ height: 0, opacity: 0 }} animate={{ height: "auto", opacity: 1 }} exit={{ height: 0, opacity: 0 }} transition={{ duration: 0.2 }}
                                    style={{ overflow: "hidden", paddingLeft: "2rem" }}>
                                    {!cantons[pref.id] ? (
                                      <div style={{ padding: "6px 10px", color: "var(--text-secondary)", fontSize: 13 }}>Chargement...</div>
                                    ) : cantons[pref.id].length === 0 ? (
                                      <div style={{ padding: "6px 10px", color: "var(--text-secondary)", fontSize: 13 }}>Aucun canton</div>
                                    ) : (
                                      <div style={{ display: "flex", flexWrap: "wrap", gap: 6, padding: "6px 0 10px" }}>
                                        {cantons[pref.id].map(canton => (
                                          <span key={canton.id} style={{ display: "inline-block", padding: "4px 12px", borderRadius: 100, background: "var(--bg)", border: "1px solid var(--border)", fontSize: 13, color: "var(--text)", fontWeight: 500 }}>
                                            {canton.nom}
                                          </span>
                                        ))}
                                      </div>
                                    )}
                                  </motion.div>
                                )}
                              </AnimatePresence>
                            </div>
                          ))}
                        </div>
                      )}
                    </div>
                  </motion.div>
                )}
              </AnimatePresence>
            </div>
          ))}
        </div>
      )}

      <style>{`
        @keyframes spin { to { transform: rotate(360deg); } }
      `}</style>
    </div>
  );
}
