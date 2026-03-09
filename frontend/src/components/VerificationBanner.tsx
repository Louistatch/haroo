import React from "react";
import { useNavigate } from "react-router-dom";
import { motion } from "framer-motion";

interface Verification {
  is_verified: boolean;
  status: string;
  status_label: string;
  message: string;
  action_required: string;
  can_use_platform: boolean;
}

const IconShield = () => (
  <svg width="20" height="20" viewBox="0 0 20 20" fill="none">
    <path d="M10 1L2 5v5c0 4.4 3.4 8.6 8 9.9 4.6-1.3 8-5.5 8-9.9V5l-8-4z" stroke="currentColor" strokeWidth="1.5" strokeLinejoin="round"/>
  </svg>
);
const IconClock = () => (
  <svg width="20" height="20" viewBox="0 0 20 20" fill="none">
    <circle cx="10" cy="10" r="8" stroke="currentColor" strokeWidth="1.5"/>
    <path d="M10 6v4l2.5 2.5" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round"/>
  </svg>
);
const IconX = () => (
  <svg width="20" height="20" viewBox="0 0 20 20" fill="none">
    <circle cx="10" cy="10" r="8" stroke="currentColor" strokeWidth="1.5"/>
    <path d="M7 7l6 6M13 7l-6 6" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round"/>
  </svg>
);
const IconCheck = () => (
  <svg width="20" height="20" viewBox="0 0 20 20" fill="none">
    <circle cx="10" cy="10" r="8" stroke="currentColor" strokeWidth="1.5"/>
    <path d="M6 10l2.5 2.5L14 7" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round"/>
  </svg>
);

const STATUS_STYLES: Record<string, { bg: string; border: string; icon: React.ReactNode; color: string; textColor: string }> = {
  NON_VERIFIE: {
    bg: "rgba(239,68,68,0.06)", border: "rgba(239,68,68,0.2)",
    icon: <IconShield />, color: "#dc2626", textColor: "#991b1b",
  },
  EN_ATTENTE: {
    bg: "rgba(245,158,11,0.06)", border: "rgba(245,158,11,0.2)",
    icon: <IconClock />, color: "#d97706", textColor: "#92400e",
  },
  REJETE: {
    bg: "rgba(239,68,68,0.06)", border: "rgba(239,68,68,0.2)",
    icon: <IconX />, color: "#dc2626", textColor: "#991b1b",
  },
  VERIFIE: {
    bg: "rgba(22,163,74,0.06)", border: "rgba(22,163,74,0.2)",
    icon: <IconCheck />, color: "#16a34a", textColor: "#166534",
  },
  VALIDE: {
    bg: "rgba(22,163,74,0.06)", border: "rgba(22,163,74,0.2)",
    icon: <IconCheck />, color: "#16a34a", textColor: "#166534",
  },
};

const ACTION_BUTTONS: Record<string, { label: string; to: string }> = {
  SUBMIT_VERIFICATION: { label: "Soumettre ma vérification", to: "/me" },
  COMPLETE_PROFILE: { label: "Compléter mon profil", to: "/me" },
  VERIFY_PHONE: { label: "Vérifier mon téléphone", to: "/me" },
  RESUBMIT: { label: "Resoumettre ma demande", to: "/me" },
};

export default function VerificationBanner({ verification }: { verification?: Verification }) {
  const navigate = useNavigate();
  if (!verification || verification.is_verified) return null;

  const style = STATUS_STYLES[verification.status] || STATUS_STYLES.NON_VERIFIE;
  const action = ACTION_BUTTONS[verification.action_required];

  return (
    <motion.div
      initial={{ opacity: 0, y: -8 }}
      animate={{ opacity: 1, y: 0 }}
      style={{
        display: "flex", alignItems: "center", gap: "0.75rem",
        padding: "1rem 1.25rem",
        background: style.bg, border: `1.5px solid ${style.border}`,
        borderRadius: "14px", marginBottom: "1.5rem",
      }}
    >
      <div style={{ color: style.color, flexShrink: 0 }}>{style.icon}</div>
      <div style={{ flex: 1 }}>
        <div style={{ fontWeight: 700, color: style.textColor, fontSize: "0.88rem" }}>
          {verification.status_label}
        </div>
        <div style={{ color: style.color, fontSize: "0.78rem", marginTop: "0.15rem", lineHeight: 1.4 }}>
          {verification.message}
        </div>
      </div>
      {action && verification.action_required !== "WAIT" && (
        <button
          onClick={() => navigate(action.to)}
          style={{
            background: style.color, color: "white", border: "none",
            borderRadius: "8px", padding: "0.5rem 1rem",
            fontWeight: 700, fontSize: "0.78rem", cursor: "pointer",
            flexShrink: 0, whiteSpace: "nowrap",
          } as any}
        >
          {action.label}
        </button>
      )}
    </motion.div>
  );
}

/**
 * Overlay bloquant pour les utilisateurs non vérifiés.
 * Empêche l'accès aux fonctionnalités de la plateforme.
 */
export function VerificationGate({
  verification,
  children,
}: {
  verification?: Verification;
  children: React.ReactNode;
}) {
  const navigate = useNavigate();
  if (!verification || verification.can_use_platform) {
    return <>{children}</>;
  }

  const style = STATUS_STYLES[verification.status] || STATUS_STYLES.NON_VERIFIE;
  const action = ACTION_BUTTONS[verification.action_required];

  return (
    <div style={{ position: "relative" }}>
      <div style={{ filter: "blur(3px)", opacity: 0.3, pointerEvents: "none", userSelect: "none" }}>
        {children}
      </div>
      <div style={{
        position: "absolute", inset: 0, display: "flex", alignItems: "center",
        justifyContent: "center", zIndex: 10,
      }}>
        <motion.div
          initial={{ opacity: 0, scale: 0.95 }}
          animate={{ opacity: 1, scale: 1 }}
          style={{
            background: "var(--surface)", border: `2px solid ${style.border}`,
            borderRadius: "20px", padding: "2.5rem", maxWidth: 440,
            textAlign: "center", boxShadow: "0 20px 60px rgba(0,0,0,0.15)",
          }}
        >
          <div style={{
            width: 56, height: 56, borderRadius: "50%",
            background: style.bg, color: style.color,
            display: "flex", alignItems: "center", justifyContent: "center",
            margin: "0 auto 1.25rem",
          }}>
            <svg width="28" height="28" viewBox="0 0 28 28" fill="none">
              <rect x="5" y="12" width="18" height="13" rx="2.5" stroke="currentColor" strokeWidth="2"/>
              <path d="M9 12V9a5 5 0 0110 0v3" stroke="currentColor" strokeWidth="2" strokeLinecap="round"/>
              <circle cx="14" cy="18.5" r="1.5" fill="currentColor"/>
            </svg>
          </div>
          <div style={{ fontWeight: 800, fontSize: "1.15rem", color: "var(--text)", marginBottom: "0.5rem" }}>
            Compte non vérifié
          </div>
          <div style={{ color: "var(--text-muted)", fontSize: "0.88rem", lineHeight: 1.5, marginBottom: "1.5rem" }}>
            {verification.message || "Vous devez vérifier votre compte pour accéder aux fonctionnalités de la plateforme."}
          </div>
          {action && verification.action_required !== "WAIT" && (
            <button
              onClick={() => navigate(action.to)}
              style={{
                background: style.color, color: "white", border: "none",
                borderRadius: "10px", padding: "0.75rem 1.5rem",
                fontWeight: 700, fontSize: "0.92rem", cursor: "pointer",
                width: "100%",
              }}
            >
              {action.label}
            </button>
          )}
          {verification.action_required === "WAIT" && (
            <div style={{
              background: style.bg, border: `1.5px solid ${style.border}`,
              borderRadius: "10px", padding: "0.75rem",
              color: style.color, fontWeight: 600, fontSize: "0.85rem",
            }}>
              Votre demande est en cours de traitement
            </div>
          )}
        </motion.div>
      </div>
    </div>
  );
}
