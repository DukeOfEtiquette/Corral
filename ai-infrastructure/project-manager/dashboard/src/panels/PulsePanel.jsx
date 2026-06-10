import React from 'react';

export default function PulsePanel({ meta, coordinator }) {
  return (
    <div className="card pulse-card">
      <div className="pulse-grid">
        <div className="pulse-item">
          <span className="pulse-label">Project</span>
          <span className="pulse-value">{meta.project}</span>
        </div>
        <div className="pulse-item">
          <span className="pulse-label">Current phase</span>
          <span className="pulse-value">
            Phase {meta.current_phase}: {meta.current_phase_title}
          </span>
        </div>
        <div className="pulse-item">
          <span className="pulse-label">Last updated</span>
          <span className="pulse-value">{meta.last_updated}</span>
        </div>
        <div className="pulse-item">
          <span className="pulse-label">Generated</span>
          <span className="pulse-value pulse-value-sm">
            {meta.generated_at.replace('T', ' ').slice(0, 19)} UTC
          </span>
        </div>
      </div>
      {meta.next_step && (
        <div className="next-step">
          <span className="next-step-label">Next step</span>
          <p className="next-step-text">{meta.next_step}</p>
        </div>
      )}
    </div>
  );
}
