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
    return {
      initials,
      name: username,
      type: TYPE_LABELS[p.user_type] || p.user_type || "",
    };
  } catch {
    return null;
  }
}

const PRIMARY_NAV = [
  { to: "/home",      label: "Tableau de bord", icon: "⊞" },
  { to: "/missions",  label: "Missions",         icon: "🌱" },
  { to: "/documents", label: "Documents",        icon: "📄" },
  { to: "/agronomists", label: "Agronomes",      icon: "👨‍🌾" },
];

const USER_MENU = [
  { to: "/me",        label: "Mon profil",    icon: ProfileIcon },
  { to: "/purchases", label: "Mes achats",    icon: BagIcon },
  { to: "/ratings",   label: "Mes avis",      icon: StarIcon },
  { to: "/security",  label: "Sécurité",      icon: ShieldIcon },
];

function ProfileIcon() {
  return <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"/><circle cx="12" cy="7" r="4"/></svg>;
}
function BagIcon() {
  return <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M6 2L3 6v14a2 2 0 002 2h14a2 2 0 002-2V6l-3-4z"/><line x1="3" y1="6" x2="21" y2="6"/><path d="M16 10a4 4 0 01-8 0"/></svg>;
}
function StarIcon() {
  return <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><polygon points="12 2 15.09 8.26 22 9.27 17 14.14 18.18 21.02 12 17.77 5.82 21.02 7 14.14 2 9.27 8.91 8.26 12 2"/></svg>;
}
function ShieldIcon() {
  return <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/></svg>;
}
function LogoutIcon() {
  return <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M9 21H5a2 2 0 01-2-2V5a2 2 0 012-2h4"/><polyline points="16 17 21 12 16 7"/><line x1="21" y1="12" x2="9" y2="12"/></svg>;
}
function SunIcon() {
  return <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><circle cx="12" cy="12" r="5"/><line x1="12" y1="1" x2="12" y2="3"/><line x1="12" y1="21" x2="12" y2="23"/><line x1="4.22" y1="4.22" x2="5.64" y2="5.64"/><line x1="18.36" y1="18.36" x2="19.78" y2="19.78"/><line x1="1" y1="12" x2="3" y2="12"/><line x1="21" y1="12" x2="23" y2="12"/><line x1="4.22" y1="19.78" x2="5.64" y2="18.36"/><line x1="18.36" y1="5.64" x2="19.78" y2="4.22"/></svg>;
}
function MoonIcon() {
  return <svg width="15" height="15" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"/></svg>;
}
function LogoIcon() {
  return (
    <svg width="28" height="28" viewBox="0 0 32 32" fill="none">
      <rect width="32" height="32" rx="8" fill="var(--primary)"/>
      <path d="M16 6C10.5 6 8 10 8 14c0 3 2 5.5 4.5 7L16 26l3.5-5C22 19.5 24 17 24 14c0-4-2.5-8-8-8z" fill="white" opacity="0.9"/>
      <circle cx="16" cy="13" r="3" fill="white"/>
    </svg>
  );
}

export const Header: React.FC<HeaderProps> = ({ isAuthenticated }) => {
  const [scrolled, setScrolled]     = useState(false);
  const [mobileOpen, setMobileOpen] = useState(false);
  const [userMenuOpen, setUserMenuOpen] = useState(false);
  const [theme, setTheme] = useState<"light" | "dark" | "auto">(() =>
    (localStorage.getItem("haroo-theme") as "light" | "dark" | "auto") || "auto"
  );

  const location = useLocation();
  const navigate  = useNavigate();
  const userMenuRef = useRef<HTMLDivElement>(null);
  const isLandingPage = location.pathname === "/";
  const onScroll = scrolled || !isLandingPage;
  const userInfo = isAuthenticated ? getUserInfo() : null;

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
    function onClick(e: MouseEvent) {
      if (userMenuRef.current && !userMenuRef.current.contains(e.target as Node)) {
        setUserMenuOpen(false);
      }
    }
    document.addEventListener("mousedown", onClick);
    return () => document.removeEventListener("mousedown", onClick);
  }, []);

  const isDark = theme === "dark" || (theme === "auto" && window.matchMedia("(prefers-color-scheme: dark)").matches);
  const toggleTheme = () => setTheme(t => t === "dark" ? "light" : "dark");

  const handleLogout = () => {
    localStorage.removeItem("access_token");
    localStorage.removeItem("refresh_token");
    setUserMenuOpen(false);
    navigate("/");
  };

  const textColor = onScroll ? "var(--text-secondary)" : "rgba(255,255,255,0.85)";

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
          backdropFilter: onScroll ? "blur(20px) saturate(180%)" : "none",
          WebkitBackdropFilter: onScroll ? "blur(20px) saturate(180%)" : "none",
          borderBottom: `1px solid ${onScroll ? "var(--header-border)" : "transparent"}`,
          boxShadow: onScroll ? "0 1px 20px rgba(0,0,0,0.07)" : "none",
          transition: "all 0.3s ease",
        }}>
          <div className="container" style={{ display: "flex", alignItems: "center", height: 64, gap: 0 }}>

            {/* ── Logo ── */}
            <Link to={isAuthenticated ? "/home" : "/"} style={{ display: "flex", alignItems: "center", gap: 9, textDecoration: "none", marginRight: "2rem", flexShrink: 0 }}>
              <motion.div whileHover={{ scale: 1.06 }} whileTap={{ scale: 0.94 }}>
                <LogoIcon />
              </motion.div>
              <span style={{ fontWeight: 800, fontSize: "1.15rem", letterSpacing: "-0.03em", color: onScroll ? "var(--text)" : "white", transition: "color 0.3s" }}>
                Haroo
              </span>
            </Link>

            {/* ── Desktop primary nav ── */}
            <nav className="hide-mobile" style={{ display: "flex", alignItems: "center", gap: "0.25rem", flex: 1 }}>
              {(isAuthenticated ? PRIMARY_NAV : [{ to: "/documents", label: "Documents", icon: "📄" }, { to: "/agronomists", label: "Agronomes", icon: "👨‍🌾" }]).map((link) => {
                const active = location.pathname === link.to;
                return (
                  <Link
                    key={link.to}
                    to={link.to}
                    style={{
                      position: "relative",
                      padding: "6px 12px",
                      borderRadius: 8,
                      color: active ? (onScroll ? "var(--primary)" : "white") : textColor,
                      fontWeight: active ? 600 : 500,
                      fontSize: "0.88rem",
                      textDecoration: "none",
                      background: active && onScroll ? "rgba(var(--primary-rgb), 0.08)" : "transparent",
                      transition: "all 0.2s",
                    }}
                    onMouseEnter={(e) => { if (!active) (e.currentTarget as HTMLElement).style.color = onScroll ? "var(--text)" : "white"; }}
                    onMouseLeave={(e) => { if (!active) (e.currentTarget as HTMLElement).style.color = textColor; }}
                  >
                    {link.label}
                    {active && (
                      <motion.div layoutId="nav-pill" style={{ position: "absolute", bottom: -1, left: 8, right: 8, height: 2, background: onScroll ? "var(--primary)" : "white", borderRadius: 2 }} />
                    )}
                  </Link>
                );
              })}
            </nav>

            {/* ── Right actions ── */}
            <div className="hide-mobile" style={{ display: "flex", alignItems: "center", gap: 8, flexShrink: 0 }}>

              {/* Theme toggle */}
              <motion.button
                whileHover={{ scale: 1.08 }} whileTap={{ scale: 0.92 }}
                onClick={toggleTheme}
                title={isDark ? "Mode clair" : "Mode sombre"}
                style={{
                  width: 34, height: 34, borderRadius: 8, border: "none",
                  background: onScroll ? "var(--bg-secondary)" : "rgba(255,255,255,0.15)",
                  color: onScroll ? "var(--text-secondary)" : "white",
                  display: "flex", alignItems: "center", justifyContent: "center",
                  cursor: "pointer", transition: "all 0.2s",
                }}
              >
                {isDark ? <SunIcon /> : <MoonIcon />}
              </motion.button>

              {isAuthenticated && userInfo ? (
                /* ── User avatar + dropdown ── */
                <div ref={userMenuRef} style={{ position: "relative" }}>
                  <motion.button
                    whileHover={{ scale: 1.03 }} whileTap={{ scale: 0.97 }}
                    onClick={() => setUserMenuOpen(o => !o)}
                    style={{
                      display: "flex", alignItems: "center", gap: 8,
                      padding: "5px 10px 5px 5px",
                      borderRadius: 10,
                      border: `1px solid ${onScroll ? "var(--border)" : "rgba(255,255,255,0.25)"}`,
                      background: onScroll ? "var(--bg-secondary)" : "rgba(255,255,255,0.12)",
                      cursor: "pointer", transition: "all 0.2s",
                    }}
                  >
                    {/* Avatar */}
                    <div style={{
                      width: 28, height: 28, borderRadius: 7,
                      background: "var(--primary)",
                      display: "flex", alignItems: "center", justifyContent: "center",
                      color: "#fff", fontWeight: 700, fontSize: 12, flexShrink: 0,
                    }}>
                      {userInfo.initials}
                    </div>
                    <div style={{ textAlign: "left" }}>
                      <p style={{ margin: 0, fontSize: 13, fontWeight: 600, color: onScroll ? "var(--text)" : "white", lineHeight: 1.2 }}>
                        {userInfo.name}
                      </p>
                      {userInfo.type && (
                        <p style={{ margin: 0, fontSize: 10, color: onScroll ? "var(--muted)" : "rgba(255,255,255,0.7)", lineHeight: 1.2 }}>
                          {userInfo.type}
                        </p>
                      )}
                    </div>
                    <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke={onScroll ? "var(--muted)" : "rgba(255,255,255,0.7)"} strokeWidth="2.5" strokeLinecap="round" style={{ marginLeft: 2, transition: "transform 0.2s", transform: userMenuOpen ? "rotate(180deg)" : "rotate(0deg)" }}>
                      <polyline points="6 9 12 15 18 9"/>
                    </svg>
                  </motion.button>

                  {/* Dropdown */}
                  <AnimatePresence>
                    {userMenuOpen && (
                      <motion.div
                        initial={{ opacity: 0, scale: 0.95, y: -6 }}
                        animate={{ opacity: 1, scale: 1, y: 0 }}
                        exit={{ opacity: 0, scale: 0.95, y: -6 }}
                        transition={{ duration: 0.15 }}
                        style={{
                          position: "absolute", top: "calc(100% + 8px)", right: 0,
                          width: 220,
                          background: "var(--card)",
                          border: "1px solid var(--border)",
                          borderRadius: 14,
                          boxShadow: "0 16px 48px rgba(0,0,0,0.14)",
                          overflow: "hidden",
                          zIndex: 500,
                        }}
                      >
                        {/* User header in dropdown */}
                        <div style={{ padding: "14px 16px 10px", borderBottom: "1px solid var(--border)" }}>
                          <div style={{ display: "flex", alignItems: "center", gap: 10 }}>
                            <div style={{ width: 36, height: 36, borderRadius: 9, background: "var(--primary)", display: "flex", alignItems: "center", justifyContent: "center", color: "#fff", fontWeight: 700, fontSize: 14 }}>
                              {userInfo.initials}
                            </div>
                            <div>
                              <p style={{ margin: 0, fontSize: 13, fontWeight: 700, color: "var(--text)" }}>{userInfo.name}</p>
                              {userInfo.type && (
                                <span style={{ display: "inline-block", marginTop: 2, padding: "1px 7px", borderRadius: 10, fontSize: 10, fontWeight: 600, background: "rgba(var(--primary-rgb),0.12)", color: "var(--primary)" }}>
                                  {userInfo.type}
                                </span>
                              )}
                            </div>
                          </div>
                        </div>

                        {/* Menu links */}
                        <div style={{ padding: "6px 0" }}>
                          {USER_MENU.map((item) => {
                            const active = location.pathname === item.to;
                            return (
                              <Link
                                key={item.to}
                                to={item.to}
                                style={{
                                  display: "flex", alignItems: "center", gap: 10,
                                  padding: "9px 16px",
                                  color: active ? "var(--primary)" : "var(--text)",
                                  fontWeight: active ? 600 : 400,
                                  fontSize: 14,
                                  textDecoration: "none",
                                  background: active ? "rgba(var(--primary-rgb),0.07)" : "transparent",
                                  transition: "background 0.15s",
                                }}
                                onMouseEnter={(e) => { if (!active) (e.currentTarget as HTMLElement).style.background = "var(--bg)"; }}
                                onMouseLeave={(e) => { (e.currentTarget as HTMLElement).style.background = active ? "rgba(var(--primary-rgb),0.07)" : "transparent"; }}
                              >
                                <span style={{ color: active ? "var(--primary)" : "var(--muted)", display: "flex" }}>
                                  <item.icon />
                                </span>
                                {item.label}
                              </Link>
                            );
                          })}
                        </div>

                        {/* Divider + logout + theme */}
                        <div style={{ borderTop: "1px solid var(--border)", padding: "6px 0 4px" }}>
                          <button
                            onClick={toggleTheme}
                            style={{
                              width: "100%", display: "flex", alignItems: "center", gap: 10,
                              padding: "9px 16px", background: "none", border: "none",
                              color: "var(--text)", fontSize: 14, cursor: "pointer",
                              transition: "background 0.15s",
                            }}
                            onMouseEnter={(e) => { (e.currentTarget as HTMLElement).style.background = "var(--bg)"; }}
                            onMouseLeave={(e) => { (e.currentTarget as HTMLElement).style.background = "none"; }}
                          >
                            <span style={{ color: "var(--muted)", display: "flex" }}>{isDark ? <SunIcon /> : <MoonIcon />}</span>
                            {isDark ? "Mode clair" : "Mode sombre"}
                          </button>
                          <button
                            onClick={handleLogout}
                            style={{
                              width: "100%", display: "flex", alignItems: "center", gap: 10,
                              padding: "9px 16px", background: "none", border: "none",
                              color: "#dc2626", fontSize: 14, fontWeight: 500, cursor: "pointer",
                              transition: "background 0.15s",
                            }}
                            onMouseEnter={(e) => { (e.currentTarget as HTMLElement).style.background = "#fee2e2"; }}
                            onMouseLeave={(e) => { (e.currentTarget as HTMLElement).style.background = "none"; }}
                          >
                            <span style={{ display: "flex" }}><LogoutIcon /></span>
                            Déconnexion
                          </button>
                        </div>
                      </motion.div>
                    )}
                  </AnimatePresence>
                </div>
              ) : (
                /* ── Guest actions ── */
                <>
                  <Link to="/login" style={{ padding: "7px 14px", borderRadius: 8, color: onScroll ? "var(--text-secondary)" : "rgba(255,255,255,0.85)", fontWeight: 500, fontSize: "0.88rem", textDecoration: "none", transition: "color 0.2s" }}
                    onMouseEnter={(e) => { (e.currentTarget as HTMLElement).style.color = onScroll ? "var(--text)" : "white"; }}
                    onMouseLeave={(e) => { (e.currentTarget as HTMLElement).style.color = onScroll ? "var(--text-secondary)" : "rgba(255,255,255,0.85)"; }}
                  >
                    Connexion
                  </Link>
                  <motion.div whileHover={{ scale: 1.02 }} whileTap={{ scale: 0.97 }}>
                    <Link to="/register" style={{ padding: "8px 18px", borderRadius: 8, background: onScroll ? "var(--primary)" : "white", color: onScroll ? "white" : "var(--green-700)", fontWeight: 700, fontSize: "0.88rem", textDecoration: "none", display: "inline-block", boxShadow: "var(--shadow-sm)", transition: "all 0.2s" }}>
                      Commencer →
                    </Link>
                  </motion.div>
                </>
              )}
            </div>

            {/* ── Mobile burger ── */}
            <motion.button
              className="hide-desktop"
              whileTap={{ scale: 0.88 }}
              onClick={() => setMobileOpen(o => !o)}
              aria-label="Menu"
              style={{ background: "transparent", border: "none", cursor: "pointer", padding: 8, color: onScroll ? "var(--text)" : "white", display: "flex", alignItems: "center", marginLeft: "auto" }}
            >
              <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round">
                {mobileOpen ? (
                  <><line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/></>
                ) : (
                  <><line x1="4" y1="7" x2="20" y2="7"/><line x1="4" y1="14" x2="20" y2="14"/></>
                )}
              </svg>
            </motion.button>
          </div>
        </div>
      </motion.header>

      {/* ── Mobile menu ── */}
      <AnimatePresence>
        {mobileOpen && (
          <>
            <motion.div
              className="hide-desktop"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              onClick={() => setMobileOpen(false)}
              style={{ position: "fixed", inset: 0, background: "rgba(0,0,0,0.3)", zIndex: 398, top: 64 }}
            />
            <motion.div
              className="hide-desktop"
              initial={{ opacity: 0, x: "100%" }}
              animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0, x: "100%" }}
              transition={{ type: "spring", damping: 28, stiffness: 280 }}
              style={{
                position: "fixed", top: 64, right: 0, bottom: 0, width: "min(300px, 85vw)",
                background: "var(--card)",
                borderLeft: "1px solid var(--border)",
                zIndex: 399,
                overflowY: "auto",
                display: "flex", flexDirection: "column",
              }}
            >
              {/* User card in mobile */}
              {isAuthenticated && userInfo && (
                <div style={{ padding: "1.25rem 1.25rem 1rem", borderBottom: "1px solid var(--border)", background: "var(--bg)" }}>
                  <div style={{ display: "flex", alignItems: "center", gap: 12 }}>
                    <div style={{ width: 44, height: 44, borderRadius: 11, background: "var(--primary)", display: "flex", alignItems: "center", justifyContent: "center", color: "#fff", fontWeight: 800, fontSize: 16 }}>
                      {userInfo.initials}
                    </div>
                    <div>
                      <p style={{ margin: 0, fontWeight: 700, fontSize: 15, color: "var(--text)" }}>{userInfo.name}</p>
                      {userInfo.type && (
                        <span style={{ display: "inline-block", marginTop: 3, padding: "1px 8px", borderRadius: 10, fontSize: 11, fontWeight: 600, background: "rgba(var(--primary-rgb),0.12)", color: "var(--primary)" }}>
                          {userInfo.type}
                        </span>
                      )}
                    </div>
                  </div>
                </div>
              )}

              {/* Primary nav */}
              <div style={{ padding: "0.75rem", flex: 1 }}>
                <p style={{ margin: "0 0 6px 8px", fontSize: 11, fontWeight: 700, letterSpacing: 0.8, color: "var(--muted)", textTransform: "uppercase" }}>
                  {isAuthenticated ? "Navigation" : "Explorer"}
                </p>
                {(isAuthenticated ? PRIMARY_NAV : [{ to: "/documents", label: "Documents", icon: "📄" }, { to: "/agronomists", label: "Agronomes", icon: "👨‍🌾" }]).map((link) => {
                  const active = location.pathname === link.to;
                  return (
                    <Link
                      key={link.to}
                      to={link.to}
                      style={{
                        display: "flex", alignItems: "center", gap: 10,
                        padding: "11px 12px", borderRadius: 10,
                        color: active ? "var(--primary)" : "var(--text)",
                        fontWeight: active ? 600 : 400,
                        fontSize: 15, textDecoration: "none",
                        background: active ? "rgba(var(--primary-rgb),0.09)" : "transparent",
                        marginBottom: 2,
                      }}
                    >
                      <span style={{ fontSize: 16 }}>{link.icon}</span>
                      {link.label}
                    </Link>
                  );
                })}

                {isAuthenticated && (
                  <>
                    <p style={{ margin: "16px 0 6px 8px", fontSize: 11, fontWeight: 700, letterSpacing: 0.8, color: "var(--muted)", textTransform: "uppercase" }}>
                      Mon compte
                    </p>
                    {USER_MENU.map((item) => {
                      const active = location.pathname === item.to;
                      return (
                        <Link
                          key={item.to}
                          to={item.to}
                          style={{
                            display: "flex", alignItems: "center", gap: 10,
                            padding: "11px 12px", borderRadius: 10,
                            color: active ? "var(--primary)" : "var(--text)",
                            fontWeight: active ? 600 : 400,
                            fontSize: 15, textDecoration: "none",
                            background: active ? "rgba(var(--primary-rgb),0.09)" : "transparent",
                            marginBottom: 2,
                          }}
                        >
                          <span style={{ color: active ? "var(--primary)" : "var(--muted)", display: "flex" }}>
                            <item.icon />
                          </span>
                          {item.label}
                        </Link>
                      );
                    })}
                  </>
                )}
              </div>

              {/* Bottom actions */}
              <div style={{ padding: "0.75rem 0.75rem 1.25rem", borderTop: "1px solid var(--border)" }}>
                <button
                  onClick={toggleTheme}
                  style={{
                    width: "100%", display: "flex", alignItems: "center", gap: 10,
                    padding: "11px 12px", borderRadius: 10, background: "var(--bg)",
                    border: "1px solid var(--border)", color: "var(--text)",
                    fontSize: 14, cursor: "pointer", marginBottom: 8,
                  }}
                >
                  <span style={{ display: "flex" }}>{isDark ? <SunIcon /> : <MoonIcon />}</span>
                  {isDark ? "Passer en mode clair" : "Passer en mode sombre"}
                </button>

                {isAuthenticated ? (
                  <button
                    onClick={handleLogout}
                    style={{
                      width: "100%", display: "flex", alignItems: "center", justifyContent: "center", gap: 8,
                      padding: "12px", borderRadius: 10, border: "none",
                      background: "#fee2e2", color: "#dc2626",
                      fontSize: 14, fontWeight: 600, cursor: "pointer",
                    }}
                  >
                    <LogoutIcon />
                    Déconnexion
                  </button>
                ) : (
                  <div style={{ display: "flex", flexDirection: "column", gap: 8 }}>
                    <Link to="/login" style={{ textAlign: "center", padding: "11px", borderRadius: 10, background: "var(--bg)", border: "1px solid var(--border)", color: "var(--text)", fontWeight: 500, fontSize: 14, textDecoration: "none", display: "block" }}>
                      Connexion
                    </Link>
                    <Link to="/register" style={{ textAlign: "center", padding: "11px", borderRadius: 10, background: "var(--primary)", color: "white", fontWeight: 700, fontSize: 14, textDecoration: "none", display: "block" }}>
                      Commencer gratuitement →
                    </Link>
                  </div>
                )}
              </div>
            </motion.div>
          </>
        )}
      </AnimatePresence>
    </>
  );
};

export default Header;
