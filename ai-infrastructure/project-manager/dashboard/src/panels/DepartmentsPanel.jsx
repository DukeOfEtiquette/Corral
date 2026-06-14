import React from 'react';

export default function DepartmentsPanel({ departments, title }) {
  return (
    <div className="card">
      <h3>{title}</h3>
      <div className="table-scroll">
        <table className="dept-table">
          <thead>
            <tr>
              <th>Department</th>
              <th className="count">Backlog</th>
              <th className="count">In progress</th>
              <th className="count">Blocked</th>
              <th className="count">Done</th>
              <th className="count">Total</th>
            </tr>
          </thead>
          <tbody>
            {departments.map((dept) => {
              const isOrphaned = dept.exists && !dept.orchestrator_command;
              const isNoEpic = !!dept.no_epic_warning;
              const rowClass = !dept.exists
                ? 'dept-planned'
                : isOrphaned
                ? 'dept-orphaned'
                : isNoEpic
                ? 'dept-no-epic'
                : '';
              const rowTitle = isOrphaned
                ? '⚠ Department exists, orchestrator missing ⚠'
                : isNoEpic
                ? dept.no_epic_warning
                : undefined;
              return (
                <tr
                  key={dept.slug}
                  className={rowClass}
                  title={rowTitle}
                >
                  <td>
                    <a
                      href={`#/workspace/${dept.slug}`}
                      className="dept-link"
                    >
                      {dept.slug}
                    </a>
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
    </div>
  );
}
