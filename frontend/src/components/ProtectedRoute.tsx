import React, { useEffect, useState } from "react";
import { Navigate } from "react-router-dom";
import { me } from "../api/auth";

type Props = {
  children: React.ReactElement;
  allowedRoles?: string[];
};

export default function ProtectedRoute({ children, allowedRoles }: Props) {
  const token = localStorage.getItem("access_token");
  const [status, setStatus] = useState<"loading" | "ok" | "denied" | "unauth">(
    token ? "loading" : "unauth"
  );

  useEffect(() => {
    if (!token) return;
    if (!allowedRoles || allowedRoles.length === 0) {
      setStatus("ok");
      return;
    }
    me()
      .then((user) => {
        const role = user.user_type || "";
        const isAdmin = user.is_staff || role === "ADMIN";
        if (isAdmin || allowedRoles.includes(role)) {
          setStatus("ok");
        } else {
          setStatus("denied");
        }
      })
      .catch(() => setStatus("unauth"));
  }, [token, allowedRoles]);

  if (status === "unauth") return <Navigate to="/login" replace />;
  if (status === "denied") return <Navigate to="/home" replace />;
  if (status === "loading") return null;
  return children;
}
