/**
 * TASK-9.1: Hooks React Query pour les notifications
 */
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { getNotifications, getUnreadCount, markRead, markAllRead } from "../api/notifications";
import { isLoggedIn } from "../api/auth";

export function useNotifications() {
  return useQuery({
    queryKey: ["notifications"],
    queryFn: getNotifications,
    enabled: isLoggedIn(),
  });
}

export function useUnreadCount() {
  return useQuery({
    queryKey: ["notifications", "unread"],
    queryFn: getUnreadCount,
    enabled: isLoggedIn(),
    refetchInterval: 30_000, // Refresh toutes les 30s
  });
}

export function useMarkRead() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (id: number) => markRead(id),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["notifications"] });
    },
  });
}

export function useMarkAllRead() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: markAllRead,
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: ["notifications"] });
    },
  });
}
