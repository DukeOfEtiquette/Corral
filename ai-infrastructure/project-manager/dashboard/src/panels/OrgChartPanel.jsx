import React from 'react';

export default function OrgChartPanel({ orgChart }) {
  return (
    <div className="card">
      <h3>Org chart</h3>
      <pre className="org-chart">{orgChart}</pre>
    </div>
  );
}
