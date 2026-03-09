import React, { useEffect, useState } from "react";
import { motion } from "framer-motion";
import api from "../../api/auth";

const IconDoc = () => <svg width="24" height="24" viewBox="0 0 24 24" fill="none"><path d="M4 3h9l5 5v11a2 2 0 01-2 2H4a2 2 0 01-2-2V5a2 2 0 012-2z" stroke="currentColor" strokeWidth="1.5"/><path d="M13 3v5h5M7 11h8M7 15h5" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round"/></svg>;
const IconFilter = () => <svg width="20" height="20" viewBox="0 0 20 20" fill="none"><path d="M2 4h16M5 9h10M8 14h4" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round"/></svg>;
const IconDownload = () => <svg width="18" height="18" viewBox="0 0 18 18" fill="none"><path d="M9 2v10M6 9l3 3 3-3M3 15h12" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round"/></svg>;
const IconEye = () => <svg width="18" height="18" viewBox="0 0 18 18" fill="none"><path d="M1 9s3-6 8-6 8 6 8 6-3 6-8 6-8-6-8-6z" stroke="currentColor" strokeWidth="1.5"/><circle cx="9" cy="9" r="2.5" stroke="currentColor" strokeWidth="1.5"/></svg>;

const CULTURES = ['Maïs', 'Riz', 'Manioc', 'Tomate', 'Oignon', 'Arachide', 'Niébé', 'Sorgho', 'Soja', 'Coton'];
const REGIONS = ['Maritime', 'Plateaux', 'Centrale', 'Kara', 'Savanes'];

const CULTURE_COLORS: Record<string, string> = {
  Maïs: '#f59e0b', Riz: '#3b82f6', Manioc: '#8b5cf6', Tomate: '#ef4444',
  Oignon: '#f97316', Arachide: '#d97706', Niébé: '#10b981', Sorgho: '#6366f1',
  Soja: '#22c55e', Coton: '#0ea5e9',
};

interface Document {
  id: number;
  titre: string;
  description: string;
  prix: string;
  culture: string;
  region: string;
  prefecture: string;
  canton: string;
  date_creation: string;
}

export default function RapportsSectoriels() {
  const [documents, setDocuments] = useState<Document[]>([]);
  const [loading, setLoading] = useState(true);
  const [filters, setFilters] = useState({ culture: '', region: '', search: '' });

  useEffect(() => {
    const fetchDocuments = async () => {
      try {
        const params = new URLSearchParams();
        if (filters.culture) params.append('culture', filters.culture);
        if (filters.region) params.append('region', filters.region);
        if (filters.search) params.append('search', filters.search);
        
        const response = await api.get(`/documents/?${params}`);
        const docs = response.data.results || response.data || [];
        setDocuments(docs);
        setLoading(false);
      } catch (error) {
        console.error('Erreur chargement documents:', error);
        setDocuments([]);
        setLoading(false);
      }
    };

    fetchDocuments();
  }, [filters]);

  const hasActiveFilters = filters.culture !== '' || filters.region !== '' || filters.search !== '';

  // Statistiques
  const stats = {
    total: documents.length,
    parCulture: documents.reduce((acc: any, doc) => {
      acc[doc.culture] = (acc[doc.culture] || 0) + 1;
      return acc;
    }, {}),
    parRegion: documents.reduce((acc: any, doc) => {
      acc[doc.region] = (acc[doc.region] || 0) + 1;
      return acc;
    }, {}),
  };

  return (
    <div style={{ minHeight: "100vh", background: "var(--bg)", paddingTop: "5rem" }}>
      <div style={{ maxWidth: 1400, margin: "0 auto", padding: "2rem 1.5rem" }}>
        
        {/* Header */}
        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }}>
          <div style={{ marginBottom: "0.5rem" }}>
            <a href="/dashboard" style={{ color: "var(--text-muted)", fontSize: "0.85rem", textDecoration: "none" }}>
              ← Retour au dashboard
            </a>
          </div>
          <h1 style={{ fontSize: "2rem", fontWeight: 800, color: "var(--text)", margin: "0 0 0.5rem", letterSpacing: "-0.02em" }}>
            Rapports Sectoriels
          </h1>
          <p style={{ color: "var(--text-muted)", fontSize: "0.95rem", margin: 0 }}>
            Bibliothèque de documents techniques et guides agricoles par culture et région
          </p>
        </motion.div>

        {/* Statistiques rapides */}
        <motion.div initial={{ opacity: 0, y: 16 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.1 }}
          style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(200px, 1fr))", gap: "1rem", margin: "2rem 0" }}>
          <div style={{ background: "var(--surface)", border: "1px solid var(--border)", borderRadius: "14px", padding: "1.2rem" }}>
            <div style={{ fontSize: "0.75rem", fontWeight: 600, color: "var(--text-muted)", textTransform: "uppercase", letterSpacing: "0.05em", marginBottom: "0.5rem" }}>
              Total documents
            </div>
            <div style={{ fontSize: "2rem", fontWeight: 800, color: "var(--text)" }}>{loading ? "…" : stats.total}</div>
          </div>
          <div style={{ background: "var(--surface)", border: "1px solid var(--border)", borderRadius: "14px", padding: "1.2rem" }}>
            <div style={{ fontSize: "0.75rem", fontWeight: 600, color: "var(--text-muted)", textTransform: "uppercase", letterSpacing: "0.05em", marginBottom: "0.5rem" }}>
              Cultures couvertes
            </div>
            <div style={{ fontSize: "2rem", fontWeight: 800, color: "var(--text)" }}>{loading ? "…" : Object.keys(stats.parCulture).length}</div>
          </div>
          <div style={{ background: "var(--surface)", border: "1px solid var(--border)", borderRadius: "14px", padding: "1.2rem" }}>
            <div style={{ fontSize: "0.75rem", fontWeight: 600, color: "var(--text-muted)", textTransform: "uppercase", letterSpacing: "0.05em", marginBottom: "0.5rem" }}>
              Régions couvertes
            </div>
            <div style={{ fontSize: "2rem", fontWeight: 800, color: "var(--text)" }}>{loading ? "…" : Object.keys(stats.parRegion).length}</div>
          </div>
        </motion.div>

        <div style={{ display: "grid", gridTemplateColumns: "280px 1fr", gap: "2rem", alignItems: "start" }}>
          
          {/* Filtres */}
          <motion.aside initial={{ opacity: 0, x: -20 }} animate={{ opacity: 1, x: 0 }} transition={{ delay: 0.2 }}
            style={{ background: "var(--surface)", border: "1px solid var(--border)", borderRadius: "16px", padding: "1.5rem", position: "sticky", top: "88px" }}>
            <div style={{ display: "flex", alignItems: "center", gap: "8px", marginBottom: "1.5rem" }}>
              <IconFilter />
              <h3 style={{ fontSize: "1rem", fontWeight: 700, color: "var(--text)", margin: 0 }}>Filtres</h3>
              {hasActiveFilters && (
                <span style={{ marginLeft: "auto", background: "var(--primary)", color: "white", borderRadius: "100px", padding: "2px 10px", fontSize: "0.75rem", fontWeight: 600 }}>
                  Actifs
                </span>
              )}
            </div>

            <div style={{ marginBottom: "1.25rem" }}>
              <label style={{ display: "block", fontSize: "0.8rem", fontWeight: 600, color: "var(--text-muted)", textTransform: "uppercase", letterSpacing: "0.06em", marginBottom: "0.5rem" }}>
                Rechercher
              </label>
              <input
                type="text"
                placeholder="Titre du document..."
                value={filters.search}
                onChange={e => setFilters({ ...filters, search: e.target.value })}
                style={{ width: "100%", padding: "0.6rem 0.9rem", border: "1.5px solid var(--border)", borderRadius: "10px", background: "var(--bg)", color: "var(--text)", fontSize: "0.9rem", outline: "none", boxSizing: "border-box" }}
              />
            </div>

            <div style={{ marginBottom: "1.25rem" }}>
              <label style={{ display: "block", fontSize: "0.8rem", fontWeight: 600, color: "var(--text-muted)", textTransform: "uppercase", letterSpacing: "0.06em", marginBottom: "0.5rem" }}>
                Culture
              </label>
              <select
                value={filters.culture}
                onChange={e => setFilters({ ...filters, culture: e.target.value })}
                style={{ width: "100%", padding: "0.6rem 0.9rem", border: "1.5px solid var(--border)", borderRadius: "10px", background: "var(--bg)", color: "var(--text)", fontSize: "0.9rem", outline: "none", cursor: "pointer" }}>
                <option value="">Toutes les cultures</option>
                {CULTURES.map(c => <option key={c} value={c}>{c}</option>)}
              </select>
            </div>

            <div style={{ marginBottom: "1.5rem" }}>
              <label style={{ display: "block", fontSize: "0.8rem", fontWeight: 600, color: "var(--text-muted)", textTransform: "uppercase", letterSpacing: "0.06em", marginBottom: "0.5rem" }}>
                Région
              </label>
              <select
                value={filters.region}
                onChange={e => setFilters({ ...filters, region: e.target.value })}
                style={{ width: "100%", padding: "0.6rem 0.9rem", border: "1.5px solid var(--border)", borderRadius: "10px", background: "var(--bg)", color: "var(--text)", fontSize: "0.9rem", outline: "none", cursor: "pointer" }}>
                <option value="">Toutes les régions</option>
                {REGIONS.map(r => <option key={r} value={r}>{r}</option>)}
              </select>
            </div>

            {hasActiveFilters && (
              <button
                onClick={() => setFilters({ culture: '', region: '', search: '' })}
                style={{ width: "100%", padding: "0.6rem", background: "transparent", border: "1.5px solid var(--border)", borderRadius: "10px", color: "var(--text-muted)", fontSize: "0.9rem", fontWeight: 600, cursor: "pointer", transition: "all 0.2s" }}>
                Réinitialiser
              </button>
            )}
          </motion.aside>

          {/* Liste des documents */}
          <main>
            {!loading && (
              <div style={{ marginBottom: "1.5rem", color: "var(--text-muted)", fontSize: "0.9rem" }}>
                <strong style={{ color: "var(--text)" }}>{documents.length}</strong> document{documents.length !== 1 ? 's' : ''} trouvé{documents.length !== 1 ? 's' : ''}
              </div>
            )}

            {loading && (
              <div style={{ display: "grid", gap: "1rem" }}>
                {Array.from({ length: 5 }).map((_, i) => (
                  <div key={i} style={{ background: "var(--surface)", border: "1px solid var(--border)", borderRadius: "14px", padding: "1.5rem", height: "140px" }}>
                    <div style={{ width: "60%", height: "20px", borderRadius: "6px", background: "var(--bg)", marginBottom: "0.75rem", animation: "shimmer 1.5s infinite" }} />
                    <div style={{ width: "100%", height: "14px", borderRadius: "6px", background: "var(--bg)", marginBottom: "0.5rem", animation: "shimmer 1.5s infinite" }} />
                    <div style={{ width: "80%", height: "14px", borderRadius: "6px", background: "var(--bg)", animation: "shimmer 1.5s infinite" }} />
                  </div>
                ))}
              </div>
            )}

            {!loading && documents.length === 0 && (
              <div style={{ textAlign: "center", padding: "4rem 2rem", background: "var(--surface)", border: "1px solid var(--border)", borderRadius: "16px" }}>
                <div style={{ width: 56, height: 56, borderRadius: "14px", background: "var(--bg)", border: "1px solid var(--border)", display: "flex", alignItems: "center", justifyContent: "center", margin: "0 auto 1rem" }}>
                  <IconDoc />
                </div>
                <h3 style={{ color: "var(--text)", marginBottom: "0.5rem" }}>Aucun document trouvé</h3>
                <p style={{ color: "var(--text-muted)", fontSize: "0.9rem" }}>Essayez de modifier vos filtres de recherche</p>
              </div>
            )}

            {!loading && documents.length > 0 && (
              <div style={{ display: "grid", gap: "1rem" }}>
                {documents.map((doc, i) => {
                  const cultureColor = CULTURE_COLORS[doc.culture] || '#16a34a';
                  return (
                    <motion.div
                      key={doc.id}
                      initial={{ opacity: 0, y: 20 }}
                      animate={{ opacity: 1, y: 0 }}
                      transition={{ delay: i * 0.05 }}
                      style={{ background: "var(--surface)", border: "1px solid var(--border)", borderRadius: "14px", padding: "1.5rem", position: "relative", overflow: "hidden" }}>
                      
                      {/* Accent bar */}
                      <div style={{ position: "absolute", top: 0, left: 0, bottom: 0, width: "4px", background: cultureColor }} />

                      <div style={{ display: "flex", gap: "1.5rem", alignItems: "start" }}>
                        <div style={{ width: 56, height: 56, borderRadius: "12px", background: `${cultureColor}15`, color: cultureColor, display: "flex", alignItems: "center", justifyContent: "center", flexShrink: 0 }}>
                          <IconDoc />
                        </div>

                        <div style={{ flex: 1 }}>
                          <h3 style={{ fontSize: "1.1rem", fontWeight: 700, color: "var(--text)", margin: "0 0 0.5rem", lineHeight: 1.3 }}>
                            {doc.titre}
                          </h3>
                          <p style={{ fontSize: "0.9rem", color: "var(--text-muted)", lineHeight: 1.5, marginBottom: "1rem" }}>
                            {doc.description}
                          </p>

                          <div style={{ display: "flex", gap: "0.75rem", flexWrap: "wrap", alignItems: "center" }}>
                            <span style={{ display: "inline-flex", alignItems: "center", gap: "5px", padding: "4px 12px", borderRadius: "100px", background: `${cultureColor}18`, color: cultureColor, fontSize: "0.8rem", fontWeight: 600 }}>
                              🌾 {doc.culture}
                            </span>
                            <span style={{ display: "inline-flex", alignItems: "center", gap: "5px", padding: "4px 12px", borderRadius: "100px", background: "var(--bg)", color: "var(--text-muted)", fontSize: "0.8rem", fontWeight: 500 }}>
                              📍 {doc.canton || doc.prefecture || doc.region}
                            </span>
                            <span style={{ display: "inline-flex", alignItems: "center", gap: "5px", padding: "4px 12px", borderRadius: "100px", background: "var(--bg)", color: "var(--text-muted)", fontSize: "0.8rem", fontWeight: 500 }}>
                              💰 {parseInt(doc.prix).toLocaleString()} FCFA
                            </span>
                          </div>
                        </div>

                        <div style={{ display: "flex", gap: "0.5rem", flexShrink: 0 }}>
                          <button
                            style={{ padding: "0.6rem 1rem", background: "var(--bg)", border: "1px solid var(--border)", borderRadius: "10px", color: "var(--text)", fontSize: "0.85rem", fontWeight: 600, cursor: "pointer", display: "flex", alignItems: "center", gap: "6px", transition: "all 0.2s" }}
                            onMouseEnter={e => {
                              e.currentTarget.style.background = "var(--primary)";
                              e.currentTarget.style.color = "white";
                              e.currentTarget.style.borderColor = "var(--primary)";
                            }}
                            onMouseLeave={e => {
                              e.currentTarget.style.background = "var(--bg)";
                              e.currentTarget.style.color = "var(--text)";
                              e.currentTarget.style.borderColor = "var(--border)";
                            }}>
                            <IconEye /> Consulter
                          </button>
                        </div>
                      </div>
                    </motion.div>
                  );
                })}
              </div>
            )}
          </main>
        </div>
      </div>

      <style>{`
        @keyframes shimmer {
          0% { opacity: 1; }
          50% { opacity: 0.5; }
          100% { opacity: 1; }
        }
        @media (max-width: 900px) {
          div[style*="grid-template-columns: 280px 1fr"] {
            grid-template-columns: 1fr !important;
          }
        }
      `}</style>
    </div>
  );
}
