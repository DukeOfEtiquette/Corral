"""Migration up/down round-trip assertion for the v1 baseline (DB-T-002).

Contract source: DB-T-001 kickoff (the baseline `downgrade()` is a clean drop)
and ADR-014 Consequence 5 ("the baseline downgrade is a clean drop"). The
round-trip contract:

  - after `alembic downgrade base`: NONE of the eleven contract tables exist;
  - after `alembic upgrade head`:   ALL eleven contract tables exist again.

IMPORTANT (authored blind, per ADR-016): this assertion is authored from the
contract, not from the migration. It inherently drives Alembic, so it is NOT
part of the test-designer's red check (the red check runs the schema-shape
tests against a fresh, non-migrated Postgres without running migrations). It is
validated by the Orchestrator's green run (`migrate` then `test` against the
migrated database).

The one-shot `test` compose image deliberately excludes the `alembic/`
directory and does not install Alembic (DB-T-001 Decision 5). When Alembic or
the migration project is not reachable from the runtime, this test SKIPS rather
than failing, so it never produces a false red and never blocks the schema
characterization suite. It exercises the round-trip only where the Alembic
project is present (the Orchestrator's green validation environment).
"""

import importlib.util
import os
import subprocess

import pytest

CONTRACT_TABLES = (
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
)

# Candidate working directory for the Alembic project, overridable by env.
ALEMBIC_PROJECT_DIR = os.environ.get("ALEMBIC_PROJECT_DIR", "/app/db")


def _alembic_available():
    """True only when the Alembic package is importable AND an alembic.ini is
    present in the project dir. Both are absent in the test-only image, so the
    round-trip test self-skips there.
    """
    if importlib.util.find_spec("alembic") is None:
        return False
    return os.path.isfile(os.path.join(ALEMBIC_PROJECT_DIR, "alembic.ini"))


pytestmark = pytest.mark.skipif(
    not _alembic_available(),
    reason=(
        "Alembic project not reachable in this runtime (expected in the "
        "test-only image); the round-trip is validated by the Orchestrator's "
        "green run, not the red check"
    ),
)


def _present_contract_tables(cur):
    cur.execute(
        """
        select table_name
        from information_schema.tables
        where table_schema = 'public' and table_type = 'BASE TABLE'
        """
    )
    present = {row[0] for row in cur.fetchall()}
    return present & set(CONTRACT_TABLES)


def _run_alembic(*args):
    subprocess.run(
        ["alembic", *args],
        cwd=ALEMBIC_PROJECT_DIR,
        check=True,
        capture_output=True,
        text=True,
    )


def test_baseline_downgrade_is_a_clean_drop_then_upgrade_restores(conn, cur):
    """`alembic downgrade base` drops all eleven contract tables; a subsequent
    `alembic upgrade head` recreates all eleven (ADR-014: clean-drop baseline).

    The test leaves the database migrated to head at the end so it does not
    disturb the rest of the suite's expectations.
    """
    # Down: after downgrade to base, none of the eleven contract tables exist.
    _run_alembic("downgrade", "base")
    conn.commit()
    after_down = _present_contract_tables(cur)
    conn.rollback()
    assert after_down == set(), (
        "after `alembic downgrade base`, no contract table should remain; "
        f"still present: {sorted(after_down)}"
    )

    # Up: after upgrade to head, all eleven contract tables exist again.
    _run_alembic("upgrade", "head")
    conn.commit()
    after_up = _present_contract_tables(cur)
    assert after_up == set(CONTRACT_TABLES), (
        "after `alembic upgrade head`, all eleven contract tables should exist; "
        f"missing: {sorted(set(CONTRACT_TABLES) - after_up)}"
    )
