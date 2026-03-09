import React, { useEffect, useState, useRef } from "react";
import { useNavigate } from "react-router-dom";
import { motion, AnimatePresence } from "framer-motion";
import { me, updateProfile, changePassword, logout } from "../api/auth";
import { uploadProfilePhoto, validateFile } from "../api/storage";
import { getRegions, getPrefectures, getCantons, Region, Prefecture, Canton } from "../api/locations";
import AcheteurProfileForm from "../components/AcheteurProfileForm";

const IconUser = () => <svg width="20" height="20" viewBox="0 0 20 20" fill="none"><circle cx="10" cy="6" r="4" stroke="currentColor" strokeWidth="1.4"/><path d="M2 18c0-4.4 3.6-8 8-8s8 3.6 8 8" stroke="currentColor" strokeWidth="1.4" strokeLinecap="round"/></svg>;
const IconPhone = () => <svg width="18" height="18" viewBox="0 0 18 18" fill="none"><path d="M3 2.5A1.5 1.5 0 014.5 1h1a2 2 0 012 2v1a2 2 0 01-2 2H4L3 8s1 6 7 7c6-1 7-7 7-7l-1-2h-1.5a2 2 0 01-2-2V3a2 2 0 012-2h1A1.5 1.5 0 0117 2.5" stroke="currentColor" strokeWidth="1.4" strokeLinecap="round"/></svg>;
const IconLock = () => <svg width="18" height="18" viewBox="0 0 18 18" fill="none"><rect x="3" y="8" width="12" height="9" rx="2" stroke="currentColor" strokeWidth="1.4"/><path d="M6 8V6a3 3 0 016 0v2" stroke="currentColor" strokeWidth="1.4" strokeLinecap="round"/><circle cx="9" cy="12.5" r="1.2" fill="currentColor"/></svg>;
const IconEye = ({ open }: { open: boolean }) => open ? (
  <svg width="16" height="16" viewBox="0 0 16 16" fill="none"><path d="M1 8s3-5 7-5 7 5 7 5-3 5-7 5-7-5-7-5z" stroke="currentColor" strokeWidth="1.3"/><circle cx="8" cy="8" r="2" stroke="currentColor" strokeWidth="1.3"/></svg>
) : (
  <svg width="16" height="16" viewBox="0 0 16 16" fill="none"><path d="M1 8s3-5 7-5 7 5 7 5-3 5-7 5-7-5-7-5z" stroke="currentColor" strokeWidth="1.3"/><circle cx="8" cy="8" r="2" stroke="currentColor" strokeWidth="1.3"/><line x1="2" y1="2" x2="14" y2="14" stroke="currentColor" strokeWidth="1.3" strokeLinecap="round"/></svg>
);
const IconCheck = () => <svg width="14" height="14" viewBox="0 0 14 14" fill="none"><path d="M2 7l3.5 3.5L12 3" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/></svg>;
const IconLogout = () => <svg width="18" height="18" viewBox="0 0 18 18" fill="none"><path d="M7 16H3a1 1 0 01-1-1V3a1 1 0 011-1h4" stroke="currentColor" strokeWidth="1.4" strokeLinecap="round"/><path d="M12 13l5-4-5-4M17 9H7" stroke="currentColor" strokeWidth="1.4" strokeLinecap="round" strokeLinejoin="round"/></svg>;
const IconEdit = () => <svg width="16" height="16" viewBox="0 0 16 16" fill="none"><path d="M11 2.5l2.5 2.5L5 13.5H2.5V11L11 2.5z" stroke="currentColor" strokeWidth="1.3" strokeLinejoin="round"/></svg>;
const IconX = () => <svg width="16" height="16" viewBox="0 0 16 16" fill="none"><path d="M3 3l10 10M13 3L3 13" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round"/></svg>;

const USER_TYPE_CONFIG: Record<string, { label: string; color: string }> = {
  EXPLOITANT:  { label: "Exploitant Agricole", color: "#16a34a" },
  AGRONOME:    { label: "Agronome",             color: "#2563eb" },
  OUVRIER:     { label: "Ouvrier Agricole",     color: "#d97706" },
  ACHETEUR:    { label: "Acheteur",             color: "#7c3aed" },
  INSTITUTION: { label: "Institution",          color: "#0e7490" },
};

function getInitials(user: any) {
  const f = user.first_name?.[0] || "";
  const l = user.last_name?.[0] || "";
  return (f + l).toUpperCase() || user.username?.[0]?.toUpperCase() || "?";
}

const inputBase: React.CSSProperties = {
  width: "100%", padding: "0.75rem 1rem", borderRadius: "10px",
  border: "1.5px solid var(--border)", background: "var(--bg)",
  color: "var(--text)", fontSize: "0.95rem", outline: "none",
  transition: "border-color 0.2s, box-shadow 0.2s", boxSizing: "border-box",
};

function Field({ label, children }: { label: string; children: React.ReactNode }) {
  return (
    <div>
      <label style={{ display: "block", fontSize: "0.75rem", fontWeight: 700, color: "var(--text-secondary)", textTransform: "uppercase", letterSpacing: "0.06em", marginBottom: "0.4rem" }}>
        {label}
      </label>
      {children}
    </div>
  );
}

const IconMap = () => <svg width="20" height="20" viewBox="0 0 20 20" fill="none"><path d="M10 17s-6-4.35-6-8.5a6 6 0 0112 0C16 12.65 10 17 10 17z" stroke="currentColor" strokeWidth="1.4"/><circle cx="10" cy="8.5" r="2" stroke="currentColor" strokeWidth="1.4"/></svg>;

function ExploitationSection({ user, onUpdate }: { user: any; onUpdate: (u: any) => void }) {
  const profile = user.exploitant_profile;
  const [editExploit, setEditExploit] = useState(false);
  const [saving, setSaving] = useState(false);
  const [msg, setMsg] = useState("");
  const [err, setErr] = useState("");

  // Location cascade
  const [regions, setRegions] = useState<Region[]>([]);
  const [prefectures, setPrefectures] = useState<Prefecture[]>([]);
  const [cantons, setCantons] = useState<Canton[]>([]);
  const [selRegion, setSelRegion] = useState<number | "">("");
  const [selPrefecture, setSelPrefecture] = useState<number | "">("");
  const [selCanton, setSelCanton] = useState<number | "">(profile?.canton_principal || "");

  const [superficie, setSuperficie] = useState(profile?.superficie_totale || "");
  const [gpsLat, setGpsLat] = useState(profile?.coordonnees_gps?.lat || "");
  const [gpsLon, setGpsLon] = useState(profile?.coordonnees_gps?.lon || "");
  const [cultures, setCultures] = useState((profile?.cultures_actuelles || []).join(", "));

  useEffect(() => { getRegions().then(setRegions).catch(() => {}); }, []);

  useEffect(() => {
    if (selRegion) {
      getPrefectures({ region: selRegion }).then(setPrefectures).catch(() => {});
      setSelPrefecture(""); setSelCanton(""); setCantons([]);
    }
  }, [selRegion]);

  useEffect(() => {
    if (selPrefecture) {
      getCantons({ prefecture: selPrefecture }).then(setCantons).catch(() => {});
      setSelCanton("");
    }
  }, [selPrefecture]);

  const handleGetGPS = () => {
    if (!navigator.geolocation) { setErr("Géolocalisation non supportée"); return; }
    navigator.geolocation.getCurrentPosition(
      (pos) => { setGpsLat(pos.coords.latitude.toFixed(6)); setGpsLon(pos.coords.longitude.toFixed(6)); },
      () => setErr("Impossible d'obtenir la position GPS"),
      { enableHighAccuracy: true, timeout: 10000 }
    );
  };

  const handleSave = async () => {
    if (!selCanton) { setErr("Veuillez sélectionner un canton"); return; }
    if (!superficie || parseFloat(superficie) <= 0) { setErr("Veuillez renseigner la superficie"); return; }
    setSaving(true); setErr(""); setMsg("");
    try {
      const payload: any = {
        exploitant_profile: {
          canton_principal: Number(selCanton),
          superficie_totale: parseFloat(superficie),
          cultures_actuelles: cultures.split(",").map((c: string) => c.trim()).filter(Boolean),
        }
      };
      if (gpsLat && gpsLon) {
        payload.exploitant_profile.coordonnees_gps = { lat: parseFloat(gpsLat), lon: parseFloat(gpsLon) };
      }
      const res = await updateProfile(payload);
      onUpdate(res.user || { ...user, exploitant_profile: { ...profile, ...payload.exploitant_profile } });
      setMsg("Profil d'exploitation mis à jour");
      setEditExploit(false);
      setTimeout(() => setMsg(""), 3000);
    } catch (ex: any) {
      setErr(ex?.response?.data?.detail || ex?.response?.data?.exploitant_profile?.canton_principal?.[0] || "Erreur lors de la mise à jour");
    } finally { setSaving(false); }
  };

  const isComplete = profile && profile.canton_principal && parseFloat(profile.superficie_totale) > 0;
  const statusColor = isComplete ? "#16a34a" : "#d97706";
  const statusLabel = isComplete ? "Profil complet" : "À compléter";
  const verificationLabels: Record<string, { label: string; color: string }> = {
    NON_VERIFIE: { label: "Non vérifié", color: "#d97706" },
    EN_ATTENTE: { label: "En attente", color: "#2563eb" },
    VERIFIE: { label: "Vérifié", color: "#16a34a" },
    REJETE: { label: "Rejeté", color: "#dc2626" },
  };
  const verif = verificationLabels[profile?.statut_verification] || verificationLabels.NON_VERIFIE;

  return (
    <div style={{ background: "var(--surface)", border: `1.5px solid ${isComplete ? "var(--border)" : "#d9770640"}`, borderRadius: "16px", padding: "1.5rem", marginBottom: "1rem" }}>
      <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", marginBottom: "1.25rem" }}>
        <div style={{ display: "flex", alignItems: "center", gap: "0.5rem" }}>
          <div style={{ color: "var(--text-muted)" }}><IconMap /></div>
          <span style={{ fontWeight: 700, color: "var(--text)", fontSize: "0.92rem" }}>Mon exploitation</span>
          <span style={{ background: `${statusColor}15`, color: statusColor, padding: "0.15rem 0.55rem", borderRadius: "100px", fontSize: "0.72rem", fontWeight: 700 }}>{statusLabel}</span>
        </div>
        <button onClick={() => setEditExploit(!editExploit)}
          style={{ padding: "0.4rem 0.8rem", borderRadius: "8px", border: "1px solid var(--border)", background: editExploit ? "var(--bg)" : "var(--primary)", color: editExploit ? "var(--text-secondary)" : "white", fontWeight: 600, fontSize: "0.8rem", cursor: "pointer" }}>
          {editExploit ? "Annuler" : "Modifier"}
        </button>
      </div>

      {msg && <div style={{ padding: "0.6rem 0.8rem", background: "#f0fdf4", border: "1px solid #bbf7d0", borderRadius: "8px", color: "#16a34a", fontSize: "0.85rem", fontWeight: 600, marginBottom: "0.75rem" }}>{msg}</div>}
      {err && <div style={{ padding: "0.6rem 0.8rem", background: "rgba(239,68,68,0.08)", border: "1px solid rgba(239,68,68,0.2)", borderRadius: "8px", color: "#ef4444", fontSize: "0.85rem", fontWeight: 500, marginBottom: "0.75rem" }}>{err}</div>}

      {!isComplete && !editExploit && (
        <div style={{ padding: "0.8rem 1rem", background: "#fffbeb", border: "1px solid #fde68a", borderRadius: "10px", marginBottom: "1rem", fontSize: "0.85rem", color: "#92400e", lineHeight: 1.5 }}>
          ⚠️ Veuillez compléter votre profil d'exploitation (canton, superficie) pour pouvoir publier des offres d'emploi ou accéder aux marchés de proximité.
        </div>
      )}

      {!editExploit ? (
        <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "0.75rem" }}>
          {[
            ["Superficie", profile?.superficie_totale ? `${parseFloat(profile.superficie_totale).toFixed(1)} ha` : "—"],
            ["Canton", profile?.canton_principal_nom || "—"],
            ["Vérification", verif.label],
            ["GPS", profile?.coordonnees_gps?.lat ? `${parseFloat(profile.coordonnees_gps.lat).toFixed(4)}, ${parseFloat(profile.coordonnees_gps.lon).toFixed(4)}` : "—"],
            ["Cultures", (profile?.cultures_actuelles || []).join(", ") || "—"],
          ].map(([k, v], i) => (
            <div key={k} style={{ padding: "0.75rem", background: "var(--bg)", borderRadius: "10px", gridColumn: i === 4 ? "1 / -1" : undefined }}>
              <div style={{ fontSize: "0.7rem", fontWeight: 700, color: "var(--text-muted)", textTransform: "uppercase", letterSpacing: "0.05em", marginBottom: "0.25rem" }}>{k}</div>
              <div style={{ fontWeight: 600, color: k === "Vérification" ? verif.color : "var(--text)", fontSize: "0.88rem" }}>{v}</div>
            </div>
          ))}
        </div>
      ) : (
        <div style={{ display: "flex", flexDirection: "column", gap: "0.85rem" }}>
          <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr 1fr", gap: "0.75rem" }}>
            <Field label="Région">
              <select value={selRegion} onChange={e => setSelRegion(e.target.value ? Number(e.target.value) : "")} style={inputBase}>
                <option value="">— Choisir —</option>
                {regions.map(r => <option key={r.id} value={r.id}>{r.nom}</option>)}
              </select>
            </Field>
            <Field label="Préfecture">
              <select value={selPrefecture} onChange={e => setSelPrefecture(e.target.value ? Number(e.target.value) : "")} style={inputBase} disabled={!selRegion}>
                <option value="">— Choisir —</option>
                {prefectures.map(p => <option key={p.id} value={p.id}>{p.nom}</option>)}
              </select>
            </Field>
            <Field label="Canton">
              <select value={selCanton} onChange={e => setSelCanton(e.target.value ? Number(e.target.value) : "")} style={inputBase} disabled={!selPrefecture}>
                <option value="">— Choisir —</option>
                {cantons.map(c => <option key={c.id} value={c.id}>{c.nom}</option>)}
              </select>
            </Field>
          </div>
          <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr 1fr", gap: "0.75rem" }}>
            <Field label="Superficie (ha)">
              <input type="number" step="0.1" min="0.01" value={superficie} onChange={e => setSuperficie(e.target.value)} style={inputBase} placeholder="Ex: 5.5" />
            </Field>
            <Field label="Latitude GPS">
              <input type="number" step="0.0001" value={gpsLat} onChange={e => setGpsLat(e.target.value)} style={inputBase} placeholder="Ex: 6.1725" />
            </Field>
            <Field label="Longitude GPS">
              <input type="number" step="0.0001" value={gpsLon} onChange={e => setGpsLon(e.target.value)} style={inputBase} placeholder="Ex: 1.2314" />
            </Field>
          </div>
          <div style={{ display: "flex", gap: "0.75rem", alignItems: "flex-end" }}>
            <div style={{ flex: 1 }}>
              <Field label="Cultures actuelles (séparées par des virgules)">
                <input value={cultures} onChange={e => setCultures(e.target.value)} style={inputBase} placeholder="Maïs, Soja, Riz..." />
              </Field>
            </div>
            <button type="button" onClick={handleGetGPS}
              style={{ padding: "0.75rem 1rem", borderRadius: "10px", border: "1px solid var(--border)", background: "var(--bg)", color: "var(--text)", fontWeight: 600, fontSize: "0.82rem", cursor: "pointer", whiteSpace: "nowrap" }}>
              📍 Ma position
            </button>
          </div>
          <button onClick={handleSave} disabled={saving}
            style={{ padding: "0.8rem", background: "var(--primary)", color: "white", border: "none", borderRadius: "10px", fontWeight: 700, fontSize: "0.95rem", cursor: saving ? "not-allowed" : "pointer", opacity: saving ? 0.8 : 1 }}>
            {saving ? "Enregistrement..." : "Enregistrer l'exploitation"}
          </button>
        </div>
      )}
    </div>
  );
}

export default function Profile() {
  const [user, setUser] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const navigate = useNavigate();

  // Edit form
  const [editing, setEditing] = useState(false);
  const [form, setForm] = useState({ first_name: "", last_name: "", username: "", email: "" });
  const [saving, setSaving] = useState(false);
  const [saveMsg, setSaveMsg] = useState("");
  const [saveErr, setSaveErr] = useState("");

  // Change password modal
  const [showPwdModal, setShowPwdModal] = useState(false);
  const [pwd, setPwd] = useState({ old: "", new: "", confirm: "" });
  const [showOld, setShowOld] = useState(false);
  const [showNew, setShowNew] = useState(false);
  const [pwdSaving, setPwdSaving] = useState(false);
  const [pwdMsg, setPwdMsg] = useState("");
  const [pwdErr, setPwdErr] = useState("");

  // Photo upload
  const fileInputRef = useRef<HTMLInputElement>(null);
  const [photoUrl, setPhotoUrl] = useState<string>("");
  const [photoUploading, setPhotoUploading] = useState(false);

  async function handlePhotoUpload(e: React.ChangeEvent<HTMLInputElement>) {
    const file = e.target.files?.[0];
    if (!file) return;
    const err = validateFile(file, 'image');
    if (err) { setSaveErr(err); return; }
    setPhotoUploading(true); setSaveErr("");
    try {
      const url = await uploadProfilePhoto(file, user?.id || 'anon');
      setPhotoUrl(url);
      setSaveMsg("Photo de profil mise à jour");
      setTimeout(() => setSaveMsg(""), 3000);
    } catch (ex: any) {
      setSaveErr(ex?.message || "Erreur upload photo");
    } finally { setPhotoUploading(false); }
  }

  useEffect(() => {
    me()
      .then((u) => { setUser(u); setForm({ first_name: u.first_name, last_name: u.last_name, username: u.username, email: u.email }); })
      .catch(() => { logout(); navigate("/login"); })
      .finally(() => setLoading(false));
  }, [navigate]);

  async function handleSave(e: React.FormEvent) {
    e.preventDefault();
    setSaving(true); setSaveErr(""); setSaveMsg("");
    try {
      const res = await updateProfile(form);
      setUser(res.user || { ...user, ...form });
      setSaveMsg("Profil mis à jour avec succès");
      setEditing(false);
      setTimeout(() => setSaveMsg(""), 3000);
    } catch (err: any) {
      const d = err?.response?.data;
      setSaveErr(d?.detail || d?.username?.[0] || d?.email?.[0] || "Erreur lors de la mise à jour");
    } finally { setSaving(false); }
  }

  async function handleChangePassword(e: React.FormEvent) {
    e.preventDefault();
    if (pwd.new !== pwd.confirm) { setPwdErr("Les mots de passe ne correspondent pas"); return; }
    setPwdSaving(true); setPwdErr(""); setPwdMsg("");
    try {
      await changePassword(pwd.old, pwd.new, pwd.confirm);
      setPwdMsg("Mot de passe modifié avec succès");
      setPwd({ old: "", new: "", confirm: "" });
      setTimeout(() => { setPwdMsg(""); setShowPwdModal(false); }, 2000);
    } catch (err: any) {
      const d = err?.response?.data;
      setPwdErr(d?.detail || d?.old_password?.[0] || d?.new_password?.[0] || "Erreur lors du changement de mot de passe");
    } finally { setPwdSaving(false); }
  }

  if (loading) {
    return (
      <div style={{ minHeight: "100vh", display: "flex", alignItems: "center", justifyContent: "center", background: "var(--bg)" }}>
        <motion.div animate={{ rotate: 360 }} transition={{ duration: 0.8, repeat: Infinity, ease: "linear" }}
          style={{ width: 32, height: 32, border: "3px solid var(--border)", borderTop: "3px solid var(--primary)", borderRadius: "50%" }} />
      </div>
    );
  }

  if (!user) return null;

  const typeConf = USER_TYPE_CONFIG[user.user_type] || { label: user.user_type, color: "#6366f1" };

  return (
    <div style={{ minHeight: "100vh", background: "var(--bg)", paddingTop: "5rem" }}>
      <div style={{ maxWidth: 700, margin: "0 auto", padding: "2rem 1.5rem" }}>

        {/* ── Header card ── */}
        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.45 }}
          style={{ background: "var(--surface)", border: "1px solid var(--border)", borderRadius: "20px", padding: "2rem", marginBottom: "1.25rem", display: "flex", alignItems: "center", gap: "1.5rem" }}>
          <div
            onClick={() => fileInputRef.current?.click()}
            style={{ width: 70, height: 70, borderRadius: "50%", background: `${typeConf.color}18`, border: `2px solid ${typeConf.color}40`, display: "flex", alignItems: "center", justifyContent: "center", flexShrink: 0, cursor: "pointer", position: "relative", overflow: "hidden" }}
            title="Changer la photo de profil"
          >
            {photoUrl ? (
              <img src={photoUrl} alt="Photo de profil" style={{ width: "100%", height: "100%", objectFit: "cover", borderRadius: "50%" }} />
            ) : (
              <span style={{ color: typeConf.color, fontWeight: 800, fontSize: "1.6rem", letterSpacing: "-0.02em" }}>{getInitials(user)}</span>
            )}
            {photoUploading && (
              <div style={{ position: "absolute", inset: 0, background: "rgba(0,0,0,0.4)", display: "flex", alignItems: "center", justifyContent: "center", borderRadius: "50%" }}>
                <motion.div animate={{ rotate: 360 }} transition={{ duration: 0.8, repeat: Infinity, ease: "linear" }}
                  style={{ width: 20, height: 20, border: "2px solid #fff4", borderTop: "2px solid #fff", borderRadius: "50%" }} />
              </div>
            )}
            <input ref={fileInputRef} type="file" accept="image/jpeg,image/png" onChange={handlePhotoUpload} style={{ display: "none" }} />
          </div>
          <div style={{ flex: 1 }}>
            <h1 style={{ margin: "0 0 0.25rem", fontSize: "1.4rem", fontWeight: 800, color: "var(--text)", letterSpacing: "-0.02em" }}>
              {user.first_name ? `${user.first_name} ${user.last_name}` : user.username}
            </h1>
            <div style={{ display: "flex", flexWrap: "wrap", gap: "0.5rem", alignItems: "center" }}>
              <span style={{ background: `${typeConf.color}15`, color: typeConf.color, padding: "0.2rem 0.65rem", borderRadius: "100px", fontSize: "0.78rem", fontWeight: 700 }}>
                {typeConf.label}
              </span>
              <span style={{ color: "var(--text-muted)", fontSize: "0.82rem" }}>{user.phone_number}</span>
              {user.phone_verified && (
                <span style={{ display: "flex", alignItems: "center", gap: "4px", background: "#dcfce7", color: "#16a34a", padding: "0.15rem 0.55rem", borderRadius: "100px", fontSize: "0.75rem", fontWeight: 600 }}>
                  <IconCheck /> Vérifié
                </span>
              )}
            </div>
          </div>
          <motion.button whileHover={{ scale: 1.04 }} whileTap={{ scale: 0.96 }}
            onClick={() => setEditing(!editing)}
            style={{ display: "flex", alignItems: "center", gap: "0.4rem", padding: "0.55rem 1rem", background: editing ? "var(--bg)" : "var(--primary)", color: editing ? "var(--text-secondary)" : "white", border: editing ? "1.5px solid var(--border)" : "none", borderRadius: "10px", fontWeight: 600, fontSize: "0.85rem", cursor: "pointer" }}>
            <IconEdit /> {editing ? "Annuler" : "Modifier"}
          </motion.button>
        </motion.div>

        {/* success/error global */}
        <AnimatePresence>
          {saveMsg && (
            <motion.div initial={{ opacity: 0, y: -8 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0 }}
              style={{ display: "flex", alignItems: "center", gap: "0.5rem", padding: "0.75rem 1rem", background: "#f0fdf4", border: "1.5px solid #bbf7d0", borderRadius: "10px", marginBottom: "1rem", color: "#16a34a", fontWeight: 600, fontSize: "0.88rem" }}>
              <IconCheck /> {saveMsg}
            </motion.div>
          )}
        </AnimatePresence>

        {/* ── Edit Form ── */}
        <AnimatePresence>
          {editing && (
            <motion.div initial={{ opacity: 0, height: 0 }} animate={{ opacity: 1, height: "auto" }} exit={{ opacity: 0, height: 0 }}
              style={{ background: "var(--surface)", border: "1.5px solid var(--primary)", borderRadius: "16px", padding: "1.75rem", marginBottom: "1.25rem", overflow: "hidden" }}>
              <div style={{ fontWeight: 700, color: "var(--text)", marginBottom: "1.25rem", fontSize: "0.95rem" }}>Modifier le profil</div>
              <form onSubmit={handleSave} style={{ display: "flex", flexDirection: "column", gap: "1rem" }}>
                <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "1rem" }}>
                  <Field label="Prénom">
                    <input value={form.first_name} onChange={e => setForm(f => ({ ...f, first_name: e.target.value }))} style={inputBase}
                      onFocus={e => { e.target.style.borderColor = "var(--primary)"; e.target.style.boxShadow = "0 0 0 3px rgba(22,163,74,0.12)"; }}
                      onBlur={e => { e.target.style.borderColor = "var(--border)"; e.target.style.boxShadow = "none"; }} />
                  </Field>
                  <Field label="Nom">
                    <input value={form.last_name} onChange={e => setForm(f => ({ ...f, last_name: e.target.value }))} style={inputBase}
                      onFocus={e => { e.target.style.borderColor = "var(--primary)"; e.target.style.boxShadow = "0 0 0 3px rgba(22,163,74,0.12)"; }}
                      onBlur={e => { e.target.style.borderColor = "var(--border)"; e.target.style.boxShadow = "none"; }} />
                  </Field>
                </div>
                <Field label="Nom d'utilisateur">
                  <input value={form.username} onChange={e => setForm(f => ({ ...f, username: e.target.value }))} required style={inputBase}
                    onFocus={e => { e.target.style.borderColor = "var(--primary)"; e.target.style.boxShadow = "0 0 0 3px rgba(22,163,74,0.12)"; }}
                    onBlur={e => { e.target.style.borderColor = "var(--border)"; e.target.style.boxShadow = "none"; }} />
                </Field>
                <Field label="Email (optionnel)">
                  <input type="email" value={form.email} onChange={e => setForm(f => ({ ...f, email: e.target.value }))} style={inputBase}
                    onFocus={e => { e.target.style.borderColor = "var(--primary)"; e.target.style.boxShadow = "0 0 0 3px rgba(22,163,74,0.12)"; }}
                    onBlur={e => { e.target.style.borderColor = "var(--border)"; e.target.style.boxShadow = "none"; }} />
                </Field>
                {saveErr && (
                  <div style={{ color: "#ef4444", fontSize: "0.85rem", fontWeight: 500 }}>{saveErr}</div>
                )}
                <motion.button type="submit" disabled={saving} whileHover={{ scale: 1.01 }} whileTap={{ scale: 0.98 }}
                  style={{ padding: "0.8rem", background: "var(--primary)", color: "white", border: "none", borderRadius: "10px", fontWeight: 700, fontSize: "0.95rem", cursor: saving ? "not-allowed" : "pointer", display: "flex", alignItems: "center", justifyContent: "center", gap: "0.5rem", opacity: saving ? 0.8 : 1 }}>
                  {saving ? (
                    <><motion.div animate={{ rotate: 360 }} transition={{ duration: 0.7, repeat: Infinity, ease: "linear" }}
                      style={{ width: 16, height: 16, border: "2px solid rgba(255,255,255,0.4)", borderTop: "2px solid white", borderRadius: "50%" }} />
                    Enregistrement...</>
                  ) : "Enregistrer les modifications"}
                </motion.button>
              </form>
            </motion.div>
          )}
        </AnimatePresence>

        {/* ── Info sections ── */}
        <motion.div initial={{ opacity: 0, y: 16 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.1 }}
          style={{ display: "flex", flexDirection: "column", gap: "1rem" }}>

          {/* Personal info */}
          <div style={{ background: "var(--surface)", border: "1px solid var(--border)", borderRadius: "16px", padding: "1.5rem" }}>
            <div style={{ display: "flex", alignItems: "center", gap: "0.5rem", marginBottom: "1.25rem" }}>
              <div style={{ color: "var(--text-muted)" }}><IconUser /></div>
              <span style={{ fontWeight: 700, color: "var(--text)", fontSize: "0.92rem" }}>Informations personnelles</span>
            </div>
            <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "0.75rem" }}>
              {[
                ["Prénom", user.first_name || "—"],
                ["Nom", user.last_name || "—"],
                ["Nom d'utilisateur", user.username],
                ["Email", user.email || "Non renseigné"],
              ].map(([k, v]) => (
                <div key={k} style={{ padding: "0.75rem", background: "var(--bg)", borderRadius: "10px" }}>
                  <div style={{ fontSize: "0.7rem", fontWeight: 700, color: "var(--text-muted)", textTransform: "uppercase", letterSpacing: "0.05em", marginBottom: "0.25rem" }}>{k}</div>
                  <div style={{ fontWeight: 600, color: "var(--text)", fontSize: "0.88rem" }}>{v}</div>
                </div>
              ))}
            </div>
          </div>

          {/* Contact */}
          <div style={{ background: "var(--surface)", border: "1px solid var(--border)", borderRadius: "16px", padding: "1.5rem" }}>
            <div style={{ display: "flex", alignItems: "center", gap: "0.5rem", marginBottom: "1.25rem" }}>
              <div style={{ color: "var(--text-muted)" }}><IconPhone /></div>
              <span style={{ fontWeight: 700, color: "var(--text)", fontSize: "0.92rem" }}>Contact & vérification</span>
            </div>
            <div style={{ display: "flex", flexDirection: "column", gap: "0.75rem" }}>
              <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", padding: "0.85rem 1rem", background: "var(--bg)", borderRadius: "10px" }}>
                <div>
                  <div style={{ fontSize: "0.7rem", fontWeight: 700, color: "var(--text-muted)", textTransform: "uppercase", letterSpacing: "0.05em", marginBottom: "0.2rem" }}>Téléphone</div>
                  <div style={{ fontWeight: 600, color: "var(--text)", fontSize: "0.9rem" }}>{user.phone_number}</div>
                </div>
                <span style={{ padding: "0.2rem 0.7rem", borderRadius: "100px", fontSize: "0.75rem", fontWeight: 600, background: user.phone_verified ? "#dcfce7" : "#fef3c7", color: user.phone_verified ? "#16a34a" : "#92400e" }}>
                  {user.phone_verified ? "Vérifié" : "Non vérifié"}
                </span>
              </div>
            </div>
          </div>

          {/* ── Exploitation Profile (EXPLOITANT only) ── */}
          {user.user_type === 'EXPLOITANT' && <ExploitationSection user={user} onUpdate={(u: any) => setUser(u)} />}

          {/* ── Acheteur Profile (ACHETEUR only) ── */}
          {user.user_type === 'ACHETEUR' && (
            <motion.div initial={{ opacity: 0, y: 16 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.15 }}
              style={{ background: "var(--surface)", border: "1px solid var(--border)", borderRadius: "16px", padding: "1.5rem" }}>
              <div style={{ display: "flex", alignItems: "center", gap: "0.5rem", marginBottom: "1.25rem" }}>
                <div style={{ color: "var(--text-muted)" }}><IconMap /></div>
                <span style={{ fontWeight: 700, color: "var(--text)", fontSize: "0.92rem" }}>Profil Acheteur</span>
                {user.acheteur_profile?.profil_complet && (
                  <span style={{ background: "#dcfce7", color: "#16a34a", padding: "0.15rem 0.55rem", borderRadius: "100px", fontSize: "0.72rem", fontWeight: 700 }}>Complet</span>
                )}
              </div>
              <AcheteurProfileForm 
                profile={user.acheteur_profile}
                onSave={async (data) => {
                  console.log('Données à sauvegarder:', data);
                  setSaving(true);
                  setSaveErr("");
                  setSaveMsg("");
                  try {
                    const res = await updateProfile({ acheteur_profile: data });
                    console.log('Réponse de mise à jour:', res);
                    setUser(res.user || { ...user, acheteur_profile: { ...user.acheteur_profile, ...data, profil_complet: true } });
                    setSaveMsg("Profil acheteur mis à jour avec succès");
                  } catch (err: any) {
                    console.error('Erreur de mise à jour:', err);
                    const d = err?.response?.data;
                    const errorMsg = d?.detail || d?.acheteur_profile?.region?.[0] || d?.acheteur_profile?.prefecture?.[0] || d?.acheteur_profile?.canton?.[0] || "Erreur lors de la mise à jour du profil";
                    setSaveErr(errorMsg);
                    console.error('Message d\'erreur:', errorMsg);
                  } finally {
                    setSaving(false);
                  }
                }}
                isSaving={saving}
                saveError={saveErr}
                saveSuccess={saveMsg}
              />
            </motion.div>
          )}

          {/* Security */}
          <div style={{ background: "var(--surface)", border: "1px solid var(--border)", borderRadius: "16px", padding: "1.5rem" }}>
            <div style={{ display: "flex", alignItems: "center", gap: "0.5rem", marginBottom: "1.25rem" }}>
              <div style={{ color: "var(--text-muted)" }}><IconLock /></div>
              <span style={{ fontWeight: 700, color: "var(--text)", fontSize: "0.92rem" }}>Sécurité</span>
            </div>
            <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", padding: "0.85rem 1rem", background: "var(--bg)", borderRadius: "10px", marginBottom: "0.75rem" }}>
              <div>
                <div style={{ fontWeight: 600, color: "var(--text)", fontSize: "0.9rem" }}>Authentification 2FA</div>
                <div style={{ color: "var(--text-muted)", fontSize: "0.78rem" }}>{user.two_factor_enabled ? "Activée" : "Non configurée"}</div>
              </div>
              <span style={{ padding: "0.2rem 0.7rem", borderRadius: "100px", fontSize: "0.75rem", fontWeight: 600, background: user.two_factor_enabled ? "#dcfce7" : "var(--border)", color: user.two_factor_enabled ? "#16a34a" : "var(--text-muted)" }}>
                {user.two_factor_enabled ? "Actif" : "Inactif"}
              </span>
            </div>
            <motion.button whileHover={{ scale: 1.01 }} whileTap={{ scale: 0.98 }}
              onClick={() => { setShowPwdModal(true); setPwd({ old: "", new: "", confirm: "" }); setPwdErr(""); setPwdMsg(""); }}
              style={{ width: "100%", padding: "0.75rem", background: "var(--bg)", border: "1.5px solid var(--border)", borderRadius: "10px", color: "var(--text)", fontWeight: 600, fontSize: "0.88rem", cursor: "pointer" }}>
              Changer le mot de passe
            </motion.button>
          </div>

          {/* Account meta */}
          <div style={{ background: "var(--surface)", border: "1px solid var(--border)", borderRadius: "16px", padding: "1.5rem" }}>
            <div style={{ fontSize: "0.75rem", fontWeight: 700, color: "var(--text-muted)", textTransform: "uppercase", letterSpacing: "0.06em", marginBottom: "1rem" }}>Informations du compte</div>
            <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "0.75rem" }}>
              {[
                ["Membre depuis", new Date(user.created_at).toLocaleDateString("fr-FR", { day: "2-digit", month: "long", year: "numeric" })],
                ["Dernière mise à jour", new Date(user.updated_at).toLocaleDateString("fr-FR", { day: "2-digit", month: "long", year: "numeric" })],
              ].map(([k, v]) => (
                <div key={k} style={{ padding: "0.75rem", background: "var(--bg)", borderRadius: "10px" }}>
                  <div style={{ fontSize: "0.7rem", fontWeight: 700, color: "var(--text-muted)", textTransform: "uppercase", letterSpacing: "0.05em", marginBottom: "0.25rem" }}>{k}</div>
                  <div style={{ fontWeight: 600, color: "var(--text)", fontSize: "0.85rem" }}>{v}</div>
                </div>
              ))}
            </div>
          </div>

          {/* Logout */}
          <motion.button whileHover={{ scale: 1.01 }} whileTap={{ scale: 0.98 }}
            onClick={() => { logout(); navigate("/login"); }}
            style={{ display: "flex", alignItems: "center", justifyContent: "center", gap: "0.5rem", padding: "0.85rem", background: "rgba(239,68,68,0.06)", border: "1.5px solid rgba(239,68,68,0.2)", borderRadius: "12px", color: "#ef4444", fontWeight: 700, fontSize: "0.95rem", cursor: "pointer" }}>
            <IconLogout /> Se déconnecter
          </motion.button>
        </motion.div>
      </div>

      {/* ── Change Password Modal ── */}
      <AnimatePresence>
        {showPwdModal && (
          <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}
            style={{ position: "fixed", inset: 0, background: "rgba(0,0,0,0.5)", backdropFilter: "blur(4px)", zIndex: 1000, display: "flex", alignItems: "center", justifyContent: "center", padding: "1.5rem" }}
            onClick={e => { if (e.target === e.currentTarget) setShowPwdModal(false); }}>
            <motion.div initial={{ scale: 0.92, opacity: 0 }} animate={{ scale: 1, opacity: 1 }} exit={{ scale: 0.92, opacity: 0 }}
              transition={{ duration: 0.25, ease: [0.22, 1, 0.36, 1] }}
              style={{ background: "var(--surface)", borderRadius: "20px", width: "100%", maxWidth: 440, padding: "2rem", boxShadow: "0 24px 60px rgba(0,0,0,0.2)" }}>
              <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "1.5rem" }}>
                <div style={{ fontWeight: 800, color: "var(--text)", fontSize: "1.1rem" }}>Changer le mot de passe</div>
                <button onClick={() => setShowPwdModal(false)}
                  style={{ background: "var(--bg)", border: "1px solid var(--border)", borderRadius: "8px", width: 32, height: 32, display: "flex", alignItems: "center", justifyContent: "center", cursor: "pointer", color: "var(--text-muted)" }}>
                  <IconX />
                </button>
              </div>

              <AnimatePresence>
                {pwdErr && (
                  <motion.div initial={{ opacity: 0, y: -6 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0 }}
                    style={{ padding: "0.75rem 1rem", background: "rgba(239,68,68,0.08)", border: "1.5px solid rgba(239,68,68,0.2)", borderRadius: "10px", color: "#ef4444", fontSize: "0.85rem", fontWeight: 500, marginBottom: "1rem" }}>
                    {pwdErr}
                  </motion.div>
                )}
                {pwdMsg && (
                  <motion.div initial={{ opacity: 0, y: -6 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0 }}
                    style={{ display: "flex", alignItems: "center", gap: "0.5rem", padding: "0.75rem 1rem", background: "#f0fdf4", border: "1.5px solid #bbf7d0", borderRadius: "10px", color: "#16a34a", fontSize: "0.85rem", fontWeight: 600, marginBottom: "1rem" }}>
                    <IconCheck /> {pwdMsg}
                  </motion.div>
                )}
              </AnimatePresence>

              <form onSubmit={handleChangePassword} style={{ display: "flex", flexDirection: "column", gap: "1rem" }}>
                {[
                  { label: "Mot de passe actuel", key: "old" as const, show: showOld, toggleShow: () => setShowOld(v => !v) },
                  { label: "Nouveau mot de passe", key: "new" as const, show: showNew, toggleShow: () => setShowNew(v => !v) },
                  { label: "Confirmer le nouveau", key: "confirm" as const, show: showNew, toggleShow: () => setShowNew(v => !v) },
                ].map(({ label, key, show, toggleShow }) => (
                  <Field key={key} label={label}>
                    <div style={{ position: "relative" }}>
                      <input type={show ? "text" : "password"} value={pwd[key]} required
                        onChange={e => setPwd(p => ({ ...p, [key]: e.target.value }))}
                        style={{ ...inputBase, paddingRight: "2.8rem" }}
                        onFocus={e => { e.target.style.borderColor = "var(--primary)"; e.target.style.boxShadow = "0 0 0 3px rgba(22,163,74,0.12)"; }}
                        onBlur={e => { e.target.style.borderColor = "var(--border)"; e.target.style.boxShadow = "none"; }} />
                      <button type="button" onClick={toggleShow}
                        style={{ position: "absolute", right: "0.75rem", top: "50%", transform: "translateY(-50%)", background: "none", border: "none", cursor: "pointer", color: "var(--text-muted)", display: "flex" }}>
                        <IconEye open={show} />
                      </button>
                    </div>
                  </Field>
                ))}
                <motion.button type="submit" disabled={pwdSaving} whileHover={{ scale: 1.01 }} whileTap={{ scale: 0.98 }}
                  style={{ padding: "0.85rem", background: "var(--primary)", color: "white", border: "none", borderRadius: "10px", fontWeight: 700, fontSize: "0.95rem", cursor: pwdSaving ? "not-allowed" : "pointer", display: "flex", alignItems: "center", justifyContent: "center", gap: "0.5rem", opacity: pwdSaving ? 0.8 : 1, marginTop: "0.25rem" }}>
                  {pwdSaving ? (
                    <><motion.div animate={{ rotate: 360 }} transition={{ duration: 0.7, repeat: Infinity, ease: "linear" }}
                      style={{ width: 16, height: 16, border: "2px solid rgba(255,255,255,0.4)", borderTop: "2px solid white", borderRadius: "50%" }} />
                    Modification...</>
                  ) : "Confirmer le changement"}
                </motion.button>
              </form>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}
