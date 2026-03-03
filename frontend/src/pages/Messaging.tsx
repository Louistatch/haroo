import React, { useState, useEffect, useRef } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { getConversations, getMessages, sendMessage, Conversation, Message } from "../api/messaging";
import { useLocation } from "react-router-dom";

const BLUE = "#2563eb";

export default function Messaging() {
  const [conversations, setConversations] = useState<Conversation[]>([]);
  const [selectedConv, setSelectedConv] = useState<Conversation | null>(null);
  const [messages, setMessages] = useState<Message[]>([]);
  const [newMessage, setNewMessage] = useState("");
  const [loading, setLoading] = useState(true);
  const [sending, setSending] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const location = useLocation();

  const currentUserId = (() => {
    try {
      const token = localStorage.getItem("access_token");
      if (!token) return null;
      return JSON.parse(atob(token.split(".")[1])).user_id;
    } catch { return null; }
  })();

  const fetchConversations = async () => {
    try {
      const data = await getConversations();
      setConversations(data);
      if (data.length > 0 && !selectedConv) {
        // Check if we came from a specific context
        const state = location.state as { conversationId?: number } | null;
        if (state?.conversationId) {
          const found = data.find(c => c.id === state.conversationId);
          if (found) setSelectedConv(found);
          else setSelectedConv(data[0]);
        } else {
          setSelectedConv(data[0]);
        }
      }
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const fetchMessages = async (convId: number) => {
    try {
      const data = await getMessages(convId);
      setMessages(data);
    } catch (err) {
      console.error(err);
    }
  };

  useEffect(() => {
    fetchConversations();
    const interval = setInterval(fetchConversations, 5000);
    return () => clearInterval(interval);
  }, []);

  useEffect(() => {
    if (selectedConv) {
      fetchMessages(selectedConv.id);
      const interval = setInterval(() => fetchMessages(selectedConv.id), 5000);
      return () => clearInterval(interval);
    }
  }, [selectedConv]);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const handleSend = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedConv || !newMessage.trim() || sending) return;

    setSending(true);
    try {
      const msg = await sendMessage(selectedConv.id, newMessage);
      setMessages([...messages, msg]);
      setNewMessage("");
    } catch (err) {
      console.error(err);
    } finally {
      setSending(false);
    }
  };

  if (loading && conversations.length === 0) {
    return (
      <div style={{ display: "flex", alignItems: "center", justifyContent: "center", height: "calc(100vh - 64px)" }}>
        <div className="loader">Chargement des messages...</div>
      </div>
    );
  }

  if (conversations.length === 0) {
    return (
      <div style={{ padding: "4rem 2rem", textAlign: "center", color: "var(--text-muted)" }}>
        <svg width="64" height="64" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" style={{ marginBottom: "1rem", opacity: 0.5 }}>
          <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z" />
        </svg>
        <h3>Aucune conversation</h3>
        <p>Vos messages s'afficheront ici.</p>
      </div>
    );
  }

  return (
    <div style={{ display: "flex", height: "calc(100vh - 64px)", background: "var(--bg)" }}>
      {/* Sidebar */}
      <div style={{ width: "320px", borderRight: "1px solid var(--border)", background: "var(--surface)", display: "flex", flexDirection: "column" }}>
        <div style={{ padding: "1.5rem", borderBottom: "1px solid var(--border)" }}>
          <h2 style={{ fontSize: "1.25rem", fontWeight: 800, margin: 0 }}>Messages</h2>
        </div>
        <div style={{ flex: 1, overflowY: "auto" }}>
          {conversations.map(conv => (
            <div
              key={conv.id}
              onClick={() => setSelectedConv(conv)}
              style={{
                padding: "1rem 1.5rem",
                cursor: "pointer",
                background: selectedConv?.id === conv.id ? "rgba(37, 99, 235, 0.05)" : "transparent",
                borderLeft: `4px solid ${selectedConv?.id === conv.id ? BLUE : "transparent"}`,
                transition: "all 0.2s"
              }}
            >
              <div style={{ display: "flex", alignItems: "center", gap: "0.75rem" }}>
                <div style={{ width: "40px", height: "40px", borderRadius: "50%", background: BLUE, color: "white", display: "flex", alignItems: "center", justifyContent: "center", fontWeight: 700 }}>
                  {conv.interlocuteur_nom?.[0]?.toUpperCase() || "U"}
                </div>
                <div style={{ flex: 1, minWidth: 0 }}>
                  <div style={{ fontWeight: 700, fontSize: "0.9rem", color: "var(--text)", marginBottom: "0.2rem" }}>
                    {conv.interlocuteur_nom}
                  </div>
                  <div style={{ fontSize: "0.8rem", color: "var(--text-muted)", whiteSpace: "nowrap", overflow: "hidden", textOverflow: "ellipsis" }}>
                    {conv.last_message?.contenu || "Commencer la discussion"}
                  </div>
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Chat Area */}
      <div style={{ flex: 1, display: "flex", flexDirection: "column", background: "var(--bg)" }}>
        {selectedConv ? (
          <>
            <div style={{ padding: "1rem 1.5rem", borderBottom: "1px solid var(--border)", background: "var(--surface)", display: "flex", alignItems: "center", gap: "0.75rem" }}>
              <div style={{ width: "32px", height: "32px", borderRadius: "50%", background: BLUE, color: "white", display: "flex", alignItems: "center", justifyContent: "center", fontWeight: 700, fontSize: "0.8rem" }}>
                {selectedConv.interlocuteur_nom?.[0]?.toUpperCase() || "U"}
              </div>
              <div style={{ fontWeight: 700 }}>{selectedConv.interlocuteur_nom}</div>
            </div>

            <div style={{ flex: 1, overflowY: "auto", padding: "1.5rem", display: "flex", flexDirection: "column", gap: "1rem" }}>
              {messages.map((msg, i) => {
                const isMe = msg.expediteur === currentUserId;
                return (
                  <div key={msg.id || i} style={{ display: "flex", justifyContent: isMe ? "flex-end" : "flex-start" }}>
                    <div style={{
                      maxWidth: "70%",
                      padding: "0.75rem 1rem",
                      borderRadius: "16px",
                      background: isMe ? BLUE : "var(--surface)",
                      color: isMe ? "white" : "var(--text)",
                      border: isMe ? "none" : "1px solid var(--border)",
                      boxShadow: "0 2px 4px rgba(0,0,0,0.05)",
                      fontSize: "0.95rem",
                      lineHeight: 1.5
                    }}>
                      {msg.contenu}
                      <div style={{ fontSize: "0.7rem", marginTop: "0.3rem", opacity: 0.7, textAlign: "right" }}>
                        {new Date(msg.created_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                      </div>
                    </div>
                  </div>
                );
              })}
              <div ref={messagesEndRef} />
            </div>

            <form onSubmit={handleSend} style={{ padding: "1.25rem", background: "var(--surface)", borderTop: "1px solid var(--border)" }}>
              <div style={{ display: "flex", gap: "0.75rem" }}>
                <input
                  type="text"
                  value={newMessage}
                  onChange={(e) => setNewMessage(e.target.value)}
                  placeholder="Écrivez votre message..."
                  style={{
                    flex: 1,
                    padding: "0.75rem 1rem",
                    borderRadius: "12px",
                    border: "1px solid var(--border)",
                    background: "var(--bg)",
                    color: "var(--text)",
                    outline: "none"
                  }}
                />
                <button
                  type="submit"
                  disabled={!newMessage.trim() || sending}
                  style={{
                    padding: "0 1.25rem",
                    borderRadius: "12px",
                    background: BLUE,
                    color: "white",
                    border: "none",
                    fontWeight: 700,
                    cursor: "pointer",
                    opacity: (!newMessage.trim() || sending) ? 0.6 : 1
                  }}
                >
                  {sending ? "..." : "Envoyer"}
                </button>
              </div>
            </form>
          </>
        ) : (
          <div style={{ flex: 1, display: "flex", alignItems: "center", justifyContent: "center", color: "var(--text-muted)" }}>
            Sélectionnez une conversation pour commencer
          </div>
        )}
      </div>
    </div>
  );
}
