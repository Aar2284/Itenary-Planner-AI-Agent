import { useState } from "react";
import { sendMessage } from "./api";

export default function ChatPanel({ onTrace }) {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);

  const handleSend = async () => {
    if (!input.trim() || loading) return;

    const userMsg = input;
    setInput("");
    setMessages((prev) => [...prev, { role: "user", content: userMsg }]);
    setLoading(true);

    try {
      const data = await sendMessage(userMsg);
      setMessages((prev) => [...prev, { role: "assistant", content: data.response }]);
      if (data.trace?.length > 0) {
        onTrace(data.trace);
      }
    } catch (err) {
      setMessages((prev) => [...prev, { role: "assistant", content: "Error connecting to agent." }]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="chat-panel">
      <div className="messages">
        {messages.map((msg, i) => (
          <div key={i} className={`message ${msg.role}`}>
            <strong>{msg.role === "user" ? "You" : "Agent"}:</strong> {msg.content}
          </div>
        ))}
        {loading && <div className="message assistant">Thinking...</div>}
      </div>
      <div className="input-row">
        <input
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={(e) => e.key === "Enter" && handleSend()}
          placeholder="Ask about places, routes..."
        />
        <button onClick={handleSend} disabled={loading}>Send</button>
      </div>
    </div>
  );
}
