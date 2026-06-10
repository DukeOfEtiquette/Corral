import React from 'react';
import PulsePanel from '../panels/PulsePanel.jsx';
import RoadmapPanel from '../panels/RoadmapPanel.jsx';
import OrgChartPanel from '../panels/OrgChartPanel.jsx';
import DepartmentsPanel from '../panels/DepartmentsPanel.jsx';
import ActivityPanel from '../panels/ActivityPanel.jsx';

export default function LandingView({ data }) {
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
        <div className="two-col">
          <RoadmapPanel roadmap={data.roadmap} />
          <OrgChartPanel orgChart={data.org_chart} />
        </div>
        <DepartmentsPanel departments={data.departments} />
        <ActivityPanel activity={data.recent_activity} />
      </main>
    </div>
  );
}
