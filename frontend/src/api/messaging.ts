import api from "./auth";

export interface UserShort {
  id: number;
  username: string;
  full_name: string;
  email: string;
}

export interface Conversation {
  id: number;
  participant_1: UserShort;
  participant_2: UserShort;
  type_relation: "MISSION" | "CONTRAT_SAISONNIER" | "GENERAL";
  reference_id: number | null;
  derniere_activite: string;
  interlocuteur?: UserShort;
  unread_count?: number;
  last_message?: Message;
}

export interface Message {
  id: number;
  conversation: number;
  expediteur: number;
  expediteur_nom?: string;
  contenu: string;
  fichier_url?: string | null;
  nom_fichier?: string;
  taille_fichier?: number;
  lu: boolean;
  signale: boolean;
  created_at: string;
}

export async function getConversations(): Promise<Conversation[]> {
  const res = await api.get("/conversations/");
  return Array.isArray(res.data) ? res.data : (res.data.results || []);
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
  const res = await api.get(`/messages/`, { params: { conversation: conversationId } });
  return Array.isArray(res.data) ? res.data : (res.data.results || []);
}

export async function sendMessage(conversationId: number, contenu: string, fichier?: File): Promise<Message> {
  if (fichier) {
    const formData = new FormData();
    formData.append('conversation', String(conversationId));
    if (contenu) formData.append('contenu', contenu);
    formData.append('fichier', fichier);
    const res = await api.post(`/messages/`, formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    });
    return res.data;
  }
  const res = await api.post(`/messages/`, { conversation: conversationId, contenu });
  return res.data;
}

export async function markRead(messageId: number): Promise<void> {
  await api.post(`/messages/${messageId}/mark-read/`);
}

export async function reportMessage(messageId: number, motif: string): Promise<void> {
  await api.post(`/messages/${messageId}/report/`, { motif });
}
