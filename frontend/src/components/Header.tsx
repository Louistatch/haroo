import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';

interface HeaderProps {
  isAuthenticated: boolean;
}

/**
 * Responsive header component with improved navigation
 */
export const Header: React.FC<HeaderProps> = ({ isAuthenticated }) => {
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
  const navigate = useNavigate();

  const toggleMobileMenu = () => {
    setMobileMenuOpen(!mobileMenuOpen);
  };

  const handleLogout = () => {
    localStorage.removeItem("access_token");
    localStorage.removeItem("refresh_token");
    setMobileMenuOpen(false);
    navigate('/');
  };

  return (
    <header style={{
      background: 'linear-gradient(135deg, #2e7d32 0%, #4caf50 100%)',
      boxShadow: '0 2px 8px rgba(0, 0, 0, 0.15)',
      position: 'sticky',
      top: 0,
      zIndex: 1000
    }}>
      <div style={{ 
        maxWidth: '1200px', 
        margin: '0 auto',
        padding: '0 1rem'
      }}>
        <nav style={{
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          minHeight: '64px'
        }}>
          {/* Logo */}
          <Link 
            to={isAuthenticated ? "/home" : "/"} 
            style={{
              fontSize: '1.5rem',
              fontWeight: 'bold',
              color: 'white',
              textDecoration: 'none',
              display: 'flex',
              alignItems: 'center',
              gap: '0.5rem'
            }}
          >
            <span style={{ fontSize: '1.8rem' }}>🌾</span>
            <span className="hide-mobile">Plateforme Agricole Togo</span>
            <span className="hide-desktop">PAT</span>
          </Link>

          {/* Desktop Navigation */}
          <div className="hide-mobile" style={{ 
            display: 'flex', 
            gap: '2rem', 
            alignItems: 'center' 
          }}>
            {isAuthenticated ? (
              <>
                <Link 
                  to="/home" 
                  style={{ 
                    color: 'white', 
                    textDecoration: 'none',
                    fontWeight: 500,
                    transition: 'opacity 0.2s'
                  }}
                  onMouseEnter={(e) => e.currentTarget.style.opacity = '0.8'}
                  onMouseLeave={(e) => e.currentTarget.style.opacity = '1'}
                >
                  Accueil
                </Link>
                <Link 
                  to="/me" 
                  style={{ 
                    color: 'white', 
                    textDecoration: 'none',
                    fontWeight: 500,
                    transition: 'opacity 0.2s'
                  }}
                  onMouseEnter={(e) => e.currentTarget.style.opacity = '0.8'}
                  onMouseLeave={(e) => e.currentTarget.style.opacity = '1'}
                >
                  Mon Profil
                </Link>
                <button 
                  onClick={handleLogout}
                  style={{
                    background: 'rgba(255, 255, 255, 0.2)',
                    color: 'white',
                    border: '1px solid white',
                    padding: '0.5rem 1.5rem',
                    borderRadius: '6px',
                    cursor: 'pointer',
                    fontWeight: 500,
                    transition: 'all 0.2s'
                  }}
                  onMouseEnter={(e) => {
                    e.currentTarget.style.background = 'white';
                    e.currentTarget.style.color = '#2e7d32';
                  }}
                  onMouseLeave={(e) => {
                    e.currentTarget.style.background = 'rgba(255, 255, 255, 0.2)';
                    e.currentTarget.style.color = 'white';
                  }}
                >
                  Déconnexion
                </button>
              </>
            ) : (
              <>
                <Link 
                  to="/" 
                  style={{ 
                    color: 'white', 
                    textDecoration: 'none',
                    fontWeight: 500,
                    transition: 'opacity 0.2s'
                  }}
                  onMouseEnter={(e) => e.currentTarget.style.opacity = '0.8'}
                  onMouseLeave={(e) => e.currentTarget.style.opacity = '1'}
                >
                  Accueil
                </Link>
                <Link 
                  to="/login" 
                  style={{ 
                    color: 'white', 
                    textDecoration: 'none',
                    fontWeight: 500,
                    transition: 'opacity 0.2s'
                  }}
                  onMouseEnter={(e) => e.currentTarget.style.opacity = '0.8'}
                  onMouseLeave={(e) => e.currentTarget.style.opacity = '1'}
                >
                  Connexion
                </Link>
                <Link to="/register">
                  <button 
                    style={{
                      background: 'white',
                      color: '#2e7d32',
                      border: 'none',
                      padding: '0.5rem 1.5rem',
                      borderRadius: '6px',
                      cursor: 'pointer',
                      fontWeight: 'bold',
                      transition: 'transform 0.2s',
                      boxShadow: '0 2px 4px rgba(0,0,0,0.1)'
                    }}
                    onMouseEnter={(e) => e.currentTarget.style.transform = 'translateY(-2px)'}
                    onMouseLeave={(e) => e.currentTarget.style.transform = 'translateY(0)'}
                  >
                    Inscription
                  </button>
                </Link>
              </>
            )}
          </div>

          {/* Mobile Menu Button */}
          <button
            className="hide-desktop"
            onClick={toggleMobileMenu}
            style={{
              background: 'transparent',
              border: 'none',
              padding: '0.5rem',
              cursor: 'pointer',
              minHeight: '44px',
              minWidth: '44px',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              color: 'white'
            }}
            aria-label="Menu"
          >
            <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5">
              {mobileMenuOpen ? (
                <>
                  <line x1="18" y1="6" x2="6" y2="18" />
                  <line x1="6" y1="6" x2="18" y2="18" />
                </>
              ) : (
                <>
                  <line x1="3" y1="12" x2="21" y2="12" />
                  <line x1="3" y1="6" x2="21" y2="6" />
                  <line x1="3" y1="18" x2="21" y2="18" />
                </>
              )}
            </svg>
          </button>
        </nav>

        {/* Mobile Menu */}
        {mobileMenuOpen && (
          <div 
            className="hide-desktop"
            style={{
              borderTop: '1px solid rgba(255, 255, 255, 0.2)',
              paddingTop: '1rem',
              paddingBottom: '1rem'
            }}
          >
            {isAuthenticated ? (
              <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
                <Link 
                  to="/home" 
                  onClick={() => setMobileMenuOpen(false)}
                  style={{
                    padding: '0.75rem 1rem',
                    textDecoration: 'none',
                    color: 'white',
                    borderRadius: '6px',
                    background: 'rgba(255, 255, 255, 0.1)',
                    fontWeight: 500
                  }}
                >
                  🏠 Accueil
                </Link>
                <Link 
                  to="/me" 
                  onClick={() => setMobileMenuOpen(false)}
                  style={{
                    padding: '0.75rem 1rem',
                    textDecoration: 'none',
                    color: 'white',
                    borderRadius: '6px',
                    background: 'rgba(255, 255, 255, 0.1)',
                    fontWeight: 500
                  }}
                >
                  👤 Mon Profil
                </Link>
                <button 
                  onClick={handleLogout}
                  style={{
                    padding: '0.75rem 1rem',
                    background: 'white',
                    color: '#2e7d32',
                    border: 'none',
                    borderRadius: '6px',
                    cursor: 'pointer',
                    fontWeight: 'bold',
                    textAlign: 'left'
                  }}
                >
                  🚪 Déconnexion
                </button>
              </div>
            ) : (
              <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
                <Link 
                  to="/" 
                  onClick={() => setMobileMenuOpen(false)}
                  style={{
                    padding: '0.75rem 1rem',
                    textDecoration: 'none',
                    color: 'white',
                    borderRadius: '6px',
                    background: 'rgba(255, 255, 255, 0.1)',
                    fontWeight: 500
                  }}
                >
                  🏠 Accueil
                </Link>
                <Link 
                  to="/login" 
                  onClick={() => setMobileMenuOpen(false)}
                >
                  <button 
                    style={{
                      width: '100%',
                      padding: '0.75rem 1rem',
                      background: 'rgba(255, 255, 255, 0.2)',
                      color: 'white',
                      border: '1px solid white',
                      borderRadius: '6px',
                      cursor: 'pointer',
                      fontWeight: 500
                    }}
                  >
                    Connexion
                  </button>
                </Link>
                <Link 
                  to="/register" 
                  onClick={() => setMobileMenuOpen(false)}
                >
                  <button 
                    style={{
                      width: '100%',
                      padding: '0.75rem 1rem',
                      background: 'white',
                      color: '#2e7d32',
                      border: 'none',
                      borderRadius: '6px',
                      cursor: 'pointer',
                      fontWeight: 'bold'
                    }}
                  >
                    Inscription
                  </button>
                </Link>
              </div>
            )}
          </div>
        )}
      </div>

      <style>{`
        @media (max-width: 768px) {
          .hide-mobile {
            display: none !important;
          }
        }
        @media (min-width: 769px) {
          .hide-desktop {
            display: none !important;
          }
        }
      `}</style>
    </header>
  );
};

export default Header;
