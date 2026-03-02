/**
 * Image Optimization Utilities for 3G Connections
 * Optimizes images for mobile data consumption
 */

export interface ImageOptimizationOptions {
  maxWidth?: number;
  maxHeight?: number;
  quality?: number;
  format?: 'jpeg' | 'webp' | 'png';
}

/**
 * Compress and resize an image file for optimal mobile performance
 * @param file - The image file to optimize
 * @param options - Optimization options
 * @returns Promise with optimized blob
 */
export async function optimizeImage(
  file: File,
  options: ImageOptimizationOptions = {}
): Promise<Blob> {
  const {
    maxWidth = 1200,
    maxHeight = 1200,
    quality = 0.8,
    format = 'jpeg'
  } = options;

  return new Promise((resolve, reject) => {
    const reader = new FileReader();
    
    reader.onload = (e) => {
      const img = new Image();
      
      img.onload = () => {
        // Calculate new dimensions while maintaining aspect ratio
        let width = img.width;
        let height = img.height;
        
        if (width > maxWidth) {
          height = (height * maxWidth) / width;
          width = maxWidth;
        }
        
        if (height > maxHeight) {
          width = (width * maxHeight) / height;
          height = maxHeight;
        }
        
        // Create canvas and draw resized image
        const canvas = document.createElement('canvas');
        canvas.width = width;
        canvas.height = height;
        
        const ctx = canvas.getContext('2d');
        if (!ctx) {
          reject(new Error('Could not get canvas context'));
          return;
        }
        
        ctx.drawImage(img, 0, 0, width, height);
        
        // Convert to blob with compression
        canvas.toBlob(
          (blob) => {
            if (blob) {
              resolve(blob);
            } else {
              reject(new Error('Failed to create blob'));
            }
          },
          `image/${format}`,
          quality
        );
      };
      
      img.onerror = () => reject(new Error('Failed to load image'));
      img.src = e.target?.result as string;
    };
    
    reader.onerror = () => reject(new Error('Failed to read file'));
    reader.readAsDataURL(file);
  });
}

/**
 * Generate responsive image srcset for different screen sizes
 * @param baseUrl - Base URL of the image
 * @param widths - Array of widths to generate
 * @returns srcset string
 */
export function generateSrcSet(baseUrl: string, widths: number[] = [320, 640, 768, 1024, 1280]): string {
  return widths
    .map(width => `${baseUrl}?w=${width} ${width}w`)
    .join(', ');
}

/**
 * Generate sizes attribute for responsive images
 * @returns sizes string
 */
export function generateSizes(): string {
  return '(max-width: 640px) 100vw, (max-width: 1024px) 50vw, 33vw';
}

/**
 * Lazy load images using Intersection Observer
 * @param imageElement - The image element to lazy load
 */
export function lazyLoadImage(imageElement: HTMLImageElement): void {
  if ('IntersectionObserver' in window) {
    const observer = new IntersectionObserver((entries) => {
      entries.forEach(entry => {
        if (entry.isIntersecting) {
          const img = entry.target as HTMLImageElement;
          const src = img.dataset.src;
          const srcset = img.dataset.srcset;
          
          if (src) {
            img.src = src;
          }
          if (srcset) {
            img.srcset = srcset;
          }
          
          img.classList.add('loaded');
          observer.unobserve(img);
        }
      });
    }, {
      rootMargin: '50px' // Start loading 50px before entering viewport
    });
    
    observer.observe(imageElement);
  } else {
    // Fallback for browsers without Intersection Observer
    const src = imageElement.dataset.src;
    const srcset = imageElement.dataset.srcset;
    
    if (src) {
      imageElement.src = src;
    }
    if (srcset) {
      imageElement.srcset = srcset;
    }
  }
}

/**
 * Calculate optimal image dimensions based on container and device pixel ratio
 * @param containerWidth - Width of the container
 * @param containerHeight - Height of the container
 * @returns Optimal dimensions
 */
export function calculateOptimalDimensions(
  containerWidth: number,
  containerHeight: number
): { width: number; height: number } {
  const dpr = window.devicePixelRatio || 1;
  
  // Cap DPR at 2 for mobile to save bandwidth
  const effectiveDpr = Math.min(dpr, 2);
  
  return {
    width: Math.ceil(containerWidth * effectiveDpr),
    height: Math.ceil(containerHeight * effectiveDpr)
  };
}

/**
 * Check if user is on a slow connection (3G or slower)
 * @returns true if connection is slow
 */
export function isSlowConnection(): boolean {
  if ('connection' in navigator) {
    const connection = (navigator as any).connection;
    
    if (connection) {
      // Check effective type
      if (connection.effectiveType) {
        return ['slow-2g', '2g', '3g'].includes(connection.effectiveType);
      }
      
      // Check save data preference
      if (connection.saveData) {
        return true;
      }
    }
  }
  
  return false;
}

/**
 * Get image quality based on connection speed
 * @returns Quality value (0-1)
 */
export function getAdaptiveQuality(): number {
  if (isSlowConnection()) {
    return 0.6; // Lower quality for slow connections
  }
  return 0.8; // Standard quality
}

/**
 * Preload critical images
 * @param urls - Array of image URLs to preload
 */
export function preloadImages(urls: string[]): void {
  urls.forEach(url => {
    const link = document.createElement('link');
    link.rel = 'preload';
    link.as = 'image';
    link.href = url;
    document.head.appendChild(link);
  });
}

/**
 * Convert file size to human readable format
 * @param bytes - File size in bytes
 * @returns Formatted string
 */
export function formatFileSize(bytes: number): string {
  if (bytes === 0) return '0 Bytes';
  
  const k = 1024;
  const sizes = ['Bytes', 'KB', 'MB', 'GB'];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  
  return Math.round((bytes / Math.pow(k, i)) * 100) / 100 + ' ' + sizes[i];
}

/**
 * Validate image file before upload
 * @param file - File to validate
 * @param maxSize - Maximum file size in bytes (default 10MB)
 * @returns Validation result
 */
export function validateImageFile(
  file: File,
  maxSize: number = 10 * 1024 * 1024
): { valid: boolean; error?: string } {
  // Check file type
  const validTypes = ['image/jpeg', 'image/jpg', 'image/png', 'image/webp'];
  if (!validTypes.includes(file.type)) {
    return {
      valid: false,
      error: 'Format de fichier non supporté. Utilisez JPEG, PNG ou WebP.'
    };
  }
  
  // Check file size
  if (file.size > maxSize) {
    return {
      valid: false,
      error: `La taille du fichier dépasse ${formatFileSize(maxSize)}.`
    };
  }
  
  return { valid: true };
}
