import React, { useState, useEffect, useRef } from "react";
import { Link, useLocation, useNavigate } from "react-router-dom";
import { motion, AnimatePresence } from "framer-motion";

interface HeaderProps {
  isAuthenticated: boolean;
}

function getUserInfo(): { initials: string; name: string; type: string } | null {
  try {
    const token = localStorage.getItem("access_token");
    if (!token) return null;
    const p = JSON.parse(atob(token.split(".")[1]));
    const username: string = p.username || "";
    const parts = username.split("_");
    const initials = parts.map((w: string) => w[0]?.toUpperCase() || "").join("").slice(0, 2) || "U";
    const TYPE_LABELS: Record<string, string> = {
      EXPLOITANT: "Exploitant",
      AGRONOME: "Agronome",
      OUVRIER: "Ouvrier",
      ACHETEUR: "Acheteur",
      INSTITUTION: "Institution",
    };
    return { initials, name: username, type: TYPE_LABELS[p.user_type] || p.user_type || "" };
  } catch { return null; }
}

/* ── SVG icons ── */
function IconDashboard() {
  return <svg width="17" height="17" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round"><rect x="3" y="3" width="7" height="7" rx="1"/><rect x="14" y="3" width="7" height="7" rx="1"/><rect x="3" y="14" width="7" height="7" rx="1"/><rect x="14" y="14" width="7" height="7" rx="1"/></svg>;
}
function IconMissions() {
  return <svg width="17" height="17" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round"><path d="M12 2L2 7l10 5 10-5-10-5z"/><path d="M2 17l10 5 10-5"/><path d="M2 12l10 5 10-5"/></svg>;
}
function IconDocuments() {
  return <svg width="17" height="17" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round"><path d="M14 2H6a2 2 0 00-2 2v16a2 2 0 002 2h12a2 2 0 002-2V8z"/><polyline points="14 2 14 8 20 8"/><line x1="9" y1="13" x2="15" y2="13"/><line x1="9" y1="17" x2="13" y2="17"/></svg>;
}
function IconAgronomes() {
  return <svg width="17" height="17" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round"><path d="M17 21v-2a4 4 0 00-4-4H5a4 4 0 00-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M23 21v-2a4 4 0 00-3-3.87"/><path d="M16 3.13a4 4 0 010 7.75"/></svg>;
}
function IconProfile() {
  return <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round"><path d="M20 21v-2a4 4 0 00-4-4H8a4 4 0 00-4 4v2"/><circle cx="12" cy="7" r="4"/></svg>;
}
function IconBag() {
  return <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round"><path d="M6 2L3 6v14a2 2 0 002 2h14a2 2 0 002-2V6l-3-4z"/><line x1="3" y1="6" x2="21" y2="6"/><path d="M16 10a4 4 0 01-8 0"/></svg>;
}
function IconStar() {
  return <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round"><polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"/></svg>;
}
function IconShield() {
  return <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/></svg>;
}
function IconLogout() {
  return <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round"><path d="M9 21H5a2 2 0 01-2-2V5a2 2 0 012-2h4"/><polyline points="16 17 21 12 16 7"/><line x1="21" y1="12" x2="9" y2="12"/></svg>;
}
function IconSun() {
  return <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round"><circle cx="12" cy="12" r="5"/><line x1="12" y1="1" x2="12" y2="3"/><line x1="12" y1="21" x2="12" y2="23"/><line x1="4.22" y1="4.22" x2="5.64" y2="5.64"/><line x1="18.36" y1="18.36" x2="19.78" y2="19.78"/><line x1="1" y1="12" x2="3" y2="12"/><line x1="21" y1="12" x2="23" y2="12"/><line x1="4.22" y1="19.78" x2="5.64" y2="18.36"/><line x1="18.36" y1="5.64" x2="19.78" y2="4.22"/></svg>;
}
function IconMoon() {
  return <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round"><path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"/></svg>;
}
function LogoIcon() {
  return (
    <svg width="30" height="30" viewBox="0 0 32 32" fill="none">
      <rect width="32" height="32" rx="9" fill="var(--primary)"/>
      <path d="M16 6C10.5 6 8 10 8 14c0 3 2 5.5 4.5 7L16 26l3.5-5C22 19.5 24 17 24 14c0-4-2.5-8-8-8z" fill="white" opacity="0.9"/>
      <circle cx="16" cy="13" r="3" fill="white"/>
    </svg>
  );
}

const PRIMARY_NAV = [
  { to: "/home",        label: "Tableau de bord", Icon: IconDashboard },
  { to: "/missions",    label: "Missions",         Icon: IconMissions  },
  { to: "/documents",   label: "Documents",        Icon: IconDocuments },
  { to: "/agronomists", label: "Agronomes",        Icon: IconAgronomes },
];

const USER_MENU = [
  { to: "/me",        label: "Mon profil",  Icon: IconProfile },
  { to: "/purchases", label: "Mes achats",  Icon: IconBag     },
  { to: "/ratings",   label: "Mes avis",   Icon: IconStar    },
  { to: "/security",  label: "Sécurité",   Icon: IconShield  },
];

const GUEST_NAV = [
  { to: "/documents",   label: "Documents", Icon: IconDocuments },
  { to: "/agronomists", label: "Agronomes", Icon: IconAgronomes },
];

/* Stagger variants for mobile items */
const listVariants = {
  hidden: {},
  visible: { transition: { staggerChildren: 0.055 } },
};
const itemVariants = {
  hidden: { opacity: 0, x: 18 },
  visible: { opacity: 1, x: 0, transition: { type: "spring", stiffness: 320, damping: 28 } },
};

export const Header: React.FC<HeaderProps> = ({ isAuthenticated }) => {
  const [scrolled, setScrolled]       = useState(false);
  const [mobileOpen, setMobileOpen]   = useState(false);
  const [userMenuOpen, setUserMenuOpen] = useState(false);
  const [theme, setTheme] = useState<"light" | "dark" | "auto">(() =>
    (localStorage.getItem("haroo-theme") as "light" | "dark" | "auto") || "auto"
  );

  const location    = useLocation();
  const navigate    = useNavigate();
  const userMenuRef = useRef<HTMLDivElement>(null);
  const isLanding   = location.pathname === "/";
  const onScroll    = scrolled || !isLanding;
  const userInfo    = isAuthenticated ? getUserInfo() : null;
  const mainNav     = isAuthenticated ? PRIMARY_NAV : GUEST_NAV;

  useEffect(() => {
    const fn = () => setScrolled(window.scrollY > 12);
    window.addEventListener("scroll", fn, { passive: true });
    return () => window.removeEventListener("scroll", fn);
  }, []);

  useEffect(() => { setMobileOpen(false); setUserMenuOpen(false); }, [location.pathname]);

  useEffect(() => {
    const root = document.documentElement;
    if (theme === "auto") root.removeAttribute("data-theme");
    else root.setAttribute("data-theme", theme);
    localStorage.setItem("haroo-theme", theme);
  }, [theme]);

  useEffect(() => {
    function handler(e: MouseEvent) {
      if (userMenuRef.current && !userMenuRef.current.contains(e.target as Node)) setUserMenuOpen(false);
    }
    document.addEventListener("mousedown", handler);
    return () => document.removeEventListener("mousedown", handler);
  }, []);

  const isDark = theme === "dark" || (theme === "auto" && window.matchMedia("(prefers-color-scheme: dark)").matches);
  const toggleTheme = () => setTheme(t => t === "dark" ? "light" : "dark");
  const handleLogout = () => { localStorage.removeItem("access_token"); localStorage.removeItem("refresh_token"); navigate("/"); };

  const ghostText = onScroll ? "var(--text-secondary)" : "rgba(255,255,255,0.8)";

  return (
    <>
      <motion.header
        initial={{ y: -64, opacity: 0 }}
        animate={{ y: 0, opacity: 1 }}
        transition={{ duration: 0.45, ease: [0, 0, 0.2, 1] }}
        style={{ position: "fixed", top: 0, left: 0, right: 0, zIndex: 400 }}
      >
        <div style={{
          background: onScroll ? "var(--header-bg)" : "transparent",
          backdropFilter: onScroll ? "blur(22px) saturate(180%)" : "none",
          WebkitBackdropFilter: onScroll ? "blur(22px) saturate(180%)" : "none",
          borderBottom: `1px solid ${onScroll ? "var(--header-border)" : "transparent"}`,
          boxShadow: onScroll ? "0 1px 24px rgba(0,0,0,0.07)" : "none",
          transition: "all 0.3s ease",
        }}>
          <div className="container" style={{ display: "flex", alignItems: "center", height: 64 }}>

            {/* Logo */}
            <Link to={isAuthenticated ? "/home" : "/"} style={{ display: "flex", alignItems: "center", gap: 9, textDecoration: "none", marginRight: "2.25rem", flexShrink: 0 }}>
              <motion.div whileHover={{ rotate: [0, -6, 6, 0], scale: 1.05 }} transition={{ duration: 0.4 }}>
                <LogoIcon />
              </motion.div>
              <span style={{ fontWeight: 800, fontSize: "1.15rem", letterSpacing: "-0.03em", color: onScroll ? "var(--text)" : "white", transition: "color 0.3s" }}>
                Haroo
              </span>
            </Link>

            {/* Desktop primary nav */}
            <nav className="hide-mobile" style={{ display: "flex", alignItems: "center", gap: "2px", flex: 1 }}>
              {mainNav.map(({ to, label }) => {
                const active = location.pathname === to;
                return (
                  <Link
                    key={to}
                    to={to}
                    style={{
                      position: "relative",
                      padding: "6px 13px",
                      borderRadius: 8,
                      color: active ? (onScroll ? "var(--primary)" : "white") : ghostText,
                      fontWeight: active ? 600 : 500,
                      fontSize: "0.875rem",
                      textDecoration: "none",
                      background: active && onScroll ? "rgba(var(--primary-rgb),0.09)" : "transparent",
                      transition: "color 0.2s, background 0.2s",
                    }}
                    onMouseEnter={(e) => { if (!active) (e.currentTarget as HTMLElement).style.color = onScroll ? "var(--text)" : "white"; }}
                    onMouseLeave={(e) => { if (!active) (e.currentTarget as HTMLElement).style.color = ghostText; }}
                  >
                    {label}
                    {active && (
                      <motion.span
                        layoutId="nav-underline"
                        style={{ position: "absolute", bottom: 1, left: 10, right: 10, height: 2, background: onScroll ? "var(--primary)" : "white", borderRadius: 2, display: "block" }}
                      />
                    )}
                  </Link>
                );
              })}
            </nav>

            {/* Right actions */}
            <div className="hide-mobile" style={{ display: "flex", alignItems: "center", gap: 8, flexShrink: 0 }}>
              <motion.button
                whileHover={{ scale: 1.08 }} whileTap={{ scale: 0.9 }}
                onClick={toggleTheme}
                title={isDark ? "Mode clair" : "Mode sombre"}
                style={{ width: 34, height: 34, borderRadius: 8, border: "none", background: onScroll ? "var(--bg-secondary)" : "rgba(255,255,255,0.15)", color: onScroll ? "var(--text-secondary)" : "white", display: "flex", alignItems: "center", justifyContent: "center", cursor: "pointer", transition: "all 0.2s" }}
              >
                <AnimatePresence mode="wait">
                  <motion.span key={isDark ? "sun" : "moon"} initial={{ opacity: 0, rotate: -30, scale: 0.7 }} animate={{ opacity: 1, rotate: 0, scale: 1 }} exit={{ opacity: 0, rotate: 30, scale: 0.7 }} transition={{ duration: 0.2 }} style={{ display: "flex" }}>
                    {isDark ? <IconSun /> : <IconMoon />}
                  </motion.span>
                </AnimatePresence>
              </motion.button>

              {isAuthenticated && userInfo ? (
                <div ref={userMenuRef} style={{ position: "relative" }}>
                  <motion.button
                    whileHover={{ scale: 1.02 }} whileTap={{ scale: 0.97 }}
                    onClick={() => setUserMenuOpen(o => !o)}
                    style={{ display: "flex", alignItems: "center", gap: 8, padding: "5px 10px 5px 5px", borderRadius: 10, border: `1px solid ${onScroll ? "var(--border)" : "rgba(255,255,255,0.2)"}`, background: onScroll ? "var(--bg-secondary)" : "rgba(255,255,255,0.1)", cursor: "pointer", transition: "all 0.2s" }}
                  >
                    <motion.div
                      whileHover={{ scale: 1.08 }}
                      style={{ width: 28, height: 28, borderRadius: 7, background: "var(--primary)", display: "flex", alignItems: "center", justifyContent: "center", color: "#fff", fontWeight: 800, fontSize: 12, flexShrink: 0, letterSpacing: "-0.02em" }}
                    >
                      {userInfo.initials}
                    </motion.div>
                    <div style={{ textAlign: "left" }}>
                      <p style={{ margin: 0, fontSize: 13, fontWeight: 600, color: onScroll ? "var(--text)" : "white", lineHeight: 1.2 }}>{userInfo.name}</p>
                      {userInfo.type && <p style={{ margin: 0, fontSize: 10, color: onScroll ? "var(--muted)" : "rgba(255,255,255,0.65)", lineHeight: 1.2 }}>{userInfo.type}</p>}
                    </div>
                    <motion.svg animate={{ rotate: userMenuOpen ? 180 : 0 }} transition={{ duration: 0.22 }} width="11" height="11" viewBox="0 0 24 24" fill="none" stroke={onScroll ? "var(--muted)" : "rgba(255,255,255,0.6)"} strokeWidth="2.5" strokeLinecap="round" style={{ marginLeft: 2, flexShrink: 0 }}>
                      <polyline points="6 9 12 15 18 9"/>
                    </motion.svg>
                  </motion.button>

                  <AnimatePresence>
                    {userMenuOpen && (
                      <motion.div
                        initial={{ opacity: 0, scale: 0.94, y: -8 }}
                        animate={{ opacity: 1, scale: 1, y: 0 }}
                        exit={{ opacity: 0, scale: 0.94, y: -8 }}
                        transition={{ type: "spring", stiffness: 360, damping: 30 }}
                        style={{ position: "absolute", top: "calc(100% + 10px)", right: 0, width: 228, background: "var(--card)", border: "1px solid var(--border)", borderRadius: 14, boxShadow: "0 20px 60px rgba(0,0,0,0.13), 0 4px 16px rgba(0,0,0,0.06)", overflow: "hidden", zIndex: 500 }}
                      >
                        {/* Header strip */}
                        <div style={{ padding: "14px 16px 12px", background: "linear-gradient(135deg, rgba(var(--primary-rgb),0.08) 0%, transparent 100%)", borderBottom: "1px solid var(--border)" }}>
                          <div style={{ display: "flex", alignItems: "center", gap: 10 }}>
                            <div style={{ width: 38, height: 38, borderRadius: 10, background: "var(--primary)", display: "flex", alignItems: "center", justifyContent: "center", color: "#fff", fontWeight: 800, fontSize: 15, letterSpacing: "-0.02em" }}>
                              {userInfo.initials}
                            </div>
                            <div>
                              <p style={{ margin: 0, fontSize: 13, fontWeight: 700, color: "var(--text)" }}>{userInfo.name}</p>
                              {userInfo.type && <span style={{ display: "inline-block", marginTop: 2, padding: "1px 8px", borderRadius: 20, fontSize: 10, fontWeight: 600, background: "rgba(var(--primary-rgb),0.13)", color: "var(--primary)" }}>{userInfo.type}</span>}
                            </div>
                          </div>
                        </div>

                        {/* Links */}
                        <div style={{ padding: "6px 6px" }}>
                          {USER_MENU.map(({ to, label, Icon }) => {
                            const active = location.pathname === to;
                            return (
                              <motion.div key={to} whileHover={{ x: 2 }} transition={{ type: "spring", stiffness: 400, damping: 28 }}>
                                <Link
                                  to={to}
                                  style={{ display: "flex", alignItems: "center", gap: 10, padding: "9px 12px", borderRadius: 9, color: active ? "var(--primary)" : "var(--text)", fontWeight: active ? 600 : 400, fontSize: 14, textDecoration: "none", background: active ? "rgba(var(--primary-rgb),0.08)" : "transparent", transition: "background 0.15s" }}
                                  onMouseEnter={(e) => { if (!active) (e.currentTarget as HTMLElement).style.background = "var(--bg)"; }}
                                  onMouseLeave={(e) => { (e.currentTarget as HTMLElement).style.background = active ? "rgba(var(--primary-rgb),0.08)" : "transparent"; }}
                                >
                                  <span style={{ color: active ? "var(--primary)" : "var(--muted)", display: "flex" }}><Icon /></span>
                                  {label}
                                </Link>
                              </motion.div>
                            );
                          })}
                        </div>

                        <div style={{ borderTop: "1px solid var(--border)", padding: "6px 6px 6px" }}>
                          <motion.button
                            whileHover={{ x: 2 }}
                            transition={{ type: "spring", stiffness: 400, damping: 28 }}
                            onClick={toggleTheme}
                            style={{ width: "100%", display: "flex", alignItems: "center", gap: 10, padding: "9px 12px", borderRadius: 9, background: "none", border: "none", color: "var(--text-secondary)", fontSize: 14, cursor: "pointer", transition: "background 0.15s" }}
                            onMouseEnter={(e) => { (e.currentTarget as HTMLElement).style.background = "var(--bg)"; }}
                            onMouseLeave={(e) => { (e.currentTarget as HTMLElement).style.background = "none"; }}
                          >
                            <span style={{ display: "flex" }}>{isDark ? <IconSun /> : <IconMoon />}</span>
                            {isDark ? "Mode clair" : "Mode sombre"}
                          </motion.button>
                          <motion.button
                            whileHover={{ x: 2 }}
                            transition={{ type: "spring", stiffness: 400, damping: 28 }}
                            onClick={handleLogout}
                            style={{ width: "100%", display: "flex", alignItems: "center", gap: 10, padding: "9px 12px", borderRadius: 9, background: "none", border: "none", color: "#ef4444", fontSize: 14, fontWeight: 500, cursor: "pointer", transition: "background 0.15s" }}
                            onMouseEnter={(e) => { (e.currentTarget as HTMLElement).style.background = "rgba(239,68,68,0.08)"; }}
                            onMouseLeave={(e) => { (e.currentTarget as HTMLElement).style.background = "none"; }}
                          >
                            <IconLogout /> Déconnexion
                          </motion.button>
                        </div>
                      </motion.div>
                    )}
                  </AnimatePresence>
                </div>
              ) : (
                <>
                  <Link to="/login"
                    style={{ padding: "7px 14px", borderRadius: 8, color: ghostText, fontWeight: 500, fontSize: "0.875rem", textDecoration: "none", transition: "color 0.2s" }}
                    onMouseEnter={(e) => { (e.currentTarget as HTMLElement).style.color = onScroll ? "var(--text)" : "white"; }}
                    onMouseLeave={(e) => { (e.currentTarget as HTMLElement).style.color = ghostText; }}
                  >
                    Connexion
                  </Link>
                  <motion.div whileHover={{ scale: 1.03 }} whileTap={{ scale: 0.97 }}>
                    <Link to="/register" style={{ padding: "8px 18px", borderRadius: 8, background: onScroll ? "var(--primary)" : "white", color: onScroll ? "white" : "var(--green-700)", fontWeight: 700, fontSize: "0.875rem", textDecoration: "none", display: "inline-block", boxShadow: "var(--shadow-sm)", transition: "all 0.2s" }}>
                      Commencer →
                    </Link>
                  </motion.div>
                </>
              )}
            </div>

            {/* Mobile burger */}
            <motion.button
              className="hide-desktop"
              onClick={() => setMobileOpen(o => !o)}
              aria-label="Menu"
              style={{ background: "transparent", border: "none", cursor: "pointer", padding: "8px", color: onScroll ? "var(--text)" : "white", display: "flex", alignItems: "center", marginLeft: "auto" }}
            >
              <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.2" strokeLinecap="round">
                <AnimatePresence mode="wait">
                  {mobileOpen ? (
                    <motion.g key="x" initial={{ opacity: 0, rotate: -45 }} animate={{ opacity: 1, rotate: 0 }} exit={{ opacity: 0 }} transition={{ duration: 0.18 }}>
                      <line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/>
                    </motion.g>
                  ) : (
                    <motion.g key="bars" initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }} transition={{ duration: 0.18 }}>
                      <line x1="4" y1="7" x2="20" y2="7"/><line x1="4" y1="14" x2="20" y2="14"/>
                    </motion.g>
                  )}
                </AnimatePresence>
              </svg>
            </motion.button>
          </div>
        </div>
      </motion.header>

      {/* Mobile menu */}
      <AnimatePresence>
        {mobileOpen && (
          <>
            <motion.div
              className="hide-desktop"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              transition={{ duration: 0.2 }}
              onClick={() => setMobileOpen(false)}
              style={{ position: "fixed", inset: 0, top: 64, background: "rgba(0,0,0,0.35)", backdropFilter: "blur(4px)", zIndex: 398 }}
            />
            <motion.div
              className="hide-desktop"
              initial={{ x: "100%", opacity: 0 }}
              animate={{ x: 0, opacity: 1 }}
              exit={{ x: "100%", opacity: 0 }}
              transition={{ type: "spring", stiffness: 320, damping: 32 }}
              style={{ position: "fixed", top: 64, right: 0, bottom: 0, width: "min(290px, 84vw)", background: "var(--card)", borderLeft: "1px solid var(--border)", zIndex: 399, overflowY: "auto", display: "flex", flexDirection: "column" }}
            >
              {/* User identity strip */}
              {isAuthenticated && userInfo && (
                <motion.div
                  initial={{ opacity: 0, y: -10 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: 0.08 }}
                  style={{ padding: "1.25rem 1.25rem 1rem", borderBottom: "1px solid var(--border)", background: "linear-gradient(135deg, rgba(var(--primary-rgb),0.07) 0%, transparent 100%)" }}
                >
                  <div style={{ display: "flex", alignItems: "center", gap: 12 }}>
                    <div style={{ width: 46, height: 46, borderRadius: 12, background: "var(--primary)", display: "flex", alignItems: "center", justifyContent: "center", color: "#fff", fontWeight: 800, fontSize: 17, letterSpacing: "-0.02em", boxShadow: "0 4px 14px rgba(var(--primary-rgb),0.35)" }}>
                      {userInfo.initials}
                    </div>
                    <div>
                      <p style={{ margin: 0, fontWeight: 700, fontSize: 15, color: "var(--text)" }}>{userInfo.name}</p>
                      {userInfo.type && <span style={{ display: "inline-block", marginTop: 3, padding: "2px 9px", borderRadius: 20, fontSize: 11, fontWeight: 600, background: "rgba(var(--primary-rgb),0.12)", color: "var(--primary)" }}>{userInfo.type}</span>}
                    </div>
                  </div>
                </motion.div>
              )}

              {/* Nav items with stagger */}
              <div style={{ padding: "0.75rem 0.75rem", flex: 1 }}>
                <motion.div
                  variants={listVariants}
                  initial="hidden"
                  animate="visible"
                  style={{ display: "flex", flexDirection: "column", gap: 2 }}
                >
                  {mainNav.map(({ to, label, Icon }) => {
                    const active = location.pathname === to;
                    return (
                      <motion.div key={to} variants={itemVariants}>
                        <Link
                          to={to}
                          style={{ display: "flex", alignItems: "center", gap: 12, padding: "12px 14px", borderRadius: 11, color: active ? "var(--primary)" : "var(--text)", fontWeight: active ? 600 : 400, fontSize: 15, textDecoration: "none", background: active ? "rgba(var(--primary-rgb),0.1)" : "transparent", transition: "background 0.15s" }}
                          onMouseEnter={(e) => { if (!active) (e.currentTarget as HTMLElement).style.background = "var(--bg)"; }}
                          onMouseLeave={(e) => { (e.currentTarget as HTMLElement).style.background = active ? "rgba(var(--primary-rgb),0.1)" : "transparent"; }}
                        >
                          <span style={{ color: active ? "var(--primary)" : "var(--muted)", display: "flex", flexShrink: 0 }}><Icon /></span>
                          {label}
                          {active && <motion.span layoutId="mob-active" style={{ marginLeft: "auto", width: 6, height: 6, borderRadius: 3, background: "var(--primary)", display: "block" }} />}
                        </Link>
                      </motion.div>
                    );
                  })}

                  {isAuthenticated && (
                    <>
                      <div style={{ height: 1, background: "var(--border)", margin: "8px 4px" }} />
                      {USER_MENU.map(({ to, label, Icon }, i) => {
                        const active = location.pathname === to;
                        return (
                          <motion.div key={to} variants={itemVariants} custom={i + mainNav.length}>
                            <Link
                              to={to}
                              style={{ display: "flex", alignItems: "center", gap: 12, padding: "12px 14px", borderRadius: 11, color: active ? "var(--primary)" : "var(--text-secondary)", fontWeight: active ? 600 : 400, fontSize: 14, textDecoration: "none", background: active ? "rgba(var(--primary-rgb),0.1)" : "transparent", transition: "background 0.15s" }}
                              onMouseEnter={(e) => { if (!active) (e.currentTarget as HTMLElement).style.background = "var(--bg)"; }}
                              onMouseLeave={(e) => { (e.currentTarget as HTMLElement).style.background = active ? "rgba(var(--primary-rgb),0.1)" : "transparent"; }}
                            >
                              <span style={{ color: active ? "var(--primary)" : "var(--muted)", display: "flex", flexShrink: 0 }}><Icon /></span>
                              {label}
                            </Link>
                          </motion.div>
                        );
                      })}
                    </>
                  )}
                </motion.div>
              </div>

              {/* Bottom bar */}
              <motion.div
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.2 }}
                style={{ padding: "0.75rem", borderTop: "1px solid var(--border)" }}
              >
                <button
                  onClick={toggleTheme}
                  style={{ width: "100%", display: "flex", alignItems: "center", gap: 10, padding: "11px 14px", borderRadius: 11, background: "var(--bg)", border: "1px solid var(--border)", color: "var(--text-secondary)", fontSize: 14, cursor: "pointer", marginBottom: 8, transition: "background 0.15s" }}
                >
                  <span style={{ display: "flex" }}>{isDark ? <IconSun /> : <IconMoon />}</span>
                  {isDark ? "Mode clair" : "Mode sombre"}
                </button>

                {isAuthenticated ? (
                  <button
                    onClick={handleLogout}
                    style={{ width: "100%", display: "flex", alignItems: "center", justifyContent: "center", gap: 8, padding: "12px", borderRadius: 11, border: "none", background: "rgba(239,68,68,0.09)", color: "#ef4444", fontSize: 14, fontWeight: 600, cursor: "pointer" }}
                  >
                    <IconLogout /> Déconnexion
                  </button>
                ) : (
                  <div style={{ display: "flex", flexDirection: "column", gap: 8 }}>
                    <Link to="/login" style={{ textAlign: "center", padding: "11px", borderRadius: 11, background: "var(--bg)", border: "1px solid var(--border)", color: "var(--text)", fontWeight: 500, fontSize: 14, textDecoration: "none", display: "block" }}>Connexion</Link>
                    <Link to="/register" style={{ textAlign: "center", padding: "11px", borderRadius: 11, background: "var(--primary)", color: "white", fontWeight: 700, fontSize: 14, textDecoration: "none", display: "block" }}>Commencer →</Link>
                  </div>
                )}
              </motion.div>
            </motion.div>
          </>
        )}
      </AnimatePresence>
    </>
  );
};

export default Header;
