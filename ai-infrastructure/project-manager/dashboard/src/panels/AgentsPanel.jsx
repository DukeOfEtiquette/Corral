import React from 'react';

export default function AgentsPanel({ agents }) {
  const executors = agents.filter(a => a.kind === 'executor');
  const dispatchers = agents.filter(a => a.kind === 'dispatch');

  return (
    <div className="card">
      <h3>Agent Fleet</h3>
      <AgentGroup title="Executors" agents={executors} />
      <AgentGroup title="Dispatch-loop & checkers" agents={dispatchers} />
    </div>
  );
}

function AgentGroup({ title, agents }) {
  if (!agents || agents.length === 0) return null;
  return (
    <div className="agent-group">
      <div className="agent-group-heading">{title}</div>
      <table className="agent-table">
        <thead>
          <tr>
            <th>Agent</th>
            <th>Model</th>
            <th>Purpose</th>
          </tr>
        </thead>
        <tbody>
          {agents.map(agent => (
            <tr key={agent.name}>
              <td className="agent-name">{agent.name}</td>
              <td>
                <span className={`badge badge-model-${agent.model}`}>{agent.model}</span>
              </td>
              <td className="agent-purpose">{agent.purpose}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
