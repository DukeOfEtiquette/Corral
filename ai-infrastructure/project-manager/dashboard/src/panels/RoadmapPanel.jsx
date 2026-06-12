import React from 'react';

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
            </div>
            <p className="roadmap-deliverables">{item.deliverables}</p>
            {item.milestones && item.milestones.length > 0 && (
              <ul className="roadmap-milestones">
                {item.milestones.map((ms) => (
                  <li key={ms.id} className="roadmap-milestone-item">
                    <span className="roadmap-milestone-id">{ms.id}</span>
                    <span className="roadmap-milestone-title">{ms.title}</span>
                    {ms.refs && ms.refs.length > 0 && (
                      <span className="roadmap-milestone-refs">
                        {ms.refs.map((r, i) => (
                          <RefBadge key={i} badge={r} />
                        ))}
                      </span>
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
