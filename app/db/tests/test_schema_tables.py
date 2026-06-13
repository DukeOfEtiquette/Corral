"""Table-inventory assertions for the v1 schema (DB-T-002).

Contract source: DB-T-001 kickoff "Decisions resolved by the Orchestrator"
(the eleven-table baseline) and ADR-014 (single Alembic baseline `0001`).

The eleven tables (DB-T-001 "Auth scope is FULL"):
  users, agent_credentials, issues, labels, issue_labels, views,
  view_labels, issue_comments, issue_events, invites, sessions.

Beyond those eleven, only Alembic's own version table (alembic_version,
ADR-014) may exist; no other table is permitted.
"""

import pytest

EXPECTED_TABLES = {
    "users",
    "agent_credentials",
    "issues",
    "labels",
    "issue_labels",
    "views",
    "view_labels",
    "issue_comments",
    "issue_events",
    "invites",
    "sessions",
}

# Alembic maintains its own version-tracking table (ADR-014); it is the only
# table allowed beyond the eleven contract tables.
ALEMBIC_VERSION_TABLE = "alembic_version"


def _public_tables(cur):
    cur.execute(
        """
        select table_name
        from information_schema.tables
        where table_schema = 'public'
          and table_type = 'BASE TABLE'
        """
    )
    return {row[0] for row in cur.fetchall()}


@pytest.mark.parametrize("table", sorted(EXPECTED_TABLES))
def test_expected_table_exists(cur, table):
    """Each of the eleven contract tables exists in the public schema."""
    assert table in _public_tables(cur), f"expected table '{table}' is missing"


def test_no_unexpected_tables(cur):
    """No table exists beyond the eleven contract tables plus Alembic's
    version table. An extra table is a contract divergence (a FINDING),
    never a reason to relax this assertion.
    """
    allowed = EXPECTED_TABLES | {ALEMBIC_VERSION_TABLE}
    actual = _public_tables(cur)
    unexpected = actual - allowed
    assert not unexpected, f"unexpected tables present: {sorted(unexpected)}"


def test_exactly_eleven_contract_tables(cur):
    """Exactly eleven contract tables exist (no more, no fewer)."""
    actual = _public_tables(cur)
    present_contract = actual & EXPECTED_TABLES
    assert present_contract == EXPECTED_TABLES, (
        "contract table set mismatch; "
        f"missing={sorted(EXPECTED_TABLES - actual)}, "
        f"present={sorted(present_contract)}"
    )
