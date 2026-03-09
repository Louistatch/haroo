import React, { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { motion } from "framer-motion";
import { me } from "../api/auth";
import ExploitantDashboard from "./dashboards/ExploitantDashboard";
import AgronomeDashboard from "./dashboards/AgronomeDashboard";
import OuvrierDashboard from "./dashboards/OuvrierDashboard";
import AcheteurDashboard from "./dashboards/AcheteurDashboard";
import InstitutionDashboard from "./dashboards/InstitutionDashboard";

function LoadingScreen() {
  return (
    <div style={{ minHeight: "100vh", display: "flex", alignItems: "center", justifyContent: "center", background: "var(--bg)" }}>
      <motion.div animate={{ rotate: 360 }} transition={{ duration: 0.8, repeat: Infinity, ease: "linear" }}
        style={{ width: 32, height: 32, border: "3px solid var(--border)", borderTop: "3px solid var(--primary)", borderRadius: "50%" }} />
    </div>
  );
}

export default function Home() {
  const [user, setUser] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const navigate = useNavigate();

  useEffect(() => {
    me()
      .then((data) => {
        if (!data.user_type) {
          navigate("/choose-profile", { replace: true });
          return;
        }
        setUser(data);
      })
      .catch(() => navigate("/login"))
      .finally(() => setLoading(false));
  }, [navigate]);

  if (loading) return <LoadingScreen />;
  if (!user) return null;

  switch (user.user_type) {
    case "EXPLOITANT":
      return <ExploitantDashboard user={user} />;
    case "AGRONOME":
      return <AgronomeDashboard user={user} />;
    case "OUVRIER":
      return <OuvrierDashboard user={user} />;
    case "ACHETEUR":
      return <AcheteurDashboard user={user} />;
    case "INSTITUTION":
      return <InstitutionDashboard user={user} />;
    default:
      navigate("/choose-profile", { replace: true });
      return null;
  }
}
