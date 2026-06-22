import React from 'react';

export default function ServicesPanel({ services }) {
  if (!services || services.length === 0) {
    return (
      <div className="card">
        <h3>Services</h3>
        <p>No services recorded.</p>
      </div>
    );
  }

  return (
    <div className="card">
      <h3>Services</h3>
      <div className="table-scroll">
        <table className="dept-table">
          <thead>
            <tr>
              <th>Service</th>
              <th>Domain</th>
              <th>Host:Port</th>
              <th>Endpoints</th>
              <th>Owner</th>
            </tr>
          </thead>
          <tbody>
            {services.map((svc) => {
              const isPlanned = svc.status === 'planned';
              const hasWarning = !!svc.warning;
              const rowClass = isPlanned
                ? 'dept-planned'
                : hasWarning
                ? 'dept-no-epic'
                : '';
              const rowTitle = hasWarning ? svc.warning : undefined;

              const hostPort = svc.host && svc.ports && svc.ports.length > 0
                ? svc.ports.map(p => `${svc.host}:${p}`).join(', ')
                : svc.host || '';

              const domainLabel = svc.domain === 1 ? '1 (web-app)' : svc.domain === 2 ? '2 (ai-infra)' : String(svc.domain ?? '');

              const hasBaseUrl = !!svc.base_url;

              const hostPortCell = hasBaseUrl
                ? (
                  <a href={svc.base_url} target="_blank" rel="noopener noreferrer">
                    {hostPort}
                  </a>
                )
                : hostPort;

              const endpointsCell = Array.isArray(svc.endpoints) && svc.endpoints.length > 0
                ? svc.endpoints.map((ep, i) => (
                  <span key={ep.path}>
                    {i > 0 ? ', ' : ''}
                    {hasBaseUrl
                      ? (
                        <a href={svc.base_url + ep.path} target="_blank" rel="noopener noreferrer">
                          {ep.path} ({ep.kind})
                        </a>
                      )
                      : `${ep.path} (${ep.kind})`
                    }
                  </span>
                ))
                : '';

              return (
                <tr
                  key={svc.id}
                  className={rowClass}
                  title={rowTitle}
                >
                  <td>
                    <span className="dept-link">{svc.name}</span>
                    {' '}
                    <span style={{ opacity: 0.6, fontSize: '0.85em' }}>({svc.id})</span>
                  </td>
                  <td>{domainLabel}</td>
                  <td>{hostPortCell}</td>
                  <td>{endpointsCell}</td>
                  <td>{svc.workspace}</td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>
    </div>
  );
}
