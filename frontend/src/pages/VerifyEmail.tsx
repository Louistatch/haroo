import React, { useState, useEffect } from "react";
import { Link, useSearchParams } from "react-router-dom";
import { motion } from "framer-motion";
import { verifyEmail, resendVerificationEmail } from "../api/auth";

type Status = "loading" | "success" | "error" | "no-token";

export default function VerifyEmail() {
  const [searchParams] = useSearchParams();
  const token = searchParams.get("token");

  const [status, setStatus] = useState<Status>(token ? "loading" : "no-token");
  const [message, setMessage] = useState("");
  const [resending, setResending] = useState(false);
  const [resendMsg, setResendMsg] = useState("");

  useEffect(() => {
    if (!token) return;
    (async () => {
      try {
        const res = await verifyEmail(token);
        setMessage(res.message || "Email vérifié avec succès.");
        setStatus("success");
      } catch (err: any) {
        const msg = err?.response?.data?.detail;
        setMessage(msg || "Lien expiré ou invalide.");
        setStatus("error");
      }
    })();
  }, [token]);

  async function handleResend() {
    setResending(true);
    setResendMsg("");
    try {
      await resendVerificationEmail();
      setResendMsg("Email de vérification renvoyé. Vérifiez votre boîte de réception.");
    } catch (err: any) {
      const msg = err?.response?.data?.detail || err?.response?.data?.message;
      setResendMsg(msg || "Erreur lors de l'envoi. Êtes-vous connecté ?");
    } finally {
      setResending(false);
    }
  }

  const icons: Record<Status, React.ReactNode> = {
    loading: (
      <div style={{ width: 40, height: 40, borderRadius: "50%", border: "3px solid var(--border)", borderTopColor: "var(--primary)", animation: "spin 0.8s linear infinite" }} />
    ),
    success: (
      <svg width="40" height="40" viewBox="0 0 24 24" fill="none" stroke="var(--primary)" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
        <polyline points="20 6 9 17 4 12"/>
      </svg>
    ),
    error: (
      <svg width="40" height="40" viewBox="0 0 24 24" fill="none" stroke="#ef4444" strokeWidth="2" strokeLinecap="round">
        <circle cx="12" cy="12" r="10"/><path d="M12 8v4M12 16h.01"/>
      </svg>
    ),
    "no-token": (
      <svg width="40" height="40" viewBox="0 0 24 24" fill="none" stroke="#f59e0b" strokeWidth="2" strokeLinecap="round">
        <circle cx="12" cy="12" r="10"/><path d="M12 8v4M12 16h.01"/>
      </svg>
    ),
  };

  const titles: Record<Status, string> = {
    loading: "Vérification en cours...",
    success: "Email vérifié",
    error: "Vérification échouée",
    "no-token": "Vérification d'email",
  };

  const bgColor: Record<Status, string> = {
    loading: "rgba(22,163,74,0.1)",
    success: "rgba(22,163,74,0.1)",
    error: "rgba(239,68,68,0.1)",
    "no-token": "rgba(245,158,11,0.1)",
  };

  return (
    <div style={{ minHeight: "100vh", display: "flex", alignItems: "center", justifyContent: "center", background: "var(--bg)", padding: "2rem" }}>
      <motion.div initial={{ opacity: 0, y: 24 }} animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
        style={{ width: "100%", maxWidth: 440, textAlign: "center" }}>

        <div style={{ width: 72, height: 72, borderRadius: "50%", background: bgColor[status], display: "flex", alignItems: "center", justifyContent: "center", margin: "0 auto 1.5rem" }}>
          {icons[status]}
        </div>

        <h1 style={{ fontSize: "1.5rem", fontWeight: 800, color: "var(--text)", margin: "0 0 0.75rem" }}>
          {titles[status]}
        </h1>

        {status === "loading" && (
          <p style={{ color: "var(--text-muted)", fontSize: "0.95rem" }}>
            Veuillez patienter pendant que nous vérifions votre adresse email...
          </p>
        )}

        {status === "success" && (
          <>
            <p style={{ color: "var(--text-muted)", fontSize: "0.95rem", lineHeight: 1.7, margin: "0 0 2rem" }}>
              {message}
            </p>
            <Link to="/home" style={{ display: "inline-flex", alignItems: "center", justifyContent: "center", width: "100%", padding: "0.9rem", background: "var(--primary)", color: "white", borderRadius: 12, fontSize: "1rem", fontWeight: 700, textDecoration: "none", boxShadow: "0 4px 14px rgba(22,163,74,0.3)" }}>
              Accéder à mon espace
            </Link>
          </>
        )}

        {status === "error" && (
          <>
            <p style={{ color: "var(--text-muted)", fontSize: "0.95rem", lineHeight: 1.7, margin: "0 0 1.5rem" }}>
              {message}
            </p>
            <div style={{ display: "flex", flexDirection: "column", gap: "0.75rem" }}>
              <button onClick={handleResend} disabled={resending}
                style={{ width: "100%", padding: "0.85rem", background: "var(--primary)", color: "white", border: "none", borderRadius: 12, fontSize: "0.95rem", fontWeight: 700, cursor: resending ? "wait" : "pointer", opacity: resending ? 0.7 : 1 }}>
                {resending ? "Envoi..." : "Renvoyer l'email de vérification"}
              </button>
              <Link to="/login" style={{ display: "block", color: "var(--primary)", fontWeight: 600, fontSize: "0.9rem", textDecoration: "none" }}>
                Retour à la connexion
              </Link>
            </div>
          </>
        )}

        {status === "no-token" && (
          <>
            <p style={{ color: "var(--text-muted)", fontSize: "0.95rem", lineHeight: 1.7, margin: "0 0 1.5rem" }}>
              Cliquez sur le lien reçu par email pour vérifier votre adresse, ou demandez un nouvel email ci-dessous.
            </p>
            <div style={{ display: "flex", flexDirection: "column", gap: "0.75rem" }}>
              <button onClick={handleResend} disabled={resending}
                style={{ width: "100%", padding: "0.85rem", background: "var(--primary)", color: "white", border: "none", borderRadius: 12, fontSize: "0.95rem", fontWeight: 700, cursor: resending ? "wait" : "pointer", opacity: resending ? 0.7 : 1 }}>
                {resending ? "Envoi..." : "Renvoyer l'email de vérification"}
              </button>
              <Link to="/home" style={{ display: "block", color: "var(--primary)", fontWeight: 600, fontSize: "0.9rem", textDecoration: "none" }}>
                Retour à l'accueil
              </Link>
            </div>
          </>
        )}

        {resendMsg && (
          <motion.p initial={{ opacity: 0 }} animate={{ opacity: 1 }}
            style={{ marginTop: "1rem", fontSize: "0.85rem", color: resendMsg.includes("Erreur") ? "#ef4444" : "var(--primary)", fontWeight: 500 }}>
            {resendMsg}
          </motion.p>
        )}

        <style>{`@keyframes spin { to { transform: rotate(360deg); } }`}</style>
      </motion.div>
    </div>
  );
}
