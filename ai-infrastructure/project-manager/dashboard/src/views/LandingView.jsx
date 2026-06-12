import React from 'react';
import PulsePanel from '../panels/PulsePanel.jsx';
import RoadmapPanel from '../panels/RoadmapPanel.jsx';
import DepartmentsPanel from '../panels/DepartmentsPanel.jsx';
import ActivityPanel from '../panels/ActivityPanel.jsx';
import AgentsPanel from '../panels/AgentsPanel.jsx';

export default function LandingView({ data }) {
  // The project-manager coordinator is not in data.departments (which is the
  // ADR-021 department roster); assemble a roster row for it from the
  // coordinator workspace data so it heads the AI Roster.
  const pmDetails = data.workspace_details && data.workspace_details['project-manager'];
  const pmRow = pmDetails && {
    slug: data.coordinator.slug,
    domain: 'ai-infrastructure',
    exists: true,
    orchestrator_command: true,
    task_counts: pmDetails.task_counts,
  };
  const aiDepts = [
    ...(pmRow ? [pmRow] : []),
    ...data.departments.filter(d => d.domain === 'ai-infrastructure'),
  ];
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
        <AgentsPanel agents={data.agents} />
        <RoadmapPanel roadmap={data.roadmap} />
        <ActivityPanel activity={data.recent_activity} />
      </main>
    </div>
  );
}
