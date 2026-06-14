import React from 'react';

/**
 * BlockedPanel -- global blocked-task surface for the landing view.
 *
 * Receives the top-level data.blocked list ({workspace, id, title, reason}[]).
 * Always renders: shows 'No blocked work' when the list is empty, and a
 * per-entry list when populated (ADR-040 decision 4).
 */
export default function BlockedPanel({ blocked }) {
  const items = blocked || [];
  return (
    <div className="card">
      <h3>Blocked work</h3>
      {items.length === 0 ? (
        <p className="muted">No blocked work</p>
      ) : (
        <ol className="activity-list">
          {items.map((entry, i) => (
            <li key={i} className="activity-item blocked-item">
              <span className="blocked-id">{entry.id}</span>
              <span className="blocked-workspace muted">{entry.workspace}</span>
              <span className="blocked-title activity-text">{entry.title}</span>
              {entry.reason && (
                <span className="blocked-reason muted">{entry.reason}</span>
              )}
            </li>
          ))}
        </ol>
      )}
    </div>
  );
}
