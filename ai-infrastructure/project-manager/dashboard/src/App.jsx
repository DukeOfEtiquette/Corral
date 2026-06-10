import React, { useState, useEffect } from 'react';
import LandingView from './views/LandingView.jsx';
import WorkspaceView from './views/WorkspaceView.jsx';

function parseRoute(hash) {
  // Hash-based routing: "" -> landing, "#/workspace/<slug>" -> workspace detail
  if (!hash || hash === '#' || hash === '#/') {
    return { view: 'landing' };
  }
  const m = hash.match(/^#\/workspace\/(.+)$/);
  if (m) {
    return { view: 'workspace', slug: m[1] };
  }
  return { view: 'landing' };
}

export default function App() {
  const [data, setData] = useState(null);
  const [error, setError] = useState(null);
  const [route, setRoute] = useState(() => parseRoute(window.location.hash));

  useEffect(() => {
    fetch('./data.json')
      .then((r) => {
        if (!r.ok) throw new Error(`HTTP ${r.status}`);
        return r.json();
      })
      .then(setData)
      .catch((e) => setError(e.message));
  }, []);

  useEffect(() => {
    function onHashChange() {
      setRoute(parseRoute(window.location.hash));
    }
    window.addEventListener('hashchange', onHashChange);
    return () => window.removeEventListener('hashchange', onHashChange);
  }, []);

  if (error) {
    return (
      <div className="error-screen">
        <h2>Failed to load dashboard data</h2>
        <p>{error}</p>
        <p>Ensure the ETL ran successfully and data.json is present.</p>
      </div>
    );
  }

  if (!data) {
    return <div className="loading-screen">Loading...</div>;
  }

  if (route.view === 'workspace') {
    return <WorkspaceView data={data} slug={route.slug} />;
  }
  return <LandingView data={data} />;
}
