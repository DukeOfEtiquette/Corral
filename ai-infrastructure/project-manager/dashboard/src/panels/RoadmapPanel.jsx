import React, { useState } from 'react';

// Map a resolved_status to a CSS class suffix for the ref badge.
// Uses existing color values per the kickoff's palette decision.
function refBadgeClass(status) {
  switch (status) {
    case 'done':
    case 'accepted':
      return 'ref-done';
    case 'in-progress':
      return 'ref-in-progress';
    case 'blocked':
      return 'ref-blocked';
    case 'backlog':
    case 'planned':
    case 'pending':
      return 'ref-planned';
    case 'mixed':
      return 'ref-mixed';
    case 'unresolved':
      return 'ref-unresolved';
    default:
      return 'ref-planned';
  }
}

function SingleBadge({ badge: r }) {
  return (
    <span className={`badge badge-ref badge-${refBadgeClass(r.resolved_status)}`}>
      {r.label}
    </span>
  );
}

function RangeBadge({ badge: r }) {
  const label = `${r.label} · ${r.member_count} ${r.rollup_status}`;
  return (
    <span className={`badge badge-ref badge-ref-range badge-${refBadgeClass(r.resolved_status)}`}>
      {label}
    </span>
  );
}

function UnresolvedBadge({ badge: r }) {
  return (
    <span className="badge badge-ref badge-ref-unresolved">
      {'? '}{r.label}
    </span>
  );
}

function RefBadge({ badge: r }) {
  if (r.flavor === 'range') return <RangeBadge badge={r} />;
  if (r.flavor === 'unresolved' || r.resolved_status === 'unresolved') return <UnresolvedBadge badge={r} />;
  return <SingleBadge badge={r} />;
}

// Department badge: left-most badge on each epic header.
// Displays the epic's owning department slug in a neutral category-tag style.
function DeptBadge({ dept }) {
  if (!dept) return null;
  return (
    <span className="badge badge-dept" title={`Department: ${dept}`}>
      {dept}
    </span>
  );
}

// Epic rollup badge: a single status-colored badge showing task progress.
// Modeled on RangeBadge but specific to epic-level rollup.
function EpicRollupBadge({ epic }) {
  const { task_count, done_count, status } = epic;
  let text;
  if (task_count === 0) {
    text = 'planned';
  } else if (done_count === task_count) {
    text = `${done_count} done`;
  } else {
    text = `${done_count}/${task_count}`;
  }
  return (
    <span className={`badge badge-ref badge-epic-rollup badge-${refBadgeClass(status)}`}>
      {text}
    </span>
  );
}

export default function RoadmapPanel({ roadmap }) {
  const [expandedEpics, setExpandedEpics] = useState(new Set());

  function toggleEpic(epicId) {
    setExpandedEpics(prev => {
      const next = new Set(prev);
      if (next.has(epicId)) {
        next.delete(epicId);
      } else {
        next.add(epicId);
      }
      return next;
    });
  }

  return (
    <div className="card">
      <h3>Roadmap</h3>
      <ol className="roadmap-list">
        {roadmap.map((item) => {
          const isLegacy = item.legacy === true;
          return (
            <li
              key={item.phase}
              className={`roadmap-item roadmap-${item.status}${isLegacy ? ' roadmap-legacy' : ''}`}
            >
              <div className="roadmap-header">
                <span className="roadmap-phase">Phase {item.phase}</span>
                <span className="roadmap-title">{item.title}</span>
                {item.warning && (
                  <span
                    className="badge badge-ref badge-ref-unresolved roadmap-cardinality-warning"
                    title={item.warning}
                  >
                    !
                  </span>
                )}
              </div>
              <p className="roadmap-deliverables">{item.deliverables}</p>
              {!isLegacy && item.epics && item.epics.length > 0 && (
                <ul className="roadmap-epics">
                  {item.epics.map((ep) => {
                    const epicKey = `${item.phase}-${ep.id}`;
                    const isExpanded = expandedEpics.has(epicKey);
                    const hasTasks = ep.tasks && ep.tasks.length > 0;
                    return (
                      <li key={ep.id} className="roadmap-epic-item">
                        <div className="roadmap-epic-header">
                          <span className="roadmap-epic-id">{ep.id}</span>
                          <span className="roadmap-epic-title">{ep.title}</span>
                          <span className="roadmap-epic-badges">
                            <DeptBadge dept={ep.dept} />
                            <EpicRollupBadge epic={ep} />
                            {ep.adrs && ep.adrs.map((r, i) => (
                              <RefBadge key={i} badge={r} />
                            ))}
                            {ep.warning && (
                              <span
                                className="badge badge-ref badge-ref-unresolved roadmap-cardinality-warning"
                                title={ep.warning}
                              >
                                !
                              </span>
                            )}
                            {ep.cross_dept_warning && (
                              <span
                                className="badge badge-ref badge-ref-unresolved roadmap-cardinality-warning"
                                title={ep.cross_dept_warning}
                              >
                                dept!
                              </span>
                            )}
                          </span>
                          {hasTasks && (
                            <button
                              className="roadmap-epic-toggle"
                              onClick={() => toggleEpic(epicKey)}
                              aria-expanded={isExpanded}
                              aria-label={isExpanded ? `Collapse ${ep.id}` : `Expand ${ep.id}`}
                            >
                              {isExpanded ? '▾' : '▸'}
                            </button>
                          )}
                        </div>
                        {isExpanded && hasTasks && (
                          <div className="roadmap-epic-tasks">
                            {ep.tasks.map((r, i) => (
                              <RefBadge key={i} badge={r} />
                            ))}
                          </div>
                        )}
                      </li>
                    );
                  })}
                </ul>
              )}
            </li>
          );
        })}
      </ol>
    </div>
  );
}
