import React, { useEffect, useRef, useState } from 'react';
import { lazyLoadImage, generateSrcSet, generateSizes } from '../utils/imageOptimization';

interface ResponsiveImageProps {
  src: string;
  alt: string;
  className?: string;
  lazy?: boolean;
  widths?: number[];
  sizes?: string;
  onLoad?: () => void;
  onError?: () => void;
}

/**
 * Responsive image component with lazy loading and optimization
 * Automatically generates srcset for different screen sizes
 */
export const ResponsiveImage: React.FC<ResponsiveImageProps> = ({
  src,
  alt,
  className = '',
  lazy = true,
  widths = [320, 640, 768, 1024, 1280],
  sizes,
  onLoad,
  onError
}) => {
  const imgRef = useRef<HTMLImageElement>(null);
  const [loaded, setLoaded] = useState(false);

  useEffect(() => {
    if (lazy && imgRef.current) {
      lazyLoadImage(imgRef.current);
    }
  }, [lazy]);

  const handleLoad = () => {
    setLoaded(true);
    onLoad?.();
  };

  const handleError = () => {
    onError?.();
  };

  const imgClasses = [
    'img-responsive',
    loaded && 'loaded',
    className
  ].filter(Boolean).join(' ');

  if (lazy) {
    return (
      <img
        ref={imgRef}
        data-src={src}
        data-srcset={generateSrcSet(src, widths)}
        sizes={sizes || generateSizes()}
        alt={alt}
        className={imgClasses}
        onLoad={handleLoad}
        onError={handleError}
        loading="lazy"
      />
    );
  }

  return (
    <img
      ref={imgRef}
      src={src}
      srcSet={generateSrcSet(src, widths)}
      sizes={sizes || generateSizes()}
      alt={alt}
      className={imgClasses}
      onLoad={handleLoad}
      onError={handleError}
    />
  );
};

export default ResponsiveImage;
