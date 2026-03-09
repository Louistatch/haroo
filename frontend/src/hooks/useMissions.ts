/**
 * TASK-9.1: Hooks React Query pour les missions
 */
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { getMissions, getMission, createMission, acceptMission, completeMission, type MissionCreatePayload } from "../api/missions";
import { isLoggedIn } from "../api/auth";

export function useMissions() {
  return useQuery({
    queryKey: ["missions"],
    queryFn: getMissions,
    enabled: isLoggedIn(),
  });
}

export function useMission(id: number) {
  return useQuery({
    queryKey: ["missions", id],
    queryFn: () => getMission(id),
    enabled: isLoggedIn() && id > 0,
  });
}

export function useCreateMission() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (payload: MissionCreatePayload) => createMission(payload),
    onSuccess: () => { qc.invalidateQueries({ queryKey: ["missions"] }); },
  });
}

export function useAcceptMission() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (id: number) => acceptMission(id),
    onSuccess: () => { qc.invalidateQueries({ queryKey: ["missions"] }); },
  });
}

export function useCompleteMission() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (id: number) => completeMission(id),
    onSuccess: () => { qc.invalidateQueries({ queryKey: ["missions"] }); },
  });
}
