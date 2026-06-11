import React from 'react';
import PulsePanel from '../panels/PulsePanel.jsx';
import RoadmapPanel from '../panels/RoadmapPanel.jsx';
import DepartmentsPanel from '../panels/DepartmentsPanel.jsx';
import ActivityPanel from '../panels/ActivityPanel.jsx';

export default function LandingView({ data }) {
  const aiDepts = data.departments.filter(d => d.domain === 'ai-infrastructure');
  const webDepts = data.departments.filter(d => d.domain === 'web-app');
  return (
    <div className="layout">
      <header className="site-header">
        <div className="header-inner">
          <span className="header-logo">Corral</span>
          <span className="header-title">Project Manager Dashboard</span>
          <span className="header-source">
            source: {data.meta.source}
          </span>
        </div>
      </header>
      <main className="main-content">
        <PulsePanel meta={data.meta} coordinator={data.coordinator} />
        <div className="roster-row">
          <DepartmentsPanel departments={aiDepts} title="AI Roster" />
          <DepartmentsPanel departments={webDepts} title="Web App Roster" />
        </div>
        <RoadmapPanel roadmap={data.roadmap} />
        <ActivityPanel activity={data.recent_activity} />
      </main>
    </div>
  );
}
