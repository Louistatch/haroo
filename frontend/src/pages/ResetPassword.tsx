import React, { useState } from "react";
import { Link, useSearchParams } from "react-router-dom";
import { motion, AnimatePresence } from "framer-motion";
import { resetPassword } from "../api/auth";

const LockIcon = () => (
  <svg width="18" height="18" viewBox="0 0 18 18" fill="none">
    <rect x="3" y="8" width="12" height="9" rx="2" stroke="currentColor" strokeWidth="1.4"/>
    <path d="M6 8V6a3 3 0 016 0v2" stroke="currentColor" strokeWidth="1.4" strokeLinecap="round"/>
    <circle cx="9" cy="12.5" r="1.2" fill="currentColor"/>
  </svg>
);

const EyeIcon = ({ open }: { open: boolean }) => open ? (
  <svg width="18" height="18" viewBox="0 0 18 18" fill="none">
    <path d="M1 9s3-6 8-6 8 6 8 6-3 6-8 6-8-6-8-6z" stroke="currentColor" strokeWidth="1.4"/>
    <circle cx="9" cy="9" r="2.5" stroke="currentColor" strokeWidth="1.4"/>
  </svg>
) : (
  <svg width="18" height="18" viewBox="0 0 18 18" fill="none">
    <path d="M1 9s3-6 8-6 8 6 8 6-3 6-8 6-8-6-8-6z" stroke="currentColor" strokeWidth="1.4"/>
    <circle cx="9" cy="9" r="2.5" stroke="currentColor" strokeWidth="1.4"/>
    <line x1="2" y1="2" x2="16" y2="16" stroke="currentColor" strokeWidth="1.4" strokeLinecap="round"/>
  </svg>
);

function pwdStrength(pwd: string) {
  let score = 0;
  if (pwd.length >= 8) score++;
  if (/[A-Z]/.test(pwd)) score++;
  if (/[0-9]/.test(pwd)) score++;
  if (/[^A-Za-z0-9]/.test(pwd)) score++;
  return score;
}

export default function ResetPassword() {
  const [searchParams] = useSearchParams();
  const token = searchParams.get("token") || "";

  const [password, setPassword] = useState("");
  const [confirm, setConfirm] = useState("");
  const [showPwd, setShowPwd] = useState(false);
  const [loading, setLoading] = useState(false);
  const [success, setSuccess] = useState(false);
  const [error, setError] = useState("");

  const strength = pwdStrength(password);
  const strengthColor = ["#ef4444", "#ef4444", "#f59e0b", "#22c55e", "#16a34a"][strength];
  const strengthLabel = ["", "Trop court", "Faible", "Moyen", "Fort"][strength];

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (password !== confirm) { setError("Les mots de passe ne correspondent pas."); return; }
    if (password.length < 8) { setError("Le mot de passe doit faire au moins 8 caractères."); return; }
    setLoading(true);
    setError("");
    try {
      await resetPassword(token, password, confirm);
      setSuccess(true);
    } catch (err: any) {
      const msg = err?.response?.data?.detail;
      setError(msg || "Lien expiré ou invalide. Demandez un nouveau lien.");
    } finally {
      setLoading(false);
    }
  }

  if (!token) {
    return (
      <div style={{ minHeight: "100vh", display: "flex", alignItems: "center", justifyContent: "center", background: "var(--bg)", padding: "2rem" }}>
        <div style={{ textAlign: "center", maxWidth: 400 }}>
          <div style={{ width: 64, height: 64, borderRadius: "50%", background: "rgba(239,68,68,0.1)", display: "flex", alignItems: "center", justifyContent: "center", margin: "0 auto 1.5rem" }}>
            <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="#ef4444" strokeWidth="2" strokeLinecap="round"><circle cx="12" cy="12" r="10"/><path d="M12 8v4M12 16h.01"/></svg>
          </div>
          <h2 style={{ fontSize: "1.4rem", fontWeight: 800, color: "var(--text)", margin: "0 0 0.75rem" }}>Lien invalide</h2>
          <p style={{ color: "var(--text-muted)", fontSize: "0.95rem", margin: "0 0 1.5rem" }}>Ce lien de réinitialisation est invalide ou a expiré.</p>
          <Link to="/forgot-password" style={{ color: "var(--primary)", fontWeight: 600, textDecoration: "none" }}>Demander un nouveau lien</Link>
        </div>
      </div>
    );
  }

  return (
    <div style={{ minHeight: "100vh", display: "flex", alignItems: "center", justifyContent: "center", background: "var(--bg)", padding: "2rem" }}>
      <motion.div initial={{ opacity: 0, y: 24 }} animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5, ease: [0.22, 1, 0.36, 1] }}
        style={{ width: "100%", maxWidth: 440 }}>

        {!success ? (
          <>
            <div style={{ marginBottom: "2rem" }}>
              <div style={{ width: 56, height: 56, borderRadius: 16, background: "rgba(22,163,74,0.1)", display: "flex", alignItems: "center", justifyContent: "center", marginBottom: "1.25rem" }}>
                <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="var(--primary)" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
                  <path d="M12 2a5 5 0 015 5v3H7V7a5 5 0 015-5z"/><rect x="3" y="10" width="18" height="12" rx="2"/><circle cx="12" cy="16" r="1"/>
                </svg>
              </div>
              <h1 style={{ fontSize: "1.7rem", fontWeight: 800, color: "var(--text)", margin: "0 0 0.5rem" }}>
                Nouveau mot de passe
              </h1>
              <p style={{ color: "var(--text-muted)", fontSize: "0.95rem", margin: 0 }}>
                Choisissez un mot de passe fort pour sécuriser votre compte.
              </p>
            </div>

            <AnimatePresence>
              {error && (
                <motion.div initial={{ opacity: 0, y: -8 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0, y: -8 }}
                  style={{ display: "flex", alignItems: "center", gap: "0.75rem", padding: "0.9rem 1rem", background: "rgba(239,68,68,0.08)", border: "1.5px solid rgba(239,68,68,0.25)", borderRadius: 12, marginBottom: "1.5rem" }}>
                  <svg width="18" height="18" viewBox="0 0 18 18" fill="none"><circle cx="9" cy="9" r="8" stroke="#ef4444" strokeWidth="1.5"/><path d="M9 5v4M9 13v.5" stroke="#ef4444" strokeWidth="1.5" strokeLinecap="round"/></svg>
                  <span style={{ color: "#ef4444", fontSize: "0.9rem", fontWeight: 500 }}>{error}</span>
                </motion.div>
              )}
            </AnimatePresence>

            <form onSubmit={handleSubmit} style={{ display: "flex", flexDirection: "column", gap: "1.1rem" }}>
              <div>
                <label style={{ display: "block", fontSize: "0.85rem", fontWeight: 600, color: "var(--text)", marginBottom: "0.4rem" }}>Nouveau mot de passe</label>
                <div style={{ position: "relative" }}>
                  <div style={{ position: "absolute", left: "0.9rem", top: "50%", transform: "translateY(-50%)", color: "var(--text-muted)" }}><LockIcon /></div>
                  <input type={showPwd ? "text" : "password"} value={password} onChange={e => setPassword(e.target.value)}
                    placeholder="Au moins 8 caractères" required minLength={8}
                    style={{ width: "100%", padding: "0.8rem 3rem 0.8rem 2.8rem", border: "1.5px solid var(--border)", borderRadius: 12, background: "var(--bg)", color: "var(--text)", fontSize: "1rem", outline: "none", boxSizing: "border-box", transition: "border-color 0.2s, box-shadow 0.2s" }}
                    onFocus={e => { e.target.style.borderColor = "var(--primary)"; e.target.style.boxShadow = "0 0 0 3px rgba(22,163,74,0.12)"; }}
                    onBlur={e => { e.target.style.borderColor = "var(--border)"; e.target.style.boxShadow = "none"; }}
                  />
                  <button type="button" onClick={() => setShowPwd(!showPwd)}
                    style={{ position: "absolute", right: "0.9rem", top: "50%", transform: "translateY(-50%)", background: "none", border: "none", cursor: "pointer", color: "var(--text-muted)", padding: 0 }}>
                    <EyeIcon open={showPwd} />
                  </button>
                </div>
                {password && (
                  <div style={{ display: "flex", gap: 4, marginTop: "0.4rem" }}>
                    {[1, 2, 3, 4].map(i => (
                      <div key={i} style={{ flex: 1, height: 3, borderRadius: 2, background: i <= strength ? strengthColor : "var(--border)", transition: "background 0.3s" }} />
                    ))}
                    <span style={{ fontSize: "0.72rem", color: strengthColor, marginLeft: "0.5rem", fontWeight: 600, whiteSpace: "nowrap" }}>{strengthLabel}</span>
                  </div>
                )}
              </div>

              <div>
                <label style={{ display: "block", fontSize: "0.85rem", fontWeight: 600, color: "var(--text)", marginBottom: "0.4rem" }}>Confirmer le mot de passe</label>
                <div style={{ position: "relative" }}>
                  <div style={{ position: "absolute", left: "0.9rem", top: "50%", transform: "translateY(-50%)", color: "var(--text-muted)" }}><LockIcon /></div>
                  <input type="password" value={confirm} onChange={e => setConfirm(e.target.value)}
                    placeholder="••••••••" required
                    style={{ width: "100%", padding: "0.8rem 0.9rem 0.8rem 2.8rem", border: `1.5px solid ${confirm && confirm !== password ? "#ef4444" : "var(--border)"}`, borderRadius: 12, background: "var(--bg)", color: "var(--text)", fontSize: "1rem", outline: "none", boxSizing: "border-box", transition: "border-color 0.2s, box-shadow 0.2s" }}
                    onFocus={e => { e.target.style.borderColor = "var(--primary)"; e.target.style.boxShadow = "0 0 0 3px rgba(22,163,74,0.12)"; }}
                    onBlur={e => { e.target.style.borderColor = confirm && confirm !== password ? "#ef4444" : "var(--border)"; e.target.style.boxShadow = "none"; }}
                  />
                </div>
                {confirm && confirm !== password && (
                  <span style={{ fontSize: "0.75rem", color: "#ef4444", marginTop: "0.3rem", display: "block" }}>Les mots de passe ne correspondent pas.</span>
                )}
              </div>

              <motion.button type="submit" disabled={loading} whileTap={{ scale: 0.98 }}
                style={{ width: "100%", padding: "0.9rem", background: loading ? "var(--primary-muted)" : "var(--primary)", color: "white", border: "none", borderRadius: 12, fontSize: "1rem", fontWeight: 700, cursor: loading ? "not-allowed" : "pointer", boxShadow: loading ? "none" : "0 4px 14px rgba(22,163,74,0.3)", marginTop: "0.4rem" }}>
                {loading ? "Réinitialisation..." : "Réinitialiser le mot de passe"}
              </motion.button>
            </form>
          </>
        ) : (
          <motion.div initial={{ opacity: 0, scale: 0.95 }} animate={{ opacity: 1, scale: 1 }} style={{ textAlign: "center" }}>
            <div style={{ width: 64, height: 64, borderRadius: "50%", background: "rgba(22,163,74,0.1)", display: "flex", alignItems: "center", justifyContent: "center", margin: "0 auto 1.5rem" }}>
              <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="var(--primary)" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
                <polyline points="20 6 9 17 4 12"/>
              </svg>
            </div>
            <h2 style={{ fontSize: "1.5rem", fontWeight: 800, color: "var(--text)", margin: "0 0 0.75rem" }}>
              Mot de passe réinitialisé
            </h2>
            <p style={{ color: "var(--text-muted)", fontSize: "0.95rem", lineHeight: 1.7, margin: "0 0 2rem" }}>
              Votre mot de passe a été modifié avec succès. Vous pouvez maintenant vous connecter.
            </p>
            <Link to="/login" style={{ display: "inline-flex", alignItems: "center", justifyContent: "center", width: "100%", padding: "0.9rem", background: "var(--primary)", color: "white", borderRadius: 12, fontSize: "1rem", fontWeight: 700, textDecoration: "none", boxShadow: "0 4px 14px rgba(22,163,74,0.3)" }}>
              Se connecter
            </Link>
          </motion.div>
        )}
      </motion.div>
    </div>
  );
}
