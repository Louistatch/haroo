import React, { useState, useEffect } from "react";
import {
  getDashboardStats, getAdminUsers, suspendUser, activateUser,
  getModerationQueue, moderateRating, getQualityAlerts,
  DashboardStats, AdminUser
} from "../api/admin";

const BLUE = "#2563eb";
const GREEN = "#16a34a";
const RED = "#ef4444";
const ORANGE = "#f59e0b";
const GRAY = "#6b7280";

const USER_TYPE_LABELS: Record<string, string> = {
  EXPLOITANT: "Exploitant", AGRONOME: "Agronome", OUVRIER: "Ouvrier",
  ACHETEUR: "Acheteur", INSTITUTION: "Institution", ADMIN: "Admin", "": "Non défini"
};

type Tab = "overview" | "users" | "moderation";

export default function AdminDashboard() {
  const [tab, setTab] = useState<Tab>("overview");
  const [stats, setStats] = useState<DashboardStats | null>(null);
  const [users, setUsers] = useState<AdminUser[]>([]);
  const [usersTotal, setUsersTotal] = useState(0);
  const [usersPage, setUsersPage] = useState(1);
  const [search, setSearch] = useState("");
  const [filterType, setFilterType] = useState("");
  const [modQueue, setModQueue] = useState<any[]>([]);
  const [alerts, setAlerts] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [actionMsg, setActionMsg] = useState("");
  const [suspendModal, setSuspendModal] = useState<{ userId: number; name: string } | null>(null);
  const [justification, setJustification] = useState("");

  useEffect(() => {
    loadStats();
  }, []);

  useEffect(() => {
    if (tab === "users") loadUsers();
    if (tab === "moderation") loadModeration();
  }, [tab, usersPage, search, filterType]);

  const loadStats = async () => {
    setLoading(true);
    try {
      const data = await getDashboardStats();
      setStats(data);
      setError("");
    } catch (e: any) {
      setError(e?.response?.data?.detail || "Erreur de chargement");
    } finally { setLoading(false); }
  };

  const loadUsers = async () => {
    try {
      const params: any = { page: usersPage };
      if (search) params.search = search;
      if (filterType) params.user_type = filterType;
      const data = await getAdminUsers(params);
      setUsers(data.results);
      setUsersTotal(data.total);
    } catch {}
  };

  const loadModeration = async () => {
    try {
      const [queue, alertsData] = await Promise.all([getModerationQueue(), getQualityAlerts()]);
      setModQueue(queue);
      setAlerts(alertsData);
    } catch {}
  };

  const handleSuspend = async () => {
    if (!suspendModal || !justification.trim()) return;
    try {
      await suspendUser(suspendModal.userId, justification);
      setActionMsg(`Compte de ${suspendModal.name} suspendu.`);
      setSuspendModal(null);
      setJustification("");
      loadUsers();
    } catch { setActionMsg("Erreur lors de la suspension."); }
    setTimeout(() => setActionMsg(""), 3000);
  };

  const handleActivate = async (userId: number, name: string) => {
    try {
      await activateUser(userId);
      setActionMsg(`Compte de ${name} réactivé.`);
      loadUsers();
    } catch { setActionMsg("Erreur lors de la réactivation."); }
    setTimeout(() => setActionMsg(""), 3000);
  };

  const handleModerate = async (id: number, action: "approve" | "reject") => {
    try {
      await moderateRating(id, action);
      setActionMsg(action === "approve" ? "Notation approuvée." : "Notation rejetée.");
      loadModeration();
    } catch { setActionMsg("Erreur de modération."); }
    setTimeout(() => setActionMsg(""), 3000);
  };

  if (error) {
    return (
      <div style={{ padding: "4rem 2rem", textAlign: "center" }}>
        <h2 style={{ color: RED }}>Accès refusé</h2>
        <p style={{ color: GRAY }}>{error}</p>
      </div>
    );
  }

  const cardStyle: React.CSSProperties = {
    background: "var(--surface)", borderRadius: "12px", padding: "1.25rem",
    border: "1px solid var(--border)", flex: "1 1 200px", minWidth: "180px"
  };
  const labelStyle: React.CSSProperties = { fontSize: "0.8rem", color: GRAY, marginBottom: "0.25rem" };
  const valueStyle: React.CSSProperties = { fontSize: "1.75rem", fontWeight: 800, color: "var(--text)" };

  return (
    <div style={{ maxWidth: "1200px", margin: "0 auto", padding: "2rem 1.5rem" }}>
      <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", marginBottom: "1.5rem" }}>
        <h1 style={{ fontSize: "1.5rem", fontWeight: 800, margin: 0 }}>Administration Haroo</h1>
        <button onClick={loadStats} style={{ padding: "0.5rem 1rem", borderRadius: "8px", border: "1px solid var(--border)", background: "var(--bg)", cursor: "pointer", color: "var(--text)", fontSize: "0.85rem" }}>
          ↻ Actualiser
        </button>
      </div>

      {actionMsg && (
        <div style={{ padding: "0.75rem 1rem", borderRadius: "8px", background: "rgba(37,99,235,0.08)", color: BLUE, marginBottom: "1rem", fontSize: "0.9rem" }}>
          {actionMsg}
        </div>
      )}

      {/* Tabs */}
      <div style={{ display: "flex", gap: "0.5rem", marginBottom: "1.5rem", borderBottom: "2px solid var(--border)", paddingBottom: "0.5rem" }}>
        {([["overview", "Vue d'ensemble"], ["users", "Utilisateurs"], ["moderation", "Modération"]] as [Tab, string][]).map(([key, label]) => (
          <button key={key} onClick={() => setTab(key)}
            style={{
              padding: "0.5rem 1.25rem", borderRadius: "8px 8px 0 0", border: "none", cursor: "pointer",
              background: tab === key ? BLUE : "transparent", color: tab === key ? "white" : "var(--text)",
              fontWeight: tab === key ? 700 : 500, fontSize: "0.9rem", transition: "all 0.2s"
            }}>{label}</button>
        ))}
      </div>

      {loading && !stats ? (
        <div style={{ textAlign: "center", padding: "3rem", color: GRAY }}>Chargement...</div>
      ) : tab === "overview" && stats ? (
        <OverviewTab stats={stats} cardStyle={cardStyle} labelStyle={labelStyle} valueStyle={valueStyle} />
      ) : tab === "users" ? (
        <UsersTab
          users={users} total={usersTotal} page={usersPage} search={search} filterType={filterType}
          onSearchChange={setSearch} onFilterChange={setFilterType} onPageChange={setUsersPage}
          onSuspend={(id, name) => setSuspendModal({ userId: id, name })}
          onActivate={handleActivate}
        />
      ) : tab === "moderation" ? (
        <ModerationTab queue={modQueue} alerts={alerts} onModerate={handleModerate} />
      ) : null}

      {/* Suspend modal */}
      {suspendModal && (
        <div style={{ position: "fixed", inset: 0, background: "rgba(0,0,0,0.4)", display: "flex", alignItems: "center", justifyContent: "center", zIndex: 1000 }}
          onClick={() => setSuspendModal(null)}>
          <div onClick={e => e.stopPropagation()} style={{ background: "var(--surface)", borderRadius: "12px", padding: "1.5rem", width: "90%", maxWidth: "420px" }}>
            <h3 style={{ margin: "0 0 0.5rem", fontSize: "1rem" }}>Suspendre {suspendModal.name}</h3>
            <p style={{ fontSize: "0.85rem", color: GRAY, margin: "0 0 1rem" }}>Une justification est requise pour chaque suspension.</p>
            <textarea value={justification} onChange={e => setJustification(e.target.value)}
              placeholder="Motif de la suspension..."
              style={{ width: "100%", minHeight: "80px", padding: "0.75rem", borderRadius: "8px", border: "1px solid var(--border)", background: "var(--bg)", color: "var(--text)", resize: "vertical" }} />
            <div style={{ display: "flex", gap: "0.75rem", marginTop: "1rem", justifyContent: "flex-end" }}>
              <button onClick={() => { setSuspendModal(null); setJustification(""); }}
                style={{ padding: "0.5rem 1rem", borderRadius: "8px", border: "1px solid var(--border)", background: "var(--bg)", color: "var(--text)", cursor: "pointer" }}>Annuler</button>
              <button onClick={handleSuspend} disabled={!justification.trim()}
                style={{ padding: "0.5rem 1rem", borderRadius: "8px", border: "none", background: RED, color: "white", cursor: "pointer", fontWeight: 600, opacity: justification.trim() ? 1 : 0.5 }}>Suspendre</button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}


/* ─── Overview Tab ─── */
function OverviewTab({ stats, cardStyle, labelStyle, valueStyle }: {
  stats: DashboardStats; cardStyle: React.CSSProperties; labelStyle: React.CSSProperties; valueStyle: React.CSSProperties;
}) {
  const maxSignups = Math.max(...(stats.utilisateurs.inscriptions_quotidiennes.map(d => d.count) || [1]), 1);

  return (
    <div>
      {/* KPI Cards */}
      <div style={{ display: "flex", flexWrap: "wrap", gap: "1rem", marginBottom: "1.5rem" }}>
        <div style={cardStyle}>
          <div style={labelStyle}>Utilisateurs totaux</div>
          <div style={valueStyle}>{stats.utilisateurs.total}</div>
          <div style={{ fontSize: "0.8rem", color: GREEN }}>+{stats.utilisateurs.nouveaux_7j} cette semaine</div>
        </div>
        <div style={cardStyle}>
          <div style={labelStyle}>Missions</div>
          <div style={valueStyle}>{stats.missions.total ?? 0}</div>
          <div style={{ fontSize: "0.8rem", color: BLUE }}>{stats.missions.en_cours ?? 0} en cours</div>
        </div>
        <div style={cardStyle}>
          <div style={labelStyle}>Emplois</div>
          <div style={valueStyle}>{stats.emplois.total ?? 0}</div>
          <div style={{ fontSize: "0.8rem", color: BLUE }}>{stats.emplois.publiees ?? 0} publiées</div>
        </div>
        <div style={cardStyle}>
          <div style={labelStyle}>Préventes</div>
          <div style={valueStyle}>{stats.preventes.total ?? 0}</div>
          <div style={{ fontSize: "0.8rem", color: GREEN }}>{stats.preventes.actives ?? 0} actives</div>
        </div>
        <div style={cardStyle}>
          <div style={labelStyle}>Volume paiements</div>
          <div style={valueStyle}>{((stats.paiements.volume_total ?? 0) / 1000).toFixed(0)}k</div>
          <div style={{ fontSize: "0.8rem", color: GRAY }}>{stats.paiements.completed ?? 0} transactions</div>
        </div>
      </div>

      {/* Alerts row */}
      <div style={{ display: "flex", flexWrap: "wrap", gap: "1rem", marginBottom: "1.5rem" }}>
        {(stats.moderation.signalees ?? 0) > 0 && (
          <div style={{ ...cardStyle, borderColor: ORANGE, background: "rgba(245,158,11,0.05)" }}>
            <div style={{ fontSize: "0.85rem", fontWeight: 700, color: ORANGE }}>⚠ {stats.moderation.signalees} notation(s) signalée(s)</div>
            <div style={{ fontSize: "0.8rem", color: GRAY, marginTop: "0.25rem" }}>À modérer dans l'onglet Modération</div>
          </div>
        )}
        {(stats.messagerie.messages_signales ?? 0) > 0 && (
          <div style={{ ...cardStyle, borderColor: RED, background: "rgba(239,68,68,0.05)" }}>
            <div style={{ fontSize: "0.85rem", fontWeight: 700, color: RED }}>⚑ {stats.messagerie.messages_signales} message(s) signalé(s)</div>
          </div>
        )}
      </div>

      {/* Users by type */}
      <div style={{ ...cardStyle, marginBottom: "1.5rem", flex: "unset" }}>
        <div style={{ fontWeight: 700, marginBottom: "1rem", fontSize: "0.95rem" }}>Répartition des utilisateurs</div>
        <div style={{ display: "flex", flexWrap: "wrap", gap: "1rem" }}>
          {Object.entries(stats.utilisateurs.par_type).map(([type, count]) => (
            <div key={type} style={{ textAlign: "center", minWidth: "80px" }}>
              <div style={{ fontSize: "1.25rem", fontWeight: 800 }}>{count}</div>
              <div style={{ fontSize: "0.75rem", color: GRAY }}>{USER_TYPE_LABELS[type] || type}</div>
            </div>
          ))}
        </div>
      </div>

      {/* Signups chart (simple bar chart) */}
      {stats.utilisateurs.inscriptions_quotidiennes.length > 0 && (
        <div style={{ ...cardStyle, flex: "unset" }}>
          <div style={{ fontWeight: 700, marginBottom: "1rem", fontSize: "0.95rem" }}>Inscriptions (30 derniers jours)</div>
          <div style={{ display: "flex", alignItems: "flex-end", gap: "3px", height: "120px" }}>
            {stats.utilisateurs.inscriptions_quotidiennes.map((d, i) => (
              <div key={i} style={{ flex: 1, display: "flex", flexDirection: "column", alignItems: "center", justifyContent: "flex-end", height: "100%" }}
                title={`${d.date}: ${d.count} inscription(s)`}>
                <div style={{
                  width: "100%", maxWidth: "20px", borderRadius: "3px 3px 0 0",
                  background: BLUE, opacity: 0.7 + (d.count / maxSignups) * 0.3,
                  height: `${Math.max((d.count / maxSignups) * 100, 4)}%`,
                  transition: "height 0.3s"
                }} />
              </div>
            ))}
          </div>
          <div style={{ display: "flex", justifyContent: "space-between", marginTop: "0.5rem", fontSize: "0.7rem", color: GRAY }}>
            <span>{stats.utilisateurs.inscriptions_quotidiennes[0]?.date}</span>
            <span>{stats.utilisateurs.inscriptions_quotidiennes[stats.utilisateurs.inscriptions_quotidiennes.length - 1]?.date}</span>
          </div>
        </div>
      )}
    </div>
  );
}

/* ─── Users Tab ─── */
function UsersTab({ users, total, page, search, filterType, onSearchChange, onFilterChange, onPageChange, onSuspend, onActivate }: {
  users: AdminUser[]; total: number; page: number; search: string; filterType: string;
  onSearchChange: (v: string) => void; onFilterChange: (v: string) => void; onPageChange: (v: number) => void;
  onSuspend: (id: number, name: string) => void; onActivate: (id: number, name: string) => void;
}) {
  return (
    <div>
      <div style={{ display: "flex", gap: "0.75rem", marginBottom: "1rem", flexWrap: "wrap" }}>
        <input value={search} onChange={e => { onSearchChange(e.target.value); onPageChange(1); }}
          placeholder="Rechercher (nom, email, téléphone)..."
          style={{ flex: "1 1 250px", padding: "0.6rem 1rem", borderRadius: "8px", border: "1px solid var(--border)", background: "var(--bg)", color: "var(--text)" }} />
        <select value={filterType} onChange={e => { onFilterChange(e.target.value); onPageChange(1); }}
          style={{ padding: "0.6rem 1rem", borderRadius: "8px", border: "1px solid var(--border)", background: "var(--bg)", color: "var(--text)" }}>
          <option value="">Tous les types</option>
          {Object.entries(USER_TYPE_LABELS).filter(([k]) => k).map(([k, v]) => (
            <option key={k} value={k}>{v}</option>
          ))}
        </select>
      </div>

      <div style={{ fontSize: "0.85rem", color: GRAY, marginBottom: "0.75rem" }}>{total} utilisateur(s)</div>

      <div style={{ overflowX: "auto" }}>
        <table style={{ width: "100%", borderCollapse: "collapse", fontSize: "0.85rem" }}>
          <thead>
            <tr style={{ borderBottom: "2px solid var(--border)", textAlign: "left" }}>
              <th style={{ padding: "0.5rem" }}>Nom</th>
              <th style={{ padding: "0.5rem" }}>Email</th>
              <th style={{ padding: "0.5rem" }}>Téléphone</th>
              <th style={{ padding: "0.5rem" }}>Type</th>
              <th style={{ padding: "0.5rem" }}>Statut</th>
              <th style={{ padding: "0.5rem" }}>Inscrit le</th>
              <th style={{ padding: "0.5rem" }}>Actions</th>
            </tr>
          </thead>
          <tbody>
            {users.map(u => (
              <tr key={u.id} style={{ borderBottom: "1px solid var(--border)" }}>
                <td style={{ padding: "0.5rem" }}>{u.first_name} {u.last_name}</td>
                <td style={{ padding: "0.5rem" }}>{u.email}</td>
                <td style={{ padding: "0.5rem" }}>{u.phone_number}</td>
                <td style={{ padding: "0.5rem" }}>
                  <span style={{ padding: "0.15rem 0.5rem", borderRadius: "4px", background: "rgba(37,99,235,0.08)", fontSize: "0.8rem" }}>
                    {USER_TYPE_LABELS[u.user_type] || u.user_type}
                  </span>
                </td>
                <td style={{ padding: "0.5rem" }}>
                  <span style={{ color: u.is_active ? GREEN : RED, fontWeight: 600 }}>
                    {u.is_active ? "Actif" : "Suspendu"}
                  </span>
                </td>
                <td style={{ padding: "0.5rem", color: GRAY }}>{new Date(u.date_joined).toLocaleDateString()}</td>
                <td style={{ padding: "0.5rem" }}>
                  {u.is_active ? (
                    <button onClick={() => onSuspend(u.id, `${u.first_name} ${u.last_name}`)}
                      style={{ padding: "0.25rem 0.75rem", borderRadius: "6px", border: `1px solid ${RED}`, background: "transparent", color: RED, cursor: "pointer", fontSize: "0.8rem" }}>
                      Suspendre
                    </button>
                  ) : (
                    <button onClick={() => onActivate(u.id, `${u.first_name} ${u.last_name}`)}
                      style={{ padding: "0.25rem 0.75rem", borderRadius: "6px", border: `1px solid ${GREEN}`, background: "transparent", color: GREEN, cursor: "pointer", fontSize: "0.8rem" }}>
                      Réactiver
                    </button>
                  )}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {total > 50 && (
        <div style={{ display: "flex", justifyContent: "center", gap: "0.5rem", marginTop: "1rem" }}>
          <button disabled={page <= 1} onClick={() => onPageChange(page - 1)}
            style={{ padding: "0.4rem 0.8rem", borderRadius: "6px", border: "1px solid var(--border)", background: "var(--bg)", cursor: page > 1 ? "pointer" : "default", opacity: page > 1 ? 1 : 0.5 }}>← Précédent</button>
          <span style={{ padding: "0.4rem 0.8rem", fontSize: "0.85rem", color: GRAY }}>Page {page} / {Math.ceil(total / 50)}</span>
          <button disabled={page * 50 >= total} onClick={() => onPageChange(page + 1)}
            style={{ padding: "0.4rem 0.8rem", borderRadius: "6px", border: "1px solid var(--border)", background: "var(--bg)", cursor: page * 50 < total ? "pointer" : "default", opacity: page * 50 < total ? 1 : 0.5 }}>Suivant →</button>
        </div>
      )}
    </div>
  );
}

/* ─── Moderation Tab ─── */
function ModerationTab({ queue, alerts, onModerate }: {
  queue: any[]; alerts: any[]; onModerate: (id: number, action: "approve" | "reject") => void;
}) {
  return (
    <div>
      {/* Quality alerts */}
      {alerts.length > 0 && (
        <div style={{ marginBottom: "1.5rem" }}>
          <h3 style={{ fontSize: "1rem", fontWeight: 700, marginBottom: "0.75rem", color: ORANGE }}>⚠ Alertes qualité</h3>
          <div style={{ display: "flex", flexWrap: "wrap", gap: "0.75rem" }}>
            {alerts.map((a: any, i: number) => (
              <div key={i} style={{ padding: "0.75rem 1rem", borderRadius: "8px", border: `1px solid ${ORANGE}`, background: "rgba(245,158,11,0.05)", fontSize: "0.85rem" }}>
                <div style={{ fontWeight: 700 }}>{a.user_name}</div>
                <div style={{ color: GRAY }}>Type: {a.type} — Note: {a.note_moyenne}/5 ({a.nombre_avis} avis)</div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Moderation queue */}
      <h3 style={{ fontSize: "1rem", fontWeight: 700, marginBottom: "0.75rem" }}>File de modération ({queue.length})</h3>
      {queue.length === 0 ? (
        <div style={{ padding: "2rem", textAlign: "center", color: GRAY, background: "var(--surface)", borderRadius: "12px", border: "1px solid var(--border)" }}>
          Aucune notation à modérer. Tout est en ordre.
        </div>
      ) : (
        <div style={{ display: "flex", flexDirection: "column", gap: "0.75rem" }}>
          {queue.map((n: any) => (
            <div key={n.id} style={{ padding: "1rem", borderRadius: "10px", border: "1px solid var(--border)", background: "var(--surface)" }}>
              <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", gap: "1rem", flexWrap: "wrap" }}>
                <div style={{ flex: 1 }}>
                  <div style={{ fontWeight: 700, fontSize: "0.9rem" }}>
                    {n.notateur?.first_name} {n.notateur?.last_name} → {n.note?.first_name} {n.note?.last_name}
                  </div>
                  <div style={{ display: "flex", gap: "0.5rem", alignItems: "center", margin: "0.25rem 0" }}>
                    <span style={{ color: ORANGE }}>{"★".repeat(n.note_valeur)}{"☆".repeat(5 - n.note_valeur)}</span>
                    <span style={{ fontSize: "0.8rem", color: RED }}>{n.nombre_signalements} signalement(s)</span>
                  </div>
                  <div style={{ fontSize: "0.85rem", color: "var(--text)", marginTop: "0.25rem" }}>{n.commentaire}</div>
                  <div style={{ fontSize: "0.75rem", color: GRAY, marginTop: "0.25rem" }}>{new Date(n.created_at).toLocaleDateString()}</div>
                </div>
                <div style={{ display: "flex", gap: "0.5rem" }}>
                  <button onClick={() => onModerate(n.id, "approve")}
                    style={{ padding: "0.4rem 1rem", borderRadius: "8px", border: "none", background: GREEN, color: "white", cursor: "pointer", fontWeight: 600, fontSize: "0.85rem" }}>
                    Approuver
                  </button>
                  <button onClick={() => onModerate(n.id, "reject")}
                    style={{ padding: "0.4rem 1rem", borderRadius: "8px", border: "none", background: RED, color: "white", cursor: "pointer", fontWeight: 600, fontSize: "0.85rem" }}>
                    Rejeter
                  </button>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
