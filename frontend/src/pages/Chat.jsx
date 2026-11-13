// Chat.jsx — ask the AI assistant questions.
// Each answer shows WHICH tool the AI picked (analytics / documents / both)
// and the evidence it used, so you can see the RAG flow, not just the reply.
import { useState } from "react";
import { api } from "../api.js";

const EXAMPLES = [
  "What is the overall success rate?",
  "Which are the top merchants by volume?",
  "What does BANK_TIMEOUT mean?",
  "Why might a payment take too long to receive confirmation?",
  "What are the most common failure reasons and how should we investigate them?",
];

function Message({ msg }) {
  if (msg.role === "user") return <div className="bubble user">{msg.text}</div>;
  if (msg.role === "error") return <div className="bubble error">{msg.text}</div>;

  const r = msg.result;
  return (
    <div className="bubble bot">
      <div className="answer">{r.answer}</div>
      <div className="meta">
        Route: <span className="tag">{r.route}</span>
        {r.analytics_metric && <> · Metric: <span className="tag">{r.analytics_metric}</span></>}
      </div>
      {r.sources.length > 0 && (
        <details>
          <summary>Document passages used ({r.sources.length})</summary>
          {r.sources.map((s) => (
            <div key={s.chunk_id} className="source">
              <strong>[{s.chunk_id}]</strong> {s.text}
            </div>
          ))}
        </details>
      )}
      {r.analytics_data && (
        <details>
          <summary>Analytics data used</summary>
          <pre>{JSON.stringify(r.analytics_data, null, 2)}</pre>
        </details>
      )}
    </div>
  );
}

export default function Chat() {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);

  async function ask(question) {
    if (!question.trim() || loading) return;
    // Functional update (prev => ...) so we never overwrite newer state.
    setMessages((prev) => [...prev, { role: "user", text: question }]);
    setInput("");
    setLoading(true);
    try {
      const result = await api.chat(question);
      setMessages((prev) => [...prev, { role: "bot", result }]);
    } catch (err) {
      setMessages((prev) => [...prev, { role: "error", text: err.message }]);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="stack">
      <h2>AI Assistant</h2>
      <div className="examples">
        {EXAMPLES.map((q) => (
          <button key={q} className="chip" onClick={() => ask(q)} disabled={loading}>
            {q}
          </button>
        ))}
      </div>

      <div className="card chat">
        {messages.length === 0 && <p className="muted">Ask about transactions, merchants, or payment policies.</p>}
        {messages.map((m, i) => (
          <Message key={i} msg={m} />
        ))}
        {loading && <div className="bubble bot muted">Thinking… (the local model can take a few seconds)</div>}
      </div>

      {/* onSubmit + preventDefault: stop the browser from reloading the page. */}
      <form
        className="ask"
        onSubmit={(e) => {
          e.preventDefault();
          ask(input);
        }}
      >
        <input value={input} onChange={(e) => setInput(e.target.value)} placeholder="Type your question…" maxLength={500} />
        <button type="submit" disabled={loading || input.trim().length < 2}>Ask</button>
      </form>
    </div>
  );
}
