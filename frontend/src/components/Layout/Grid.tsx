import React from 'react';

interface GridProps {
  children: React.ReactNode;
  cols?: {
    xs?: number;
    sm?: number;
    md?: number;
    lg?: number;
  };
  gap?: 'sm' | 'md' | 'lg';
  className?: string;
}

/**
 * Responsive grid component
 * Supports different column counts for different breakpoints
 */
export const Grid: React.FC<GridProps> = ({ 
  children, 
  cols = { xs: 1, sm: 2, md: 3, lg: 4 },
  gap = 'md',
  className = '' 
}) => {
  const gridClasses = [
    'grid',
    cols.sm && `grid-sm-${cols.sm}`,
    cols.md && `grid-md-${cols.md}`,
    cols.lg && `grid-lg-${cols.lg}`,
    `gap-${gap}`,
    className
  ].filter(Boolean).join(' ');

  return (
    <div className={gridClasses}>
      {children}
    </div>
  );
};

export default Grid;
