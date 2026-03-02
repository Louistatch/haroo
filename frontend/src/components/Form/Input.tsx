import React from 'react';

interface InputProps extends React.InputHTMLAttributes<HTMLInputElement> {
  label?: string;
  error?: string;
  helpText?: string;
}

/**
 * Touch-friendly input component
 * Optimized for mobile with minimum 44px touch target
 */
export const Input: React.FC<InputProps> = ({ 
  label, 
  error, 
  helpText,
  className = '',
  id,
  ...props 
}) => {
  const inputId = id || `input-${Math.random().toString(36).substr(2, 9)}`;
  const inputClasses = [
    error && 'form-error',
    className
  ].filter(Boolean).join(' ');

  return (
    <div className="form-group">
      {label && (
        <label htmlFor={inputId}>
          {label}
          {props.required && <span style={{ color: 'var(--error)' }}> *</span>}
        </label>
      )}
      <input
        id={inputId}
        className={inputClasses}
        {...props}
      />
      {error && <span className="error-message">{error}</span>}
      {helpText && !error && <span className="form-help">{helpText}</span>}
    </div>
  );
};

export default Input;
