"""CHECK-constraint and no-native-ENUM assertions for the v1 schema (DB-T-002).

Contract source: DB-T-001 kickoff DDL plus ADR-012 (status / priority text +
CHECK; the explicit no-native-ENUM choice) and ADR-025 (issues.type CHECK,
default 'task') and ADR-026 (users.kind CHECK).

The four CHECK columns and their exact allowed-value sets:
  users.kind      in ('human', 'machine')
  issues.status   in ('backlog', 'in-progress', 'blocked', 'done')
  issues.priority in ('P0', 'P1', 'P2', 'P3')
  issues.type     in ('task', 'epic')   (default 'task')

These are `text` + CHECK, NOT native Postgres ENUM types (ADR-012's explicit
choice). test_no_native_enum_types asserts the negative.
"""

import pytest

# (table, column) -> the exact set of allowed values the CHECK must permit.
CHECK_VALUE_SETS = {
    ("users", "kind"): {"human", "machine"},
    ("issues", "status"): {"backlog", "in-progress", "blocked", "done"},
    ("issues", "priority"): {"P0", "P1", "P2", "P3"},
    ("issues", "type"): {"task", "epic"},
}


def _check_clauses_for_column(cur, table, column):
    """Return the list of CHECK clause source texts that reference `column`
    on `table`. Uses pg_catalog to read the constraint definition text, which
    captures the literal allowed-value list regardless of the generated
    constraint name (DB-T-001 pins default constraint names).
    """
    cur.execute(
        """
        select pg_get_constraintdef(c.oid)
        from pg_constraint c
        join pg_class t on t.oid = c.conrelid
        join pg_namespace n on n.oid = t.relnamespace
        where n.nspname = 'public'
          and t.relname = %s
          and c.contype = 'c'
        """,
        (table,),
    )
    clauses = [row[0] for row in cur.fetchall()]
    return [clause for clause in clauses if column in clause]


@pytest.mark.parametrize(
    "table,column,allowed",
    [
        pytest.param(t, col, vals, id=f"{t}.{col}")
        for (t, col), vals in CHECK_VALUE_SETS.items()
    ],
)
def test_check_constraint_allowed_values(cur, table, column, allowed):
    """Each CHECK column has a constraint whose clause names exactly the
    contract's allowed-value set. Each expected literal must appear; an
    unexpected literal in the clause is a divergence.
    """
    clauses = _check_clauses_for_column(cur, table, column)
    assert clauses, f"no CHECK constraint references {table}.{column}"
    combined = " ".join(clauses)

    for value in allowed:
        assert f"'{value}'" in combined, (
            f"{table}.{column} CHECK does not permit '{value}'; "
            f"clause(s)={clauses}"
        )

    # No allowed value outside the contract set may appear as a quoted literal
    # in the CHECK clause. This catches a widened or altered enumeration.
    import re

    literals = set(re.findall(r"'([^']*)'", combined))
    unexpected = literals - allowed
    assert not unexpected, (
        f"{table}.{column} CHECK permits unexpected values {sorted(unexpected)}; "
        f"contract set is {sorted(allowed)}"
    )


def test_no_native_enum_types(cur):
    """No native Postgres ENUM type exists. status / priority / type / kind are
    text + CHECK (ADR-012's explicit choice); a native ENUM is a contract
    divergence.
    """
    cur.execute(
        """
        select t.typname
        from pg_type t
        join pg_namespace n on n.oid = t.typnamespace
        where t.typtype = 'e' and n.nspname = 'public'
        """
    )
    enums = [row[0] for row in cur.fetchall()]
    assert not enums, f"native ENUM types present (must be text+CHECK): {enums}"
