"""Shared fixtures for the v1 schema characterization suite (DB-T-002).

These tests are authored BLIND to the migration implementation (ADR-016 TDD
phase 1, red). Every assertion is derived from the contract: the DB-T-001
pinned DDL specification and the ADRs it cites (ADR-012, ADR-011, ADR-025,
ADR-026, ADR-014). They assert the live schema via information_schema /
pg_catalog, so they validate the implementation against its intended design
rather than being catered to whatever the migration happened to build.

Run path is compose only (ADR-003): `docker compose run --rm test`.
"""

import os

import psycopg2
import pytest


@pytest.fixture(scope="session")
def db_url():
    """The Postgres connection string, supplied via the environment (ADR-006:
    secrets / connection strings via env only). The compose `test` service sets
    DATABASE_URL identically to the `migrate` service.
    """
    url = os.environ.get("DATABASE_URL")
    if not url:
        pytest.fail(
            "DATABASE_URL is not set; the compose `test` service must provide it"
        )
    return url


@pytest.fixture()
def conn(db_url):
    """A psycopg2 connection to the target database, rolled back and closed at
    the end of each test. Schema-shape tests are read-only against the catalog;
    autocommit is left off and nothing is committed.
    """
    connection = psycopg2.connect(db_url)
    try:
        yield connection
    finally:
        connection.rollback()
        connection.close()


@pytest.fixture()
def cur(conn):
    """A cursor over the per-test connection."""
    cursor = conn.cursor()
    try:
        yield cursor
    finally:
        cursor.close()
