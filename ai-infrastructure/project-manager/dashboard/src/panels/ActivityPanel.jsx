import React from 'react';

export default function ActivityPanel({ activity }) {
  if (!activity || activity.length === 0) {
    return (
      <div className="card">
        <h3>Recent activity</h3>
        <p className="muted">No activity recorded yet.</p>
      </div>
    );
  }
  return (
    <div className="card">
      <h3>Recent activity ({activity.length})</h3>
      <ol className="activity-list">
        {activity.map((item, i) => (
          <li key={i} className="activity-item">
            <span className="activity-date">{item.date}</span>
            <a href={`#/workspace/${item.workspace}`} className="activity-workspace">
              {item.workspace}
            </a>
            <span className="activity-text">{item.text}</span>
          </li>
        ))}
      </ol>
    </div>
  );
}
