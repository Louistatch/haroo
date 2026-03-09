import { useEffect } from "react";
import { useNavigate } from "react-router-dom";

/**
 * OAuth callback page — kept for backward compatibility.
 * With Firebase popup auth, this page is no longer needed.
 * Redirects to login.
 */
export default function OAuthCallbackPage() {
  const navigate = useNavigate();

  useEffect(() => {
    navigate("/login", { replace: true });
  }, [navigate]);

  return (
    <div style={{
      minHeight: "100vh", display: "flex", alignItems: "center", justifyContent: "center",
      background: "var(--bg)",
    }}>
      <span style={{ color: "var(--text-muted)", fontSize: "0.95rem" }}>Redirection...</span>
    </div>
  );
}
