import React from 'react';

interface TextAreaProps extends React.TextareaHTMLAttributes<HTMLTextAreaElement> {
  label?: string;
  error?: string;
  helpText?: string;
}

/**
 * Touch-friendly textarea component
 * Optimized for mobile with minimum 44px touch target
 */
export const TextArea: React.FC<TextAreaProps> = ({ 
  label, 
  error, 
  helpText,
  className = '',
  id,
  ...props 
}) => {
  const textareaId = id || `textarea-${Math.random().toString(36).substr(2, 9)}`;
  const textareaClasses = [
    error && 'form-error',
    className
  ].filter(Boolean).join(' ');

  return (
    <div className="form-group">
      {label && (
        <label htmlFor={textareaId}>
          {label}
          {props.required && <span style={{ color: 'var(--error)' }}> *</span>}
        </label>
      )}
      <textarea
        id={textareaId}
        className={textareaClasses}
        {...props}
      />
      {error && <span className="error-message">{error}</span>}
      {helpText && !error && <span className="form-help">{helpText}</span>}
    </div>
  );
};

export default TextArea;
