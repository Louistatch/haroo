import React, { useState } from "react";
import { useNavigate, Link } from "react-router-dom";
import { motion, AnimatePresence } from "framer-motion";
import { register } from "../api/auth";

const UserIcon = () => (
  <svg width="18" height="18" viewBox="0 0 18 18" fill="none">
    <circle cx="9" cy="6" r="3.5" stroke="currentColor" strokeWidth="1.4"/>
    <path d="M2 16c0-3.5 3-6 7-6s7 2.5 7 6" stroke="currentColor" strokeWidth="1.4" strokeLinecap="round"/>
  </svg>
);

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

const CheckIcon = () => (
  <svg width="14" height="14" viewBox="0 0 14 14" fill="none">
    <path d="M2.5 7l3 3 6-6" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round"/>
  </svg>
);

const USER_TYPES = [
  {
    value: "EXPLOITANT",
    label: "Exploitant Agricole",
    desc: "Je gère une exploitation",
    icon: "🌾",
    color: "#16a34a",
  },
  {
    value: "AGRONOME",
    label: "Agronome",
    desc: "Je suis un expert agricole",
    icon: "🎓",
    color: "#2563eb",
  },
  {
    value: "OUVRIER",
    label: "Ouvrier Agricole",
    desc: "Je travaille sur les champs",
    icon: "🤝",
    color: "#d97706",
  },
  {
    value: "ACHETEUR",
    label: "Acheteur",
    desc: "J'achète des produits agricoles",
    icon: "🛒",
    color: "#7c3aed",
  },
];

const STEPS = ["Votre profil", "Vos informations", "Sécurité"];

export default function Register() {
  const [step, setStep] = useState(0);
  const [userType, setUserType] = useState("");
  const [name, setName] = useState("");
  const [phone, setPhone] = useState("");
  const [password, setPassword] = useState("");
  const [showPwd, setShowPwd] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [success, setSuccess] = useState(false);
  const navigate = useNavigate();

  const pwdStrength = (() => {
    if (password.length === 0) return 0;
    let s = 0;
    if (password.length >= 8) s++;
    if (/[A-Z]/.test(password)) s++;
    if (/[0-9]/.test(password)) s++;
    if (/[^A-Za-z0-9]/.test(password)) s++;
    return s;
  })();

  const pwdLabel = ["", "Faible", "Moyen", "Bon", "Excellent"][pwdStrength];
  const pwdColor = ["", "#ef4444", "#f59e0b", "#3b82f6", "#16a34a"][pwdStrength];

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (step < 2) { setStep(s => s + 1); return; }
    setLoading(true);
    setError("");
    try {
      await register({ phone, password, name, user_type: userType });
      setSuccess(true);
      setTimeout(() => navigate("/login"), 2500);
    } catch (err: any) {
      const data = err?.response?.data;
      const msg = data?.detail || data?.phone_number?.[0] || data?.password?.[0] || "Erreur lors de l'inscription";
      setError(msg);
    } finally {
      setLoading(false);
    }
  }

  const canProceed = [
    userType !== "",
    name.trim().length >= 2 && phone.length >= 8,
    password.length >= 8,
  ][step];

  if (success) {
    return (
      <div style={{ minHeight: "100vh", display: "flex", alignItems: "center", justifyContent: "center", background: "var(--bg)" }}>
        <motion.div initial={{ scale: 0.8, opacity: 0 }} animate={{ scale: 1, opacity: 1 }} transition={{ duration: 0.5, ease: [0.22, 1, 0.36, 1] }}
          style={{ textAlign: "center", padding: "3rem" }}>
          <motion.div initial={{ scale: 0 }} animate={{ scale: 1 }} transition={{ delay: 0.2, type: "spring", stiffness: 300 }}
            style={{ width: 80, height: 80, borderRadius: "50%", background: "linear-gradient(135deg, #16a34a, #4ade80)", display: "flex", alignItems: "center", justifyContent: "center", margin: "0 auto 1.5rem" }}>
            <svg width="36" height="36" viewBox="0 0 36 36" fill="none">
              <path d="M8 18l7 7 13-13" stroke="white" strokeWidth="3" strokeLinecap="round" strokeLinejoin="round"/>
            </svg>
          </motion.div>
          <h2 style={{ fontSize: "1.8rem", fontWeight: 800, color: "var(--text)", marginBottom: "0.75rem" }}>Inscription réussie !</h2>
          <p style={{ color: "var(--text-muted)", fontSize: "1rem" }}>Vous allez être redirigé vers la connexion...</p>
        </motion.div>
      </div>
    );
  }

  return (
    <div style={{ minHeight: "100vh", display: "flex", background: "var(--bg)" }}>

      {/* ── LEFT PANEL ── */}
      <div style={{
        flex: "0 0 400px", display: "flex", flexDirection: "column",
        background: "linear-gradient(160deg, #1e1b4b 0%, #312e81 50%, #4338ca 100%)",
        padding: "3rem", position: "relative", overflow: "hidden",
      }} className="auth-left-panel">
        <div style={{ position: "absolute", inset: 0, backgroundImage: "linear-gradient(rgba(255,255,255,0.02) 1px, transparent 1px), linear-gradient(90deg, rgba(255,255,255,0.02) 1px, transparent 1px)", backgroundSize: "60px 60px" }} />
        <div style={{ position: "absolute", inset: 0, backgroundImage: "radial-gradient(circle at 70% 30%, rgba(167,139,250,0.1) 0%, transparent 50%)" }} />

        {/* logo */}
        <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ duration: 0.5 }}
          style={{ display: "flex", alignItems: "center", gap: "10px", position: "relative", marginBottom: "3rem" }}>
          <div style={{ width: 36, height: 36, background: "rgba(167,139,250,0.2)", border: "1px solid rgba(167,139,250,0.4)", borderRadius: "10px", display: "flex", alignItems: "center", justifyContent: "center" }}>
            <svg width="20" height="20" viewBox="0 0 20 20" fill="none">
              <path d="M10 2C6 2 3 5 3 8c0 4.5 7 10 7 10s7-5.5 7-10c0-3-3-6-7-6z" fill="#a78bfa" fillOpacity="0.9"/>
              <circle cx="10" cy="8" r="2.5" fill="white" fillOpacity="0.9"/>
            </svg>
          </div>
          <span style={{ color: "white", fontSize: "1.3rem", fontWeight: 800, letterSpacing: "-0.02em" }}>Haroo</span>
        </motion.div>

        {/* steps */}
        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.5, delay: 0.1 }}
          style={{ position: "relative", flexGrow: 1 }}>
          <div style={{ fontSize: "0.75rem", fontWeight: 700, color: "#a78bfa", textTransform: "uppercase", letterSpacing: "0.1em", marginBottom: "1rem" }}>
            CRÉER UN COMPTE
          </div>
          <h2 style={{ fontSize: "clamp(1.5rem, 2.5vw, 2.2rem)", fontWeight: 800, color: "white", lineHeight: 1.3, marginBottom: "2.5rem" }}>
            Rejoignez la communauté<br />
            <span style={{ color: "#a78bfa" }}>agricole</span>
          </h2>

          <div style={{ display: "flex", flexDirection: "column", gap: "0" }}>
            {STEPS.map((s, i) => {
              const done = i < step;
              const active = i === step;
              return (
                <div key={s} style={{ display: "flex", alignItems: "flex-start", gap: "0.85rem", paddingBottom: i < STEPS.length - 1 ? "1.5rem" : 0, position: "relative" }}>
                  {i < STEPS.length - 1 && (
                    <div style={{ position: "absolute", left: 15, top: 32, width: 2, height: "calc(100% - 16px)", background: done ? "#a78bfa" : "rgba(255,255,255,0.1)" }} />
                  )}
                  <div style={{ width: 32, height: 32, borderRadius: "50%", background: done ? "#a78bfa" : active ? "rgba(167,139,250,0.2)" : "rgba(255,255,255,0.08)", border: `2px solid ${done ? "#a78bfa" : active ? "rgba(167,139,250,0.6)" : "rgba(255,255,255,0.15)"}`, display: "flex", alignItems: "center", justifyContent: "center", flexShrink: 0, transition: "all 0.3s" }}>
                    {done ? <CheckIcon /> : <span style={{ fontSize: "0.75rem", fontWeight: 700, color: active ? "#a78bfa" : "rgba(255,255,255,0.4)" }}>{i + 1}</span>}
                  </div>
                  <div style={{ paddingTop: "0.3rem" }}>
                    <div style={{ fontSize: "0.85rem", fontWeight: done || active ? 700 : 500, color: done || active ? "white" : "rgba(255,255,255,0.4)", transition: "all 0.3s" }}>{s}</div>
                    {active && <div style={{ fontSize: "0.75rem", color: "#a78bfa", fontWeight: 500, marginTop: "0.2rem" }}>Étape en cours</div>}
                    {done && <div style={{ fontSize: "0.75rem", color: "rgba(167,139,250,0.7)", fontWeight: 500, marginTop: "0.2rem" }}>Complété ✓</div>}
                  </div>
                </div>
              );
            })}
          </div>
        </motion.div>

        <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ duration: 0.5, delay: 0.5 }}
          style={{ position: "relative", marginTop: "2rem", paddingTop: "1.5rem", borderTop: "1px solid rgba(255,255,255,0.1)", color: "rgba(255,255,255,0.5)", fontSize: "0.82rem" }}>
          Déjà inscrit ?{" "}
          <Link to="/login" style={{ color: "#a78bfa", fontWeight: 600, textDecoration: "none" }}>Se connecter</Link>
        </motion.div>
      </div>

      {/* ── RIGHT PANEL ── */}
      <div style={{ flex: 1, display: "flex", alignItems: "center", justifyContent: "center", padding: "2rem" }}>
        <motion.div
          initial={{ opacity: 0, y: 24 }} animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.55, ease: [0.22, 1, 0.36, 1] }}
          style={{ width: "100%", maxWidth: "500px" }}>

          <div style={{ marginBottom: "2rem" }}>
            <div style={{ display: "flex", gap: "0.5rem", marginBottom: "1.25rem" }}>
              {STEPS.map((_, i) => (
                <div key={i} style={{ height: 4, flex: 1, borderRadius: "100px", background: i <= step ? "var(--primary)" : "var(--border)", transition: "background 0.4s" }} />
              ))}
            </div>
            <div style={{ fontSize: "0.78rem", color: "var(--text-muted)", fontWeight: 600, textTransform: "uppercase", letterSpacing: "0.06em", marginBottom: "0.4rem" }}>
              Étape {step + 1} sur {STEPS.length}
            </div>
            <h1 style={{ fontSize: "1.7rem", fontWeight: 800, color: "var(--text)", margin: 0, letterSpacing: "-0.03em" }}>
              {["Quel est votre profil ?", "Vos informations", "Sécurité du compte"][step]}
            </h1>
          </div>

          {/* error */}
          <AnimatePresence>
            {error && (
              <motion.div
                initial={{ opacity: 0, y: -8 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0, y: -8 }}
                transition={{ duration: 0.25 }}
                style={{ display: "flex", gap: "0.75rem", padding: "0.9rem 1rem", background: "rgba(239,68,68,0.08)", border: "1.5px solid rgba(239,68,68,0.25)", borderRadius: "12px", marginBottom: "1.5rem" }}>
                <svg width="18" height="18" viewBox="0 0 18 18" fill="none" style={{ flexShrink: 0, marginTop: 1 }}>
                  <circle cx="9" cy="9" r="8" stroke="#ef4444" strokeWidth="1.5"/>
                  <path d="M9 5v4M9 13v.5" stroke="#ef4444" strokeWidth="1.5" strokeLinecap="round"/>
                </svg>
                <span style={{ color: "#ef4444", fontSize: "0.9rem", fontWeight: 500 }}>{error}</span>
              </motion.div>
            )}
          </AnimatePresence>

          <form onSubmit={handleSubmit}>
            <AnimatePresence mode="wait">

              {/* STEP 0 – user type */}
              {step === 0 && (
                <motion.div key="step0"
                  initial={{ opacity: 0, x: 30 }} animate={{ opacity: 1, x: 0 }} exit={{ opacity: 0, x: -30 }}
                  transition={{ duration: 0.3, ease: [0.22, 1, 0.36, 1] }}>
                  <p style={{ color: "var(--text-muted)", fontSize: "0.9rem", marginBottom: "1.5rem" }}>
                    Sélectionnez le profil qui correspond à votre activité.
                  </p>
                  <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "0.85rem", marginBottom: "1.75rem" }}>
                    {USER_TYPES.map(t => {
                      const selected = userType === t.value;
                      return (
                        <motion.button key={t.value} type="button"
                          onClick={() => setUserType(t.value)}
                          whileHover={{ scale: 1.02 }} whileTap={{ scale: 0.97 }}
                          style={{
                            padding: "1.1rem", borderRadius: "14px", cursor: "pointer",
                            border: selected ? `2px solid ${t.color}` : "1.5px solid var(--border)",
                            background: selected ? `${t.color}10` : "var(--surface)",
                            textAlign: "left", transition: "all 0.2s",
                            boxShadow: selected ? `0 0 0 4px ${t.color}18` : "none",
                            position: "relative",
                          }}>
                          {selected && (
                            <motion.div initial={{ scale: 0 }} animate={{ scale: 1 }} transition={{ type: "spring", stiffness: 400 }}
                              style={{ position: "absolute", top: "0.6rem", right: "0.6rem", width: 20, height: 20, borderRadius: "50%", background: t.color, display: "flex", alignItems: "center", justifyContent: "center" }}>
                              <CheckIcon />
                            </motion.div>
                          )}
                          <div style={{ fontSize: "1.6rem", marginBottom: "0.5rem" }}>{t.icon}</div>
                          <div style={{ fontSize: "0.9rem", fontWeight: 700, color: selected ? t.color : "var(--text)", marginBottom: "0.25rem" }}>{t.label}</div>
                          <div style={{ fontSize: "0.75rem", color: "var(--text-muted)", lineHeight: 1.4 }}>{t.desc}</div>
                        </motion.button>
                      );
                    })}
                  </div>
                </motion.div>
              )}

              {/* STEP 1 – name + phone */}
              {step === 1 && (
                <motion.div key="step1"
                  initial={{ opacity: 0, x: 30 }} animate={{ opacity: 1, x: 0 }} exit={{ opacity: 0, x: -30 }}
                  transition={{ duration: 0.3, ease: [0.22, 1, 0.36, 1] }}
                  style={{ display: "flex", flexDirection: "column", gap: "1.1rem", marginBottom: "1.75rem" }}>
                  <RegField label="Nom complet">
                    <div style={{ position: "relative" }}>
                      <div style={{ position: "absolute", left: "0.9rem", top: "50%", transform: "translateY(-50%)", color: "var(--text-muted)" }}><UserIcon /></div>
                      <input type="text" value={name} onChange={e => setName(e.target.value)}
                        placeholder="Jean Koffi" required
                        style={inputStyle}
                        onFocus={onFocusStyle} onBlur={onBlurStyle} />
                    </div>
                  </RegField>
                  <RegField label="Numéro de téléphone" hint="+228 suivi de votre numéro">
                    <div style={{ position: "relative" }}>
                      <div style={{ position: "absolute", left: "0.9rem", top: "50%", transform: "translateY(-50%)", color: "var(--text-muted)" }}><PhoneIcon /></div>
                      <input type="tel" value={phone} onChange={e => setPhone(e.target.value)}
                        placeholder="+228 90 12 34 56" required
                        style={inputStyle}
                        onFocus={onFocusStyle} onBlur={onBlurStyle} />
                    </div>
                  </RegField>
                </motion.div>
              )}

              {/* STEP 2 – password */}
              {step === 2 && (
                <motion.div key="step2"
                  initial={{ opacity: 0, x: 30 }} animate={{ opacity: 1, x: 0 }} exit={{ opacity: 0, x: -30 }}
                  transition={{ duration: 0.3, ease: [0.22, 1, 0.36, 1] }}
                  style={{ marginBottom: "1.75rem" }}>
                  <RegField label="Mot de passe" hint="Minimum 8 caractères">
                    <div style={{ position: "relative" }}>
                      <div style={{ position: "absolute", left: "0.9rem", top: "50%", transform: "translateY(-50%)", color: "var(--text-muted)" }}><LockIcon /></div>
                      <input type={showPwd ? "text" : "password"} value={password}
                        onChange={e => setPassword(e.target.value)} required placeholder="Choisissez un mot de passe"
                        style={{ ...inputStyle, paddingRight: "3rem" }}
                        onFocus={onFocusStyle} onBlur={onBlurStyle} />
                      <button type="button" onClick={() => setShowPwd(v => !v)}
                        style={{ position: "absolute", right: "0.9rem", top: "50%", transform: "translateY(-50%)", background: "none", border: "none", cursor: "pointer", color: "var(--text-muted)", padding: 0, display: "flex" }}>
                        <EyeIcon open={showPwd} />
                      </button>
                    </div>
                    {password.length > 0 && (
                      <motion.div initial={{ opacity: 0, height: 0 }} animate={{ opacity: 1, height: "auto" }} style={{ marginTop: "0.75rem" }}>
                        <div style={{ display: "flex", gap: "4px", marginBottom: "0.35rem" }}>
                          {[1, 2, 3, 4].map(i => (
                            <div key={i} style={{ flex: 1, height: 4, borderRadius: "100px", background: i <= pwdStrength ? pwdColor : "var(--border)", transition: "background 0.3s" }} />
                          ))}
                        </div>
                        <div style={{ fontSize: "0.78rem", fontWeight: 600, color: pwdColor }}>{pwdLabel}</div>
                      </motion.div>
                    )}
                  </RegField>

                  {/* summary */}
                  <div style={{ marginTop: "1.5rem", padding: "1rem", background: "var(--bg-secondary)", borderRadius: "12px", border: "1px solid var(--border)" }}>
                    <div style={{ fontSize: "0.75rem", fontWeight: 700, color: "var(--text-secondary)", textTransform: "uppercase", letterSpacing: "0.05em", marginBottom: "0.75rem" }}>Récapitulatif</div>
                    {[
                      ["Profil", USER_TYPES.find(t => t.value === userType)?.label || ""],
                      ["Nom", name],
                      ["Téléphone", phone],
                    ].map(([label, val]) => (
                      <div key={label} style={{ display: "flex", justifyContent: "space-between", marginBottom: "0.4rem" }}>
                        <span style={{ color: "var(--text-muted)", fontSize: "0.85rem" }}>{label}</span>
                        <span style={{ color: "var(--text)", fontSize: "0.85rem", fontWeight: 600 }}>{val}</span>
                      </div>
                    ))}
                  </div>
                </motion.div>
              )}
            </AnimatePresence>

            <div style={{ display: "flex", gap: "0.75rem" }}>
              {step > 0 && (
                <motion.button type="button" onClick={() => { setStep(s => s - 1); setError(""); }}
                  whileHover={{ scale: 1.01 }} whileTap={{ scale: 0.98 }}
                  style={{ flex: "0 0 auto", padding: "0.85rem 1.25rem", background: "var(--bg)", border: "1.5px solid var(--border)", borderRadius: "12px", color: "var(--text-secondary)", fontWeight: 600, fontSize: "0.95rem", cursor: "pointer" }}>
                  ← Retour
                </motion.button>
              )}
              <motion.button type="submit" disabled={!canProceed || loading}
                whileHover={canProceed && !loading ? { scale: 1.01 } : {}}
                whileTap={canProceed && !loading ? { scale: 0.98 } : {}}
                style={{
                  flex: 1, padding: "0.85rem",
                  background: canProceed ? "linear-gradient(135deg, #4338ca, #6366f1)" : "var(--bg-secondary)",
                  color: canProceed ? "white" : "var(--text-muted)",
                  border: "none", borderRadius: "12px", fontSize: "1rem", fontWeight: 700,
                  cursor: canProceed && !loading ? "pointer" : "not-allowed",
                  display: "flex", alignItems: "center", justifyContent: "center", gap: "0.5rem",
                  boxShadow: canProceed ? "0 4px 16px rgba(99,102,241,0.3)" : "none",
                  transition: "all 0.25s",
                  opacity: loading ? 0.85 : 1,
                }}>
                {loading ? (
                  <>
                    <motion.div animate={{ rotate: 360 }} transition={{ duration: 0.7, repeat: Infinity, ease: "linear" }}
                      style={{ width: 18, height: 18, border: "2px solid rgba(255,255,255,0.35)", borderTop: "2px solid white", borderRadius: "50%" }} />
                    Inscription...
                  </>
                ) : step < 2 ? "Continuer →" : "Créer mon compte →"}
              </motion.button>
            </div>
          </form>

          <div style={{ textAlign: "center", marginTop: "1.75rem", color: "var(--text-muted)", fontSize: "0.9rem" }}>
            Déjà inscrit ?{" "}
            <Link to="/login" style={{ color: "#6366f1", fontWeight: 700, textDecoration: "none" }}>
              Se connecter
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

const inputStyle: React.CSSProperties = {
  width: "100%", padding: "0.8rem 0.9rem 0.8rem 2.8rem",
  border: "1.5px solid var(--border)", borderRadius: "12px",
  background: "var(--bg)", color: "var(--text)", fontSize: "1rem",
  outline: "none", transition: "border-color 0.2s, box-shadow 0.2s",
  boxSizing: "border-box",
};

function onFocusStyle(e: React.FocusEvent<HTMLInputElement>) {
  e.target.style.borderColor = "#6366f1";
  e.target.style.boxShadow = "0 0 0 3px rgba(99,102,241,0.12)";
}

function onBlurStyle(e: React.FocusEvent<HTMLInputElement>) {
  e.target.style.borderColor = "var(--border)";
  e.target.style.boxShadow = "none";
}

function RegField({ label, hint, children }: { label: string; hint?: string; children: React.ReactNode }) {
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
