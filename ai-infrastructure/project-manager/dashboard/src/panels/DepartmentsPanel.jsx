import React from 'react';

export default function DepartmentsPanel({ departments }) {
  return (
    <div className="card">
      <h3>Department roster</h3>
      <table className="dept-table">
        <thead>
          <tr>
            <th>Department</th>
            <th>Domain</th>
            <th>Workspace</th>
            <th>Orchestrator</th>
            <th>Backlog</th>
            <th>In progress</th>
            <th>Blocked</th>
            <th>Done</th>
            <th>Total</th>
          </tr>
        </thead>
        <tbody>
          {departments.map((dept) => (
            <tr key={dept.slug} className={dept.exists ? '' : 'dept-planned'}>
              <td>
                <a
                  href={`#/workspace/${dept.slug}`}
                  className="dept-link"
                >
                  {dept.slug}
                </a>
              </td>
              <td>
                <span className={`domain-tag domain-${dept.domain.replace('-', '')}`}>
                  {dept.domain}
                </span>
              </td>
              <td>
                {dept.exists ? (
                  <span className="badge badge-exists">exists</span>
                ) : (
                  <span className="badge badge-planned">planned</span>
                )}
              </td>
              <td>
                {dept.orchestrator_command ? (
                  <span className="badge badge-exists">yes</span>
                ) : (
                  <span className="badge badge-missing">no</span>
                )}
              </td>
              <td className="count">{dept.task_counts.backlog}</td>
              <td className="count">{dept.task_counts['in-progress']}</td>
              <td className="count">{dept.task_counts.blocked}</td>
              <td className="count">{dept.task_counts.done}</td>
              <td className="count count-total">{dept.task_counts.total}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
