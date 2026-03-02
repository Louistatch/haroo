import React from 'react';

interface ContainerProps {
  children: React.ReactNode;
  className?: string;
}

/**
 * Responsive container component
 * Adapts to screen sizes from 320px to 1920px
 */
export const Container: React.FC<ContainerProps> = ({ children, className = '' }) => {
  return (
    <div className={`container ${className}`}>
      {children}
    </div>
  );
};

export default Container;
