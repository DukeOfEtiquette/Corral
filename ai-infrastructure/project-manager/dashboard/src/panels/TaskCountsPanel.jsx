import React from 'react';

export default function TaskCountsPanel({ counts }) {
  if (!counts) return null;
  return (
    <div className="task-counts">
      <span className="tc-label">Tasks:</span>
      <span className="tc-item tc-backlog">{counts.backlog} backlog</span>
      <span className="tc-sep" />
      <span className="tc-item tc-inprogress">{counts['in-progress']} in-progress</span>
      <span className="tc-sep" />
      <span className="tc-item tc-blocked">{counts.blocked} blocked</span>
      <span className="tc-sep" />
      <span className="tc-item tc-done">{counts.done} done</span>
      <span className="tc-sep" />
      <span className="tc-item tc-total">{counts.total} total</span>
    </div>
  );
}
