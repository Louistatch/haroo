import React from 'react';

interface SelectOption {
  value: string;
  label: string;
}

interface SelectProps extends React.SelectHTMLAttributes<HTMLSelectElement> {
  label?: string;
  error?: string;
  helpText?: string;
  options: SelectOption[];
  placeholder?: string;
}

/**
 * Touch-friendly select component
 * Optimized for mobile with minimum 44px touch target
 */
export const Select: React.FC<SelectProps> = ({ 
  label, 
  error, 
  helpText,
  options,
  placeholder,
  className = '',
  id,
  ...props 
}) => {
  const selectId = id || `select-${Math.random().toString(36).substr(2, 9)}`;
  const selectClasses = [
    error && 'form-error',
    className
  ].filter(Boolean).join(' ');

  return (
    <div className="form-group">
      {label && (
        <label htmlFor={selectId}>
          {label}
          {props.required && <span style={{ color: 'var(--error)' }}> *</span>}
        </label>
      )}
      <select
        id={selectId}
        className={selectClasses}
        {...props}
      >
        {placeholder && (
          <option value="" disabled>
            {placeholder}
          </option>
        )}
        {options.map((option) => (
          <option key={option.value} value={option.value}>
            {option.label}
          </option>
        ))}
      </select>
      {error && <span className="error-message">{error}</span>}
      {helpText && !error && <span className="form-help">{helpText}</span>}
    </div>
  );
};

export default Select;
