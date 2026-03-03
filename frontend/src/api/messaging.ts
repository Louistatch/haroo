import api from "./auth";

export interface Conversation {
  id: number;
  participant_1: number;
  participant_2: number;
  type_relation: "MISSION" | "CONTRAT_SAISONNIER" | "GENERAL";
  reference_id: number | null;
  derniere_activite: string;
  interlocuteur_nom?: string;
  last_message?: Message;
}

export interface Message {
  id: number;
  conversation: number;
  expediteur: number;
  expediteur_nom?: string;
  contenu: string;
  lu: boolean;
  created_at: string;
}

export async function getConversations(): Promise<Conversation[]> {
  const res = await api.get("/conversations/");
  return res.data;
}

export async function getOrCreateConversation(participantId: number, typeRelation: string = "GENERAL", referenceId?: number): Promise<Conversation> {
  const res = await api.post("/conversations/", {
    participant_id: participantId,
    type_relation: typeRelation,
    reference_id: referenceId
  });
  return res.data;
}

export async function getMessages(conversationId: number): Promise<Message[]> {
  const res = await api.get(`/conversations/${conversationId}/messages/`);
  return res.data;
}

export async function sendMessage(conversationId: number, contenu: string): Promise<Message> {
  const res = await api.post(`/conversations/${conversationId}/messages/`, { contenu });
  return res.data;
}

export async function markRead(messageId: number): Promise<void> {
  await api.post(`/messages/${messageId}/mark_read/`);
}
