import React, { useEffect } from "react";
import { Routes, Route, Navigate, useLocation } from "react-router-dom";
import Landing from "./pages/Landing";
import Login from "./pages/Login";
import Register from "./pages/Register";
import Profile from "./pages/Profile";
import Home from "./pages/Home";
import Dashboard from "./pages/Dashboard";
import Documents from "./pages/Documents";
import Agronomists from "./pages/Agronomists";
import PurchaseHistory from "./pages/PurchaseHistory";
import PaymentSuccess from "./pages/PaymentSuccess";
import Missions from "./pages/Missions";
import Security from "./pages/Security";
import Ratings from "./pages/Ratings";
import Messaging from "./pages/Messaging";
import Notifications from "./pages/Notifications";
import Jobs from "./pages/Jobs";
import Presales from "./pages/Presales";
import ProtectedRoute from "./components/ProtectedRoute";
import Header from "./components/Header";

function isAuthenticated() {
  return Boolean(localStorage.getItem("access_token"));
}

function ScrollToTop() {
  const { pathname } = useLocation();
  useEffect(() => {
    window.scrollTo({ top: 0, behavior: "instant" });
  }, [pathname]);
  return null;
}

const LANDING_ROUTES = ["/"];

export default function App() {
  const location = useLocation();
  const isLanding = LANDING_ROUTES.includes(location.pathname);

  return (
    <div style={{ minHeight: "100vh", background: "var(--bg)" }}>
      <ScrollToTop />
      <Header isAuthenticated={isAuthenticated()} />
      <main style={{ paddingTop: isLanding ? "0" : "64px" }}>
        <Routes>
          <Route path="/" element={<Landing />} />
          <Route path="/login" element={<Login />} />
          <Route path="/register" element={<Register />} />
          <Route path="/home" element={<ProtectedRoute><Home /></ProtectedRoute>} />
          <Route path="/dashboard" element={<ProtectedRoute><Dashboard /></ProtectedRoute>} />
          <Route path="/documents" element={<Documents />} />
          <Route path="/agronomists" element={<Agronomists />} />
          <Route path="/purchases" element={<ProtectedRoute><PurchaseHistory /></ProtectedRoute>} />
          <Route path="/missions" element={<ProtectedRoute><Missions /></ProtectedRoute>} />
          <Route path="/jobs" element={<ProtectedRoute><Jobs /></ProtectedRoute>} />
          <Route path="/presales" element={<ProtectedRoute><Presales /></ProtectedRoute>} />
          <Route path="/security" element={<ProtectedRoute><Security /></ProtectedRoute>} />
          <Route path="/ratings" element={<ProtectedRoute><Ratings /></ProtectedRoute>} />
          <Route path="/messages" element={<ProtectedRoute><Messaging /></ProtectedRoute>} />
          <Route path="/notifications" element={<ProtectedRoute><Notifications /></ProtectedRoute>} />
          <Route path="/payment/success" element={<PaymentSuccess />} />
          <Route path="/me" element={<ProtectedRoute><Profile /></ProtectedRoute>} />
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </main>
    </div>
  );
}
