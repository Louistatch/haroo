import React from 'react';

interface IconProps {
  name: string;
  size?: number;
  className?: string;
}

/**
 * Composant Icon - Remplace les émojis par des images réelles
 * Utilise les images téléchargées dans /images
 */
export const Icon: React.FC<IconProps> = ({ 
  name, 
  size = 24, 
  className = '' 
}) => {
  // Mapping des noms d'icônes vers les images
  const iconMap: Record<string, string> = {
    // Agriculture
    'wheat': '/images/cultures/mais.jpg',
    'plant': '/images/cultures/riz.jpg',
    'culture': '/images/cultures/mais.jpg',
    
    // Documents
    'document': '/images/placeholder/document-default.jpg',
    'file': '/images/placeholder/document-default.jpg',
    
    // Utilisateurs
    'user': '/images/placeholder/user-default.jpg',
    'agronomist': '/images/users/agronomist-1.jpg',
    'farmer': '/images/hero/farmer.jpg',
    
    // Actions
    'download': '/images/hero/harvest.jpg',
    'cart': '/images/hero/market.jpg',
    'check': '/images/hero/agriculture.jpg',
    'warning': '/images/hero/market.jpg',
    'error': '/images/hero/market.jpg',
    
    // Stats
    'stats': '/images/hero/agriculture.jpg',
    'money': '/images/hero/market.jpg',
  };

  const imageSrc = iconMap[name] || '/images/placeholder/culture-default.jpg';

  return (
    <img 
      src={imageSrc}
      alt={name}
      className={`icon ${className}`}
      style={{
        width: size,
        height: size,
        objectFit: 'cover',
        borderRadius: '50%',
      }}
    />
  );
};

export default Icon;
