import React, { Suspense, useEffect } from "react";
import { Routes, Route, Navigate, useLocation } from "react-router-dom";
import ProtectedRoute from "./components/ProtectedRoute";
import OAuthCallback from "./components/OAuthCallback";
import Header from "./components/Header";
import AIChat from "./components/AIChat";

// Lazy-loaded pages
const Landing = React.lazy(() => import("./pages/Landing"));
const Login = React.lazy(() => import("./pages/Login"));
const Register = React.lazy(() => import("./pages/Register"));
const Profile = React.lazy(() => import("./pages/Profile"));
const Home = React.lazy(() => import("./pages/Home"));
const Dashboard = React.lazy(() => import("./pages/Dashboard"));
const Documents = React.lazy(() => import("./pages/Documents"));
const Agronomists = React.lazy(() => import("./pages/Agronomists"));
const PurchaseHistory = React.lazy(() => import("./pages/PurchaseHistory"));
const PaymentSuccess = React.lazy(() => import("./pages/PaymentSuccess"));
const Missions = React.lazy(() => import("./pages/Missions"));
const Security = React.lazy(() => import("./pages/Security"));
const Ratings = React.lazy(() => import("./pages/Ratings"));
const Messaging = React.lazy(() => import("./pages/Messaging"));
const Notifications = React.lazy(() => import("./pages/Notifications"));
const Jobs = React.lazy(() => import("./pages/Jobs"));
const Exploitants = React.lazy(() => import("./pages/Exploitants"));
const Ouvriers = React.lazy(() => import("./pages/Ouvriers"));
const Presales = React.lazy(() => import("./pages/Presales"));
const Locations = React.lazy(() => import("./pages/Locations"));
const Institutional = React.lazy(() => import("./pages/Institutional"));
const Compliance = React.lazy(() => import("./pages/Compliance"));
const ForgotPassword = React.lazy(() => import("./pages/ForgotPassword"));
const ResetPassword = React.lazy(() => import("./pages/ResetPassword"));
const VerifyEmail = React.lazy(() => import("./pages/VerifyEmail"));
const Markets = React.lazy(() => import("./pages/Markets"));
const Payment = React.lazy(() => import("./pages/Payment"));
const ChooseProfile = React.lazy(() => import("./pages/ChooseProfile"));
const OAuthCallbackPage = React.lazy(() => import("./pages/OAuthCallbackPage"));
const AdminDashboard = React.lazy(() => import("./pages/AdminDashboard"));
const Settings = React.lazy(() => import("./pages/Settings"));
const ProductionStats = React.lazy(() => import("./pages/institution/ProductionStats"));
const EmploiStats = React.lazy(() => import("./pages/institution/EmploiStats"));
const EconomieStats = React.lazy(() => import("./pages/institution/EconomieStats"));
const TerritoireStats = React.lazy(() => import("./pages/institution/TerritoireStats"));
const RapportsSectoriels = React.lazy(() => import("./pages/institution/RapportsSectoriels"));
const NotFound = React.lazy(() => import("./pages/NotFound"));
const Elearning = React.lazy(() => import("./pages/Elearning"));
const CoursDetail = React.lazy(() => import("./pages/CoursDetail"));
const MesCours = React.lazy(() => import("./pages/MesCours"));

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

function PageLoader() {
  return (
    <div style={{ minHeight: "60vh", display: "flex", alignItems: "center", justifyContent: "center" }}>
      <div style={{ width: 32, height: 32, border: "3px solid var(--border)", borderTop: "3px solid var(--primary)", borderRadius: "50%", animation: "spin 0.8s linear infinite" }} />
    </div>
  );
}

const LANDING_ROUTES = ["/"];

export default function App() {
  const location = useLocation();
  const isLanding = LANDING_ROUTES.includes(location.pathname);

  return (
    <div style={{ minHeight: "100vh", background: "var(--bg)" }}>
      <ScrollToTop />
      <OAuthCallback />
      <Header isAuthenticated={isAuthenticated()} />
      <main style={{ paddingTop: isLanding ? "0" : "64px" }}>
        <Suspense fallback={<PageLoader />}>
          <Routes>
            <Route path="/" element={<Landing />} />
            <Route path="/login" element={<Login />} />
            <Route path="/register" element={<Register />} />
            <Route path="/forgot-password" element={<ForgotPassword />} />
            <Route path="/reset-password" element={<ResetPassword />} />
            <Route path="/verify-email" element={<VerifyEmail />} />
            <Route path="/oauth-callback" element={<OAuthCallbackPage />} />
            <Route path="/choose-profile" element={<ProtectedRoute><ChooseProfile /></ProtectedRoute>} />
            <Route path="/home" element={<ProtectedRoute><Home /></ProtectedRoute>} />
            <Route path="/dashboard" element={<ProtectedRoute><Dashboard /></ProtectedRoute>} />
            <Route path="/documents" element={<Documents />} />
            <Route path="/agronomists" element={<Agronomists />} />
            <Route path="/purchases" element={<ProtectedRoute><PurchaseHistory /></ProtectedRoute>} />
            <Route path="/missions" element={<ProtectedRoute><Missions /></ProtectedRoute>} />
            <Route path="/jobs" element={<ProtectedRoute><Jobs /></ProtectedRoute>} />
            <Route path="/exploitants" element={<ProtectedRoute><Exploitants /></ProtectedRoute>} />
            <Route path="/ouvriers" element={<ProtectedRoute><Ouvriers /></ProtectedRoute>} />
            <Route path="/presales" element={<ProtectedRoute><Presales /></ProtectedRoute>} />
            <Route path="/elearning" element={<Elearning />} />
            <Route path="/elearning/mes-cours" element={<ProtectedRoute><MesCours /></ProtectedRoute>} />
            <Route path="/elearning/:slug" element={<CoursDetail />} />
            <Route path="/security" element={<ProtectedRoute><Security /></ProtectedRoute>} />
            <Route path="/ratings" element={<ProtectedRoute><Ratings /></ProtectedRoute>} />
            <Route path="/messages" element={<ProtectedRoute><Messaging /></ProtectedRoute>} />
            <Route path="/notifications" element={<ProtectedRoute><Notifications /></ProtectedRoute>} />
            <Route path="/locations" element={<Locations />} />
            <Route path="/markets" element={<Markets />} />
            <Route path="/institutional" element={<ProtectedRoute allowedRoles={["INSTITUTION", "ADMIN"]}><Institutional /></ProtectedRoute>} />
            <Route path="/institution/production" element={<ProtectedRoute allowedRoles={["INSTITUTION", "ADMIN"]}><ProductionStats /></ProtectedRoute>} />
            <Route path="/institution/emploi" element={<ProtectedRoute allowedRoles={["INSTITUTION", "ADMIN"]}><EmploiStats /></ProtectedRoute>} />
            <Route path="/institution/economie" element={<ProtectedRoute allowedRoles={["INSTITUTION", "ADMIN"]}><EconomieStats /></ProtectedRoute>} />
            <Route path="/institution/territoire" element={<ProtectedRoute allowedRoles={["INSTITUTION", "ADMIN"]}><TerritoireStats /></ProtectedRoute>} />
            <Route path="/institution/rapports" element={<ProtectedRoute allowedRoles={["INSTITUTION", "ADMIN"]}><RapportsSectoriels /></ProtectedRoute>} />
            <Route path="/compliance" element={<Compliance />} />
            <Route path="/payment/success" element={<PaymentSuccess />} />
            <Route path="/payment" element={<ProtectedRoute><Payment /></ProtectedRoute>} />
            <Route path="/admin" element={<ProtectedRoute allowedRoles={["ADMIN"]}><AdminDashboard /></ProtectedRoute>} />
            <Route path="/me" element={<ProtectedRoute><Profile /></ProtectedRoute>} />
            <Route path="/settings" element={<ProtectedRoute><Settings /></ProtectedRoute>} />
            <Route path="*" element={<NotFound />} />
          </Routes>
        </Suspense>
      </main>
      <AIChat context={{ page: location.pathname }} />
    </div>
  );
}
