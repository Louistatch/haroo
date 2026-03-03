import React, { useState, useEffect } from "react";
import { motion } from "framer-motion";
import { getNotifications, markRead, markAllRead, Notification } from "../api/notifications";

const GREEN = "#16a34a";

export default function Notifications() {
  const [notifications, setNotifications] = useState<Notification[]>([]);
  const [loading, setLoading] = useState(true);

  const fetchNotifications = async () => {
    try {
      const data = await getNotifications();
      setNotifications(data);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchNotifications();
  }, []);

  const handleMarkRead = async (id: number) => {
    try {
      await markRead(id);
      setNotifications(notifications.map(n => n.id === id ? { ...n, lue: true } : n));
    } catch (err) {
      console.error(err);
    }
  };

  const handleMarkAllRead = async () => {
    try {
      await markAllRead();
      setNotifications(notifications.map(n => ({ ...n, lue: true })));
    } catch (err) {
      console.error(err);
    }
  };

  const getIcon = (type: string) => {
    switch (type) {
      case "NOUVEAU_MESSAGE":
        return <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z" /></svg>;
      case "PAIEMENT_RECU":
        return <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><rect x="2" y="5" width="20" height="14" rx="2" /><line x1="2" y1="10" x2="22" y2="10" /></svg>;
      case "ALERTE_SYSTEME":
        return <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><circle cx="12" cy="12" r="10" /><line x1="12" y1="8" x2="12" y2="12" /><line x1="12" y1="16" x2="12.01" y2="16" /></svg>;
      default:
        return <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M18 8A6 6 0 0 0 6 8c0 7-3 9-3 9h18s-3-2-3-9" /><path d="M13.73 21a2 2 0 0 1-3.46 0" /></svg>;
    }
  };

  const formatDate = (dateStr: string) => {
    const date = new Date(dateStr);
    const now = new Date();
    const diff = now.getTime() - date.getTime();
    const days = Math.floor(diff / (1000 * 60 * 60 * 24));
    
    if (days === 0) {
      const hours = Math.floor(diff / (1000 * 60 * 60));
      if (hours === 0) {
        const mins = Math.floor(diff / (1000 * 60));
        return `Il y a ${mins} min`;
      }
      return `Il y a ${hours}h`;
    }
    if (days < 7) return `Il y a ${days}j`;
    return date.toLocaleDateString("fr-FR");
  };

  if (loading) {
    return (
      <div style={{ maxWidth: "800px", margin: "0 auto", padding: "4rem 2rem", textAlign: "center" }}>
        Chargement...
      </div>
    );
  }

  const unreadCount = notifications.filter(n => !n.lue).length;

  return (
    <div style={{ maxWidth: "800px", margin: "0 auto", padding: "2rem 1.5rem" }}>
      <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", marginBottom: "2rem" }}>
        <h1 style={{ fontSize: "1.75rem", fontWeight: 800, margin: 0 }}>Notifications</h1>
        {unreadCount > 0 && (
          <button
            onClick={handleMarkAllRead}
            style={{
              background: "none",
              border: "none",
              color: GREEN,
              fontWeight: 600,
              fontSize: "0.9rem",
              cursor: "pointer",
              padding: "0.5rem 1rem",
              borderRadius: "8px",
              transition: "background 0.2s"
            }}
            onMouseEnter={e => e.currentTarget.style.background = `${GREEN}10`}
            onMouseLeave={e => e.currentTarget.style.background = "none"}
          >
            Tout marquer comme lu
          </button>
        )}
      </div>

      {notifications.length === 0 ? (
        <div style={{ textAlign: "center", padding: "4rem 2rem", background: "var(--surface)", borderRadius: "16px", border: "1px solid var(--border)" }}>
          <div style={{ width: "64px", height: "64px", borderRadius: "50%", background: "var(--bg)", display: "flex", alignItems: "center", justifyContent: "center", margin: "0 auto 1.5rem", color: "var(--text-muted)" }}>
            <svg width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5"><path d="M18 8A6 6 0 0 0 6 8c0 7-3 9-3 9h18s-3-2-3-9" /><path d="M13.73 21a2 2 0 0 1-3.46 0" /></svg>
          </div>
          <h3 style={{ margin: "0 0 0.5rem 0" }}>Aucune notification</h3>
          <p style={{ color: "var(--text-muted)", margin: 0 }}>Nous vous préviendrons dès qu'il y aura du nouveau.</p>
        </div>
      ) : (
        <div style={{ display: "flex", flexDirection: "column", gap: "0.75rem" }}>
          {notifications.map(notification => (
            <motion.div
              key={notification.id}
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              onClick={() => !notification.lue && handleMarkRead(notification.id)}
              style={{
                display: "flex",
                gap: "1rem",
                padding: "1.25rem",
                background: notification.lue ? "var(--surface)" : `${GREEN}05`,
                border: `1px solid ${notification.lue ? "var(--border)" : `${GREEN}20`}`,
                borderRadius: "16px",
                cursor: notification.lue ? "default" : "pointer",
                position: "relative"
              }}
            >
              <div style={{
                width: "40px",
                height: "40px",
                borderRadius: "10px",
                background: notification.lue ? "var(--bg)" : `${GREEN}15`,
                color: notification.lue ? "var(--text-muted)" : GREEN,
                display: "flex",
                alignItems: "center",
                justifyContent: "center",
                flexShrink: 0
              }}>
                {getIcon(notification.type_notification)}
              </div>
              <div style={{ flex: 1 }}>
                <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", marginBottom: "0.25rem" }}>
                  <h4 style={{ margin: 0, fontSize: "1rem", fontWeight: 700, color: "var(--text)" }}>{notification.titre}</h4>
                  <span style={{ fontSize: "0.75rem", color: "var(--text-muted)" }}>{formatDate(notification.created_at)}</span>
                </div>
                <p style={{ margin: 0, fontSize: "0.9rem", color: "var(--text-secondary)", lineHeight: 1.5 }}>{notification.message}</p>
                {notification.lien && (
                  <a href={notification.lien} style={{ display: "inline-block", marginTop: "0.75rem", fontSize: "0.85rem", color: GREEN, fontWeight: 600, textDecoration: "none" }}>
                    Voir les détails →
                  </a>
                )}
              </div>
              {!notification.lue && (
                <div style={{ position: "absolute", top: "1.25rem", right: "1.25rem", width: "8px", height: "8px", borderRadius: "50%", background: GREEN }} />
              )}
            </motion.div>
          ))}
        </div>
      )}
    </div>
  );
}
