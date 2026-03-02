import React from 'react';

interface CheckboxProps extends Omit<React.InputHTMLAttributes<HTMLInputElement>, 'type'> {
  label: string;
  error?: string;
}

/**
 * Touch-friendly checkbox component
 * Optimized for mobile with larger touch targets
 */
export const Checkbox: React.FC<CheckboxProps> = ({ 
  label, 
  error,
  className = '',
  id,
  ...props 
}) => {
  const checkboxId = id || `checkbox-${Math.random().toString(36).substr(2, 9)}`;

  return (
    <div className="form-group">
      <div className="form-check">
        <input
          type="checkbox"
          id={checkboxId}
          className={className}
          {...props}
        />
        <label htmlFor={checkboxId}>
          {label}
        </label>
      </div>
      {error && <span className="error-message">{error}</span>}
    </div>
  );
};

export default Checkbox;
