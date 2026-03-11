import React, { useState, useEffect } from "react";
import { useNavigate, Link } from "react-router-dom";
import { motion, AnimatePresence } from "framer-motion";
import { auth, googleProvider } from "../lib/firebase";
import { signInWithPopup } from "firebase/auth";
import { loginEmail, firebaseExchange } from "../api/auth";

const MailIcon = () => (
  <svg width="18" height="18" viewBox="0 0 18 18" fill="none">
    <rect x="1" y="3" width="16" height="12" rx="2" stroke="currentColor" strokeWidth="1.4"/>
    <path d="M1 5l8 5 8-5" stroke="currentColor" strokeWidth="1.4" strokeLinecap="round"/>
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

const GoogleIcon = () => (
  <svg width="18" height="18" viewBox="0 0 18 18" fill="none">
    <path d="M17.64 9.2c0-.637-.057-1.251-.164-1.84H9v3.481h4.844c-.209 1.125-.843 2.078-1.796 2.717v2.258h2.908c1.702-1.567 2.684-3.875 2.684-6.615z" fill="#4285F4"/>
    <path d="M9 18c2.43 0 4.467-.806 5.956-2.18l-2.908-2.259c-.806.54-1.837.86-3.048.86-2.344 0-4.328-1.584-5.036-3.711H.957v2.332A8.997 8.997 0 009 18z" fill="#34A853"/>
    <path d="M3.964 10.71A5.41 5.41 0 013.682 9c0-.593.102-1.17.282-1.71V4.958H.957A8.996 8.996 0 000 9c0 1.452.348 2.827.957 4.042l3.007-2.332z" fill="#FBBC05"/>
    <path d="M9 3.58c1.321 0 2.508.454 3.44 1.345l2.582-2.58C13.463.891 11.426 0 9 0A8.997 8.997 0 00.957 4.958L3.964 7.29C4.672 5.163 6.656 3.58 9 3.58z" fill="#EA4335"/>
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

function AuthField({ label, hint, children }: { label: string; hint?: string; children: React.ReactNode }) {
  return (
    <div style={{ display: "flex", flexDirection: "column", gap: "0.4rem" }}>
      <label style={{ fontSize: "0.85rem", fontWeight: 600, color: "var(--text)" }}>{label}</label>
      {children}
      {hint && <span style={{ fontSize: "0.75rem", color: "var(--text-muted)" }}>{hint}</span>}
    </div>
  );
}

export default function Login() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [showPwd, setShowPwd] = useState(false);
  const [loading, setLoading] = useState(false);
  const [loadingGoogle, setLoadingGoogle] = useState(false);
  const [error, setError] = useState("");
  const navigate = useNavigate();

  // Redirect if already logged in
  useEffect(() => {
    if (localStorage.getItem("access_token")) {
      navigate("/home", { replace: true });
    }
  }, [navigate]);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setLoading(true);
    setError("");
    try {
      const data = await loginEmail(email, password);
      const dest = data?.user?.user_type ? "/home" : "/choose-profile";
      navigate(dest);
    } catch (err: any) {
      const data = err?.response?.data;
      if (data?.error) {
        setError(data.error);
      } else {
        setError("Email ou mot de passe incorrect.");
      }
    } finally {
      setLoading(false);
    }
  }

  async function handleGoogle() {
    setLoadingGoogle(true);
    setError("");
    try {
      const result = await signInWithPopup(auth, googleProvider);
      const idToken = await result.user.getIdToken();
      const data = await firebaseExchange(idToken);
      const dest = data?.user?.user_type ? "/home" : "/choose-profile";
      navigate(dest);
    } catch (err: any) {
      if (err?.code === "auth/popup-closed-by-user") return;
      if (err?.code === "auth/unauthorized-domain") {
        setError("Domaine non autorisé dans Firebase. Contactez l'administrateur.");
      } else if (err?.response?.data?.detail) {
        setError(err.response.data.detail);
      } else {
        setError("Connexion Google échouée. Réessayez.");
      }
    } finally {
      setLoadingGoogle(false);
    }
  }

  return (
    <div style={{ minHeight: "100vh", display: "flex", background: "var(--bg)" }}>

      <div style={{
        flex: "0 0 480px", display: "flex", flexDirection: "column",
        background: "linear-gradient(160deg, #052e16 0%, #14532d 50%, #166534 100%)",
        padding: "3rem", position: "relative", overflow: "hidden",
      }} className="auth-left-panel">

        {/* Real background image */}
        <div style={{ position: "absolute", inset: 0, backgroundImage: "url('/images/hero/farmer.jpg')", backgroundSize: "cover", backgroundPosition: "center", opacity: 0.18 }} />
        <div style={{ position: "absolute", inset: 0, background: "linear-gradient(160deg, rgba(5,46,22,0.92) 0%, rgba(20,83,45,0.88) 50%, rgba(22,101,52,0.85) 100%)" }} />
        <div style={{ position: "absolute", inset: 0, backgroundImage: "linear-gradient(rgba(255,255,255,0.02) 1px, transparent 1px), linear-gradient(90deg, rgba(255,255,255,0.02) 1px, transparent 1px)", backgroundSize: "60px 60px" }} />
        <div style={{ position: "absolute", inset: 0, backgroundImage: "radial-gradient(circle at 30% 70%, rgba(74,222,128,0.1) 0%, transparent 50%)" }} />

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
                <div style={{ width: 36, height: 36, borderRadius: "10px", background: "rgba(74,222,128,0.12)", border: "1px solid rgba(74,222,128,0.2)", display: "flex", alignItems: "center", justifyContent: "center", color: "#4ade80", flexShrink: 0 }}>
                  {f.icon}
                </div>
                <span style={{ color: "rgba(255,255,255,0.8)", fontSize: "0.9rem", fontWeight: 500 }}>{f.label}</span>
              </motion.div>
            ))}
          </div>
        </motion.div>

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

          <AnimatePresence>
            {error && (
              <motion.div
                initial={{ opacity: 0, y: -8, scale: 0.97 }}
                animate={{ opacity: 1, y: 0, scale: 1 }}
                exit={{ opacity: 0, y: -8, scale: 0.97 }}
                transition={{ duration: 0.25 }}
                style={{ display: "flex", alignItems: "flex-start", gap: "0.75rem", padding: "0.9rem 1rem", background: "rgba(239,68,68,0.08)", border: "1.5px solid rgba(239,68,68,0.25)", borderRadius: "12px", marginBottom: "1.5rem" }}>
                <svg width="18" height="18" viewBox="0 0 18 18" fill="none" style={{ flexShrink: 0, marginTop: 1 }}>
                  <circle cx="9" cy="9" r="8" stroke="#ef4444" strokeWidth="1.5"/>
                  <path d="M9 5v4M9 13v.5" stroke="#ef4444" strokeWidth="1.5" strokeLinecap="round"/>
                </svg>
                <span style={{ color: "#ef4444", fontSize: "0.9rem", fontWeight: 500, lineHeight: 1.5 }}>{error}</span>
              </motion.div>
            )}
          </AnimatePresence>

          <button
            onClick={handleGoogle}
            disabled={loadingGoogle || loading}
            style={{ width: "100%", display: "flex", alignItems: "center", justifyContent: "center", gap: "0.75rem", padding: "0.85rem 1rem", background: "var(--card)", border: "1.5px solid var(--border)", borderRadius: "12px", cursor: "pointer", fontSize: "0.95rem", fontWeight: 600, color: "var(--text)", marginBottom: "1.5rem", transition: "border-color 0.2s, box-shadow 0.2s", opacity: (loadingGoogle || loading) ? 0.7 : 1 }}
            onMouseEnter={e => { (e.currentTarget as HTMLButtonElement).style.borderColor = "var(--primary)"; (e.currentTarget as HTMLButtonElement).style.boxShadow = "0 0 0 3px rgba(22,163,74,0.1)"; }}
            onMouseLeave={e => { (e.currentTarget as HTMLButtonElement).style.borderColor = "var(--border)"; (e.currentTarget as HTMLButtonElement).style.boxShadow = "none"; }}
          >
            <GoogleIcon />
            {loadingGoogle ? "Redirection..." : "Continuer avec Google"}
          </button>

          <div style={{ display: "flex", alignItems: "center", gap: "1rem", marginBottom: "1.5rem" }}>
            <div style={{ flex: 1, height: "1px", background: "var(--border)" }} />
            <span style={{ fontSize: "0.8rem", color: "var(--text-muted)", fontWeight: 500 }}>ou</span>
            <div style={{ flex: 1, height: "1px", background: "var(--border)" }} />
          </div>

          <form onSubmit={handleSubmit} style={{ display: "flex", flexDirection: "column", gap: "1.1rem" }}>

            <AuthField label="Adresse email">
              <div style={{ position: "relative" }}>
                <div style={{ position: "absolute", left: "0.9rem", top: "50%", transform: "translateY(-50%)", color: "var(--text-muted)" }}>
                  <MailIcon />
                </div>
                <input
                  type="email" value={email} onChange={e => setEmail(e.target.value)}
                  placeholder="vous@exemple.com" required
                  style={{ width: "100%", padding: "0.8rem 0.9rem 0.8rem 2.8rem", border: "1.5px solid var(--border)", borderRadius: "12px", background: "var(--bg)", color: "var(--text)", fontSize: "1rem", outline: "none", transition: "border-color 0.2s, box-shadow 0.2s", boxSizing: "border-box" }}
                  onFocus={e => { e.target.style.borderColor = "var(--primary)"; e.target.style.boxShadow = "0 0 0 3px rgba(22,163,74,0.12)"; }}
                  onBlur={e => { e.target.style.borderColor = "var(--border)"; e.target.style.boxShadow = "none"; }}
                />
              </div>
            </AuthField>

            <AuthField label="Mot de passe">
              <div style={{ position: "relative" }}>
                <div style={{ position: "absolute", left: "0.9rem", top: "50%", transform: "translateY(-50%)", color: "var(--text-muted)" }}>
                  <LockIcon />
                </div>
                <input
                  type={showPwd ? "text" : "password"} value={password} onChange={e => setPassword(e.target.value)}
                  placeholder="••••••••" required
                  style={{ width: "100%", padding: "0.8rem 3rem 0.8rem 2.8rem", border: "1.5px solid var(--border)", borderRadius: "12px", background: "var(--bg)", color: "var(--text)", fontSize: "1rem", outline: "none", transition: "border-color 0.2s, box-shadow 0.2s", boxSizing: "border-box" }}
                  onFocus={e => { e.target.style.borderColor = "var(--primary)"; e.target.style.boxShadow = "0 0 0 3px rgba(22,163,74,0.12)"; }}
                  onBlur={e => { e.target.style.borderColor = "var(--border)"; e.target.style.boxShadow = "none"; }}
                />
                <button type="button" onClick={() => setShowPwd(!showPwd)}
                  style={{ position: "absolute", right: "0.9rem", top: "50%", transform: "translateY(-50%)", background: "none", border: "none", cursor: "pointer", color: "var(--text-muted)", padding: 0 }}>
                  <EyeIcon open={showPwd} />
                </button>
              </div>
            </AuthField>

            <motion.button
              type="submit" disabled={loading}
              whileTap={{ scale: 0.98 }}
              style={{ width: "100%", padding: "0.9rem", background: loading ? "var(--primary-muted)" : "var(--primary)", color: "white", border: "none", borderRadius: "12px", fontSize: "1rem", fontWeight: 700, cursor: loading ? "not-allowed" : "pointer", transition: "background 0.2s, box-shadow 0.2s", marginTop: "0.4rem", boxShadow: loading ? "none" : "0 4px 14px rgba(22,163,74,0.3)" }}>
              {loading ? "Connexion..." : "Se connecter"}
            </motion.button>
          </form>

          <div style={{ display: "flex", justifyContent: "center", marginTop: "1rem" }}>
            <Link to="/forgot-password" style={{ color: "var(--text-muted)", fontSize: "0.85rem", textDecoration: "none", fontWeight: 500 }}>
              Mot de passe oublié ?
            </Link>
          </div>

          <p style={{ textAlign: "center", fontSize: "0.9rem", color: "var(--text-muted)", marginTop: "2rem" }}>
            Pas encore de compte ?{" "}
            <Link to="/register" style={{ color: "var(--primary)", fontWeight: 600, textDecoration: "none" }}>
              Créer un compte
            </Link>
          </p>
        </motion.div>
      </div>
    </div>
  );
}
