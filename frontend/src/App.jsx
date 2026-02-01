import { useMemo, useRef, useState, useEffect } from "react";

const API_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";

const TOOL_LABELS = {
  tarot: "塔罗",
  lenormand: "雷诺曼",
  liuyao: "六爻",
};

const createSession = () => ({
  id: crypto.randomUUID(),
  title: "新的会话",
  createdAt: new Date().toISOString(),
});

export default function App() {
  const initialSession = useMemo(() => createSession(), []);
  const [sessions, setSessions] = useState([initialSession]);
  const [activeSessionId, setActiveSessionId] = useState(initialSession.id);
  const [messagesBySession, setMessagesBySession] = useState({
    [initialSession.id]: [],
  });
  const [input, setInput] = useState("");
  const [isSending, setIsSending] = useState(false);
  const listRef = useRef(null);

  const activeMessages = messagesBySession[activeSessionId] || [];

  useEffect(() => {
    if (!listRef.current) return;
    listRef.current.scrollTop = listRef.current.scrollHeight;
  }, [activeMessages]);

  const handleNewSession = () => {
    const next = createSession();
    setSessions((prev) => [next, ...prev]);
    setMessagesBySession((prev) => ({ ...prev, [next.id]: [] }));
    setActiveSessionId(next.id);
  };

  const updateSessionTitle = (sessionId, message) => {
    setSessions((prev) =>
      prev.map((session) =>
        session.id === sessionId && session.title === "新的会话"
          ? { ...session, title: message.slice(0, 12) }
          : session
      )
    );
  };

  const appendMessage = (sessionId, message) => {
    setMessagesBySession((prev) => ({
      ...prev,
      [sessionId]: [...(prev[sessionId] || []), message],
    }));
  };

  const sendMessage = async (forceDivination = false) => {
    const content = input.trim();
    if (!content || isSending) return;

    setInput("");
    updateSessionTitle(activeSessionId, content);
    appendMessage(activeSessionId, { role: "user", content });

    setIsSending(true);
    try {
      const response = await fetch(`${API_URL}/chat`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          session_id: activeSessionId,
          message: content,
          force_divination: forceDivination,
        }),
      });

      if (!response.ok) {
        throw new Error("请求失败，请稍后再试");
      }

      const data = await response.json();
      appendMessage(activeSessionId, {
        role: "assistant",
        content: data.message,
        tool: data.tool,
        trace: data.trace,
        reading: data.reading,
      });
    } catch (error) {
      appendMessage(activeSessionId, {
        role: "assistant",
        content: "网络暂时不稳定，请稍后再试。",
      });
    } finally {
      setIsSending(false);
    }
  };

  const handleKeyDown = (event) => {
    if (event.key === "Enter" && !event.shiftKey) {
      event.preventDefault();
      sendMessage(false);
    }
  };

  return (
    <div className="app-shell">
      <aside className="sidebar">
        <div className="brand">
          <span className="brand-title">问象</span>
          <span className="brand-sub">Oracle's Choice</span>
        </div>
        <button className="primary-btn" onClick={handleNewSession}>
          新建会话
        </button>
        <div className="session-list">
          {sessions.map((session) => (
            <button
              key={session.id}
              className={
                session.id === activeSessionId ? "session-item active" : "session-item"
              }
              onClick={() => setActiveSessionId(session.id)}
            >
              <div className="session-title">{session.title}</div>
              <div className="session-time">
                {new Date(session.createdAt).toLocaleDateString("zh-CN")}
              </div>
            </button>
          ))}
        </div>
      </aside>

      <main className="chat-panel">
        <header className="chat-header">
          <div>
            <h1>占问对话</h1>
            <p>输入你的问题，系统将自动选择合适的占卜方式。</p>
          </div>
          <div className="status-chip">在线 · SpoonOS Graph Agent</div>
        </header>

        <section className="message-list" ref={listRef}>
          {activeMessages.length === 0 ? (
            <div className="empty-state">
              <h2>从一个问题开始</h2>
              <p>例如：“这段感情还有机会吗？”</p>
            </div>
          ) : (
            activeMessages.map((message, index) => (
              <article
                key={`${message.role}-${index}`}
                className={message.role === "assistant" ? "message assistant" : "message user"}
              >
                <div className="bubble">
                  <div className="meta">
                    {message.role === "assistant" ? "问象" : "我"}
                  </div>
                  <div className="content">{message.content}</div>
                  {message.role === "assistant" && message.tool && message.tool !== "chat" && (
                    <details className="detail-card">
                      <summary>展开解读细节</summary>
                      <div className="detail-grid">
                        <div>
                          <h4>使用的占卜工具</h4>
                          <p>{TOOL_LABELS[message.tool] || message.tool}</p>
                        </div>
                        {message.reading && (
                          <div>
                            <h4>结构化结果</h4>
                            <p>{message.reading.verdict}</p>
                          </div>
                        )}
                      </div>
                      {message.trace && (
                        <div className="trace-block">
                          <h4>Agent 决策过程</h4>
                          <pre>{JSON.stringify(message.trace, null, 2)}</pre>
                        </div>
                      )}
                    </details>
                  )}
                </div>
              </article>
            ))
          )}
        </section>

        <section className="composer floating">
          <textarea
            value={input}
            onChange={(event) => setInput(event.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="写下你的问题，按 Enter 发送"
            rows={3}
          />
          <div className="composer-actions">
            <span className="hint">Shift + Enter 换行</span>
            <div className="composer-buttons">
              <button className="ghost-btn" onClick={() => sendMessage(false)} disabled={isSending}>
                发送
              </button>
              <button className="primary-btn" onClick={() => sendMessage(true)} disabled={isSending}>
                占卜
              </button>
            </div>
          </div>
        </section>
      </main>
    </div>
  );
}
