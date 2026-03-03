import React, { useState } from "react";
import { useNavigate, Link } from "react-router-dom";
import { motion, AnimatePresence } from "framer-motion";
import { signUp } from "../lib/auth-client";
import { neonExchange } from "../api/auth";

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

const UserIcon = () => (
  <svg width="18" height="18" viewBox="0 0 18 18" fill="none">
    <circle cx="9" cy="6" r="3.5" stroke="currentColor" strokeWidth="1.4"/>
    <path d="M2 16c0-3.5 3-6 7-6s7 2.5 7 6" stroke="currentColor" strokeWidth="1.4" strokeLinecap="round"/>
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

const IconExploitant = ({ color }: { color: string }) => (
  <svg width="24" height="24" viewBox="0 0 24 24" fill="none">
    <path d="M3 18c0-4 3.5-7 9-7s9 3 9 7" stroke={color} strokeWidth="1.5" strokeLinecap="round"/>
    <path d="M12 11V4M9 7l3-3 3 3" stroke={color} strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round"/>
    <path d="M5 18c1-2 3-3 5-3h4c2 0 4 1 5 3" stroke={color} strokeWidth="1.5" strokeLinecap="round"/>
  </svg>
);
const IconAgronome = ({ color }: { color: string }) => (
  <svg width="24" height="24" viewBox="0 0 24 24" fill="none">
    <circle cx="12" cy="7" r="4" stroke={color} strokeWidth="1.5"/>
    <path d="M4 20c0-4 3.6-7 8-7s8 3 8 7" stroke={color} strokeWidth="1.5" strokeLinecap="round"/>
    <rect x="15" y="1" width="5" height="3" rx="1" stroke={color} strokeWidth="1.2"/>
  </svg>
);
const IconOuvrier = ({ color }: { color: string }) => (
  <svg width="24" height="24" viewBox="0 0 24 24" fill="none">
    <circle cx="12" cy="7" r="4" stroke={color} strokeWidth="1.5"/>
    <path d="M4 20c0-4 3.6-7 8-7s8 3 8 7" stroke={color} strokeWidth="1.5" strokeLinecap="round"/>
    <path d="M8 10l-2 4h2l-1 3M16 10l2 4h-2l1 3" stroke={color} strokeWidth="1.3" strokeLinecap="round"/>
  </svg>
);
const IconAcheteur = ({ color }: { color: string }) => (
  <svg width="24" height="24" viewBox="0 0 24 24" fill="none">
    <path d="M6 2L3 6v14a2 2 0 002 2h14a2 2 0 002-2V6l-3-4z" stroke={color} strokeWidth="1.5" strokeLinejoin="round"/>
    <path d="M3 6h18M16 10a4 4 0 01-8 0" stroke={color} strokeWidth="1.5" strokeLinecap="round"/>
  </svg>
);
const IconInstitution = ({ color }: { color: string }) => (
  <svg width="24" height="24" viewBox="0 0 24 24" fill="none">
    <path d="M3 21h18M3 10h18M5 6l7-3 7 3M4 10v11M20 10v11M8 10v11M12 10v11M16 10v11" stroke={color} strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round"/>
  </svg>
);

const USER_TYPES = [
  { value: "EXPLOITANT", label: "Exploitant Agricole", desc: "Je cultive de la terre", icon: IconExploitant, color: "#16a34a" },
  { value: "AGRONOME", label: "Agronome", desc: "Je conseille les agriculteurs", icon: IconAgronome, color: "#7c3aed" },
  { value: "OUVRIER", label: "Ouvrier Agricole", desc: "Je cherche du travail agricole", icon: IconOuvrier, color: "#d97706" },
  { value: "ACHETEUR", label: "Acheteur", desc: "J'achète des produits agricoles", icon: IconAcheteur, color: "#0891b2" },
  { value: "INSTITUTION", label: "Institution", desc: "Organisation publique ou privée", icon: IconInstitution, color: "#dc2626" },
];

function pwdStrength(pwd: string) {
  let score = 0;
  if (pwd.length >= 8) score++;
  if (/[A-Z]/.test(pwd)) score++;
  if (/[0-9]/.test(pwd)) score++;
  if (/[^A-Za-z0-9]/.test(pwd)) score++;
  return score;
}

function AuthField({ label, children }: { label: string; children: React.ReactNode }) {
  return (
    <div style={{ display: "flex", flexDirection: "column", gap: "0.4rem" }}>
      <label style={{ fontSize: "0.85rem", fontWeight: 600, color: "var(--text)" }}>{label}</label>
      {children}
    </div>
  );
}

export default function Register() {
  const [step, setStep] = useState(1);
  const [userType, setUserType] = useState("");
  const [name, setName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [confirm, setConfirm] = useState("");
  const [showPwd, setShowPwd] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const navigate = useNavigate();

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
      const result = await signUp.email({ email, password, name });
      if (result.error) {
        setError(result.error.message || "Inscription échouée. Cet email est peut-être déjà utilisé.");
        return;
      }
      const token = (result.data as any)?.session?.token;
      if (!token) {
        setError("Compte créé mais impossible d'ouvrir la session. Essayez de vous connecter.");
        navigate("/login");
        return;
      }
      const nameParts = name.trim().split(" ");
      const first_name = nameParts[0] || "";
      const last_name = nameParts.slice(1).join(" ") || "";
      await neonExchange({ token, user_type: userType, first_name, last_name });
      navigate("/home");
    } catch (err: any) {
      setError(err?.message || "Une erreur est survenue. Réessayez.");
    } finally {
      setLoading(false);
    }
  }

  const accentColor = userType ? (USER_TYPES.find(t => t.value === userType)?.color || "#7c3aed") : "#7c3aed";

  return (
    <div style={{ minHeight: "100vh", display: "flex", background: "var(--bg)" }}>

      <div style={{
        flex: "0 0 420px", display: "flex", flexDirection: "column",
        background: `linear-gradient(160deg, #1e0a3c 0%, #3b0764 50%, #4c1d95 100%)`,
        padding: "3rem", position: "relative", overflow: "hidden",
      }} className="auth-left-panel">
        <div style={{ position: "absolute", inset: 0, backgroundImage: "linear-gradient(rgba(255,255,255,0.02) 1px, transparent 1px), linear-gradient(90deg, rgba(255,255,255,0.02) 1px, transparent 1px)", backgroundSize: "60px 60px" }} />
        <div style={{ position: "absolute", inset: 0, backgroundImage: "radial-gradient(circle at 70% 30%, rgba(167,139,250,0.12) 0%, transparent 50%)" }} />

        <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} style={{ position: "relative", display: "flex", alignItems: "center", gap: "10px", marginBottom: "3rem" }}>
          <div style={{ width: 36, height: 36, background: "rgba(167,139,250,0.2)", border: "1px solid rgba(167,139,250,0.4)", borderRadius: "10px", display: "flex", alignItems: "center", justifyContent: "center" }}>
            <svg width="20" height="20" viewBox="0 0 20 20" fill="none">
              <path d="M10 2C6 2 3 5 3 8c0 4.5 7 10 7 10s7-5.5 7-10c0-3-3-6-7-6z" fill="#a78bfa" fillOpacity="0.9"/>
              <circle cx="10" cy="8" r="2.5" fill="white" fillOpacity="0.9"/>
            </svg>
          </div>
          <span style={{ color: "white", fontSize: "1.3rem", fontWeight: 800, letterSpacing: "-0.02em" }}>Haroo</span>
        </motion.div>

        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.5 }} style={{ position: "relative", flexGrow: 1 }}>
          <h2 style={{ fontSize: "clamp(1.5rem, 2.5vw, 2rem)", fontWeight: 800, color: "white", lineHeight: 1.3, marginBottom: "1.5rem" }}>
            Rejoignez la plateforme<br /><span style={{ color: "#a78bfa" }}>agricole du Togo.</span>
          </h2>
          <div style={{ display: "flex", flexDirection: "column", gap: "1.2rem" }}>
            {[
              { step: 1, label: "Choisir votre profil" },
              { step: 2, label: "Créer votre compte" },
            ].map(s => (
              <div key={s.step} style={{ display: "flex", alignItems: "center", gap: "0.85rem" }}>
                <div style={{
                  width: 32, height: 32, borderRadius: "50%", display: "flex", alignItems: "center", justifyContent: "center", flexShrink: 0,
                  background: step > s.step ? "rgba(167,139,250,0.3)" : step === s.step ? "rgba(167,139,250,0.2)" : "rgba(255,255,255,0.05)",
                  border: step >= s.step ? "1.5px solid rgba(167,139,250,0.5)" : "1.5px solid rgba(255,255,255,0.1)",
                  fontSize: "0.8rem", fontWeight: 700, color: step >= s.step ? "#a78bfa" : "rgba(255,255,255,0.3)",
                }}>
                  {step > s.step ? <CheckIcon /> : s.step}
                </div>
                <span style={{ fontSize: "0.9rem", fontWeight: step === s.step ? 600 : 400, color: step >= s.step ? "rgba(255,255,255,0.9)" : "rgba(255,255,255,0.35)" }}>
                  {s.label}
                </span>
              </div>
            ))}
          </div>
        </motion.div>
      </div>

      <div style={{ flex: 1, display: "flex", alignItems: "center", justifyContent: "center", padding: "2rem", minHeight: "100vh" }}>
        <motion.div
          initial={{ opacity: 0, y: 24 }} animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.55, ease: [0.22, 1, 0.36, 1] }}
          style={{ width: "100%", maxWidth: "480px" }}>

          <AnimatePresence>
            {error && (
              <motion.div
                initial={{ opacity: 0, y: -8 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0, y: -8 }}
                style={{ display: "flex", alignItems: "flex-start", gap: "0.75rem", padding: "0.9rem 1rem", background: "rgba(239,68,68,0.08)", border: "1.5px solid rgba(239,68,68,0.25)", borderRadius: "12px", marginBottom: "1.5rem" }}>
                <svg width="18" height="18" viewBox="0 0 18 18" fill="none" style={{ flexShrink: 0, marginTop: 1 }}>
                  <circle cx="9" cy="9" r="8" stroke="#ef4444" strokeWidth="1.5"/>
                  <path d="M9 5v4M9 13v.5" stroke="#ef4444" strokeWidth="1.5" strokeLinecap="round"/>
                </svg>
                <span style={{ color: "#ef4444", fontSize: "0.9rem", fontWeight: 500, lineHeight: 1.5 }}>{error}</span>
              </motion.div>
            )}
          </AnimatePresence>

          <AnimatePresence mode="wait">

            {step === 1 && (
              <motion.div key="step1"
                initial={{ opacity: 0, x: 30 }} animate={{ opacity: 1, x: 0 }} exit={{ opacity: 0, x: -30 }}
                transition={{ duration: 0.3 }}>
                <div style={{ marginBottom: "2rem" }}>
                  <h1 style={{ fontSize: "1.7rem", fontWeight: 800, color: "var(--text)", margin: "0 0 0.5rem", letterSpacing: "-0.03em" }}>Quel est votre profil ?</h1>
                  <p style={{ color: "var(--text-muted)", fontSize: "0.95rem", margin: 0 }}>Choisissez le type de compte qui vous correspond.</p>
                </div>
                <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "0.85rem" }}>
                  {USER_TYPES.map(t => {
                    const Icon = t.icon;
                    const selected = userType === t.value;
                    return (
                      <motion.button key={t.value} type="button" onClick={() => setUserType(t.value)}
                        whileTap={{ scale: 0.97 }}
                        style={{
                          padding: "1.1rem 1rem", border: selected ? `2px solid ${t.color}` : "1.5px solid var(--border)",
                          borderRadius: "14px", background: selected ? `${t.color}12` : "var(--card)",
                          cursor: "pointer", textAlign: "left", transition: "all 0.2s",
                          boxShadow: selected ? `0 0 0 3px ${t.color}20` : "none",
                        }}>
                        <div style={{ color: t.color, marginBottom: "0.6rem" }}>
                          <Icon color={t.color} />
                        </div>
                        <div style={{ fontSize: "0.88rem", fontWeight: 700, color: "var(--text)", marginBottom: "0.2rem" }}>{t.label}</div>
                        <div style={{ fontSize: "0.75rem", color: "var(--text-muted)", lineHeight: 1.4 }}>{t.desc}</div>
                      </motion.button>
                    );
                  })}
                </div>
                <motion.button
                  type="button" onClick={() => { setError(""); setStep(2); }}
                  disabled={!userType}
                  whileTap={{ scale: 0.98 }}
                  style={{ width: "100%", padding: "0.9rem", background: userType ? accentColor : "var(--border)", color: "white", border: "none", borderRadius: "12px", fontSize: "1rem", fontWeight: 700, cursor: userType ? "pointer" : "not-allowed", marginTop: "1.5rem", transition: "background 0.2s", boxShadow: userType ? `0 4px 14px ${accentColor}40` : "none" }}>
                  Continuer
                </motion.button>
                <p style={{ textAlign: "center", fontSize: "0.9rem", color: "var(--text-muted)", marginTop: "1.5rem" }}>
                  Déjà inscrit ?{" "}
                  <Link to="/login" style={{ color: accentColor, fontWeight: 600, textDecoration: "none" }}>Se connecter</Link>
                </p>
              </motion.div>
            )}

            {step === 2 && (
              <motion.div key="step2"
                initial={{ opacity: 0, x: 30 }} animate={{ opacity: 1, x: 0 }} exit={{ opacity: 0, x: -30 }}
                transition={{ duration: 0.3 }}>
                <div style={{ marginBottom: "2rem", display: "flex", alignItems: "center", gap: "1rem" }}>
                  <button type="button" onClick={() => setStep(1)}
                    style={{ background: "none", border: "1.5px solid var(--border)", borderRadius: "10px", width: 36, height: 36, display: "flex", alignItems: "center", justifyContent: "center", cursor: "pointer", color: "var(--text-muted)", flexShrink: 0 }}>
                    <svg width="16" height="16" viewBox="0 0 16 16" fill="none"><path d="M10 3L5 8l5 5" stroke="currentColor" strokeWidth="1.6" strokeLinecap="round" strokeLinejoin="round"/></svg>
                  </button>
                  <div>
                    <h1 style={{ fontSize: "1.5rem", fontWeight: 800, color: "var(--text)", margin: "0 0 0.25rem", letterSpacing: "-0.03em" }}>Créer votre compte</h1>
                    <p style={{ color: "var(--text-muted)", fontSize: "0.88rem", margin: 0 }}>
                      Compte : <strong style={{ color: accentColor }}>{USER_TYPES.find(t => t.value === userType)?.label}</strong>
                    </p>
                  </div>
                </div>

                <form onSubmit={handleSubmit} style={{ display: "flex", flexDirection: "column", gap: "1rem" }}>

                  <AuthField label="Nom complet">
                    <div style={{ position: "relative" }}>
                      <div style={{ position: "absolute", left: "0.9rem", top: "50%", transform: "translateY(-50%)", color: "var(--text-muted)" }}>
                        <UserIcon />
                      </div>
                      <input type="text" value={name} onChange={e => setName(e.target.value)}
                        placeholder="Prénom Nom" required
                        style={{ width: "100%", padding: "0.8rem 0.9rem 0.8rem 2.8rem", border: "1.5px solid var(--border)", borderRadius: "12px", background: "var(--bg)", color: "var(--text)", fontSize: "1rem", outline: "none", transition: "border-color 0.2s, box-shadow 0.2s", boxSizing: "border-box" }}
                        onFocus={e => { e.target.style.borderColor = accentColor; e.target.style.boxShadow = `0 0 0 3px ${accentColor}20`; }}
                        onBlur={e => { e.target.style.borderColor = "var(--border)"; e.target.style.boxShadow = "none"; }}
                      />
                    </div>
                  </AuthField>

                  <AuthField label="Adresse email">
                    <div style={{ position: "relative" }}>
                      <div style={{ position: "absolute", left: "0.9rem", top: "50%", transform: "translateY(-50%)", color: "var(--text-muted)" }}>
                        <MailIcon />
                      </div>
                      <input type="email" value={email} onChange={e => setEmail(e.target.value)}
                        placeholder="vous@exemple.com" required
                        style={{ width: "100%", padding: "0.8rem 0.9rem 0.8rem 2.8rem", border: "1.5px solid var(--border)", borderRadius: "12px", background: "var(--bg)", color: "var(--text)", fontSize: "1rem", outline: "none", transition: "border-color 0.2s, box-shadow 0.2s", boxSizing: "border-box" }}
                        onFocus={e => { e.target.style.borderColor = accentColor; e.target.style.boxShadow = `0 0 0 3px ${accentColor}20`; }}
                        onBlur={e => { e.target.style.borderColor = "var(--border)"; e.target.style.boxShadow = "none"; }}
                      />
                    </div>
                  </AuthField>

                  <AuthField label="Mot de passe">
                    <div style={{ position: "relative" }}>
                      <div style={{ position: "absolute", left: "0.9rem", top: "50%", transform: "translateY(-50%)", color: "var(--text-muted)" }}>
                        <LockIcon />
                      </div>
                      <input type={showPwd ? "text" : "password"} value={password} onChange={e => setPassword(e.target.value)}
                        placeholder="Au moins 8 caractères" required minLength={8}
                        style={{ width: "100%", padding: "0.8rem 3rem 0.8rem 2.8rem", border: "1.5px solid var(--border)", borderRadius: "12px", background: "var(--bg)", color: "var(--text)", fontSize: "1rem", outline: "none", transition: "border-color 0.2s, box-shadow 0.2s", boxSizing: "border-box" }}
                        onFocus={e => { e.target.style.borderColor = accentColor; e.target.style.boxShadow = `0 0 0 3px ${accentColor}20`; }}
                        onBlur={e => { e.target.style.borderColor = "var(--border)"; e.target.style.boxShadow = "none"; }}
                      />
                      <button type="button" onClick={() => setShowPwd(!showPwd)}
                        style={{ position: "absolute", right: "0.9rem", top: "50%", transform: "translateY(-50%)", background: "none", border: "none", cursor: "pointer", color: "var(--text-muted)", padding: 0 }}>
                        <EyeIcon open={showPwd} />
                      </button>
                    </div>
                    {password && (
                      <div style={{ display: "flex", gap: "4px", marginTop: "0.3rem" }}>
                        {[1, 2, 3, 4].map(i => (
                          <div key={i} style={{ flex: 1, height: 3, borderRadius: 2, background: i <= strength ? strengthColor : "var(--border)", transition: "background 0.3s" }} />
                        ))}
                        <span style={{ fontSize: "0.72rem", color: strengthColor, marginLeft: "0.5rem", fontWeight: 600, whiteSpace: "nowrap" }}>{strengthLabel}</span>
                      </div>
                    )}
                  </AuthField>

                  <AuthField label="Confirmer le mot de passe">
                    <div style={{ position: "relative" }}>
                      <div style={{ position: "absolute", left: "0.9rem", top: "50%", transform: "translateY(-50%)", color: "var(--text-muted)" }}>
                        <LockIcon />
                      </div>
                      <input type="password" value={confirm} onChange={e => setConfirm(e.target.value)}
                        placeholder="••••••••" required
                        style={{ width: "100%", padding: "0.8rem 0.9rem 0.8rem 2.8rem", border: `1.5px solid ${confirm && confirm !== password ? "#ef4444" : "var(--border)"}`, borderRadius: "12px", background: "var(--bg)", color: "var(--text)", fontSize: "1rem", outline: "none", transition: "border-color 0.2s, box-shadow 0.2s", boxSizing: "border-box" }}
                        onFocus={e => { e.target.style.borderColor = accentColor; e.target.style.boxShadow = `0 0 0 3px ${accentColor}20`; }}
                        onBlur={e => { e.target.style.borderColor = confirm && confirm !== password ? "#ef4444" : "var(--border)"; e.target.style.boxShadow = "none"; }}
                      />
                    </div>
                    {confirm && confirm !== password && (
                      <span style={{ fontSize: "0.75rem", color: "#ef4444" }}>Les mots de passe ne correspondent pas.</span>
                    )}
                  </AuthField>

                  <motion.button type="submit" disabled={loading} whileTap={{ scale: 0.98 }}
                    style={{ width: "100%", padding: "0.9rem", background: loading ? "var(--border)" : accentColor, color: "white", border: "none", borderRadius: "12px", fontSize: "1rem", fontWeight: 700, cursor: loading ? "not-allowed" : "pointer", marginTop: "0.5rem", transition: "background 0.2s", boxShadow: loading ? "none" : `0 4px 14px ${accentColor}40` }}>
                    {loading ? "Création du compte..." : "Créer mon compte"}
                  </motion.button>
                </form>

                <p style={{ textAlign: "center", fontSize: "0.85rem", color: "var(--text-muted)", marginTop: "1.5rem" }}>
                  En créant un compte, vous acceptez les{" "}
                  <span style={{ color: accentColor, cursor: "pointer", fontWeight: 500 }}>conditions d'utilisation</span> de Haroo.
                </p>
              </motion.div>
            )}
          </AnimatePresence>
        </motion.div>
      </div>
    </div>
  );
}
