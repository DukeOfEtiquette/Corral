import React, { useState, useEffect } from 'react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import TaskCountsPanel from '../panels/TaskCountsPanel.jsx';

export default function WorkspaceView({ data, slug }) {
  const detail = data.workspace_details[slug];

  return (
    <div className="layout">
      <header className="site-header">
        <div className="header-inner">
          <a href="#/" className="back-link">&larr; Overview</a>
          <span className="header-logo">Corral</span>
          <span className="header-title">
            {detail ? detail.header.display_name : slug}
          </span>
        </div>
      </header>
      <main className="main-content">
        {!detail ? (
          <div className="card">
            <p>No data found for workspace: <strong>{slug}</strong></p>
          </div>
        ) : detail.header.planned ? (
          <PlannedDeptStub detail={detail} />
        ) : (
          <WorkspaceDetailFull detail={detail} />
        )}
      </main>
    </div>
  );
}

function PlannedDeptStub({ detail }) {
  const h = detail.header;
  return (
    <div className="card">
      <div className="card-header">
        <h2>{h.display_name}</h2>
        <span className="badge badge-planned">Planned</span>
      </div>
      <p className="muted">
        This department has not been created yet. It is on the ADR-021 blessed
        roster and will be stamped out using the create-department recipe when
        sustained work warrants it.
      </p>
      <dl className="detail-list">
        <dt>Domain</dt><dd>{h.domain}</dd>
        <dt>Label</dt><dd><code>dept:{h.slug}</code></dd>
      </dl>
      <TaskCountsPanel counts={detail.task_counts} />
    </div>
  );
}

function AdrModal({ adr, onClose }) {
  useEffect(() => {
    const handler = (e) => { if (e.key === 'Escape') onClose(); };
    document.addEventListener('keydown', handler);
    return () => document.removeEventListener('keydown', handler);
  }, [onClose]);

  return (
    <div className="adr-modal" role="dialog" aria-modal="true" aria-label={adr.title}>
      <div className="adr-modal-backdrop" onClick={onClose} />
      <div className="adr-modal-content">
        <div className="adr-modal-header">
          <div className="adr-modal-header-info">
            <span className="adr-modal-id">ADR-{String(adr.adr).padStart(3, '0')}</span>
            <span className="adr-modal-title">{adr.title}</span>
            <span className={`badge badge-adr-${adr.status}`}>{adr.status}</span>
            {adr.date && <span className="adr-modal-date muted">{adr.date}</span>}
          </div>
          <button
            type="button"
            className="adr-modal-close"
            onClick={onClose}
            aria-label="Close"
          >&times;</button>
        </div>
        <div className="adr-modal-body">
          <div className="md-rendered">
            <ReactMarkdown remarkPlugins={[remarkGfm]}>
              {adr.body || ''}
            </ReactMarkdown>
          </div>
        </div>
      </div>
    </div>
  );
}

function WorkspaceDetailFull({ detail }) {
  const h = detail.header;
  const [selectedAdr, setSelectedAdr] = useState(null);

  return (
    <>
      <div className="card">
        <div className="card-header">
          <h2>{h.display_name}</h2>
          <div className="badge-row">
            <span className="badge badge-role">{h.role}</span>
            <span className="badge badge-domain">{h.domain}</span>
            {h.phase != null && (
              <span className="badge badge-phase">Phase {h.phase}</span>
            )}
          </div>
        </div>
        <dl className="detail-list">
          <dt>Slug</dt><dd>{h.slug}</dd>
          <dt>Last updated</dt><dd>{h.last_updated || 'unknown'}</dd>
        </dl>
        <TaskCountsPanel counts={detail.task_counts} />
      </div>

      {detail.recent_updates && detail.recent_updates.length > 0 && (
        <div className="card">
          <h3>Recent updates</h3>
          <ol className="activity-list">
            {detail.recent_updates.map((u, i) => (
              <li key={i} className="activity-item">
                <span className="activity-date">{u.date}</span>
                <span className="activity-text">{u.text}</span>
              </li>
            ))}
          </ol>
        </div>
      )}

      {detail.observations_count != null && (
        <div className="card">
          <h3>Observations</h3>
          <p>
            <span className="count-badge">{detail.observations_count}</span>
            {detail.observations_count === 1 ? ' observation' : ' observations'} logged
          </p>
        </div>
      )}

      {detail.adrs && detail.adrs.length > 0 && (
        <div className="card">
          <h3>Decision records ({detail.adrs.length})</h3>
          <table className="adrs-table">
            <thead>
              <tr>
                <th>ADR</th>
                <th>Title</th>
                <th>Status</th>
                <th>Date</th>
              </tr>
            </thead>
            <tbody>
              {detail.adrs.map((adr) => (
                <tr key={adr.adr}>
                  <td className="adr-num">ADR-{String(adr.adr).padStart(3, '0')}</td>
                  <td>
                    <button
                      type="button"
                      className="adr-title-btn"
                      onClick={() => setSelectedAdr(adr)}
                    >
                      {adr.title}
                    </button>
                  </td>
                  <td>
                    <span className={`badge badge-adr-${adr.status}`}>
                      {adr.status}
                    </span>
                  </td>
                  <td className="muted">{adr.date}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {selectedAdr && (
        <AdrModal adr={selectedAdr} onClose={() => setSelectedAdr(null)} />
      )}
    </>
  );
}
