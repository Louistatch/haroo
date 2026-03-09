/**
 * No longer needed with Supabase Auth.
 * Supabase redirects directly to /oauth-callback with hash params.
 * Kept as empty component to avoid breaking App.tsx import.
 */
export default function OAuthCallback() {
  return null;
}
