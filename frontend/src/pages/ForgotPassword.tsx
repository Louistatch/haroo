import React, { useState } from "react";
import { Link } from "react-router-dom";
import { motion, AnimatePresence } from "framer-motion";
import { forgotPassword } from "../api/auth";

const MailIcon = () => (
  <svg width="18" height="18" viewBox="0 0 18 18" fill="none">
    <rect x="1" y="3" width="16" height="12" rx="2" stroke="currentColor" strokeWidth="1.4"/>
    <path d="M1 5l8 5 8-5" stroke="currentColor" strokeWidth="1.4" strokeLinecap="round"/>
  </svg>
);

export default function ForgotPassword() {
  const [email, setEmail] = useState("");
  const [loading, setLoading] = useState(false);
  const [sent, setSent] = useState(false);
  const [error, setError] = useState("");

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (!email.trim()) return;
    setLoading(true);
    setError("");
    try {
      await forgotPassword(email.trim());
      setSent(true);
    } catch (err: any) {
      const msg = err?.response?.data?.detail;
      setError(msg || "Une erreur est survenue. Réessayez.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div style={{ minHeight: "100vh", display: "flex", alignItems: "center", justifyContent: "center", background: "var(--bg)", padding: "2rem" }}>
      <motion.div
        initial={{ opacity: 0, y: 24 }} animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5, ease: [0.22, 1, 0.36, 1] }}
        style={{ width: "100%", maxWidth: 440 }}>

        {/* Back link */}
        <Link to="/login" style={{ display: "inline-flex", alignItems: "center", gap: 6, color: "var(--text-muted)", fontSize: "0.9rem", textDecoration: "none", marginBottom: "2rem" }}>
          <svg width="16" height="16" viewBox="0 0 16 16" fill="none"><path d="M10 3L5 8l5 5" stroke="currentColor" strokeWidth="1.6" strokeLinecap="round" strokeLinejoin="round"/></svg>
          Retour à la connexion
        </Link>

        {!sent ? (
          <>
            <div style={{ marginBottom: "2rem" }}>
              <div style={{ width: 56, height: 56, borderRadius: 16, background: "rgba(22,163,74,0.1)", display: "flex", alignItems: "center", justifyContent: "center", marginBottom: "1.25rem" }}>
                <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="var(--primary)" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
                  <rect x="3" y="11" width="18" height="11" rx="2"/>
                  <path d="M7 11V7a5 5 0 0110 0v4"/>
                  <circle cx="12" cy="16" r="1"/>
                </svg>
              </div>
              <h1 style={{ fontSize: "1.7rem", fontWeight: 800, color: "var(--text)", margin: "0 0 0.5rem", letterSpacing: "-0.03em" }}>
                Mot de passe oublié ?
              </h1>
              <p style={{ color: "var(--text-muted)", fontSize: "0.95rem", margin: 0, lineHeight: 1.6 }}>
                Entrez votre adresse email et nous vous enverrons un lien pour réinitialiser votre mot de passe.
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
                <label style={{ display: "block", fontSize: "0.85rem", fontWeight: 600, color: "var(--text)", marginBottom: "0.4rem" }}>Adresse email</label>
                <div style={{ position: "relative" }}>
                  <div style={{ position: "absolute", left: "0.9rem", top: "50%", transform: "translateY(-50%)", color: "var(--text-muted)" }}>
                    <MailIcon />
                  </div>
                  <input type="email" value={email} onChange={e => setEmail(e.target.value)}
                    placeholder="vous@exemple.com" required
                    style={{ width: "100%", padding: "0.8rem 0.9rem 0.8rem 2.8rem", border: "1.5px solid var(--border)", borderRadius: 12, background: "var(--bg)", color: "var(--text)", fontSize: "1rem", outline: "none", boxSizing: "border-box", transition: "border-color 0.2s, box-shadow 0.2s" }}
                    onFocus={e => { e.target.style.borderColor = "var(--primary)"; e.target.style.boxShadow = "0 0 0 3px rgba(22,163,74,0.12)"; }}
                    onBlur={e => { e.target.style.borderColor = "var(--border)"; e.target.style.boxShadow = "none"; }}
                  />
                </div>
              </div>

              <motion.button type="submit" disabled={loading} whileTap={{ scale: 0.98 }}
                style={{ width: "100%", padding: "0.9rem", background: loading ? "var(--primary-muted)" : "var(--primary)", color: "white", border: "none", borderRadius: 12, fontSize: "1rem", fontWeight: 700, cursor: loading ? "not-allowed" : "pointer", boxShadow: loading ? "none" : "0 4px 14px rgba(22,163,74,0.3)", transition: "background 0.2s" }}>
                {loading ? "Envoi en cours..." : "Envoyer le lien"}
              </motion.button>
            </form>
          </>
        ) : (
          <motion.div initial={{ opacity: 0, scale: 0.95 }} animate={{ opacity: 1, scale: 1 }} transition={{ duration: 0.4 }}>
            <div style={{ textAlign: "center" }}>
              <div style={{ width: 64, height: 64, borderRadius: "50%", background: "rgba(22,163,74,0.1)", display: "flex", alignItems: "center", justifyContent: "center", margin: "0 auto 1.5rem" }}>
                <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="var(--primary)" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                  <path d="M22 2L11 13"/><path d="M22 2l-7 20-4-9-9-4 20-7z"/>
                </svg>
              </div>
              <h2 style={{ fontSize: "1.5rem", fontWeight: 800, color: "var(--text)", margin: "0 0 0.75rem" }}>
                Email envoyé
              </h2>
              <p style={{ color: "var(--text-muted)", fontSize: "0.95rem", lineHeight: 1.7, margin: "0 0 2rem" }}>
                Si un compte existe avec l'adresse <strong style={{ color: "var(--text)" }}>{email}</strong>, vous recevrez un lien de réinitialisation dans quelques minutes.
              </p>
              <p style={{ color: "var(--text-muted)", fontSize: "0.85rem", margin: "0 0 1.5rem" }}>
                Pensez à vérifier vos spams.
              </p>
              <div style={{ display: "flex", flexDirection: "column", gap: "0.75rem" }}>
                <button onClick={() => { setSent(false); setEmail(""); }}
                  style={{ width: "100%", padding: "0.8rem", border: "1.5px solid var(--border)", borderRadius: 12, background: "none", color: "var(--text)", fontSize: "0.95rem", fontWeight: 600, cursor: "pointer" }}>
                  Essayer une autre adresse
                </button>
                <Link to="/login" style={{ display: "block", textAlign: "center", color: "var(--primary)", fontWeight: 600, fontSize: "0.9rem", textDecoration: "none" }}>
                  Retour à la connexion
                </Link>
              </div>
            </div>
          </motion.div>
        )}
      </motion.div>
    </div>
  );
}
