"""Column / type / nullability assertions for the v1 schema (DB-T-002).

Contract source: DB-T-001 kickoff "Decisions resolved by the Orchestrator",
the per-table DDL blocks, plus ADR-012 (core tables), ADR-011 (auth columns),
ADR-025 (issues.type, parent_id), ADR-026 (agent_credentials).

Conventions pinned by the contract ("Column and type conventions"):
  - every `id` PK is bigserial -> a `bigint` column backed by a sequence;
  - every timestamp column is `timestamptz not null`;
  - status / priority / type / kind are `text` (+ CHECK; see test_schema_checks);
  - jsonb for issue_events.payload.

information_schema.columns reports:
  - bigint            as data_type 'bigint'
  - text              as data_type 'text'
  - timestamptz       as data_type 'timestamp with time zone'
  - jsonb             as data_type 'jsonb'
  - is_nullable       as 'YES' / 'NO'
A bigserial column also has a column_default referencing nextval(...), which
test_id_columns_are_bigserial checks.
"""

import pytest

TS = "timestamp with time zone"  # timestamptz, as information_schema reports it

# Per-table expected columns: name -> (data_type, is_nullable_bool).
# is_nullable_bool True means the column is NULLABLE.
EXPECTED_COLUMNS = {
    "users": {
        "id": ("bigint", False),
        "display_name": ("text", False),
        "kind": ("text", False),
        "email": ("text", True),  # NULLABLE (null for machine rows)
        "password_hash": ("text", True),  # NULLABLE (null for machine rows)
        "created_at": (TS, False),
    },
    "agent_credentials": {
        "user_id": ("bigint", False),  # PK
        "api_key_hash": ("text", False),
        "created_at": (TS, False),
    },
    "issues": {
        "id": ("bigint", False),
        "title": ("text", False),
        "body": ("text", True),
        "status": ("text", False),
        "priority": ("text", False),
        "type": ("text", False),  # default 'task' (see test_schema_defaults)
        "parent_id": ("bigint", True),  # nullable self-reference
        "assignee_id": ("bigint", True),  # nullable
        "external_ref": ("text", True),  # nullable, unique
        "created_at": (TS, False),
        "updated_at": (TS, False),
    },
    "labels": {
        "id": ("bigint", False),
        "name": ("text", False),  # unique not null
        "color": ("text", True),
        "description": ("text", True),
    },
    "issue_labels": {
        "issue_id": ("bigint", False),
        "label_id": ("bigint", False),
    },
    "views": {
        "id": ("bigint", False),
        "name": ("text", False),  # unique not null
    },
    "view_labels": {
        "view_id": ("bigint", False),
        "label_id": ("bigint", False),
    },
    "issue_comments": {
        "id": ("bigint", False),
        "issue_id": ("bigint", False),
        "author_id": ("bigint", False),
        "body": ("text", False),
        "created_at": (TS, False),
    },
    "issue_events": {
        "id": ("bigint", False),
        "issue_id": ("bigint", False),
        "actor_id": ("bigint", False),
        "event_type": ("text", False),
        "payload": ("jsonb", False),
        "created_at": (TS, False),
    },
    "invites": {
        "id": ("bigint", False),
        "email": ("text", False),  # not null (contrast users.email)
        "token_hash": ("text", False),
        "expires_at": (TS, False),
        "consumed_at": (TS, True),  # nullable; null = unconsumed
        "created_by": ("bigint", True),  # references users(id); nullable
        "created_at": (TS, False),
    },
    "sessions": {
        "session_id": ("text", False),  # text PK
        "user_id": ("bigint", False),
        "expires_at": (TS, False),
        "created_at": (TS, False),
    },
}


def _columns(cur, table):
    """Return {column_name: (data_type, is_nullable_bool)} for a table."""
    cur.execute(
        """
        select column_name, data_type, is_nullable
        from information_schema.columns
        where table_schema = 'public' and table_name = %s
        """,
        (table,),
    )
    out = {}
    for name, data_type, is_nullable in cur.fetchall():
        out[name] = (data_type, is_nullable == "YES")
    return out


def _column_cases():
    for table, cols in EXPECTED_COLUMNS.items():
        for column, (data_type, nullable) in cols.items():
            yield pytest.param(table, column, data_type, nullable,
                               id=f"{table}.{column}")


@pytest.mark.parametrize("table,column,data_type,nullable", list(_column_cases()))
def test_column_type_and_nullability(cur, table, column, data_type, nullable):
    """Each contract column exists with the pinned type and nullability."""
    actual = _columns(cur, table)
    assert column in actual, f"{table}.{column} is missing"
    actual_type, actual_nullable = actual[column]
    assert actual_type == data_type, (
        f"{table}.{column} type is {actual_type!r}, contract requires {data_type!r}"
    )
    assert actual_nullable == nullable, (
        f"{table}.{column} nullability is "
        f"{'NULLABLE' if actual_nullable else 'NOT NULL'}, contract requires "
        f"{'NULLABLE' if nullable else 'NOT NULL'}"
    )


@pytest.mark.parametrize("table", sorted(EXPECTED_COLUMNS))
def test_no_unexpected_columns(cur, table):
    """A table carries exactly its contract columns and no others. An extra
    column the ADRs do not name is a FINDING (DB-T-001 forbids extra columns).
    """
    actual = set(_columns(cur, table))
    expected = set(EXPECTED_COLUMNS[table])
    extra = actual - expected
    assert not extra, f"{table} has unexpected columns: {sorted(extra)}"


# --- bigserial primary keys ------------------------------------------------

# Tables whose `id` PK is bigserial (a bigint backed by a sequence default).
BIGSERIAL_ID_TABLES = [
    "users",
    "issues",
    "labels",
    "views",
    "issue_comments",
    "issue_events",
    "invites",
]


@pytest.mark.parametrize("table", BIGSERIAL_ID_TABLES)
def test_id_columns_are_bigserial(cur, table):
    """Every `id` PK is bigserial: a bigint with a nextval(...) sequence
    default (DB-T-001 "Every id primary key is bigserial").
    """
    actual = _columns(cur, table)
    assert "id" in actual, f"{table}.id is missing"
    assert actual["id"][0] == "bigint", f"{table}.id is not bigint"

    cur.execute(
        """
        select column_default
        from information_schema.columns
        where table_schema = 'public' and table_name = %s and column_name = 'id'
        """,
        (table,),
    )
    (default,) = cur.fetchone()
    assert default is not None and "nextval" in default, (
        f"{table}.id has no sequence default (column_default={default!r}); "
        "bigserial requires a nextval() default"
    )


def test_agent_credentials_user_id_is_pk_bigint(cur):
    """agent_credentials.user_id is the primary key and is bigint (ADR-026:
    user_id is the PK, not a separate bigserial id).
    """
    actual = _columns(cur, "agent_credentials")
    assert actual.get("user_id", (None, None))[0] == "bigint"
    # No surrogate `id` column on agent_credentials.
    assert "id" not in actual, "agent_credentials must not carry a surrogate id"


def test_sessions_session_id_is_text_pk(cur):
    """sessions.session_id is a text PK (ADR-011: the opaque session id stored
    hashed at rest is the key).
    """
    actual = _columns(cur, "sessions")
    assert actual.get("session_id", (None, None))[0] == "text"
    assert "id" not in actual, "sessions must not carry a surrogate bigserial id"


def test_issue_events_payload_is_jsonb_not_null(cur):
    """issue_events.payload is jsonb NOT NULL (ADR-012)."""
    actual = _columns(cur, "issue_events")
    assert actual.get("payload") == ("jsonb", False), (
        "issue_events.payload must be jsonb NOT NULL"
    )
