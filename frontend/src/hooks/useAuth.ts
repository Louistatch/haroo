/**
 * TASK-9.1: Hooks React Query pour l'authentification
 *
 * Remplace les appels manuels useEffect + useState par des hooks
 * avec cache automatique, synchronisation et gestion d'erreurs.
 */
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { me, updateProfile, changePassword, loginEmail, registerEmail, logout, isLoggedIn } from "../api/auth";

/** Récupère l'utilisateur connecté (avec cache) */
export function useUser() {
  return useQuery({
    queryKey: ["user"],
    queryFn: me,
    retry: false,
    enabled: isLoggedIn(),
  });
}

/** Mutation de connexion email */
export function useLogin() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: ({ email, password }: { email: string; password: string }) =>
      loginEmail(email, password),
    onSuccess: (data) => {
      if (data?.user) queryClient.setQueryData(["user"], data.user);
    },
  });
}

/** Mutation d'inscription email */
export function useRegister() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (params: {
      first_name?: string;
      last_name?: string;
      email: string;
      password: string;
      password_confirm: string;
      user_type: string;
    }) => registerEmail(params),
    onSuccess: (data) => {
      if (data?.user) queryClient.setQueryData(["user"], data.user);
    },
  });
}

/** Mutation de déconnexion */
export function useLogout() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: async () => { logout(); },
    onSuccess: () => { queryClient.clear(); },
  });
}

/** Mutation de mise à jour du profil */
export function useUpdateProfile() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (data: Record<string, any>) => updateProfile(data),
    onSuccess: (data) => {
      const user = data?.user || data;
      queryClient.setQueryData(["user"], (old: any) => ({ ...old, ...user }));
    },
  });
}

/** Mutation de changement de mot de passe */
export function useChangePassword() {
  return useMutation({
    mutationFn: ({ old_password, new_password, new_password_confirm }: {
      old_password: string;
      new_password: string;
      new_password_confirm: string;
    }) => changePassword(old_password, new_password, new_password_confirm),
  });
}
