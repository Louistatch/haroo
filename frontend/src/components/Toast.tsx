import React, { useEffect } from 'react';

export type ToastType = 'success' | 'error' | 'warning' | 'info';

interface ToastProps {
  message: string;
  type?: ToastType;
  duration?: number;
  onClose: () => void;
}

export const Toast: React.FC<ToastProps> = ({ 
  message, 
  type = 'info', 
  duration = 4000,
  onClose 
}) => {
  useEffect(() => {
    const timer = setTimeout(onClose, duration);
    return () => clearTimeout(timer);
  }, [duration, onClose]);

  const icons = {
    success: '✓',
    error: '✕',
    warning: '⚠',
    info: 'ℹ'
  };

  const colors = {
    success: { bg: '#d4edda', border: '#c3e6cb', text: '#155724' },
    error: { bg: '#f8d7da', border: '#f5c6cb', text: '#721c24' },
    warning: { bg: '#fff3cd', border: '#ffeaa7', text: '#856404' },
    info: { bg: '#d1ecf1', border: '#bee5eb', text: '#0c5460' }
  };

  const style = colors[type];

  return (
    <div
      role="alert"
      style={{
        position: 'fixed',
        top: '80px',
        right: '20px',
        minWidth: '300px',
        maxWidth: '500px',
        padding: '1rem 1.5rem',
        background: style.bg,
        border: `1px solid ${style.border}`,
        borderLeft: `4px solid ${style.text}`,
        borderRadius: 'var(--radius-md)',
        boxShadow: 'var(--shadow-lg)',
        display: 'flex',
        alignItems: 'center',
        gap: '1rem',
        zIndex: 'var(--z-tooltip)',
        animation: 'slideIn 0.3s ease-out'
      }}
    >
      <span style={{ 
        fontSize: '1.5rem',
        color: style.text,
        fontWeight: 'bold'
      }}>
        {icons[type]}
      </span>
      <p style={{ 
        flex: 1,
        margin: 0,
        color: style.text,
        fontSize: 'var(--font-size-base)'
      }}>
        {message}
      </p>
      <button
        onClick={onClose}
        style={{
          background: 'transparent',
          border: 'none',
          color: style.text,
          fontSize: '1.25rem',
          cursor: 'pointer',
          padding: '0.25rem',
          lineHeight: 1
        }}
        aria-label="Fermer"
      >
        ×
      </button>

      <style>{`
        @keyframes slideIn {
          from {
            transform: translateX(100%);
            opacity: 0;
          }
          to {
            transform: translateX(0);
            opacity: 1;
          }
        }

        @media (max-width: 768px) {
          div[role="alert"] {
            right: 10px;
            left: 10px;
            min-width: auto;
          }
        }
      `}</style>
    </div>
  );
};

// Hook pour gérer les toasts
export const useToast = () => {
  const [toasts, setToasts] = React.useState<Array<{
    id: number;
    message: string;
    type: ToastType;
  }>>([]);

  const showToast = (message: string, type: ToastType = 'info') => {
    const id = Date.now();
    setToasts(prev => [...prev, { id, message, type }]);
  };

  const removeToast = (id: number) => {
    setToasts(prev => prev.filter(toast => toast.id !== id));
  };

  const ToastContainer = () => (
    <>
      {toasts.map(toast => (
        <Toast
          key={toast.id}
          message={toast.message}
          type={toast.type}
          onClose={() => removeToast(toast.id)}
        />
      ))}
    </>
  );

  return { showToast, ToastContainer };
};

export default Toast;
