/**
 * TASK-9.1: Hooks React Query pour les offres d'emploi
 */
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { getOffres, getOffre, createOffre, postuler, getContrats } from "../api/jobs";
import { isLoggedIn } from "../api/auth";

export function useOffres(params?: Record<string, any>) {
  return useQuery({
    queryKey: ["offres", params],
    queryFn: () => getOffres(params),
    enabled: isLoggedIn(),
  });
}

export function useOffre(id: number) {
  return useQuery({
    queryKey: ["offres", id],
    queryFn: () => getOffre(id),
    enabled: isLoggedIn() && id > 0,
  });
}

export function useCreateOffre() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (data: any) => createOffre(data),
    onSuccess: () => { qc.invalidateQueries({ queryKey: ["offres"] }); },
  });
}

export function usePostuler() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (offreId: number) => postuler(offreId),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["offres"] });
      qc.invalidateQueries({ queryKey: ["contrats"] });
    },
  });
}

export function useContrats() {
  return useQuery({
    queryKey: ["contrats"],
    queryFn: getContrats,
    enabled: isLoggedIn(),
  });
}
