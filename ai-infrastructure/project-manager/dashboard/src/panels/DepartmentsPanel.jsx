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
            <th>Backlog</th>
            <th>In progress</th>
            <th>Blocked</th>
            <th>Done</th>
            <th>Total</th>
          </tr>
        </thead>
        <tbody>
          {departments.map((dept) => {
            const isOrphaned = dept.exists && !dept.orchestrator_command;
            const rowClass = !dept.exists
              ? 'dept-planned'
              : isOrphaned
              ? 'dept-orphaned'
              : '';
            return (
              <tr
                key={dept.slug}
                className={rowClass}
                title={isOrphaned ? '⚠ Department exists, orchestrator missing ⚠' : undefined}
              >
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
                <td className="count">{dept.task_counts.backlog}</td>
                <td className="count">{dept.task_counts['in-progress']}</td>
                <td className="count">{dept.task_counts.blocked}</td>
                <td className="count">{dept.task_counts.done}</td>
                <td className="count count-total">{dept.task_counts.total}</td>
              </tr>
            );
          })}
        </tbody>
      </table>
    </div>
  );
}
