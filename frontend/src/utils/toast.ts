/**
 * Toast Notification Utilities
 * 
 * This file provides utility functions for displaying toast notifications.
 * Use the useToast hook in components for full control, or import these
 * utilities for quick one-off notifications.
 */

import { ToastType } from '../components/Toast';

export interface ToastOptions {
  title: string;
  message?: string;
  duration?: number;
  type: ToastType;
}

/**
 * Display a success toast notification
 * @param title - Main message
 * @param message - Optional detailed message
 * @param duration - Duration in milliseconds (default: 5000)
 */
export function showSuccess(title: string, message?: string, duration?: number) {
  // This is a placeholder - actual implementation should use a global toast context
  console.log('[Toast Success]', title, message);
}

/**
 * Display an error toast notification
 * @param title - Main message
 * @param message - Optional detailed message
 * @param duration - Duration in milliseconds (default: 5000)
 */
export function showError(title: string, message?: string, duration?: number) {
  console.log('[Toast Error]', title, message);
}

/**
 * Display a warning toast notification
 * @param title - Main message
 * @param message - Optional detailed message
 * @param duration - Duration in milliseconds (default: 5000)
 */
export function showWarning(title: string, message?: string, duration?: number) {
  console.log('[Toast Warning]', title, message);
}

/**
 * Display an info toast notification
 * @param title - Main message
 * @param message - Optional detailed message
 * @param duration - Duration in milliseconds (default: 5000)
 */
export function showInfo(title: string, message?: string, duration?: number) {
  console.log('[Toast Info]', title, message);
}

/**
 * Toast notification presets for common scenarios
 */
export const ToastPresets = {
  // Authentication
  loginSuccess: () => showSuccess('Connexion réussie', 'Bienvenue sur la plateforme'),
  loginError: () => showError('Échec de connexion', 'Identifiants incorrects'),
  logoutSuccess: () => showSuccess('Déconnexion', 'À bientôt !'),
  sessionExpired: () => showWarning('Session expirée', 'Veuillez vous reconnecter'),
  
  // Purchase
  purchaseSuccess: () => showSuccess('Achat réussi', 'Votre document est disponible'),
  purchaseError: () => showError('Échec de l\'achat', 'Veuillez réessayer'),
  alreadyPurchased: () => showInfo('Déjà acheté', 'Vous possédez déjà ce document'),
  
  // Download
  downloadStarted: () => showInfo('Téléchargement', 'Le document va s\'ouvrir'),
  downloadError: () => showError('Erreur', 'Impossible de télécharger le document'),
  linkExpired: () => showWarning('Lien expiré', 'Veuillez régénérer le lien'),
  
  // Network
  networkError: () => showError('Erreur réseau', 'Vérifiez votre connexion'),
  serverError: () => showError('Erreur serveur', 'Veuillez réessayer plus tard'),
  
  // Form
  formSuccess: () => showSuccess('Enregistré', 'Vos modifications ont été sauvegardées'),
  formError: () => showError('Erreur', 'Veuillez vérifier les champs'),
  
  // Generic
  success: (message: string) => showSuccess('Succès', message),
  error: (message: string) => showError('Erreur', message),
  warning: (message: string) => showWarning('Attention', message),
  info: (message: string) => showInfo('Information', message),
};

/**
 * Example usage in components:
 * 
 * // Using the hook (recommended for components)
 * import { useToast } from '../hooks/useToast';
 * 
 * function MyComponent() {
 *   const { success, error, info, warning } = useToast();
 *   
 *   const handleAction = () => {
 *     success('Action réussie', 'Détails supplémentaires');
 *   };
 *   
 *   return <button onClick={handleAction}>Action</button>;
 * }
 * 
 * // Using presets
 * import { ToastPresets } from '../utils/toast';
 * 
 * ToastPresets.loginSuccess();
 * ToastPresets.purchaseError();
 */
