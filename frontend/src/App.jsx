import { useState } from "react";
import ChatPanel from "./ChatPanel";
import TracePanel from "./TracePanel";

export default function App() {
  const [trace, setTrace] = useState([]);

  return (
    <div className="app">
      <header>
        <h1>Route Planner AI Agent</h1>
      </header>
      <main>
        <ChatPanel onTrace={setTrace} />
        <TracePanel trace={trace} />
      </main>
    </div>
  );
}
