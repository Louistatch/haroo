import api from "./auth";

export interface Notification {
  id: number;
  type_notification: string;
  titre: string;
  message: string;
  lien: string | null;
  lue: boolean;
  created_at: string;
}

export async function getNotifications(): Promise<Notification[]> {
  const res = await api.get("/notifications/");
  return res.data;
}

export async function getUnreadCount(): Promise<{ unread_count: number }> {
  const res = await api.get("/notifications/count/");
  return res.data;
}

export async function markRead(id: number): Promise<void> {
  await api.post(`/notifications/${id}/mark-read/`);
}

export async function markAllRead(): Promise<void> {
  await api.post("/notifications/mark-all-read/");
}
