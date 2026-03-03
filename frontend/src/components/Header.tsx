import React, { useState, useEffect } from "react";
import { Link, useLocation, useNavigate } from "react-router-dom";
import { motion, AnimatePresence } from "framer-motion";

interface HeaderProps {
  isAuthenticated: boolean;
}

function SunIcon() {
  return (
    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <circle cx="12" cy="12" r="5"/>
      <line x1="12" y1="1" x2="12" y2="3"/><line x1="12" y1="21" x2="12" y2="23"/>
      <line x1="4.22" y1="4.22" x2="5.64" y2="5.64"/><line x1="18.36" y1="18.36" x2="19.78" y2="19.78"/>
      <line x1="1" y1="12" x2="3" y2="12"/><line x1="21" y1="12" x2="23" y2="12"/>
      <line x1="4.22" y1="19.78" x2="5.64" y2="18.36"/><line x1="18.36" y1="5.64" x2="19.78" y2="4.22"/>
    </svg>
  );
}

function MoonIcon() {
  return (
    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
      <path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"/>
    </svg>
  );
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

const navLinks = [
  { to: "/documents", label: "Documents" },
  { to: "/agronomists", label: "Agronomes" },
];

const authLinks = [
  { to: "/home", label: "Tableau de bord" },
  { to: "/missions", label: "Missions" },
  { to: "/documents", label: "Documents" },
  { to: "/purchases", label: "Mes achats" },
  { to: "/me", label: "Profil" },
];

export const Header: React.FC<HeaderProps> = ({ isAuthenticated }) => {
  const [scrolled, setScrolled] = useState(false);
  const [mobileOpen, setMobileOpen] = useState(false);
  const [theme, setTheme] = useState<"light" | "dark" | "auto">(() => {
    return (localStorage.getItem("haroo-theme") as "light" | "dark" | "auto") || "auto";
  });

  const location = useLocation();
  const navigate = useNavigate();
  const isLandingPage = location.pathname === "/";

  useEffect(() => {
    const onScroll = () => setScrolled(window.scrollY > 12);
    window.addEventListener("scroll", onScroll, { passive: true });
    return () => window.removeEventListener("scroll", onScroll);
  }, []);

  useEffect(() => {
    setMobileOpen(false);
  }, [location.pathname]);

  useEffect(() => {
    const root = document.documentElement;
    if (theme === "auto") {
      root.removeAttribute("data-theme");
    } else {
      root.setAttribute("data-theme", theme);
    }
    localStorage.setItem("haroo-theme", theme);
  }, [theme]);

  const toggleTheme = () => {
    setTheme((t) => {
      if (t === "auto" || t === "light") return "dark";
      return "light";
    });
  };

  const isDark =
    theme === "dark" ||
    (theme === "auto" && window.matchMedia("(prefers-color-scheme: dark)").matches);

  const handleLogout = () => {
    localStorage.removeItem("access_token");
    localStorage.removeItem("refresh_token");
    navigate("/");
  };

  const links = isAuthenticated ? authLinks : navLinks;

  return (
    <>
      <motion.header
        initial={{ y: -64, opacity: 0 }}
        animate={{ y: 0, opacity: 1 }}
        transition={{ duration: 0.5, ease: [0.0, 0, 0.2, 1] }}
        style={{
          position: "fixed",
          top: 0,
          left: 0,
          right: 0,
          zIndex: 400,
          transition: "all 0.3s ease",
        }}
      >
        <div
          style={{
            background: (scrolled || !isLandingPage) ? "var(--header-bg)" : "transparent",
            backdropFilter: (scrolled || !isLandingPage) ? "blur(20px) saturate(180%)" : "none",
            WebkitBackdropFilter: (scrolled || !isLandingPage) ? "blur(20px) saturate(180%)" : "none",
            borderBottom: (scrolled || !isLandingPage) ? `1px solid var(--header-border)` : "1px solid transparent",
            boxShadow: (scrolled || !isLandingPage) ? "0 1px 20px rgba(0,0,0,0.08)" : "none",
            transition: "all 0.3s ease",
          }}
        >
          <div className="container" style={{ display: "flex", alignItems: "center", justifyContent: "space-between", height: "64px" }}>
            {/* Logo */}
            <Link
              to={isAuthenticated ? "/home" : "/"}
              style={{
                display: "flex",
                alignItems: "center",
                gap: "10px",
                textDecoration: "none",
              }}
            >
              <motion.div whileHover={{ scale: 1.05 }} whileTap={{ scale: 0.95 }}>
                <LogoIcon />
              </motion.div>
              <span style={{
                fontWeight: 800,
                fontSize: "1.2rem",
                color: (scrolled || !isLandingPage) ? "var(--text)" : "white",
                letterSpacing: "-0.03em",
                transition: "color 0.3s ease",
              }}>
                Haroo
              </span>
            </Link>

            {/* Desktop Nav */}
            <nav className="hide-mobile" style={{ display: "flex", alignItems: "center", gap: "2rem" }}>
              {links.map((link) => (
                <Link
                  key={link.to}
                  to={link.to}
                  style={{
                    color: (scrolled || !isLandingPage) ? "var(--text-secondary)" : "rgba(255,255,255,0.85)",
                    fontWeight: 500,
                    fontSize: "0.9rem",
                    transition: "color 0.2s ease",
                    position: "relative",
                  }}
                  onMouseEnter={(e) => {
                    (e.currentTarget as HTMLElement).style.color = (scrolled || !isLandingPage) ? "var(--text)" : "white";
                  }}
                  onMouseLeave={(e) => {
                    (e.currentTarget as HTMLElement).style.color = (scrolled || !isLandingPage) ? "var(--text-secondary)" : "rgba(255,255,255,0.85)";
                  }}
                >
                  {link.label}
                  {location.pathname === link.to && (
                    <motion.div
                      layoutId="nav-indicator"
                      style={{
                        position: "absolute",
                        bottom: "-4px",
                        left: 0,
                        right: 0,
                        height: "2px",
                        background: "var(--primary)",
                        borderRadius: "2px",
                      }}
                    />
                  )}
                </Link>
              ))}
            </nav>

            {/* Right Actions */}
            <div className="hide-mobile" style={{ display: "flex", alignItems: "center", gap: "0.75rem" }}>
              {/* Dark mode toggle */}
              <motion.button
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
                onClick={toggleTheme}
                style={{
                  background: (scrolled || !isLandingPage) ? "var(--bg-secondary)" : "rgba(255,255,255,0.15)",
                  border: "none",
                  borderRadius: "var(--radius-lg)",
                  padding: "8px",
                  cursor: "pointer",
                  color: (scrolled || !isLandingPage) ? "var(--text-secondary)" : "white",
                  display: "flex",
                  alignItems: "center",
                  justifyContent: "center",
                  width: "36px",
                  height: "36px",
                  transition: "all 0.2s ease",
                }}
                title={isDark ? "Mode clair" : "Mode sombre"}
              >
                {isDark ? <SunIcon /> : <MoonIcon />}
              </motion.button>

              {isAuthenticated ? (
                <motion.button
                  whileHover={{ scale: 1.02 }}
                  whileTap={{ scale: 0.98 }}
                  onClick={handleLogout}
                  style={{
                    background: (scrolled || !isLandingPage) ? "var(--bg-secondary)" : "rgba(255,255,255,0.15)",
                    color: (scrolled || !isLandingPage) ? "var(--text)" : "white",
                    border: `1px solid ${(scrolled || !isLandingPage) ? "var(--border)" : "rgba(255,255,255,0.3)"}`,
                    padding: "8px 18px",
                    borderRadius: "var(--radius-lg)",
                    fontSize: "0.875rem",
                    fontWeight: 500,
                    cursor: "pointer",
                    transition: "all 0.2s ease",
                  }}
                >
                  Déconnexion
                </motion.button>
              ) : (
                <>
                  <Link
                    to="/login"
                    style={{
                      color: (scrolled || !isLandingPage) ? "var(--text-secondary)" : "rgba(255,255,255,0.85)",
                      fontWeight: 500,
                      fontSize: "0.9rem",
                      padding: "8px 14px",
                      transition: "color 0.2s ease",
                    }}
                  >
                    Connexion
                  </Link>
                  <motion.div whileHover={{ scale: 1.02 }} whileTap={{ scale: 0.98 }}>
                    <Link
                      to="/register"
                      style={{
                        background: (scrolled || !isLandingPage) ? "var(--primary)" : "white",
                        color: (scrolled || !isLandingPage) ? "white" : "var(--green-700)",
                        padding: "9px 20px",
                        borderRadius: "var(--radius-lg)",
                        fontSize: "0.875rem",
                        fontWeight: 700,
                        display: "inline-block",
                        boxShadow: "var(--shadow-sm)",
                        transition: "all 0.2s ease",
                      }}
                    >
                      Commencer →
                    </Link>
                  </motion.div>
                </>
              )}
            </div>

            {/* Mobile Burger */}
            <motion.button
              className="hide-desktop"
              whileTap={{ scale: 0.9 }}
              onClick={() => setMobileOpen(!mobileOpen)}
              style={{
                background: "transparent",
                border: "none",
                cursor: "pointer",
                padding: "8px",
                color: (scrolled || !isLandingPage) ? "var(--text)" : "white",
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
              }}
              aria-label="Menu"
            >
              <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round">
                {mobileOpen ? (
                  <>
                    <line x1="18" y1="6" x2="6" y2="18"/>
                    <line x1="6" y1="6" x2="18" y2="18"/>
                  </>
                ) : (
                  <>
                    <line x1="4" y1="8" x2="20" y2="8"/>
                    <line x1="4" y1="14" x2="20" y2="14"/>
                    <line x1="4" y1="20" x2="20" y2="20"/>
                  </>
                )}
              </svg>
            </motion.button>
          </div>
        </div>
      </motion.header>

      {/* Mobile Menu */}
      <AnimatePresence>
        {mobileOpen && (
          <motion.div
            className="hide-desktop"
            initial={{ opacity: 0, y: -10 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -10 }}
            transition={{ duration: 0.2 }}
            style={{
              position: "fixed",
              top: "64px",
              left: 0,
              right: 0,
              background: "var(--surface)",
              borderBottom: "1px solid var(--border)",
              zIndex: 399,
              padding: "1rem 1.5rem 1.5rem",
              boxShadow: "var(--shadow-xl)",
            }}
          >
            <div style={{ display: "flex", flexDirection: "column", gap: "0.5rem" }}>
              {links.map((link) => (
                <Link
                  key={link.to}
                  to={link.to}
                  style={{
                    padding: "12px 16px",
                    borderRadius: "var(--radius-lg)",
                    color: "var(--text)",
                    fontWeight: 500,
                    background: location.pathname === link.to ? "var(--primary-glow)" : "transparent",
                    display: "block",
                  }}
                >
                  {link.label}
                </Link>
              ))}
              <div style={{ borderTop: "1px solid var(--border)", marginTop: "0.5rem", paddingTop: "0.75rem", display: "flex", flexDirection: "column", gap: "0.5rem" }}>
                {isAuthenticated ? (
                  <button
                    onClick={handleLogout}
                    style={{
                      padding: "12px 16px", borderRadius: "var(--radius-lg)",
                      background: "var(--error)", color: "white",
                      border: "none", fontWeight: 600, textAlign: "left",
                      cursor: "pointer",
                    }}
                  >
                    Déconnexion
                  </button>
                ) : (
                  <>
                    <Link to="/login" style={{ padding: "12px 16px", borderRadius: "var(--radius-lg)", color: "var(--text)", fontWeight: 500, background: "var(--bg-secondary)", display: "block", textAlign: "center" }}>
                      Connexion
                    </Link>
                    <Link to="/register" style={{ padding: "12px 16px", borderRadius: "var(--radius-lg)", color: "white", fontWeight: 700, background: "var(--primary)", display: "block", textAlign: "center" }}>
                      Commencer gratuitement →
                    </Link>
                  </>
                )}
                <button
                  onClick={toggleTheme}
                  style={{
                    padding: "12px 16px", borderRadius: "var(--radius-lg)",
                    background: "var(--bg-secondary)", color: "var(--text-secondary)",
                    border: "none", fontWeight: 500, textAlign: "left",
                    cursor: "pointer", display: "flex", alignItems: "center", gap: "8px",
                  }}
                >
                  {isDark ? <SunIcon /> : <MoonIcon />}
                  {isDark ? "Mode clair" : "Mode sombre"}
                </button>
              </div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </>
  );
};

export default Header;
