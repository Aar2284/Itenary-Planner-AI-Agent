export default function TracePanel({ trace }) {
  if (!trace || trace.length === 0) {
    return (
      <div className="trace-panel">
        <h3>Agent Trace</h3>
        <p className="empty">No tool calls yet. Send a message to see the agent work.</p>
      </div>
    );
  }

  return (
    <div className="trace-panel">
      <h3>Agent Trace</h3>
      {trace.map((call, i) => (
        <div key={i} className="trace-entry">
          <div className="trace-header">
            <span className="tool-name">{call.tool}</span>
          </div>
          <details>
            <summary>Arguments</summary>
            <pre>{JSON.stringify(call.args, null, 2)}</pre>
          </details>
          <details>
            <summary>Result</summary>
            <pre>{JSON.stringify(call.result, null, 2)}</pre>
          </details>
        </div>
      ))}
    </div>
  );
}
