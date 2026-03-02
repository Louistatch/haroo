import React from 'react';

interface LoadingProps {
  size?: 'sm' | 'md' | 'lg';
  fullScreen?: boolean;
  message?: string;
}

export const Loading: React.FC<LoadingProps> = ({ 
  size = 'md', 
  fullScreen = false,
  message 
}) => {
  const sizes = {
    sm: '24px',
    md: '40px',
    lg: '60px'
  };

  const spinnerSize = sizes[size];

  const spinner = (
    <div style={{ textAlign: 'center' }}>
      <div
        className="spinner"
        style={{
          width: spinnerSize,
          height: spinnerSize,
          border: `${size === 'sm' ? '2px' : '3px'} solid var(--border)`,
          borderTopColor: 'var(--primary)',
          borderRadius: '50%',
          animation: 'spin 0.8s linear infinite',
          margin: '0 auto'
        }}
      />
      {message && (
        <p style={{
          marginTop: 'var(--spacing-md)',
          color: 'var(--text-secondary)',
          fontSize: 'var(--font-size-base)'
        }}>
          {message}
        </p>
      )}
    </div>
  );

  if (fullScreen) {
    return (
      <div style={{
        position: 'fixed',
        top: 0,
        left: 0,
        right: 0,
        bottom: 0,
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        background: 'var(--overlay)',
        zIndex: 'var(--z-modal)'
      }}>
        <div style={{
          background: 'var(--card)',
          padding: 'var(--spacing-xl)',
          borderRadius: 'var(--radius-lg)',
          boxShadow: 'var(--shadow-xl)'
        }}>
          {spinner}
        </div>
      </div>
    );
  }

  return spinner;
};

export default Loading;
