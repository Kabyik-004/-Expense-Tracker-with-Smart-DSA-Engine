import { useState, useRef, useEffect, useCallback, useMemo } from "react";
import {
  FiMessageCircle, FiX, FiSend, FiTrash2, FiRefreshCw,
  FiCopy, FiCheck, FiAlertCircle,
} from "react-icons/fi";

const STORAGE_KEY = "ai_assistant_messages";

const WELCOME_MESSAGE = {
  role: "assistant",
  text: "Hi! I'm your AI finance assistant. Ask me anything about your expenses, income, budgets, or analytics!",
};

const SUGGESTED_PROMPTS = [
  "How much did I spend this month?",
  "Biggest expense?",
  "Add expense of 500 for food",
  "Show my dashboard",
  "How does Undo work?",
  "Am I overspending?",
];

function loadMessages() {
  try {
    const raw = sessionStorage.getItem(STORAGE_KEY);
    if (raw) {
      const parsed = JSON.parse(raw);
      if (Array.isArray(parsed) && parsed.length) return parsed;
    }
  } catch {}
  return [WELCOME_MESSAGE];
}

function saveMessages(messages) {
  try {
    sessionStorage.setItem(STORAGE_KEY, JSON.stringify(messages.slice(-50)));
  } catch {}
}

function parseMarkdown(text) {
  const parts = [];
  let remaining = text;

  while (remaining.length > 0) {
    const codeBlockMatch = remaining.match(/^```(\w*)\n?([\s\S]*?)```/m);
    if (codeBlockMatch && codeBlockMatch.index === 0) {
      parts.push({ type: "code", lang: codeBlockMatch[1], content: codeBlockMatch[2].trimEnd() });
      remaining = remaining.slice(codeBlockMatch[0].length);
      continue;
    }

    const tableMatch = remaining.match(/^\|(.+)\|\n\|[-| :]+\|\n((?:\|.+\|\n?)*)/m);
    if (tableMatch && tableMatch.index === 0) {
      parts.push({ type: "table", raw: tableMatch[0] });
      remaining = remaining.slice(tableMatch[0].length);
      continue;
    }

    const lineEnd = remaining.indexOf("\n");
    const line = lineEnd === -1 ? remaining : remaining.slice(0, lineEnd + 1);
    parts.push({ type: "line", content: line });
    remaining = lineEnd === -1 ? "" : remaining.slice(lineEnd + 1);
  }

  return parts;
}

function renderInline(text) {
  const elements = [];
  let remaining = text;
  let idx = 0;

  while (remaining.length > 0) {
    const codeMatch = remaining.match(/^`([^`]+)`/);
    if (codeMatch) {
      elements.push(<code key={idx++} className="px-1 py-0.5 rounded bg-gray-200 dark:bg-gray-700 text-xs font-mono">{codeMatch[1]}</code>);
      remaining = remaining.slice(codeMatch[0].length);
      continue;
    }

    const boldMatch = remaining.match(/^\*\*([^*]+)\*\*/);
    if (boldMatch) {
      elements.push(<strong key={idx++} className="font-semibold">{renderInline(boldMatch[1])}</strong>);
      remaining = remaining.slice(boldMatch[0].length);
      continue;
    }

    const italicMatch = remaining.match(/^\*([^*]+)\*/);
    if (italicMatch) {
      elements.push(<em key={idx++} className="italic">{renderInline(italicMatch[1])}</em>);
      remaining = remaining.slice(italicMatch[0].length);
      continue;
    }

    const urlMatch = remaining.match(/^https?:\/\/[^\s<]+/);
    if (urlMatch) {
      const href = urlMatch[0];
      elements.push(
        <a key={idx++} href={href} target="_blank" rel="noopener noreferrer"
           className="text-emerald-600 dark:text-emerald-400 underline hover:no-underline">
          {href}
        </a>
      );
      remaining = remaining.slice(href.length);
      continue;
    }

    elements.push(remaining[0]);
    remaining = remaining.slice(1);
  }

  return elements;
}

function MessageContent({ text }) {
  const parts = useMemo(() => parseMarkdown(text), [text]);

  return parts.map((part, i) => {
    if (part.type === "code") {
      return <CodeBlock key={i} lang={part.lang} code={part.content} />;
    }
    if (part.type === "table") {
      return <TableBlock key={i} raw={part.raw} />;
    }
    return (
      <div key={i} className="min-h-[1.25em]">
        {renderInline(part.content)}
      </div>
    );
  });
}

function CodeBlock({ lang, code }) {
  const [copied, setCopied] = useState(false);

  const handleCopy = useCallback(() => {
    navigator.clipboard.writeText(code).then(() => {
      setCopied(true);
      setTimeout(() => setCopied(false), 1500);
    }).catch(() => {});
  }, [code]);

  return (
    <div className="my-2 rounded-lg overflow-hidden bg-gray-900 dark:bg-gray-950 border border-gray-700/50">
      <div className="flex items-center justify-between px-3 py-1.5 bg-gray-800 dark:bg-gray-900 text-[11px] text-gray-400">
        <span>{lang || "code"}</span>
        <button onClick={handleCopy} className="flex items-center gap-1 hover:text-white transition-colors"
                aria-label={copied ? "Copied" : "Copy code"}>
          {copied ? <FiCheck className="w-3 h-3 text-emerald-400" /> : <FiCopy className="w-3 h-3" />}
          <span>{copied ? "Copied" : "Copy"}</span>
        </button>
      </div>
      <pre className="px-3 py-2.5 text-[13px] leading-relaxed overflow-x-auto"><code>{code}</code></pre>
    </div>
  );
}

function TableBlock({ raw }) {
  const rows = raw.trim().split("\n").filter(Boolean);
  if (rows.length < 2) return null;
  const headers = rows[0].split("|").filter(Boolean).map((s) => s.trim());
  const dataRows = rows.slice(2).map((r) => r.split("|").filter(Boolean).map((s) => s.trim()));

  return (
    <div className="my-2 overflow-x-auto">
      <table className="w-full text-xs border-collapse">
        <thead>
          <tr>
            {headers.map((h, i) => (
              <th key={i} className="border border-gray-300 dark:border-gray-600 px-2 py-1 bg-gray-100 dark:bg-gray-800 text-left font-semibold">{h}</th>
            ))}
          </tr>
        </thead>
        <tbody>
          {dataRows.map((row, ri) => (
            <tr key={ri}>
              {row.map((cell, ci) => (
                <td key={ci} className="border border-gray-300 dark:border-gray-600 px-2 py-1">{cell}</td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

function ThinkingDots() {
  return (
    <div className="flex items-center gap-2.5 px-4 py-3">
      <div className="flex items-center gap-1">
        <span className="w-2 h-2 bg-emerald-400 dark:bg-emerald-500 rounded-full animate-bounce" style={{ animationDelay: "0ms" }} />
        <span className="w-2 h-2 bg-emerald-400 dark:bg-emerald-500 rounded-full animate-bounce" style={{ animationDelay: "150ms" }} />
        <span className="w-2 h-2 bg-emerald-400 dark:bg-emerald-500 rounded-full animate-bounce" style={{ animationDelay: "300ms" }} />
      </div>
      <span className="text-[11px] text-gray-400 dark:text-gray-500 font-medium">Thinking...</span>
    </div>
  );
}

export default function AIAssistant() {
  const [open, setOpen] = useState(false);
  const [messages, setMessages] = useState(loadMessages);
  const [input, setInput] = useState("");
  const [typing, setTyping] = useState(false);
  const [error, setError] = useState(null);
  const [lastSent, setLastSent] = useState(0);
  const [showPrompts, setShowPrompts] = useState(true);

  const endRef = useRef(null);
  const inputRef = useRef(null);
  const abortRef = useRef(null);
  const panelRef = useRef(null);

  useEffect(() => { saveMessages(messages); }, [messages]);

  const scrollToBottom = useCallback(() => {
    endRef.current?.scrollIntoView({ behavior: "smooth" });
  }, []);

  useEffect(() => {
    if (open) {
      const t = setTimeout(scrollToBottom, 50);
      return () => clearTimeout(t);
    }
  }, [open, scrollToBottom]);

  useEffect(() => {
    scrollToBottom();
  }, [messages, typing, scrollToBottom]);

  useEffect(() => {
    if (!open) return;
    function onKeyDown(e) {
      if (e.key === "Escape") setOpen(false);
    }
    document.addEventListener("keydown", onKeyDown);
    return () => document.removeEventListener("keydown", onKeyDown);
  }, [open]);

  const clearSessionOnServer = useCallback(async () => {
    try {
      await fetch("/api/assistant/clear", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${localStorage.getItem("access_token")}`,
        },
      });
    } catch {}
  }, []);

  const sendMessage = useCallback(async (overrideText) => {
    const text = (overrideText || input).trim();
    if (!text || typing) return;

    const now = Date.now();
    if (now - lastSent < 1000) return;
    setLastSent(now);

    setInput("");
    setError(null);
    setShowPrompts(false);

    const userMsg = { role: "user", text };
    setMessages((prev) => [...prev, userMsg]);
    setTyping(true);

    const assistantMsg = { role: "assistant", text: "" };
    setMessages((prev) => [...prev, assistantMsg]);

    abortRef.current = new AbortController();

    try {
      const history = messages.concat(userMsg).map(({ role, text: t }) => ({ role, text: t }));
      const res = await fetch("/api/assistant/chat", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${localStorage.getItem("access_token")}`,
        },
        body: JSON.stringify({ message: text, history }),
        signal: abortRef.current.signal,
      });

      if (!res.ok) {
        const errData = await res.json().catch(() => ({}));
        throw new Error(errData.message || `HTTP ${res.status}`);
      }

      const reader = res.body.getReader();
      const decoder = new TextDecoder();
      let buffer = "";

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        buffer += decoder.decode(value, { stream: true });
        const lines = buffer.split("\n");
        buffer = lines.pop() || "";

        for (const line of lines) {
          const trimmed = line.trim();
          if (!trimmed.startsWith("data: ")) continue;
          const data = trimmed.slice(6);
          if (data === '{"done":true}') break;
          try {
            const parsed = JSON.parse(data);
            if (parsed.error) {
              setError(parsed.error);
              break;
            }
            if (parsed.reply) {
              setMessages((prev) => {
                const updated = [...prev];
                const last = updated[updated.length - 1];
                if (last && last.role === "assistant") {
                  updated[updated.length - 1] = { ...last, text: last.text + parsed.reply };
                }
                return updated;
              });
            }
          } catch {}
        }
      }
    } catch (err) {
      if (err.name === "AbortError") return;

      const fallbackReply = getFallbackResponse(text);
      setMessages((prev) => {
        const updated = [...prev];
        const last = updated[updated.length - 1];
        if (last && last.role === "assistant" && !last.text) {
          updated[updated.length - 1] = { ...last, text: fallbackReply };
        }
        return updated;
      });
      setError("Connection issue. Showing offline response.");
    } finally {
      setTyping(false);
      abortRef.current = null;
      setTimeout(() => inputRef.current?.focus(), 100);
    }
  }, [input, typing, messages, lastSent]);

  const handleKeyDown = useCallback(
    (e) => {
      if (e.key === "Enter" && !e.shiftKey) {
        e.preventDefault();
        sendMessage();
      }
    },
    [sendMessage]
  );

  const clearChat = useCallback(() => {
    setMessages([WELCOME_MESSAGE]);
    setError(null);
    setShowPrompts(true);
    clearSessionOnServer();
  }, [clearSessionOnServer]);

  const retry = useCallback(() => {
    if (messages.length < 2) return;
    const lastUserMsg = [...messages].reverse().find((m) => m.role === "user");
    if (lastUserMsg) {
      setMessages((prev) => prev.slice(0, -1));
      sendMessage(lastUserMsg.text);
    }
  }, [messages, sendMessage]);

  useEffect(() => {
    if (open) {
      const t = setTimeout(() => inputRef.current?.focus(), 200);
      return () => clearTimeout(t);
    }
  }, [open]);

  return (
    <>
      <div
        className={`fixed inset-0 z-40 bg-black/20 dark:bg-black/40 backdrop-blur-sm transition-opacity duration-300
          ${open ? "opacity-100" : "opacity-0 pointer-events-none"}
          md:opacity-0 md:pointer-events-none`}
        onClick={() => setOpen(false)}
        aria-hidden="true"
      />

      <div className="fixed bottom-0 right-0 z-50 flex flex-col items-end sm:bottom-6 sm:right-6">
        {open && (
          <div
            ref={panelRef}
            role="dialog"
            aria-label="AI Finance Assistant chat"
            aria-modal="true"
            className={`mb-0 sm:mb-4
              w-full sm:w-[380px] lg:w-[400px]
              h-[100dvh] sm:h-[560px] lg:h-[600px]
              max-h-[100dvh] sm:max-h-[calc(100vh-8rem)]
              bg-white dark:bg-gray-900
              sm:rounded-2xl sm:shadow-2xl sm:shadow-black/10 dark:sm:shadow-black/30
              sm:border sm:border-gray-200/60 dark:sm:border-gray-700/60
              flex flex-col overflow-hidden
              animate-chat-open`}
          >
            <div className="flex items-center justify-between px-4 py-3 border-b border-gray-100 dark:border-gray-800 shrink-0">
              <div className="flex items-center gap-2.5 min-w-0">
                <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-emerald-400 to-emerald-600 flex items-center justify-center shrink-0">
                  <FiMessageCircle className="w-4 h-4 text-white" />
                </div>
                <div className="min-w-0">
                  <p className="text-sm font-semibold text-gray-900 dark:text-white truncate">
                    AI Assistant
                  </p>
                  <p className="text-[10px] text-gray-400 dark:text-gray-500">
                    {typing ? "Typing..." : "Online"}
                  </p>
                </div>
              </div>
              <div className="flex items-center gap-1 shrink-0">
                {error && (
                  <button
                    onClick={retry}
                    title="Retry last request"
                    aria-label="Retry"
                    className="p-1.5 rounded-lg text-amber-500 hover:text-amber-600 hover:bg-amber-50 dark:hover:bg-amber-900/30 transition-colors"
                  >
                    <FiRefreshCw className="w-3.5 h-3.5" />
                  </button>
                )}
                <button
                  onClick={clearChat}
                  title="Clear conversation"
                  aria-label="Clear conversation"
                  className="p-1.5 rounded-lg text-gray-400 dark:text-gray-500 hover:text-gray-600 dark:hover:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-800 transition-colors"
                >
                  <FiTrash2 className="w-3.5 h-3.5" />
                </button>
                <button
                  onClick={() => setOpen(false)}
                  title="Close"
                  aria-label="Close chat"
                  className="p-1.5 rounded-lg text-gray-400 dark:text-gray-500 hover:text-gray-600 dark:hover:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-800 transition-colors"
                >
                  <FiX className="w-4 h-4" />
                </button>
              </div>
            </div>

            <div
              className="flex-1 overflow-y-auto px-4 py-3 space-y-3 scroll-smooth overscroll-contain"
              role="log"
              aria-label="Chat messages"
              aria-live="polite"
            >
              {messages.map((msg, i) => (
                <div
                  key={i}
                  className={`flex ${msg.role === "user" ? "justify-end" : "justify-start"} animate-message-in`}
                >
                  <div
                    className={`max-w-[88%] sm:max-w-[82%] px-3.5 py-2.5 rounded-2xl text-sm leading-relaxed ${
                      msg.role === "user"
                        ? "bg-emerald-500 dark:bg-emerald-600 text-white rounded-br-md"
                        : "bg-gray-100 dark:bg-gray-800 text-gray-700 dark:text-gray-200 rounded-bl-md"
                    }`}
                  >
                    {msg.role === "assistant" ? (
                      <MessageContent text={msg.text} />
                    ) : (
                      <span className="whitespace-pre-wrap">{msg.text}</span>
                    )}
                  </div>
                </div>
              ))}

              {showPrompts && messages.length === 1 && !typing && (
                <div className="flex flex-wrap gap-2 pt-1">
                  {SUGGESTED_PROMPTS.map((prompt) => (
                    <button
                      key={prompt}
                      onClick={() => sendMessage(prompt)}
                      className="text-xs px-3 py-1.5 rounded-full border border-gray-200 dark:border-gray-700
                        text-gray-600 dark:text-gray-400 hover:bg-gray-100 dark:hover:bg-gray-800
                        hover:border-emerald-300 dark:hover:border-emerald-700 hover:text-emerald-600 dark:hover:text-emerald-400
                        transition-all duration-200 active:scale-95"
                      aria-label={`Ask: ${prompt}`}
                    >
                      {prompt}
                    </button>
                  ))}
                </div>
              )}

              {typing && !messages[messages.length - 1]?.text && (
                <div className="flex justify-start animate-message-in">
                  <div className="bg-gray-100 dark:bg-gray-800 rounded-2xl rounded-bl-md">
                    <ThinkingDots />
                  </div>
                </div>
              )}

              {error && (
                <div className="flex flex-col items-center gap-2" role="alert">
                  <div className="flex items-center gap-1.5 px-3.5 py-2 rounded-xl bg-red-50 dark:bg-red-900/30 border border-red-200 dark:border-red-800 text-xs text-red-600 dark:text-red-400">
                    <FiAlertCircle className="w-3.5 h-3.5 shrink-0" />
                    <span>{error}</span>
                  </div>
                  <button
                    onClick={retry}
                    className="flex items-center gap-1 text-xs text-gray-500 dark:text-gray-400 hover:text-emerald-600 dark:hover:text-emerald-400 transition-colors"
                    aria-label="Retry request"
                  >
                    <FiRefreshCw className="w-3 h-3" />
                    Retry
                  </button>
                </div>
              )}

              <div ref={endRef} />
            </div>

            <div className="px-4 py-3 border-t border-gray-100 dark:border-gray-800 shrink-0">
              <div className="flex items-center gap-2 bg-gray-50 dark:bg-gray-800/50 rounded-xl px-3 py-1.5 border border-gray-200/50 dark:border-gray-700/50 focus-within:border-emerald-400 dark:focus-within:border-emerald-500 transition-colors">
                <input
                  ref={inputRef}
                  type="text"
                  value={input}
                  onChange={(e) => setInput(e.target.value)}
                  onKeyDown={handleKeyDown}
                  placeholder="Ask about your finances..."
                  disabled={typing}
                  aria-label="Chat message"
                  className="flex-1 bg-transparent text-sm text-gray-700 dark:text-gray-200 placeholder-gray-400 dark:placeholder-gray-500 outline-none py-1.5 disabled:opacity-50"
                />
                <button
                  onClick={sendMessage}
                  disabled={!input.trim() || typing}
                  aria-label="Send message"
                  className="p-1.5 rounded-lg text-white bg-emerald-500 dark:bg-emerald-600 hover:bg-emerald-600 dark:hover:bg-emerald-500 disabled:opacity-40 disabled:cursor-not-allowed transition-all active:scale-90 shrink-0"
                >
                  <FiSend className="w-4 h-4" />
                </button>
              </div>
              <p className="mt-1 text-[10px] text-gray-400 dark:text-gray-600 text-center">
                AI may produce inaccurate information
              </p>
            </div>
          </div>
        )}

        <button
          onClick={() => setOpen((prev) => !prev)}
          aria-label={open ? "Close AI assistant" : "Open AI assistant"}
          className={`w-12 h-12 sm:w-14 sm:h-14 rounded-full flex items-center justify-center shadow-xl transition-all duration-300 active:scale-90 ${
            open
              ? "bg-gray-200 dark:bg-gray-700 shadow-black/10 dark:shadow-black/30 scale-100 mr-3 sm:mr-0 mb-3 sm:mb-0"
              : "bg-gradient-to-br from-emerald-500 to-emerald-600 dark:from-emerald-500 dark:to-emerald-700 shadow-emerald-500/30 dark:shadow-emerald-500/20 hover:shadow-emerald-500/40 hover:scale-105 animate-fab-pulse mr-3 sm:mr-0 mb-3 sm:mb-0"
          }`}
        >
          {open ? (
            <FiX className="w-5 h-5 sm:w-6 sm:h-6 text-gray-600 dark:text-gray-300" />
          ) : (
            <FiMessageCircle className="w-5 h-5 sm:w-6 sm:h-6 text-white" />
          )}
        </button>
      </div>

      <style>{`
        @keyframes chat-open {
          from { opacity: 0; transform: translateY(16px) scale(0.95); }
          to { opacity: 1; transform: translateY(0) scale(1); }
        }
        @keyframes message-in {
          from { opacity: 0; transform: translateY(8px); }
          to { opacity: 1; transform: translateY(0); }
        }
        @keyframes fab-pulse {
          0%, 100% { box-shadow: 0 8px 32px rgba(16,185,129,0.3); }
          50% { box-shadow: 0 8px 48px rgba(16,185,129,0.5); }
        }
        .animate-chat-open { animation: chat-open 0.3s cubic-bezier(0.16,1,0.3,1) forwards; }
        .animate-message-in { animation: message-in 0.25s ease-out forwards; }
        .animate-fab-pulse { animation: fab-pulse 3s ease-in-out infinite; }

        @media (max-width: 639px) {
          .animate-chat-open {
            animation: none;
          }
        }
      `}</style>
    </>
  );
}

function getFallbackResponse(text) {
  const lower = text.toLowerCase();
  if (/\b(hi|hello|hey)\b/.test(lower)) {
    return "Hello! I'm your AI finance assistant. How can I help you today?";
  }
  if (/\b(expense|spent|spend|paid|bought)\b/.test(lower)) {
    return "I can help you track your expenses! You can add expenses by telling me the amount, category, and description.";
  }
  if (/\b(income|salary|earn)\b/.test(lower)) {
    return "Great! You can add income by providing the amount and source. For example: I earned ₹50,000 as salary.";
  }
  if (/\b(budget|save)\b/.test(lower)) {
    return "Budgeting is key to financial health! I can help you set budgets for different categories.";
  }
  if (/\b(analytics|dashboard|summary)\b/.test(lower)) {
    return "Your analytics dashboard shows spending patterns, category distribution, and monthly trends.";
  }
  return "I'm your finance assistant! I can help with expenses, income, budgets, and analytics. What would you like to do?";
}
