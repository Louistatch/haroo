import { useState } from "react";
import { motion } from "framer-motion";

interface FadeImageProps {
  src: string;
  alt: string;
  fallback?: string;
  style?: React.CSSProperties;
  className?: string;
}

/**
 * Image component with lazy loading, fade-in animation, and fallback support.
 */
export default function FadeImage({ src, alt, fallback, style, className }: FadeImageProps) {
  const [loaded, setLoaded] = useState(false);
  const [error, setError] = useState(false);

  const finalSrc = error && fallback ? fallback : src;

  return (
    <motion.img
      src={finalSrc}
      alt={alt}
      loading="lazy"
      className={className}
      initial={{ opacity: 0 }}
      animate={{ opacity: loaded ? 1 : 0 }}
      transition={{ duration: 0.5, ease: "easeOut" }}
      onLoad={() => setLoaded(true)}
      onError={() => {
        if (!error) setError(true);
        else setLoaded(true); // show fallback even if it fails
      }}
      style={{
        ...style,
        background: loaded ? "transparent" : "var(--bg-secondary, #f0f0f0)",
      }}
    />
  );
}
