/**
 * TASK-9.1: Hooks React Query pour la messagerie
 */
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { getConversations, getMessages, sendMessage, getOrCreateConversation } from "../api/messaging";
import { isLoggedIn } from "../api/auth";

export function useConversations() {
  return useQuery({
    queryKey: ["conversations"],
    queryFn: getConversations,
    enabled: isLoggedIn(),
  });
}

export function useMessages(conversationId: number) {
  return useQuery({
    queryKey: ["messages", conversationId],
    queryFn: () => getMessages(conversationId),
    enabled: isLoggedIn() && conversationId > 0,
    refetchInterval: 10_000, // Refresh toutes les 10s pour les messages
  });
}

export function useSendMessage() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: ({ conversationId, contenu }: { conversationId: number; contenu: string }) =>
      sendMessage(conversationId, contenu),
    onSuccess: (_, { conversationId }) => {
      qc.invalidateQueries({ queryKey: ["messages", conversationId] });
      qc.invalidateQueries({ queryKey: ["conversations"] });
    },
  });
}

export function useGetOrCreateConversation() {
  return useMutation({
    mutationFn: ({ participantId, typeRelation, referenceId }: {
      participantId: number;
      typeRelation?: string;
      referenceId?: number;
    }) => getOrCreateConversation(participantId, typeRelation, referenceId),
  });
}
