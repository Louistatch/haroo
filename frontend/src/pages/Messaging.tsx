import React, { useState, useEffect, useRef } from "react";
import { getConversations, getMessages, sendMessage, reportMessage, Conversation, Message } from "../api/messaging";
import { useLocation } from "react-router-dom";

const BLUE = "#2563eb";
const MAX_FILE_SIZE = 5 * 1024 * 1024;

function formatFileSize(bytes: number): string {
  if (bytes < 1024) return bytes + " o";
  if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + " Ko";
  return (bytes / (1024 * 1024)).toFixed(1) + " Mo";
}

export default function Messaging() {
  const [conversations, setConversations] = useState<Conversation[]>([]);
  const [selectedConv, setSelectedConv] = useState<Conversation | null>(null);
  const [messages, setMessages] = useState<Message[]>([]);
  const [newMessage, setNewMessage] = useState("");
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [loading, setLoading] = useState(true);
  const [sending, setSending] = useState(false);
  const [reportingId, setReportingId] = useState<number | null>(null);
  const [reportMotif, setReportMotif] = useState("");
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);
  const location = useLocation();

  const currentUserId = (() => {
    try {
      const token = localStorage.getItem("access_token");
      if (!token) return null;
      return JSON.parse(atob(token.split(".")[1])).user_id;
    } catch { return null; }
  })();

  function getInterlocuteurName(conv: Conversation): string {
    return conv.interlocuteur?.full_name || conv.interlocuteur?.username || "Utilisateur";
  }
  function getInterlocuteurInitial(conv: Conversation): string {
    return (getInterlocuteurName(conv)[0] || "U").toUpperCase();
  }

  const fetchConversations = async () => {
    try {
      const data = await getConversations();
      setConversations(data);
      if (data.length > 0 && !selectedConv) {
        const state = location.state as { conversationId?: number } | null;
        if (state?.conversationId) {
          const found = data.find(c => c.id === state.conversationId);
          setSelectedConv(found || data[0]);
        } else {
          setSelectedConv(data[0]);
        }
      }
    } catch (err) { console.error(err); }
    finally { setLoading(false); }
  };

  const fetchMessages = async (convId: number) => {
    try { setMessages(await getMessages(convId)); } catch (err) { console.error(err); }
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

  useEffect(() => { messagesEndRef.current?.scrollIntoView({ behavior: "smooth" }); }, [messages]);

  const handleSend = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedConv || (!newMessage.trim() && !selectedFile) || sending) return;
    setSending(true);
    try {
      const msg = await sendMessage(selectedConv.id, newMessage, selectedFile || undefined);
      setMessages(prev => [...prev, msg]);
      setNewMessage("");
      setSelectedFile(null);
      if (fileInputRef.current) fileInputRef.current.value = "";
    } catch (err) { console.error(err); }
    finally { setSending(false); }
  };

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;
    if (file.size > MAX_FILE_SIZE) {
      alert("Le fichier ne doit pas dépasser 5 Mo.");
      e.target.value = "";
      return;
    }
    setSelectedFile(file);
  };

  const handleReport = async (msgId: number) => {
    if (!reportMotif.trim()) return;
    try {
      await reportMessage(msgId, reportMotif);
      setReportingId(null);
      setReportMotif("");
      if (selectedConv) fetchMessages(selectedConv.id);
    } catch (err) { console.error(err); }
  };

  if (loading && conversations.length === 0) {
    return (
      <div style={{ display: "flex", alignItems: "center", justifyContent: "center", height: "calc(100vh - 64px)" }}>
        <div>Chargement des messages...</div>
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
            <div key={conv.id} onClick={() => setSelectedConv(conv)}
              style={{
                padding: "1rem 1.5rem", cursor: "pointer",
                background: selectedConv?.id === conv.id ? "rgba(37,99,235,0.05)" : "transparent",
                borderLeft: `4px solid ${selectedConv?.id === conv.id ? BLUE : "transparent"}`,
                transition: "all 0.2s"
              }}>
              <div style={{ display: "flex", alignItems: "center", gap: "0.75rem" }}>
                <div style={{ width: 40, height: 40, borderRadius: "50%", background: BLUE, color: "white", display: "flex", alignItems: "center", justifyContent: "center", fontWeight: 700 }}>
                  {getInterlocuteurInitial(conv)}
                </div>
                <div style={{ flex: 1, minWidth: 0 }}>
                  <div style={{ fontWeight: 700, fontSize: "0.9rem", color: "var(--text)" }}>{getInterlocuteurName(conv)}</div>
                  <div style={{ fontSize: "0.8rem", color: "var(--text-muted)", whiteSpace: "nowrap", overflow: "hidden", textOverflow: "ellipsis" }}>
                    {conv.last_message?.contenu || "Commencer la discussion"}
                  </div>
                </div>
                {(conv.unread_count ?? 0) > 0 && (
                  <div style={{ background: BLUE, color: "white", borderRadius: "50%", width: 22, height: 22, display: "flex", alignItems: "center", justifyContent: "center", fontSize: "0.7rem", fontWeight: 700 }}>
                    {conv.unread_count}
                  </div>
                )}
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Chat Area */}
      <div style={{ flex: 1, display: "flex", flexDirection: "column" }}>
        {selectedConv ? (
          <>
            <div style={{ padding: "1rem 1.5rem", borderBottom: "1px solid var(--border)", background: "var(--surface)", display: "flex", alignItems: "center", gap: "0.75rem" }}>
              <div style={{ width: 32, height: 32, borderRadius: "50%", background: BLUE, color: "white", display: "flex", alignItems: "center", justifyContent: "center", fontWeight: 700, fontSize: "0.8rem" }}>
                {getInterlocuteurInitial(selectedConv)}
              </div>
              <div style={{ fontWeight: 700 }}>{getInterlocuteurName(selectedConv)}</div>
            </div>

            <div style={{ flex: 1, overflowY: "auto", padding: "1.5rem", display: "flex", flexDirection: "column", gap: "1rem" }}>
              {messages.map((msg, i) => {
                const isMe = msg.expediteur === currentUserId;
                return (
                  <div key={msg.id || i} style={{ display: "flex", justifyContent: isMe ? "flex-end" : "flex-start" }}>
                    <div style={{
                      maxWidth: "70%", padding: "0.75rem 1rem", borderRadius: "16px",
                      background: isMe ? BLUE : "var(--surface)", color: isMe ? "white" : "var(--text)",
                      border: isMe ? "none" : "1px solid var(--border)", boxShadow: "0 2px 4px rgba(0,0,0,0.05)",
                      fontSize: "0.95rem", lineHeight: 1.5, position: "relative"
                    }}>
                      {msg.contenu && <div>{msg.contenu}</div>}
                      {msg.fichier_url && (
                        <a href={msg.fichier_url} target="_blank" rel="noopener noreferrer"
                          style={{
                            display: "flex", alignItems: "center", gap: "0.5rem", marginTop: msg.contenu ? "0.5rem" : 0,
                            padding: "0.5rem 0.75rem", borderRadius: "8px",
                            background: isMe ? "rgba(255,255,255,0.15)" : "rgba(0,0,0,0.04)",
                            color: isMe ? "white" : BLUE, textDecoration: "none", fontSize: "0.85rem"
                          }}>
                          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2"><path d="M21.44 11.05l-9.19 9.19a6 6 0 01-8.49-8.49l9.19-9.19a4 4 0 015.66 5.66l-9.2 9.19a2 2 0 01-2.83-2.83l8.49-8.48"/></svg>
                          <span>{msg.nom_fichier || "Fichier"}</span>
                          {msg.taille_fichier ? <span style={{ opacity: 0.7 }}>({formatFileSize(msg.taille_fichier)})</span> : null}
                        </a>
                      )}
                      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginTop: "0.3rem" }}>
                        <span style={{ fontSize: "0.7rem", opacity: 0.7 }}>
                          {new Date(msg.created_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                        </span>
                        {!isMe && !msg.signale && (
                          <button onClick={(e) => { e.stopPropagation(); setReportingId(msg.id); }}
                            style={{ background: "none", border: "none", cursor: "pointer", opacity: 0.5, fontSize: "0.7rem", color: isMe ? "white" : "var(--text-muted)", padding: "0 0.25rem" }}
                            title="Signaler">⚑</button>
                        )}
                        {msg.signale && <span style={{ fontSize: "0.65rem", opacity: 0.6 }}>Signalé</span>}
                      </div>
                    </div>
                  </div>
                );
              })}
              <div ref={messagesEndRef} />
            </div>

            {/* Report modal */}
            {reportingId && (
              <div style={{ position: "fixed", inset: 0, background: "rgba(0,0,0,0.4)", display: "flex", alignItems: "center", justifyContent: "center", zIndex: 1000 }}
                onClick={() => setReportingId(null)}>
                <div onClick={e => e.stopPropagation()} style={{ background: "var(--surface)", borderRadius: "12px", padding: "1.5rem", width: "90%", maxWidth: "400px" }}>
                  <h3 style={{ margin: "0 0 1rem", fontSize: "1rem" }}>Signaler ce message</h3>
                  <textarea value={reportMotif} onChange={e => setReportMotif(e.target.value)}
                    placeholder="Décrivez le motif du signalement..."
                    style={{ width: "100%", minHeight: "80px", padding: "0.75rem", borderRadius: "8px", border: "1px solid var(--border)", background: "var(--bg)", color: "var(--text)", resize: "vertical" }} />
                  <div style={{ display: "flex", gap: "0.75rem", marginTop: "1rem", justifyContent: "flex-end" }}>
                    <button onClick={() => { setReportingId(null); setReportMotif(""); }}
                      style={{ padding: "0.5rem 1rem", borderRadius: "8px", border: "1px solid var(--border)", background: "var(--bg)", color: "var(--text)", cursor: "pointer" }}>Annuler</button>
                    <button onClick={() => handleReport(reportingId)}
                      style={{ padding: "0.5rem 1rem", borderRadius: "8px", border: "none", background: "#ef4444", color: "white", cursor: "pointer", fontWeight: 600 }}>Signaler</button>
                  </div>
                </div>
              </div>
            )}

            {/* Input area */}
            <form onSubmit={handleSend} style={{ padding: "1rem 1.5rem", background: "var(--surface)", borderTop: "1px solid var(--border)" }}>
              {selectedFile && (
                <div style={{ display: "flex", alignItems: "center", gap: "0.5rem", marginBottom: "0.5rem", padding: "0.5rem 0.75rem", background: "rgba(37,99,235,0.08)", borderRadius: "8px", fontSize: "0.85rem" }}>
                  <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke={BLUE} strokeWidth="2"><path d="M21.44 11.05l-9.19 9.19a6 6 0 01-8.49-8.49l9.19-9.19a4 4 0 015.66 5.66l-9.2 9.19a2 2 0 01-2.83-2.83l8.49-8.48"/></svg>
                  <span style={{ color: BLUE }}>{selectedFile.name}</span>
                  <span style={{ color: "var(--text-muted)" }}>({formatFileSize(selectedFile.size)})</span>
                  <button type="button" onClick={() => { setSelectedFile(null); if (fileInputRef.current) fileInputRef.current.value = ""; }}
                    style={{ marginLeft: "auto", background: "none", border: "none", cursor: "pointer", color: "#ef4444", fontWeight: 700 }}>✕</button>
                </div>
              )}
              <div style={{ display: "flex", gap: "0.5rem", alignItems: "center" }}>
                <input type="file" ref={fileInputRef} onChange={handleFileSelect} style={{ display: "none" }} />
                <button type="button" onClick={() => fileInputRef.current?.click()}
                  style={{ padding: "0.6rem", borderRadius: "10px", border: "1px solid var(--border)", background: "var(--bg)", cursor: "pointer", display: "flex", alignItems: "center" }}
                  title="Joindre un fichier (max 5 Mo)">
                  <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="var(--text-muted)" strokeWidth="2"><path d="M21.44 11.05l-9.19 9.19a6 6 0 01-8.49-8.49l9.19-9.19a4 4 0 015.66 5.66l-9.2 9.19a2 2 0 01-2.83-2.83l8.49-8.48"/></svg>
                </button>
                <input type="text" value={newMessage} onChange={e => setNewMessage(e.target.value)}
                  placeholder="Écrivez votre message..."
                  style={{ flex: 1, padding: "0.75rem 1rem", borderRadius: "12px", border: "1px solid var(--border)", background: "var(--bg)", color: "var(--text)", outline: "none" }} />
                <button type="submit" disabled={(!newMessage.trim() && !selectedFile) || sending}
                  style={{ padding: "0 1.25rem", height: "42px", borderRadius: "12px", background: BLUE, color: "white", border: "none", fontWeight: 700, cursor: "pointer", opacity: (!newMessage.trim() && !selectedFile) || sending ? 0.6 : 1 }}>
                  {sending ? "..." : "Envoyer"}
                </button>
              </div>
            </form>
          </>
        ) : (
          <div style={{ flex: 1, display: "flex", alignItems: "center", justifyContent: "center", color: "var(--text-muted)" }}>
            Sélectionnez une conversation
          </div>
        )}
      </div>
    </div>
  );
}
