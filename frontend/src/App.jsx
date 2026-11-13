// App.jsx — the page shell: header, backend status badge, and two tabs.
// Simple useState tabs instead of a router library: only 2 pages, so keep it simple.
import { useEffect, useState } from "react";
import { api } from "./api.js";
import Dashboard from "./pages/Dashboard.jsx";
import Chat from "./pages/Chat.jsx";

export default function App() {
  const [tab, setTab] = useState("dashboard");
  const [health, setHealth] = useState(null);

  // useEffect with [] = run once when the page first loads.
  useEffect(() => {
    api.health().then(setHealth).catch(() => setHealth({ status: "down" }));
  }, []);

  const connected = health && health.status !== "down";

  return (
    <div className="app">
      <header className="header">
        <div>
          <h1>Merchant Business Intelligence</h1>
          <p className="muted">UPI transaction analytics · policy search · AI assistant</p>
        </div>
        <div className="status">
          <span className={`dot ${connected ? "ok" : "bad"}`} />
          {health === null && "Checking backend…"}
          {health && !connected && "Backend not connected"}
          {connected && `Backend connected · DB ${health.database} · AI ${health.ollama}`}
        </div>
      </header>

      <nav className="tabs">
        <button className={tab === "dashboard" ? "active" : ""} onClick={() => setTab("dashboard")}>
          Dashboard
        </button>
        <button className={tab === "chat" ? "active" : ""} onClick={() => setTab("chat")}>
          AI Assistant
        </button>
      </nav>

      <main>{tab === "dashboard" ? <Dashboard /> : <Chat />}</main>
    </div>
  );
}
