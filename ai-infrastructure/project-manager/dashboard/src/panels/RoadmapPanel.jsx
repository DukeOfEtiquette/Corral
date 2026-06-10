import React from 'react';

const STATUS_LABELS = {
  done: 'Done',
  current: 'Current',
  upcoming: 'Upcoming',
};

export default function RoadmapPanel({ roadmap }) {
  return (
    <div className="card">
      <h3>Roadmap</h3>
      <ol className="roadmap-list">
        {roadmap.map((item) => (
          <li key={item.phase} className={`roadmap-item roadmap-${item.status}`}>
            <div className="roadmap-header">
              <span className="roadmap-phase">Phase {item.phase}</span>
              <span className="roadmap-title">{item.title}</span>
              <span className={`badge badge-roadmap-${item.status}`}>
                {STATUS_LABELS[item.status] || item.status}
              </span>
            </div>
            <p className="roadmap-deliverables">{item.deliverables}</p>
          </li>
        ))}
      </ol>
    </div>
  );
}
