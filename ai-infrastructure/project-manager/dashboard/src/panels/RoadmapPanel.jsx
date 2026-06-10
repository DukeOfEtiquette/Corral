import React from 'react';

const STATUS_LABELS = {
  done: 'Done',
  current: 'Current',
  upcoming: 'Upcoming',
};

const MILESTONE_STATUS_LABELS = {
  done: 'Done',
  'in-progress': 'In Progress',
  planned: 'Planned',
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
            {item.milestones && item.milestones.length > 0 && (
              <ul className="roadmap-milestones">
                {item.milestones.map((ms) => (
                  <li key={ms.id} className="roadmap-milestone-item">
                    <span className="roadmap-milestone-id">{ms.id}</span>
                    <span className="roadmap-milestone-title">{ms.title}</span>
                    <span className={`badge badge-milestone-${ms.status}`}>
                      {MILESTONE_STATUS_LABELS[ms.status] || ms.status}
                    </span>
                    {ms.task && (
                      <span className="roadmap-milestone-task">{ms.task}</span>
                    )}
                  </li>
                ))}
              </ul>
            )}
          </li>
        ))}
      </ol>
    </div>
  );
}
