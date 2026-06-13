"""Index assertions for the v1 schema (DB-T-002).

Contract source: DB-T-001 kickoff "Indexes (pinned exactly)". Exactly these
seven explicit indexes exist, by name, and no other non-constraint index:

  ix_issues_status, ix_issues_assignee_id, ix_issues_parent_id,
  ix_issue_labels_label_id, ix_view_labels_label_id,
  ix_issue_comments_issue_id, ix_issue_events_issue_id

Beyond those seven, only the indexes that PK and UNIQUE constraints create
automatically may exist (DB-T-001: "no additional non-constraint indexes
beyond those seven plus the indexes the PK and UNIQUE constraints create
automatically"). An extra hand-created index, or a missing one, is a FINDING.
"""

import pytest

EXPECTED_EXPLICIT_INDEXES = {
    "ix_issues_status": ("issues", "status"),
    "ix_issues_assignee_id": ("issues", "assignee_id"),
    "ix_issues_parent_id": ("issues", "parent_id"),
    "ix_issue_labels_label_id": ("issue_labels", "label_id"),
    "ix_view_labels_label_id": ("view_labels", "label_id"),
    "ix_issue_comments_issue_id": ("issue_comments", "issue_id"),
    "ix_issue_events_issue_id": ("issue_events", "issue_id"),
}


def _all_indexes(cur):
    """Return {index_name: table_name} for every index in the public schema."""
    cur.execute(
        """
        select indexname, tablename
        from pg_indexes
        where schemaname = 'public'
        """
    )
    return {row[0]: row[1] for row in cur.fetchall()}


def _constraint_backed_index_names(cur):
    """Return the set of index names that back a PK or UNIQUE constraint
    (these are created automatically and are NOT the seven explicit indexes).
    """
    cur.execute(
        """
        select i.relname
        from pg_constraint c
        join pg_class i on i.oid = c.conindid
        join pg_class t on t.oid = c.conrelid
        join pg_namespace n on n.oid = t.relnamespace
        where n.nspname = 'public'
          and c.contype in ('p', 'u')
        """
    )
    return {row[0] for row in cur.fetchall()}


@pytest.mark.parametrize(
    "index_name,table,column",
    [
        pytest.param(name, t, c, id=name)
        for name, (t, c) in EXPECTED_EXPLICIT_INDEXES.items()
    ],
)
def test_explicit_index_exists(cur, index_name, table, column):
    """Each of the seven pinned indexes exists, by its exact name, on the
    expected table.
    """
    indexes = _all_indexes(cur)
    assert index_name in indexes, f"expected index '{index_name}' is missing"
    assert indexes[index_name] == table, (
        f"index '{index_name}' is on table '{indexes[index_name]}', "
        f"contract places it on '{table}'"
    )

    # Confirm the index covers the named column.
    cur.execute("select indexdef from pg_indexes where indexname = %s", (index_name,))
    row = cur.fetchone()
    assert row is not None, f"no indexdef for '{index_name}'"
    (indexdef,) = row
    assert column in indexdef, (
        f"index '{index_name}' does not cover column '{column}'; def={indexdef!r}"
    )


def test_no_unexpected_explicit_indexes(cur):
    """No non-constraint index exists beyond the seven pinned ones. Indexes
    that back a PK or UNIQUE constraint are created automatically and allowed;
    any other index is an extra the contract forbids (a FINDING).
    """
    all_indexes = set(_all_indexes(cur))
    constraint_backed = _constraint_backed_index_names(cur)
    explicit = set(EXPECTED_EXPLICIT_INDEXES)

    allowed = explicit | constraint_backed
    unexpected = all_indexes - allowed
    assert not unexpected, (
        f"unexpected non-constraint indexes present: {sorted(unexpected)}; "
        f"contract allows only the seven pinned indexes plus PK/UNIQUE-backed "
        f"indexes"
    )


def test_exactly_seven_explicit_indexes(cur):
    """Exactly the seven pinned explicit indexes are present (no more, no
    fewer), once the constraint-backed indexes are excluded.
    """
    all_indexes = set(_all_indexes(cur))
    constraint_backed = _constraint_backed_index_names(cur)
    non_constraint = all_indexes - constraint_backed
    assert non_constraint == set(EXPECTED_EXPLICIT_INDEXES), (
        "explicit (non-constraint) index set mismatch; "
        f"observed={sorted(non_constraint)}, "
        f"contract={sorted(EXPECTED_EXPLICIT_INDEXES)}"
    )
