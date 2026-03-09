import React, { useState, useRef, useEffect, useCallback } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import api from '../api/auth';

const IconBot = () => (
  <svg width="26" height="26" viewBox="0 0 28 28" fill="none">
    <path d="M14 2a2 2 0 012 2v1h-4V4a2 2 0 012-2z" fill="currentColor" opacity="0.6"/>
    <rect x="4" y="6" width="20" height="16" rx="4" fill="currentColor" opacity="0.15"/>
    <rect x="4" y="6" width="20" height="16" rx="4" stroke="currentColor" strokeWidth="1.8"/>
    <circle cx="10" cy="13" r="2" fill="currentColor"/><circle cx="18" cy="13" r="2" fill="currentColor"/>
    <path d="M11 18s1.5 1.5 3 1.5 3-1.5 3-1.5" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round"/>
    <path d="M2 12h2M24 12h2" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round"/>
  </svg>
);
const IconSend = () => (<svg width="18" height="18" viewBox="0 0 20 20" fill="none"><path d="M3.5 10L17 3 13 17l-3.5-5L3.5 10z" fill="currentColor"/></svg>);
const IconClose = () => (<svg width="16" height="16" viewBox="0 0 18 18" fill="none"><path d="M4.5 4.5l9 9M13.5 4.5l-9 9" stroke="currentColor" strokeWidth="2" strokeLinecap="round"/></svg>);
const IconRefresh = () => (<svg width="14" height="14" viewBox="0 0 16 16" fill="none"><path d="M2 8a6 6 0 0110.5-4M14 8a6 6 0 01-10.5 4" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round"/><path d="M12.5 4V1.5H15M3.5 12v2.5H1" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round"/></svg>);
const IconChevron = () => (<svg width="12" height="12" viewBox="0 0 12 12" fill="none"><path d="M4.5 2.5l4 3.5-4 3.5" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round"/></svg>);

interface Message { role: 'user' | 'assistant'; content: string; timestamp: Date; }
interface AIChatProps { context?: { page?: string; cours_titre?: string }; }

const ALL_QUICK_QUESTIONS = [
  { id: 'q1', text: 'Comment utiliser la plateforme?' },
  { id: 'q2', text: "C'est quoi les preventes?" },
  { id: 'q3', text: 'Comment trouver un agronome?' },
  { id: 'q4', text: "Comment publier une offre d'emploi?" },
  { id: 'q5', text: 'Comment suivre un cours en ligne?' },
  { id: 'q6', text: 'Comment voir les prix du marche?' },
  { id: 'q7', text: 'Comment envoyer un message?' },
  { id: 'q8', text: "Comment acceder aux documents?" },
];

function renderMarkdown(text: string): React.ReactNode {
  const lines = text.split('\n');
  const elements: React.ReactNode[] = [];
  lines.forEach((line, i) => {
    let processed: React.ReactNode = line;
    if (line.includes('**')) {
      const parts = line.split(/\*\*(.*?)\*\*/g);
      processed = parts.map((part, j) =>
        j % 2 === 1 ? <strong key={j} style={{ fontWeight: 600 }}>{part}</strong> : part
      );
    }
    if (line.match(/^\s*[\*\-]\s+/)) {
      const content = line.replace(/^\s*[\*\-]\s+/, '');
      let inner: React.ReactNode = content;
      if (content.includes('**')) {
        const p = content.split(/\*\*(.*?)\*\*/g);
        inner = p.map((pt, j) =>
          j % 2 === 1 ? <strong key={j} style={{ fontWeight: 600 }}>{pt}</strong> : pt
        );
      }
      elements.push(
        <div key={i} style={{ display: 'flex', gap: 8, paddingLeft: 4, marginTop: 3 }}>
          <span style={{ color: '#0891b2', flexShrink: 0 }}>&bull;</span>
          <span>{inner}</span>
        </div>
      );
      return;
    }
    if (line.match(/^\s*\d+\.\s+/)) {
      const num = line.match(/^\s*(\d+)\./)?.[1];
      const content = line.replace(/^\s*\d+\.\s+/, '');
      let inner: React.ReactNode = content;
      if (content.includes('**')) {
        const p = content.split(/\*\*(.*?)\*\*/g);
        inner = p.map((pt, j) =>
          j % 2 === 1 ? <strong key={j} style={{ fontWeight: 600 }}>{pt}</strong> : pt
        );
      }
      elements.push(
        <div key={i} style={{ display: 'flex', gap: 8, paddingLeft: 4, marginTop: 4 }}>
          <span style={{
            background: 'linear-gradient(135deg, #0e7490, #0891b2)', color: 'white',
            width: 20, height: 20, borderRadius: '50%',
            display: 'flex', alignItems: 'center', justifyContent: 'center',
            fontSize: '0.7rem', fontWeight: 700, flexShrink: 0,
          }}>{num}</span>
          <span>{inner}</span>
        </div>
      );
      return;
    }
    if (line.trim() === '') {
      elements.push(<div key={i} style={{ height: 6 }} />);
      return;
    }
    elements.push(<div key={i}>{processed}</div>);
  });
  return <>{elements}</>;
}

const styleId = 'haroo-ai-css';
if (typeof document !== 'undefined' && !document.getElementById(styleId)) {
  const s = document.createElement('style');
  s.id = styleId;
  s.textContent = `
    @keyframes haroo-float{0%,100%{transform:translateY(0)}50%{transform:translateY(-6px)}}
    @keyframes haroo-glow{0%,100%{box-shadow:0 4px 20px rgba(8,145,178,0.35)}50%{box-shadow:0 4px 30px rgba(8,145,178,0.55)}}
    .haroo-fab{animation:haroo-float 3s ease-in-out infinite,haroo-glow 2.5s ease-in-out infinite}
    .haroo-fab:hover{animation:none}
    .haroo-sug{transition:all .2s ease}
    .haroo-sug:hover{border-color:#0891b2!important;background:rgba(8,145,178,0.05)!important;transform:translateX(3px)}
    .haroo-iw:focus-within{border-color:#0891b2!important;box-shadow:0 0 0 3px rgba(8,145,178,0.1)!important}
  `;
  document.head.appendChild(s);
}

export default function AIChat({ context }: AIChatProps) {
  const [isOpen, setIsOpen] = useState(false);
  const [messages, setMessages] = useState<Message[]>([{
    role: 'assistant',
    content: "Bonjour, je suis l'assistant Haroo. N'hesitez pas a me poser vos questions sur la plateforme, je suis la pour vous aider.",
    timestamp: new Date(),
  }]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [askedQuestions, setAskedQuestions] = useState<Set<string>>(new Set());
  const [showTooltip, setShowTooltip] = useState(true);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  const scrollToBottom = useCallback(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, []);

  useEffect(() => { scrollToBottom(); }, [messages, scrollToBottom]);
  useEffect(() => { if (isOpen && inputRef.current) inputRef.current.focus(); }, [isOpen]);
  useEffect(() => { const t = setTimeout(() => setShowTooltip(false), 12000); return () => clearTimeout(t); }, []);

  const remainingQuestions = ALL_QUICK_QUESTIONS.filter(q => !askedQuestions.has(q.id));

  const sendMessage = async (text?: string) => {
    const msg = text || input.trim();
    if (!msg || isLoading) return;
    const mq = ALL_QUICK_QUESTIONS.find(q => q.text === msg);
    if (mq) setAskedQuestions(prev => new Set(prev).add(mq.id));
    setMessages(prev => [...prev, { role: 'user', content: msg, timestamp: new Date() }]);
    setInput('');
    setIsLoading(true);
    try {
      const r = await api.post('/ai/chat/', { message: msg, context });
      setMessages(prev => [...prev, { role: 'assistant', content: r.data.response, timestamp: new Date() }]);
    } catch {
      setMessages(prev => [...prev, {
        role: 'assistant',
        content: "Desole, un souci technique m'empeche de repondre pour le moment. Essayez de nouveau dans quelques instants.",
        timestamp: new Date(),
      }]);
    } finally {
      setIsLoading(false);
    }
  };

  const resetChat = async () => {
    try { await api.post('/ai/chat/reset/'); } catch {}
    setMessages([{
      role: 'assistant',
      content: "C'est reparti. Qu'est-ce que je peux faire pour vous?",
      timestamp: new Date(),
    }]);
    setAskedQuestions(new Set());
  };

  return (
    <>
      {/* FLOATING BUTTON */}
      <AnimatePresence>
        {!isOpen && (
          <motion.div
            initial={{ scale: 0, opacity: 0 }}
            animate={{ scale: 1, opacity: 1 }}
            exit={{ scale: 0, opacity: 0 }}
            transition={{ type: 'spring', stiffness: 260, damping: 22 }}
            style={{ position: 'fixed', bottom: 28, right: 28, zIndex: 9998, display: 'flex', alignItems: 'center', gap: 12 }}
          >
            <AnimatePresence>
              {showTooltip && (
                <motion.div
                  initial={{ opacity: 0, x: 20 }}
                  animate={{ opacity: 1, x: 0 }}
                  exit={{ opacity: 0, x: 20 }}
                  transition={{ delay: 2, type: 'spring', stiffness: 300, damping: 25 }}
                  onClick={() => { setShowTooltip(false); setIsOpen(true); }}
                  style={{ background: 'white', borderRadius: 14, padding: '11px 16px', boxShadow: '0 6px 24px rgba(0,0,0,0.1), 0 0 0 1px rgba(0,0,0,0.04)', cursor: 'pointer', maxWidth: 200, position: 'relative' }}
                >
                  <div style={{ fontSize: '0.84rem', fontWeight: 600, color: '#0e7490', marginBottom: 2 }}>Besoin d'aide?</div>
                  <div style={{ fontSize: '0.76rem', color: '#64748b', lineHeight: 1.4 }}>Discutez avec l'assistant Haroo</div>
                  <div style={{ position: 'absolute', right: -6, top: '50%', transform: 'translateY(-50%) rotate(45deg)', width: 12, height: 12, background: 'white', boxShadow: '2px -2px 3px rgba(0,0,0,0.04)' }} />
                </motion.div>
              )}
            </AnimatePresence>
            <motion.button
              className="haroo-fab"
              whileHover={{ scale: 1.08 }}
              whileTap={{ scale: 0.9 }}
              onClick={() => { setShowTooltip(false); setIsOpen(true); }}
              style={{ position: 'relative', width: 64, height: 64, borderRadius: '50%', background: 'linear-gradient(145deg, #0e7490, #0891b2)', border: 'none', cursor: 'pointer', display: 'flex', alignItems: 'center', justifyContent: 'center', color: 'white' }}
            >
              <motion.div
                animate={{ scale: [1, 2], opacity: [0.25, 0] }}
                transition={{ duration: 2.5, repeat: Infinity, ease: 'easeOut' }}
                style={{ position: 'absolute', inset: 0, borderRadius: '50%', border: '2px solid #0891b2' }}
              />
              <IconBot />
              <div style={{ position: 'absolute', top: 2, right: 2, width: 14, height: 14, borderRadius: '50%', background: '#22c55e', border: '2.5px solid white', boxShadow: '0 0 6px rgba(34,197,94,0.5)' }} />
            </motion.button>
          </motion.div>
        )}
      </AnimatePresence>

      {/* CHAT WINDOW */}
      <AnimatePresence>
        {isOpen && (
          <motion.div
            initial={{ opacity: 0, y: 30, scale: 0.92 }}
            animate={{ opacity: 1, y: 0, scale: 1 }}
            exit={{ opacity: 0, y: 30, scale: 0.92 }}
            transition={{ type: 'spring', stiffness: 300, damping: 28 }}
            style={{ position: 'fixed', bottom: 28, right: 28, width: 400, maxWidth: 'calc(100vw - 2rem)', height: 620, maxHeight: 'calc(100vh - 6rem)', borderRadius: 20, overflow: 'hidden', display: 'flex', flexDirection: 'column', zIndex: 9999, boxShadow: '0 20px 60px rgba(0,0,0,0.18), 0 0 0 1px rgba(0,0,0,0.05)', background: 'var(--surface, #fff)' }}
          >
            {/* Header */}
            <div style={{ background: 'linear-gradient(145deg, #0c4a5e, #0e7490)', padding: '16px 18px', display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
                <div style={{ width: 40, height: 40, borderRadius: 12, background: 'rgba(255,255,255,0.12)', display: 'flex', alignItems: 'center', justifyContent: 'center', color: 'white' }}>
                  <IconBot />
                </div>
                <div>
                  <div style={{ fontWeight: 700, fontSize: '1rem', color: 'white', display: 'flex', alignItems: 'center', gap: 8 }}>
                    Assistant Haroo
                    <span style={{ fontSize: '0.58rem', fontWeight: 600, background: 'rgba(34,197,94,0.2)', color: '#86efac', padding: '2px 7px', borderRadius: 10, border: '1px solid rgba(34,197,94,0.25)' }}>En ligne</span>
                  </div>
                  <div style={{ fontSize: '0.76rem', color: 'rgba(255,255,255,0.6)', marginTop: 1 }}>Votre guide sur la plateforme</div>
                </div>
              </div>
              <div style={{ display: 'flex', gap: 6 }}>
                <motion.button whileHover={{ background: 'rgba(255,255,255,0.2)' }} whileTap={{ scale: 0.93 }} onClick={resetChat}
                  style={{ height: 30, borderRadius: 8, padding: '0 10px', background: 'rgba(255,255,255,0.1)', border: '1px solid rgba(255,255,255,0.12)', color: 'white', cursor: 'pointer', display: 'flex', alignItems: 'center', gap: 5, fontSize: '0.7rem', fontWeight: 500, whiteSpace: 'nowrap' as const }}>
                  <IconRefresh /> Nouveau
                </motion.button>
                <motion.button whileHover={{ background: 'rgba(255,255,255,0.2)' }} whileTap={{ scale: 0.93 }} onClick={() => setIsOpen(false)}
                  style={{ height: 30, borderRadius: 8, padding: '0 10px', background: 'rgba(255,255,255,0.1)', border: '1px solid rgba(255,255,255,0.12)', color: 'white', cursor: 'pointer', display: 'flex', alignItems: 'center', gap: 5, fontSize: '0.7rem', fontWeight: 500, whiteSpace: 'nowrap' as const }}>
                  <IconClose /> Fermer
                </motion.button>
              </div>
            </div>

            {/* Messages */}
            <div style={{ flex: 1, overflowY: 'auto', padding: '18px 14px', display: 'flex', flexDirection: 'column', gap: 14, background: 'var(--bg, #f8fafc)' }}>
              {messages.map((msg, i) => (
                <motion.div key={i} initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.25 }}
                  style={{ display: 'flex', flexDirection: msg.role === 'user' ? 'row-reverse' : 'row', gap: 10, alignItems: 'flex-end' }}>
                  {msg.role === 'assistant' && (
                    <div style={{ width: 30, height: 30, borderRadius: 10, flexShrink: 0, background: 'linear-gradient(145deg, #0e7490, #0891b2)', display: 'flex', alignItems: 'center', justifyContent: 'center', color: 'white', fontSize: '0.65rem', fontWeight: 700, boxShadow: '0 2px 6px rgba(8,145,178,0.25)' }}>H</div>
                  )}
                  <div style={{
                    maxWidth: '80%', padding: '11px 15px',
                    borderRadius: msg.role === 'user' ? '16px 16px 4px 16px' : '16px 16px 16px 4px',
                    background: msg.role === 'user' ? 'linear-gradient(145deg, #0e7490, #0891b2)' : 'var(--surface, #fff)',
                    color: msg.role === 'user' ? 'white' : 'var(--text, #1e293b)',
                    fontSize: '0.87rem', lineHeight: 1.6, wordBreak: 'break-word',
                    boxShadow: msg.role === 'user' ? '0 3px 10px rgba(8,145,178,0.25)' : '0 1px 6px rgba(0,0,0,0.05)',
                  }}>
                    {msg.role === 'assistant' ? renderMarkdown(msg.content) : msg.content}
                  </div>
                  {msg.role === 'user' && (
                    <div style={{ width: 30, height: 30, borderRadius: 10, flexShrink: 0, background: 'linear-gradient(145deg, #6366f1, #8b5cf6)', display: 'flex', alignItems: 'center', justifyContent: 'center', color: 'white', fontSize: '0.65rem', fontWeight: 700, boxShadow: '0 2px 6px rgba(99,102,241,0.25)' }}>V</div>
                  )}
                </motion.div>
              ))}

              {/* Loading */}
              {isLoading && (
                <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} style={{ display: 'flex', gap: 10, alignItems: 'flex-end' }}>
                  <div style={{ width: 30, height: 30, borderRadius: 10, flexShrink: 0, background: 'linear-gradient(145deg, #0e7490, #0891b2)', display: 'flex', alignItems: 'center', justifyContent: 'center', color: 'white', fontSize: '0.65rem', fontWeight: 700 }}>H</div>
                  <div style={{ padding: '12px 18px', borderRadius: '16px 16px 16px 4px', background: 'var(--surface, #fff)', boxShadow: '0 1px 6px rgba(0,0,0,0.05)', display: 'flex', gap: 5, alignItems: 'center' }}>
                    {[0, 1, 2].map(j => (
                      <motion.div key={j} animate={{ y: [0, -5, 0], opacity: [0.3, 0.8, 0.3] }} transition={{ duration: 0.7, repeat: Infinity, delay: j * 0.15 }}
                        style={{ width: 6, height: 6, borderRadius: '50%', background: '#0891b2' }} />
                    ))}
                    <span style={{ fontSize: '0.76rem', color: 'var(--text-muted, #94a3b8)', marginLeft: 6, fontStyle: 'italic' }}>
                      En train de repondre...
                    </span>
                  </div>
                </motion.div>
              )}

              {/* Quick Questions */}
              {!isLoading && remainingQuestions.length > 0 && (
                <motion.div initial={{ opacity: 0, y: 8 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.2 }} style={{ marginTop: 2 }}>
                  <div style={{ fontSize: '0.7rem', fontWeight: 600, color: 'var(--text-muted, #94a3b8)', textTransform: 'uppercase', letterSpacing: '0.6px', marginBottom: 8, paddingLeft: 40 }}>
                    Vous pouvez aussi demander
                  </div>
                  <div style={{ display: 'flex', flexDirection: 'column', gap: 5, paddingLeft: 40 }}>
                    {remainingQuestions.slice(0, 4).map((q, idx) => (
                      <motion.button key={q.id} className="haroo-sug"
                        initial={{ opacity: 0, x: -8 }} animate={{ opacity: 1, x: 0 }} transition={{ delay: 0.3 + idx * 0.08 }}
                        onClick={() => sendMessage(q.text)}
                        style={{ display: 'flex', alignItems: 'center', gap: 10, padding: '9px 13px', background: 'var(--surface, #fff)', border: '1px solid var(--border, #e2e8f0)', borderRadius: 12, color: 'var(--text, #1e293b)', fontSize: '0.82rem', cursor: 'pointer', textAlign: 'left', boxShadow: '0 1px 3px rgba(0,0,0,0.03)' }}>
                        <span style={{ flex: 1 }}>{q.text}</span>
                        <span style={{ color: '#0891b2', opacity: 0.4, flexShrink: 0 }}><IconChevron /></span>
                      </motion.button>
                    ))}
                  </div>
                </motion.div>
              )}
              <div ref={messagesEndRef} />
            </div>

            {/* Input */}
            <div style={{ padding: '12px 14px 14px', borderTop: '1px solid var(--border, #e2e8f0)', background: 'var(--surface, #fff)' }}>
              <div className="haroo-iw" style={{ display: 'flex', gap: 8, alignItems: 'center', background: 'var(--bg, #f8fafc)', borderRadius: 14, padding: '4px 4px 4px 14px', border: '1.5px solid var(--border, #e2e8f0)', transition: 'all 0.2s' }}>
                <input ref={inputRef} type="text" value={input} onChange={e => setInput(e.target.value)}
                  onKeyDown={e => { if (e.key === 'Enter' && !e.shiftKey) { e.preventDefault(); sendMessage(); } }}
                  placeholder="Posez votre question..." disabled={isLoading}
                  style={{ flex: 1, padding: '10px 0', border: 'none', background: 'transparent', color: 'var(--text, #1e293b)', fontSize: '0.88rem', outline: 'none' }} />
                <motion.button whileHover={{ scale: 1.04 }} whileTap={{ scale: 0.93 }}
                  onClick={() => sendMessage()} disabled={!input.trim() || isLoading}
                  style={{
                    height: 40, borderRadius: 11, padding: '0 16px',
                    background: input.trim() && !isLoading ? 'linear-gradient(145deg, #0e7490, #0891b2)' : 'var(--border, #e2e8f0)',
                    border: 'none', color: 'white', cursor: input.trim() && !isLoading ? 'pointer' : 'not-allowed',
                    display: 'flex', alignItems: 'center', gap: 6, fontSize: '0.82rem', fontWeight: 600, whiteSpace: 'nowrap' as const,
                    transition: 'all 0.2s', boxShadow: input.trim() && !isLoading ? '0 3px 10px rgba(8,145,178,0.3)' : 'none',
                  }}>
                  <IconSend /> Envoyer
                </motion.button>
              </div>
              <div style={{ textAlign: 'center', marginTop: 7, fontSize: '0.66rem', color: 'var(--text-muted, #94a3b8)' }}>
                Assistant Haroo &middot; Plateforme agricole du Togo
              </div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </>
  );
}
