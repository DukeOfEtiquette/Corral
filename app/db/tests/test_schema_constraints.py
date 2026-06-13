"""Foreign-key, UNIQUE, primary-key, and default assertions (DB-T-002).

Contract source: DB-T-001 kickoff DDL plus ADR-012 / ADR-011 / ADR-025 /
ADR-026.

Foreign keys (DB-T-001 "FK relations"):
  issues.parent_id      -> issues.id        (self-referential)
  issues.assignee_id    -> users.id
  agent_credentials.user_id -> users.id
  issue_labels.issue_id -> issues.id ; issue_labels.label_id -> labels.id
  view_labels.view_id   -> views.id  ; view_labels.label_id  -> labels.id
  issue_comments.issue_id -> issues.id ; issue_comments.author_id -> users.id
  issue_events.issue_id -> issues.id ; issue_events.actor_id -> users.id
  invites.created_by    -> users.id
  sessions.user_id      -> users.id

UNIQUE (DB-T-001 "UNIQUE constraints"):
  users.email, labels.name, views.name, issues.external_ref

Composite primary keys:
  issue_labels (issue_id, label_id)
  view_labels  (view_id, label_id)

Default: issues.type defaults to 'task' (ADR-025).
"""

import pytest

# (table, column, ref_table, ref_column)
EXPECTED_FKS = [
    ("issues", "parent_id", "issues", "id"),
    ("issues", "assignee_id", "users", "id"),
    ("agent_credentials", "user_id", "users", "id"),
    ("issue_labels", "issue_id", "issues", "id"),
    ("issue_labels", "label_id", "labels", "id"),
    ("view_labels", "view_id", "views", "id"),
    ("view_labels", "label_id", "labels", "id"),
    ("issue_comments", "issue_id", "issues", "id"),
    ("issue_comments", "author_id", "users", "id"),
    ("issue_events", "issue_id", "issues", "id"),
    ("issue_events", "actor_id", "users", "id"),
    ("invites", "created_by", "users", "id"),
    ("sessions", "user_id", "users", "id"),
]

# (table, column) carrying a UNIQUE constraint (non-PK).
EXPECTED_UNIQUE = [
    ("users", "email"),
    ("labels", "name"),
    ("views", "name"),
    ("issues", "external_ref"),
]

# (table, [pk columns in any order])
EXPECTED_PKS = {
    "users": ["id"],
    "agent_credentials": ["user_id"],
    "issues": ["id"],
    "labels": ["id"],
    "issue_labels": ["issue_id", "label_id"],
    "views": ["id"],
    "view_labels": ["view_id", "label_id"],
    "issue_comments": ["id"],
    "issue_events": ["id"],
    "invites": ["id"],
    "sessions": ["session_id"],
}


def _foreign_keys(cur):
    """Return a set of (table, column, ref_table, ref_column) tuples for every
    single-column FK in the public schema.
    """
    cur.execute(
        """
        select
            tc.table_name,
            kcu.column_name,
            ccu.table_name as ref_table,
            ccu.column_name as ref_column
        from information_schema.table_constraints tc
        join information_schema.key_column_usage kcu
            on kcu.constraint_name = tc.constraint_name
           and kcu.table_schema = tc.table_schema
        join information_schema.constraint_column_usage ccu
            on ccu.constraint_name = tc.constraint_name
           and ccu.table_schema = tc.table_schema
        where tc.constraint_type = 'FOREIGN KEY'
          and tc.table_schema = 'public'
        """
    )
    return {tuple(row) for row in cur.fetchall()}


@pytest.mark.parametrize(
    "table,column,ref_table,ref_column",
    [
        pytest.param(t, c, rt, rc, id=f"{t}.{c}->{rt}.{rc}")
        for (t, c, rt, rc) in EXPECTED_FKS
    ],
)
def test_foreign_key_exists(cur, table, column, ref_table, ref_column):
    """Each contract FK exists, pointing at the contract referent."""
    fks = _foreign_keys(cur)
    assert (table, column, ref_table, ref_column) in fks, (
        f"FK {table}.{column} -> {ref_table}.{ref_column} is missing; "
        f"observed FKs on {table}: "
        f"{sorted(fk for fk in fks if fk[0] == table)}"
    )


def test_issues_parent_id_is_self_referential(cur):
    """issues.parent_id is the self-referential FK to issues.id (ADR-025)."""
    fks = _foreign_keys(cur)
    assert ("issues", "parent_id", "issues", "id") in fks, (
        "issues.parent_id must reference issues.id (self-referential epic link)"
    )


def _unique_columns(cur):
    """Return a set of (table, column) for single-column UNIQUE constraints
    (constraint_type UNIQUE; PKs are reported separately and excluded).
    """
    cur.execute(
        """
        select tc.table_name, kcu.column_name
        from information_schema.table_constraints tc
        join information_schema.key_column_usage kcu
            on kcu.constraint_name = tc.constraint_name
           and kcu.table_schema = tc.table_schema
        where tc.constraint_type = 'UNIQUE'
          and tc.table_schema = 'public'
        """
    )
    return {tuple(row) for row in cur.fetchall()}


@pytest.mark.parametrize(
    "table,column",
    [pytest.param(t, c, id=f"{t}.{c}") for (t, c) in EXPECTED_UNIQUE],
)
def test_unique_constraint_exists(cur, table, column):
    """Each contract UNIQUE constraint exists."""
    uniques = _unique_columns(cur)
    assert (table, column) in uniques, (
        f"UNIQUE constraint on {table}.{column} is missing; "
        f"observed unique columns: {sorted(uniques)}"
    )


def _primary_key_columns(cur, table):
    cur.execute(
        """
        select kcu.column_name
        from information_schema.table_constraints tc
        join information_schema.key_column_usage kcu
            on kcu.constraint_name = tc.constraint_name
           and kcu.table_schema = tc.table_schema
        where tc.constraint_type = 'PRIMARY KEY'
          and tc.table_schema = 'public'
          and tc.table_name = %s
        """,
        (table,),
    )
    return sorted(row[0] for row in cur.fetchall())


@pytest.mark.parametrize(
    "table,pk_columns",
    [pytest.param(t, cols, id=t) for t, cols in EXPECTED_PKS.items()],
)
def test_primary_key_columns(cur, table, pk_columns):
    """Each table's primary key is exactly the contract column set. Covers the
    composite PKs on issue_labels (issue_id, label_id) and view_labels
    (view_id, label_id), and the text PK on sessions.
    """
    assert _primary_key_columns(cur, table) == sorted(pk_columns), (
        f"{table} PK columns mismatch; "
        f"observed={_primary_key_columns(cur, table)}, "
        f"contract={sorted(pk_columns)}"
    )


def test_issues_type_defaults_to_task(cur):
    """issues.type defaults to 'task' (ADR-025: default 'task' backfills every
    row so the column is non-null from the first migration).
    """
    cur.execute(
        """
        select column_default
        from information_schema.columns
        where table_schema = 'public'
          and table_name = 'issues'
          and column_name = 'type'
        """
    )
    row = cur.fetchone()
    assert row is not None, "issues.type column is missing"
    (default,) = row
    assert default is not None and "'task'" in default, (
        f"issues.type default must be 'task'; observed column_default={default!r}"
    )
