import React, { useState, useEffect, useRef } from "react";
import { motion, AnimatePresence } from "framer-motion";
import {
  get2FAStatus,
  setup2FA,
  enable2FA,
  disable2FA,
  TwoFactorStatus,
  TwoFactorSetupData,
} from "../api/twoFactor";

type View = "status" | "setup" | "disable";
type SetupStep = 1 | 2 | 3;

function ShieldIcon({ enabled }: { enabled: boolean }) {
  return (
    <svg width="44" height="44" viewBox="0 0 24 24" fill="none" stroke={enabled ? "#16a34a" : "var(--muted)"} strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
      <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z" fill={enabled ? "rgba(22,163,74,0.1)" : "rgba(100,116,139,0.08)"} />
      {enabled && <polyline points="9 12 11 14 15 10" />}
    </svg>
  );
}

function CopyIcon() {
  return (
    <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <rect x="9" y="9" width="13" height="13" rx="2" />
      <path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1" />
    </svg>
  );
}

function OTPInput({ value, onChange }: { value: string; onChange: (v: string) => void }) {
  const refs = useRef<(HTMLInputElement | null)[]>([]);
  const digits = value.padEnd(6, "").split("").slice(0, 6);

  function handleChange(i: number, v: string) {
    const clean = v.replace(/\D/g, "").slice(-1);
    const arr = digits.map((d) => d || "");
    arr[i] = clean;
    const next = arr.join("");
    onChange(next);
    if (clean && i < 5) refs.current[i + 1]?.focus();
  }

  function handleKeyDown(i: number, e: React.KeyboardEvent) {
    if (e.key === "Backspace" && !digits[i] && i > 0) {
      refs.current[i - 1]?.focus();
    }
  }

  function handlePaste(e: React.ClipboardEvent) {
    const text = e.clipboardData.getData("text").replace(/\D/g, "").slice(0, 6);
    if (text) { onChange(text); setTimeout(() => refs.current[Math.min(text.length, 5)]?.focus(), 0); }
    e.preventDefault();
  }

  return (
    <div style={{ display: "flex", gap: 10, justifyContent: "center" }} onPaste={handlePaste}>
      {Array.from({ length: 6 }).map((_, i) => (
        <input
          key={i}
          ref={(el) => (refs.current[i] = el)}
          type="text"
          inputMode="numeric"
          maxLength={1}
          value={digits[i] || ""}
          onChange={(e) => handleChange(i, e.target.value)}
          onKeyDown={(e) => handleKeyDown(i, e)}
          style={{
            width: 48,
            height: 56,
            textAlign: "center",
            fontSize: 22,
            fontWeight: 700,
            borderRadius: 10,
            border: digits[i] ? "2px solid var(--primary)" : "2px solid var(--border)",
            background: "var(--bg)",
            color: "var(--text)",
            outline: "none",
            transition: "border-color 0.15s",
            fontVariantNumeric: "tabular-nums",
          }}
        />
      ))}
    </div>
  );
}

function StatusCard({
  status,
  onSetup,
  onDisable,
}: {
  status: TwoFactorStatus;
  onSetup: () => void;
  onDisable: () => void;
}) {
  const enabled = status.two_factor_enabled;

  return (
    <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }}>
      {/* Hero status */}
      <div style={{
        background: enabled ? "rgba(22,163,74,0.06)" : "var(--card)",
        border: `1px solid ${enabled ? "rgba(22,163,74,0.25)" : "var(--border)"}`,
        borderRadius: 16,
        padding: "2rem",
        marginBottom: "1.5rem",
        display: "flex",
        alignItems: "center",
        gap: "1.5rem",
      }}>
        <ShieldIcon enabled={enabled} />
        <div style={{ flex: 1 }}>
          <h2 style={{ margin: 0, fontSize: "1.1rem", fontWeight: 700, color: "var(--text)" }}>
            Authentification à deux facteurs
          </h2>
          <p style={{ margin: "4px 0 0", color: "var(--muted)", fontSize: 14 }}>
            {enabled
              ? "Votre compte est protégé par une couche de sécurité supplémentaire."
              : "Ajoutez une couche de sécurité supplémentaire à votre compte."}
          </p>
          <span style={{
            display: "inline-block",
            marginTop: 8,
            padding: "3px 10px",
            borderRadius: 20,
            fontSize: 12,
            fontWeight: 600,
            background: enabled ? "#dcfce7" : "#f1f5f9",
            color: enabled ? "#16a34a" : "#64748b",
          }}>
            {enabled ? "Activé" : "Désactivé"}
          </span>
          {status.two_factor_required && !enabled && (
            <span style={{
              display: "inline-block",
              marginTop: 8,
              marginLeft: 6,
              padding: "3px 10px",
              borderRadius: 20,
              fontSize: 12,
              fontWeight: 600,
              background: "#fef3c7",
              color: "#b45309",
            }}>
              Obligatoire pour votre compte
            </span>
          )}
        </div>
        <button
          onClick={enabled ? onDisable : onSetup}
          style={{
            padding: "9px 20px",
            borderRadius: 10,
            border: enabled ? "1px solid var(--border)" : "none",
            background: enabled ? "none" : "var(--primary)",
            color: enabled ? "var(--text)" : "#fff",
            fontWeight: 600,
            fontSize: 14,
            cursor: "pointer",
            whiteSpace: "nowrap",
          }}
        >
          {enabled ? "Désactiver" : "Activer le 2FA"}
        </button>
      </div>

      {/* Info cards */}
      <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(220px, 1fr))", gap: 12 }}>
        {[
          {
            icon: "📱",
            title: "Application TOTP",
            desc: "Fonctionne avec Google Authenticator, Authy, Microsoft Authenticator et toute application compatible.",
          },
          {
            icon: "🔑",
            title: "Codes de secours",
            desc: "8 codes de récupération générés à l'activation pour accéder à votre compte en cas de perte de téléphone.",
          },
          {
            icon: "🔒",
            title: "Protection renforcée",
            desc: "Même si votre mot de passe est compromis, votre compte reste inaccessible sans le code TOTP.",
          },
        ].map((card) => (
          <div
            key={card.title}
            style={{
              background: "var(--card)",
              border: "1px solid var(--border)",
              borderRadius: 12,
              padding: "1.1rem",
            }}
          >
            <div style={{ fontSize: 24, marginBottom: 8 }}>{card.icon}</div>
            <p style={{ margin: "0 0 4px", fontWeight: 600, fontSize: 14, color: "var(--text)" }}>{card.title}</p>
            <p style={{ margin: 0, fontSize: 13, color: "var(--muted)", lineHeight: 1.6 }}>{card.desc}</p>
          </div>
        ))}
      </div>
    </motion.div>
  );
}

function SetupWizard({ onBack, onDone }: { onBack: () => void; onDone: () => void }) {
  const [step, setStep] = useState<SetupStep>(1);
  const [setupData, setSetupData] = useState<TwoFactorSetupData | null>(null);
  const [token, setToken] = useState("");
  const [backupCodes, setBackupCodes] = useState<string[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [copied, setCopied] = useState(false);
  const [secretRevealed, setSecretRevealed] = useState(false);

  useEffect(() => {
    (async () => {
      setLoading(true);
      try {
        const data = await setup2FA();
        setSetupData(data);
      } catch (e: unknown) {
        const err = e as { response?: { data?: { error?: string } } };
        setError(err?.response?.data?.error || "Impossible de démarrer la configuration.");
      } finally {
        setLoading(false);
      }
    })();
  }, []);

  async function handleEnable() {
    if (token.length !== 6) { setError("Entrez un code à 6 chiffres."); return; }
    setError("");
    setLoading(true);
    try {
      const result = await enable2FA(token);
      setBackupCodes(result.backup_codes || []);
      setStep(3);
    } catch (e: unknown) {
      const err = e as { response?: { data?: { error?: string } } };
      setError(err?.response?.data?.error || "Code incorrect. Vérifiez votre application et réessayez.");
    } finally {
      setLoading(false);
    }
  }

  function copyAll() {
    navigator.clipboard.writeText(backupCodes.join("\n"));
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  }

  const qrSrc = setupData?.qr_code
    ? setupData.qr_code.startsWith("data:") ? setupData.qr_code : `data:image/png;base64,${setupData.qr_code}`
    : null;

  return (
    <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }}>
      {/* Back button */}
      {step !== 3 && (
        <button onClick={onBack} style={{
          background: "none", border: "none", cursor: "pointer",
          color: "var(--muted)", fontSize: 14, padding: "0 0 1.5rem",
          display: "flex", alignItems: "center", gap: 6,
        }}>
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round"><polyline points="15 18 9 12 15 6" /></svg>
          Retour
        </button>
      )}

      {/* Progress */}
      <div style={{ display: "flex", gap: 4, marginBottom: "2rem" }}>
        {[1, 2, 3].map((s) => (
          <div key={s} style={{
            flex: 1, height: 4, borderRadius: 4,
            background: s <= step ? "var(--primary)" : "var(--border)",
            transition: "background 0.4s",
          }} />
        ))}
      </div>

      <AnimatePresence mode="wait">
        {/* Step 1 — QR Code */}
        {step === 1 && (
          <motion.div key="s1" initial={{ opacity: 0, x: -20 }} animate={{ opacity: 1, x: 0 }} exit={{ opacity: 0, x: 20 }}>
            <h2 style={{ margin: "0 0 6px", fontSize: "1.2rem", fontWeight: 700, color: "var(--text)" }}>
              Scannez le QR code
            </h2>
            <p style={{ margin: "0 0 2rem", color: "var(--muted)", fontSize: 14, lineHeight: 1.7 }}>
              Ouvrez votre application d'authentification (Google Authenticator, Authy...) et scannez ce code.
            </p>

            {loading && (
              <div style={{ textAlign: "center", padding: "3rem 0" }}>
                <div style={{ width: 32, height: 32, borderRadius: "50%", border: "3px solid var(--border)", borderTopColor: "var(--primary)", margin: "0 auto 12px", animation: "spin 0.8s linear infinite" }} />
                <p style={{ color: "var(--muted)", fontSize: 14 }}>Génération du QR code...</p>
              </div>
            )}

            {error && !loading && (
              <div style={{ padding: "1rem", borderRadius: 10, background: "#fee2e2", color: "#dc2626", fontSize: 14, marginBottom: "1rem" }}>
                {error}
              </div>
            )}

            {!loading && qrSrc && (
              <div style={{ display: "flex", flexDirection: "column", alignItems: "center", gap: "1.5rem" }}>
                <div style={{
                  background: "#fff",
                  borderRadius: 16,
                  padding: 16,
                  border: "1px solid var(--border)",
                  boxShadow: "0 4px 20px rgba(0,0,0,0.06)",
                }}>
                  <img src={qrSrc} alt="QR Code 2FA" style={{ width: 200, height: 200, display: "block" }} />
                </div>

                {/* Manual secret */}
                <div style={{ width: "100%", maxWidth: 400 }}>
                  <p style={{ fontSize: 12, color: "var(--muted)", textAlign: "center", marginBottom: 8 }}>
                    Impossible de scanner ? Entrez le code manuellement :
                  </p>
                  <div style={{
                    display: "flex", alignItems: "center", gap: 8,
                    background: "var(--bg)", border: "1px solid var(--border)",
                    borderRadius: 10, padding: "10px 14px",
                  }}>
                    <code style={{
                      flex: 1, fontSize: 13, fontFamily: "monospace",
                      color: secretRevealed ? "var(--text)" : "transparent",
                      textShadow: secretRevealed ? "none" : "0 0 8px rgba(100,116,139,0.6)",
                      letterSpacing: 2, userSelect: secretRevealed ? "all" : "none",
                    }}>
                      {setupData?.secret}
                    </code>
                    <button onClick={() => setSecretRevealed(!secretRevealed)} style={{
                      background: "none", border: "none", cursor: "pointer",
                      color: "var(--muted)", fontSize: 12, fontWeight: 500, whiteSpace: "nowrap",
                    }}>
                      {secretRevealed ? "Masquer" : "Révéler"}
                    </button>
                  </div>
                </div>

                <button onClick={() => setStep(2)} style={{
                  width: "100%", maxWidth: 400,
                  padding: "12px", borderRadius: 10, border: "none",
                  background: "var(--primary)", color: "#fff",
                  fontWeight: 600, fontSize: 15, cursor: "pointer",
                }}>
                  J'ai scanné le code →
                </button>
              </div>
            )}
          </motion.div>
        )}

        {/* Step 2 — Verify token */}
        {step === 2 && (
          <motion.div key="s2" initial={{ opacity: 0, x: -20 }} animate={{ opacity: 1, x: 0 }} exit={{ opacity: 0, x: 20 }}>
            <h2 style={{ margin: "0 0 6px", fontSize: "1.2rem", fontWeight: 700, color: "var(--text)" }}>
              Vérifiez votre application
            </h2>
            <p style={{ margin: "0 0 2rem", color: "var(--muted)", fontSize: 14, lineHeight: 1.7 }}>
              Entrez le code à 6 chiffres affiché dans votre application d'authentification pour confirmer la configuration.
            </p>

            <div style={{ display: "flex", flexDirection: "column", alignItems: "center", gap: "1.5rem" }}>
              <OTPInput value={token} onChange={setToken} />

              {error && (
                <motion.p
                  initial={{ opacity: 0, y: -8 }}
                  animate={{ opacity: 1, y: 0 }}
                  style={{ color: "#dc2626", fontSize: 13, margin: 0, textAlign: "center" }}
                >
                  {error}
                </motion.p>
              )}

              <button
                disabled={token.length !== 6 || loading}
                onClick={handleEnable}
                style={{
                  width: "100%", maxWidth: 360,
                  padding: "13px", borderRadius: 10, border: "none",
                  background: token.length === 6 ? "var(--primary)" : "var(--border)",
                  color: token.length === 6 ? "#fff" : "var(--muted)",
                  fontWeight: 600, fontSize: 15,
                  cursor: token.length === 6 && !loading ? "pointer" : "not-allowed",
                  opacity: loading ? 0.7 : 1,
                  transition: "all 0.2s",
                }}
              >
                {loading ? "Vérification..." : "Activer le 2FA"}
              </button>

              <button onClick={() => { setToken(""); setStep(1); }} style={{
                background: "none", border: "none", cursor: "pointer",
                color: "var(--muted)", fontSize: 13,
              }}>
                Retour au QR code
              </button>
            </div>
          </motion.div>
        )}

        {/* Step 3 — Backup codes */}
        {step === 3 && (
          <motion.div key="s3" initial={{ opacity: 0, scale: 0.97 }} animate={{ opacity: 1, scale: 1 }}>
            {/* Success banner */}
            <div style={{
              background: "rgba(22,163,74,0.08)",
              border: "1px solid rgba(22,163,74,0.25)",
              borderRadius: 12,
              padding: "1.25rem",
              marginBottom: "1.75rem",
              display: "flex",
              gap: 12,
              alignItems: "flex-start",
            }}>
              <div style={{
                width: 36, height: 36, borderRadius: "50%",
                background: "#16a34a", display: "flex", alignItems: "center",
                justifyContent: "center", flexShrink: 0,
              }}>
                <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#fff" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
                  <polyline points="20 6 9 17 4 12" />
                </svg>
              </div>
              <div>
                <p style={{ margin: "0 0 2px", fontWeight: 700, color: "#16a34a", fontSize: 15 }}>2FA activé avec succès</p>
                <p style={{ margin: 0, fontSize: 13, color: "var(--text)" }}>
                  Votre compte est maintenant protégé par une double authentification.
                </p>
              </div>
            </div>

            <h3 style={{ margin: "0 0 8px", fontSize: "1rem", fontWeight: 700, color: "var(--text)" }}>
              Codes de secours
            </h3>
            <p style={{ margin: "0 0 1rem", fontSize: 13, color: "var(--muted)", lineHeight: 1.7 }}>
              Conservez ces codes dans un endroit sûr. Chaque code ne peut être utilisé qu'une seule fois pour accéder à votre compte si vous perdez votre téléphone.
            </p>

            <div style={{
              background: "#0f172a",
              borderRadius: 12,
              padding: "1.25rem",
              marginBottom: "1rem",
            }}>
              <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "8px 24px" }}>
                {backupCodes.map((code, i) => (
                  <div key={i} style={{ display: "flex", alignItems: "center", gap: 8 }}>
                    <span style={{ color: "#64748b", fontSize: 11, fontWeight: 600, minWidth: 18 }}>{i + 1}.</span>
                    <code style={{ color: "#e2e8f0", fontSize: 14, letterSpacing: 2, fontFamily: "monospace" }}>{code}</code>
                  </div>
                ))}
              </div>
            </div>

            <div style={{ display: "flex", gap: 8, marginBottom: "1.75rem" }}>
              <button onClick={copyAll} style={{
                flex: 1, padding: "10px", borderRadius: 10,
                border: "1px solid var(--border)", background: "none",
                color: copied ? "#16a34a" : "var(--text)",
                fontWeight: 600, fontSize: 14, cursor: "pointer",
                display: "flex", alignItems: "center", justifyContent: "center", gap: 6,
              }}>
                <CopyIcon />
                {copied ? "Copié !" : "Copier tous les codes"}
              </button>
            </div>

            <div style={{
              background: "#fef3c7",
              border: "1px solid #fde68a",
              borderRadius: 10,
              padding: "0.9rem 1rem",
              marginBottom: "1.5rem",
              fontSize: 13,
              color: "#92400e",
              lineHeight: 1.6,
            }}>
              <strong>Attention :</strong> Ces codes ne seront plus affichés. Si vous les perdez, vous devrez désactiver et réactiver le 2FA.
            </div>

            <button onClick={onDone} style={{
              width: "100%", padding: "13px", borderRadius: 10, border: "none",
              background: "var(--primary)", color: "#fff",
              fontWeight: 600, fontSize: 15, cursor: "pointer",
            }}>
              Terminer
            </button>
          </motion.div>
        )}
      </AnimatePresence>
    </motion.div>
  );
}

function DisableFlow({ onBack, onDone }: { onBack: () => void; onDone: () => void }) {
  const [password, setPassword] = useState("");
  const [showPw, setShowPw] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  async function handleDisable() {
    if (!password) { setError("Entrez votre mot de passe."); return; }
    setError("");
    setLoading(true);
    try {
      await disable2FA(password);
      onDone();
    } catch (e: unknown) {
      const err = e as { response?: { data?: { error?: string } } };
      setError(err?.response?.data?.error || "Mot de passe incorrect.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }}>
      <button onClick={onBack} style={{
        background: "none", border: "none", cursor: "pointer",
        color: "var(--muted)", fontSize: 14, padding: "0 0 1.5rem",
        display: "flex", alignItems: "center", gap: 6,
      }}>
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round"><polyline points="15 18 9 12 15 6" /></svg>
        Retour
      </button>

      <div style={{
        background: "#fee2e2",
        border: "1px solid #fecaca",
        borderRadius: 12,
        padding: "1.25rem",
        marginBottom: "2rem",
        display: "flex",
        gap: 12,
        alignItems: "flex-start",
      }}>
        <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="#dc2626" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" style={{ flexShrink: 0, marginTop: 1 }}>
          <triangle-path />
          <path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"/>
          <line x1="12" y1="9" x2="12" y2="13"/>
          <line x1="12" y1="17" x2="12.01" y2="17"/>
        </svg>
        <div>
          <p style={{ margin: "0 0 4px", fontWeight: 700, color: "#dc2626", fontSize: 14 }}>
            Désactiver la double authentification
          </p>
          <p style={{ margin: 0, fontSize: 13, color: "#7f1d1d", lineHeight: 1.6 }}>
            Cette action réduira la sécurité de votre compte. Votre mot de passe seul suffira pour vous connecter.
          </p>
        </div>
      </div>

      <h2 style={{ margin: "0 0 6px", fontSize: "1.1rem", fontWeight: 700, color: "var(--text)" }}>
        Confirmez votre identité
      </h2>
      <p style={{ margin: "0 0 1.5rem", color: "var(--muted)", fontSize: 14 }}>
        Entrez votre mot de passe actuel pour confirmer la désactivation du 2FA.
      </p>

      <div style={{ position: "relative", marginBottom: "1.25rem" }}>
        <input
          type={showPw ? "text" : "password"}
          placeholder="Mot de passe"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          onKeyDown={(e) => e.key === "Enter" && handleDisable()}
          style={{
            width: "100%", padding: "12px 44px 12px 14px",
            borderRadius: 10, border: error ? "1.5px solid #dc2626" : "1px solid var(--border)",
            background: "var(--bg)", color: "var(--text)", fontSize: 15,
            boxSizing: "border-box", outline: "none",
          }}
        />
        <button onClick={() => setShowPw(!showPw)} style={{
          position: "absolute", right: 12, top: "50%", transform: "translateY(-50%)",
          background: "none", border: "none", cursor: "pointer", color: "var(--muted)", padding: 0,
        }}>
          {showPw ? (
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <path d="M17.94 17.94A10.07 10.07 0 0 1 12 20c-7 0-11-8-11-8a18.45 18.45 0 0 1 5.06-5.94M9.9 4.24A9.12 9.12 0 0 1 12 4c7 0 11 8 11 8a18.5 18.5 0 0 1-2.16 3.19m-6.72-1.07a3 3 0 1 1-4.24-4.24"/>
              <line x1="1" y1="1" x2="23" y2="23"/>
            </svg>
          ) : (
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"/>
              <circle cx="12" cy="12" r="3"/>
            </svg>
          )}
        </button>
      </div>

      {error && (
        <p style={{ color: "#dc2626", fontSize: 13, margin: "-0.75rem 0 1rem" }}>{error}</p>
      )}

      <button
        disabled={!password || loading}
        onClick={handleDisable}
        style={{
          width: "100%", padding: "12px", borderRadius: 10, border: "none",
          background: password ? "#dc2626" : "var(--border)",
          color: password ? "#fff" : "var(--muted)",
          fontWeight: 600, fontSize: 15,
          cursor: password && !loading ? "pointer" : "not-allowed",
          opacity: loading ? 0.7 : 1,
          transition: "all 0.2s",
        }}
      >
        {loading ? "Désactivation..." : "Désactiver le 2FA"}
      </button>
    </motion.div>
  );
}

export default function Security() {
  const [view, setView] = useState<View>("status");
  const [twoFAStatus, setTwoFAStatus] = useState<TwoFactorStatus | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [toast, setToast] = useState("");

  async function loadStatus() {
    setLoading(true);
    setError("");
    try {
      const s = await get2FAStatus();
      setTwoFAStatus(s);
    } catch {
      setError("Impossible de charger le statut de sécurité.");
    } finally {
      setLoading(false);
    }
  }

  useEffect(() => { loadStatus(); }, []);

  function showToast(msg: string) {
    setToast(msg);
    setTimeout(() => setToast(""), 3500);
  }

  return (
    <div style={{ maxWidth: 700, margin: "0 auto", padding: "2.5rem 1.5rem 5rem" }}>
      {/* Toast */}
      <AnimatePresence>
        {toast && (
          <motion.div
            initial={{ opacity: 0, y: -20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -20 }}
            style={{
              position: "fixed", top: 80, left: "50%", transform: "translateX(-50%)",
              background: "#1a1a1a", color: "#fff", padding: "10px 20px",
              borderRadius: 10, fontSize: 14, fontWeight: 500, zIndex: 500,
              boxShadow: "0 8px 24px rgba(0,0,0,0.2)",
            }}
          >
            {toast}
          </motion.div>
        )}
      </AnimatePresence>

      {/* Page header */}
      <div style={{ marginBottom: "2rem" }}>
        <h1 style={{ margin: 0, fontSize: "1.75rem", fontWeight: 800, color: "var(--text)" }}>
          Sécurité
        </h1>
        <p style={{ margin: "6px 0 0", color: "var(--muted)", fontSize: 15 }}>
          Gérez les paramètres de sécurité de votre compte
        </p>
      </div>

      {loading && (
        <div style={{ textAlign: "center", padding: "5rem 0" }}>
          <div style={{ width: 32, height: 32, borderRadius: "50%", border: "3px solid var(--border)", borderTopColor: "var(--primary)", margin: "0 auto 12px", animation: "spin 0.8s linear infinite" }} />
          <p style={{ color: "var(--muted)", fontSize: 14 }}>Chargement...</p>
        </div>
      )}

      {!loading && error && (
        <div style={{ textAlign: "center", padding: "3rem 0" }}>
          <p style={{ color: "#dc2626", marginBottom: "1rem" }}>{error}</p>
          <button onClick={loadStatus} style={{ padding: "8px 18px", borderRadius: 8, border: "1px solid var(--border)", background: "none", color: "var(--text)", cursor: "pointer" }}>
            Réessayer
          </button>
        </div>
      )}

      {!loading && !error && twoFAStatus && (
        <AnimatePresence mode="wait">
          {view === "status" && (
            <motion.div key="status" initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}>
              <StatusCard
                status={twoFAStatus}
                onSetup={() => setView("setup")}
                onDisable={() => setView("disable")}
              />
            </motion.div>
          )}

          {view === "setup" && (
            <motion.div key="setup" initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}>
              <SetupWizard
                onBack={() => setView("status")}
                onDone={() => {
                  setView("status");
                  loadStatus();
                  showToast("2FA activé avec succès. Votre compte est maintenant sécurisé.");
                }}
              />
            </motion.div>
          )}

          {view === "disable" && (
            <motion.div key="disable" initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}>
              <DisableFlow
                onBack={() => setView("status")}
                onDone={() => {
                  setView("status");
                  loadStatus();
                  showToast("2FA désactivé.");
                }}
              />
            </motion.div>
          )}
        </AnimatePresence>
      )}

      <style>{`@keyframes spin { to { transform: rotate(360deg); } }`}</style>
    </div>
  );
}
