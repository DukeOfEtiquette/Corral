"""Tests for the api docs/OpenAPI endpoint exposure gate (COR-T-056, ADR-044).

ADR-044 (Option B) configures the three FastAPI documentation endpoints
explicitly instead of inheriting the framework default, and gates their exposure
by a single environment-driven setting:

  - /docs (Swagger UI), /redoc (ReDoc), /openapi.json (schema) are served at the
    ROOT (not relocated under /api/v1);
  - enabled in local/dev by default (no .env change needed);
  - disabled in remote (API_DOCS_ENABLED=false): all three return 404, via
    docs_url=None / redoc_url=None / openapi_url=None.

The gate is read at app construction (settings.get_docs_enabled()), so each test
builds a fresh app via the create_app() factory after setting (or clearing) the
API_DOCS_ENABLED env var. Docs endpoints touch no DB; the autouse auth-table
reset in conftest still requires DATABASE_URL (supplied by the api-test compose
service, ADR-003), consistent with the other api tests.

Run path is compose-only (ADR-003): these run under the existing api-test
one-shot service.
"""

import pytest
from httpx import ASGITransport, AsyncClient

from app.api.main import create_app

# The three documentation endpoints gated together (ADR-044).
DOCS_PATHS = ("/docs", "/redoc", "/openapi.json")


def _client_for(app):
    """An httpx client bound to a freshly-constructed app via ASGITransport
    (in-process, no network listener), mirroring the conftest `client` fixture
    but over a per-test app so the gate state is whatever this test pinned.
    """
    transport = ASGITransport(app=app)
    return AsyncClient(transport=transport, base_url="http://testserver")


@pytest.mark.asyncio
async def test_docs_served_by_default(monkeypatch):
    """(a) + (d): with no API_DOCS_ENABLED set (the local/dev default), all three
    documentation endpoints are served. The gate defaults to enabled, so local
    needs no .env change.
    """
    monkeypatch.delenv("API_DOCS_ENABLED", raising=False)
    app = create_app()
    async with _client_for(app) as client:
        for path in DOCS_PATHS:
            resp = await client.get(path)
            assert resp.status_code == 200, f"{path} should be served by default"


@pytest.mark.asyncio
async def test_docs_served_when_explicitly_enabled(monkeypatch):
    """(a): an explicit API_DOCS_ENABLED=true serves all three endpoints."""
    monkeypatch.setenv("API_DOCS_ENABLED", "true")
    app = create_app()
    async with _client_for(app) as client:
        for path in DOCS_PATHS:
            resp = await client.get(path)
            assert resp.status_code == 200, f"{path} should be served when enabled"


@pytest.mark.asyncio
async def test_docs_disabled_returns_404(monkeypatch):
    """(b): with API_DOCS_ENABLED=false (the remote setting), all three endpoints
    return 404 (docs_url/redoc_url/openapi_url are None).
    """
    monkeypatch.setenv("API_DOCS_ENABLED", "false")
    app = create_app()
    async with _client_for(app) as client:
        for path in DOCS_PATHS:
            resp = await client.get(path)
            assert resp.status_code == 404, f"{path} should be 404 when disabled"


@pytest.mark.asyncio
async def test_openapi_schema_is_well_formed_when_enabled(monkeypatch):
    """When enabled, /openapi.json returns a JSON OpenAPI document (not just any
    200). Pins that the schema endpoint actually serves the schema.
    """
    monkeypatch.delenv("API_DOCS_ENABLED", raising=False)
    app = create_app()
    async with _client_for(app) as client:
        resp = await client.get("/openapi.json")
        assert resp.status_code == 200
        body = resp.json()
        assert "openapi" in body, "the schema document declares its openapi version"
        assert "paths" in body, "the schema document lists the API paths"


@pytest.mark.asyncio
async def test_docs_are_at_root_not_under_api_v1(monkeypatch):
    """(c): the documentation endpoints stay at the ROOT and are NOT relocated
    under the /api/v1 prefix (ADR-044 keeps FastAPI's conventional root paths).
    The root paths answer 200; their /api/v1-prefixed counterparts do not exist.
    """
    monkeypatch.delenv("API_DOCS_ENABLED", raising=False)
    app = create_app()
    async with _client_for(app) as client:
        for path in DOCS_PATHS:
            root = await client.get(path)
            assert root.status_code == 200, f"{path} is served at the root"

            prefixed = await client.get(f"/api/v1{path}")
            assert prefixed.status_code == 404, (
                f"/api/v1{path} must not exist; docs stay at root, not under /api/v1"
            )


def test_get_docs_enabled_defaults_to_true(monkeypatch):
    """The settings accessor defaults to enabled so local/dev keeps docs on with
    no .env change; only an explicit API_DOCS_ENABLED=false disables them.
    """
    from app.api import settings

    monkeypatch.delenv("API_DOCS_ENABLED", raising=False)
    assert settings.get_docs_enabled() is True, "defaults to enabled"

    monkeypatch.setenv("API_DOCS_ENABLED", "false")
    assert settings.get_docs_enabled() is False, "explicit false disables"

    monkeypatch.setenv("API_DOCS_ENABLED", "true")
    assert settings.get_docs_enabled() is True, "explicit true enables"
