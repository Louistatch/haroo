import React, { useState } from "react";
import { useNavigate, Link } from "react-router-dom";
import { motion, AnimatePresence } from "framer-motion";
import { login } from "../api/auth";

const PhoneIcon = () => (
  <svg width="18" height="18" viewBox="0 0 18 18" fill="none">
    <path d="M3 2.5A1.5 1.5 0 014.5 1h1a2 2 0 012 2v1a2 2 0 01-2 2H4L3 8s1 6 7 7c6-1 7-7 7-7l-1-2h-1.5a2 2 0 01-2-2V3a2 2 0 012-2h1A1.5 1.5 0 0117 2.5" stroke="currentColor" strokeWidth="1.4" strokeLinecap="round"/>
  </svg>
);

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

const FeatDoc = () => <svg width="16" height="16" viewBox="0 0 16 16" fill="none"><path d="M3 2h7l3 3v9a1 1 0 01-1 1H3a1 1 0 01-1-1V3a1 1 0 011-1z" stroke="currentColor" strokeWidth="1.4"/><path d="M10 2v3h3M5 8h6M5 11h4" stroke="currentColor" strokeWidth="1.4" strokeLinecap="round"/></svg>;
const FeatUser = () => <svg width="16" height="16" viewBox="0 0 16 16" fill="none"><circle cx="8" cy="5" r="3" stroke="currentColor" strokeWidth="1.4"/><path d="M2 14c0-3 2.7-5 6-5s6 2 6 5" stroke="currentColor" strokeWidth="1.4" strokeLinecap="round"/></svg>;
const FeatChart = () => <svg width="16" height="16" viewBox="0 0 16 16" fill="none"><path d="M2 12l4-4 3 3 5-6" stroke="currentColor" strokeWidth="1.4" strokeLinecap="round" strokeLinejoin="round"/><rect x="1" y="1" width="14" height="14" rx="2" stroke="currentColor" strokeWidth="1.2"/></svg>;
const FeatCard = () => <svg width="16" height="16" viewBox="0 0 16 16" fill="none"><rect x="1" y="3" width="14" height="10" rx="2" stroke="currentColor" strokeWidth="1.4"/><path d="M1 7h14" stroke="currentColor" strokeWidth="1.4"/><path d="M4 10h3" stroke="currentColor" strokeWidth="1.4" strokeLinecap="round"/></svg>;

const features = [
  { icon: <FeatDoc />, label: "12+ documents techniques" },
  { icon: <FeatUser />, label: "Agronomes certifiés" },
  { icon: <FeatChart />, label: "Analyses de marché" },
  { icon: <FeatCard />, label: "Paiement Mobile Money" },
];

export default function Login() {
  const [phone, setPhone] = useState("");
  const [password, setPassword] = useState("");
  const [showPwd, setShowPwd] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const navigate = useNavigate();

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setLoading(true);
    setError("");
    try {
      await login(phone, password);
      navigate("/home");
    } catch (err: any) {
      const msg = err?.response?.data?.detail || "Numéro ou mot de passe incorrect";
      setError(msg);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div style={{ minHeight: "100vh", display: "flex", background: "var(--bg)" }}>

      {/* ── LEFT PANEL ── */}
      <div style={{
        flex: "0 0 480px", display: "flex", flexDirection: "column",
        background: "linear-gradient(160deg, #052e16 0%, #14532d 50%, #166534 100%)",
        padding: "3rem", position: "relative", overflow: "hidden",
      }} className="auth-left-panel">

        {/* grid bg */}
        <div style={{ position: "absolute", inset: 0, backgroundImage: "linear-gradient(rgba(255,255,255,0.02) 1px, transparent 1px), linear-gradient(90deg, rgba(255,255,255,0.02) 1px, transparent 1px)", backgroundSize: "60px 60px" }} />
        <div style={{ position: "absolute", inset: 0, backgroundImage: "radial-gradient(circle at 30% 70%, rgba(74,222,128,0.1) 0%, transparent 50%)" }} />

        {/* logo */}
        <motion.div initial={{ opacity: 0, y: -10 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.5 }}
          style={{ display: "flex", alignItems: "center", gap: "10px", position: "relative", marginBottom: "3rem" }}>
          <div style={{ width: 36, height: 36, background: "rgba(74,222,128,0.2)", border: "1px solid rgba(74,222,128,0.4)", borderRadius: "10px", display: "flex", alignItems: "center", justifyContent: "center" }}>
            <svg width="20" height="20" viewBox="0 0 20 20" fill="none">
              <path d="M10 2C6 2 3 5 3 8c0 4.5 7 10 7 10s7-5.5 7-10c0-3-3-6-7-6z" fill="#4ade80" fillOpacity="0.9"/>
              <circle cx="10" cy="8" r="2.5" fill="white" fillOpacity="0.9"/>
            </svg>
          </div>
          <span style={{ color: "white", fontSize: "1.3rem", fontWeight: 800, letterSpacing: "-0.02em" }}>Haroo</span>
        </motion.div>

        {/* headline */}
        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.6, delay: 0.1 }}
          style={{ position: "relative", flexGrow: 1 }}>
          <div style={{ fontSize: "0.75rem", fontWeight: 700, color: "#4ade80", textTransform: "uppercase", letterSpacing: "0.1em", marginBottom: "1rem" }}>
            PLATEFORME #1 AU TOGO
          </div>
          <h2 style={{ fontSize: "clamp(1.6rem, 3vw, 2.4rem)", fontWeight: 800, color: "white", lineHeight: 1.25, marginBottom: "1rem" }}>
            L'agriculture togolaise,<br />
            <span style={{ color: "#4ade80" }}>simplifiée.</span>
          </h2>
          <p style={{ color: "rgba(255,255,255,0.6)", fontSize: "1rem", lineHeight: 1.7, marginBottom: "2.5rem" }}>
            Accédez aux outils dont vous avez besoin pour gérer et développer votre activité agricole.
          </p>

          <div style={{ display: "flex", flexDirection: "column", gap: "1rem" }}>
            {features.map((f, i) => (
              <motion.div key={f.label}
                initial={{ opacity: 0, x: -20 }} animate={{ opacity: 1, x: 0 }}
                transition={{ duration: 0.4, delay: 0.3 + i * 0.08 }}
                style={{ display: "flex", alignItems: "center", gap: "0.75rem" }}>
                <div style={{ width: 36, height: 36, borderRadius: "10px", background: "rgba(74,222,128,0.12)", border: "1px solid rgba(74,222,128,0.2)", display: "flex", alignItems: "center", justifyContent: "center", fontSize: "1rem", flexShrink: 0 }}>
                  {f.icon}
                </div>
                <span style={{ color: "rgba(255,255,255,0.8)", fontSize: "0.9rem", fontWeight: 500 }}>{f.label}</span>
              </motion.div>
            ))}
          </div>
        </motion.div>

        {/* bottom badge */}
        <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ duration: 0.5, delay: 0.8 }}
          style={{ position: "relative", marginTop: "2rem", paddingTop: "1.5rem", borderTop: "1px solid rgba(255,255,255,0.1)" }}>
          <div style={{ display: "flex", alignItems: "center", gap: "0.75rem" }}>
            <div style={{ display: "flex" }}>
              {["KA", "AM", "SE"].map((initials, i) => (
                <div key={i} style={{ width: 30, height: 30, borderRadius: "50%", background: `hsl(${140 + i * 30},60%,40%)`, border: "2px solid rgba(5,46,22,1)", display: "flex", alignItems: "center", justifyContent: "center", marginLeft: i > 0 ? "-8px" : 0, fontSize: "0.65rem", fontWeight: 700, color: "white" }}>
                  {initials}
                </div>
              ))}
            </div>
            <div>
              <div style={{ color: "white", fontSize: "0.8rem", fontWeight: 600 }}>Rejoignez des milliers d'agriculteurs</div>
              <div style={{ color: "rgba(255,255,255,0.5)", fontSize: "0.72rem" }}>déjà inscrits sur Haroo</div>
            </div>
          </div>
        </motion.div>
      </div>

      {/* ── RIGHT PANEL ── */}
      <div style={{ flex: 1, display: "flex", alignItems: "center", justifyContent: "center", padding: "2rem", minHeight: "100vh" }}>
        <motion.div
          initial={{ opacity: 0, y: 24 }} animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.55, ease: [0.22, 1, 0.36, 1] }}
          style={{ width: "100%", maxWidth: "440px" }}>

          <div style={{ marginBottom: "2.5rem" }}>
            <h1 style={{ fontSize: "1.85rem", fontWeight: 800, color: "var(--text)", margin: "0 0 0.5rem", letterSpacing: "-0.03em" }}>
              Bon retour
            </h1>
            <p style={{ color: "var(--text-muted)", fontSize: "0.95rem", margin: 0 }}>
              Connectez-vous à votre espace Haroo
            </p>
          </div>

          {/* error */}
          <AnimatePresence>
            {error && (
              <motion.div
                initial={{ opacity: 0, y: -8, scale: 0.97 }}
                animate={{ opacity: 1, y: 0, scale: 1 }}
                exit={{ opacity: 0, y: -8, scale: 0.97 }}
                transition={{ duration: 0.25 }}
                style={{
                  display: "flex", alignItems: "flex-start", gap: "0.75rem",
                  padding: "0.9rem 1rem",
                  background: "rgba(239,68,68,0.08)",
                  border: "1.5px solid rgba(239,68,68,0.25)",
                  borderRadius: "12px", marginBottom: "1.5rem",
                }}>
                <svg width="18" height="18" viewBox="0 0 18 18" fill="none" style={{ flexShrink: 0, marginTop: 1 }}>
                  <circle cx="9" cy="9" r="8" stroke="#ef4444" strokeWidth="1.5"/>
                  <path d="M9 5v4M9 13v.5" stroke="#ef4444" strokeWidth="1.5" strokeLinecap="round"/>
                </svg>
                <span style={{ color: "#ef4444", fontSize: "0.9rem", fontWeight: 500, lineHeight: 1.5 }}>{error}</span>
              </motion.div>
            )}
          </AnimatePresence>

          <form onSubmit={handleSubmit} style={{ display: "flex", flexDirection: "column", gap: "1.1rem" }}>

            {/* phone */}
            <AuthField label="Numéro de téléphone" hint="+228 suivi de votre numéro">
              <div style={{ position: "relative" }}>
                <div style={{ position: "absolute", left: "0.9rem", top: "50%", transform: "translateY(-50%)", color: "var(--text-muted)" }}>
                  <PhoneIcon />
                </div>
                <input
                  type="tel" value={phone} onChange={e => setPhone(e.target.value)}
                  placeholder="+228 90 12 34 56" required
                  style={{ width: "100%", padding: "0.8rem 0.9rem 0.8rem 2.8rem", border: "1.5px solid var(--border)", borderRadius: "12px", background: "var(--bg)", color: "var(--text)", fontSize: "1rem", outline: "none", transition: "border-color 0.2s, box-shadow 0.2s", boxSizing: "border-box" }}
                  onFocus={e => { e.target.style.borderColor = "var(--primary)"; e.target.style.boxShadow = "0 0 0 3px rgba(22,163,74,0.12)"; }}
                  onBlur={e => { e.target.style.borderColor = "var(--border)"; e.target.style.boxShadow = "none"; }}
                />
              </div>
            </AuthField>

            {/* password */}
            <AuthField label="Mot de passe">
              <div style={{ position: "relative" }}>
                <div style={{ position: "absolute", left: "0.9rem", top: "50%", transform: "translateY(-50%)", color: "var(--text-muted)" }}>
                  <LockIcon />
                </div>
                <input
                  type={showPwd ? "text" : "password"} value={password}
                  onChange={e => setPassword(e.target.value)} required
                  placeholder="Votre mot de passe"
                  style={{ width: "100%", padding: "0.8rem 3rem 0.8rem 2.8rem", border: "1.5px solid var(--border)", borderRadius: "12px", background: "var(--bg)", color: "var(--text)", fontSize: "1rem", outline: "none", transition: "border-color 0.2s, box-shadow 0.2s", boxSizing: "border-box" }}
                  onFocus={e => { e.target.style.borderColor = "var(--primary)"; e.target.style.boxShadow = "0 0 0 3px rgba(22,163,74,0.12)"; }}
                  onBlur={e => { e.target.style.borderColor = "var(--border)"; e.target.style.boxShadow = "none"; }}
                />
                <button type="button" onClick={() => setShowPwd(v => !v)}
                  style={{ position: "absolute", right: "0.9rem", top: "50%", transform: "translateY(-50%)", background: "none", border: "none", cursor: "pointer", color: "var(--text-muted)", padding: 0, display: "flex", alignItems: "center" }}>
                  <EyeIcon open={showPwd} />
                </button>
              </div>
            </AuthField>

            {/* submit */}
            <motion.button
              type="submit" disabled={loading}
              whileHover={!loading ? { scale: 1.01 } : {}}
              whileTap={!loading ? { scale: 0.98 } : {}}
              style={{
                width: "100%", padding: "0.9rem",
                background: loading ? "var(--primary)" : "linear-gradient(135deg, var(--primary-dark), var(--primary))",
                color: "white", border: "none", borderRadius: "12px",
                fontSize: "1rem", fontWeight: 700, cursor: loading ? "not-allowed" : "pointer",
                display: "flex", alignItems: "center", justifyContent: "center", gap: "0.5rem",
                boxShadow: "0 4px 16px rgba(22,163,74,0.3)",
                marginTop: "0.5rem",
                opacity: loading ? 0.85 : 1,
                transition: "opacity 0.2s",
              }}>
              {loading ? (
                <>
                  <motion.div animate={{ rotate: 360 }} transition={{ duration: 0.7, repeat: Infinity, ease: "linear" }}
                    style={{ width: 18, height: 18, border: "2px solid rgba(255,255,255,0.35)", borderTop: "2px solid white", borderRadius: "50%" }} />
                  Connexion en cours...
                </>
              ) : "Se connecter →"}
            </motion.button>
          </form>

          <div style={{ textAlign: "center", marginTop: "1.75rem", color: "var(--text-muted)", fontSize: "0.9rem" }}>
            Pas encore de compte ?{" "}
            <Link to="/register" style={{ color: "var(--primary)", fontWeight: 700, textDecoration: "none" }}>
              Créer un compte
            </Link>
          </div>
        </motion.div>
      </div>

      <style>{`
        @media (max-width: 768px) {
          .auth-left-panel { display: none !important; }
        }
      `}</style>
    </div>
  );
}

function AuthField({ label, hint, children }: { label: string; hint?: string; children: React.ReactNode }) {
  return (
    <div>
      <label style={{ display: "block", fontSize: "0.82rem", fontWeight: 700, color: "var(--text-secondary)", textTransform: "uppercase", letterSpacing: "0.05em", marginBottom: "0.45rem" }}>
        {label}
      </label>
      {children}
      {hint && <div style={{ fontSize: "0.78rem", color: "var(--text-muted)", marginTop: "0.3rem" }}>{hint}</div>}
    </div>
  );
}
