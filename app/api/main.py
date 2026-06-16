"""FastAPI application entry point for the Corral api service.

Exposes the FastAPI instance as `app` (imported by the test suite as
`from app.api.main import app as fastapi_app`).

Routes (all under the ADR-010 /api/v1 prefix):
  POST /api/v1/auth/login
  POST /api/v1/auth/logout
  GET  /api/v1/me

Admin seeding (ADR-006) runs via a FastAPI lifespan handler on startup.
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, Response
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from app.api import settings
from app.api.admin_seed import seed_admin
from app.api.auth import (
    create_session,
    delete_session,
    get_user_by_email,
    lookup_session,
    verify_password,
)


@asynccontextmanager
async def lifespan(application: FastAPI):
    seed_admin()
    yield


app = FastAPI(lifespan=lifespan)


class LoginRequest(BaseModel):
    email: str
    password: str


@app.post("/api/v1/auth/login")
def login(body: LoginRequest, response: Response):
    """Verify credentials, create a session row, set the session cookie."""
    user = get_user_by_email(body.email)
    if user is None:
        return JSONResponse(status_code=401, content={"detail": "Invalid credentials"})

    if not verify_password(body.password, user["password_hash"]):
        return JSONResponse(status_code=401, content={"detail": "Invalid credentials"})

    raw_session_id = create_session(user["id"])

    cookie_name = settings.get_cookie_name()
    cookie_secure = settings.get_cookie_secure()

    response.set_cookie(
        key=cookie_name,
        value=raw_session_id,
        httponly=True,
        samesite="lax",
        secure=cookie_secure,
    )
    return {"ok": True}


@app.post("/api/v1/auth/logout")
def logout(request: Request, response: Response):
    """Delete the session row and return 200."""
    cookie_name = settings.get_cookie_name()
    raw_cookie = request.cookies.get(cookie_name)
    if raw_cookie:
        delete_session(raw_cookie)
    return {"ok": True}


@app.get("/healthz")
def healthz():
    """Liveness probe: returns 200 with {"status": "ok"}, no auth, no DB access."""
    return {"status": "ok"}


@app.get("/api/v1/me")
def me(request: Request):
    """Return the authenticated user's identity, or 401."""
    cookie_name = settings.get_cookie_name()
    raw_cookie = request.cookies.get(cookie_name)
    if not raw_cookie:
        return JSONResponse(status_code=401, content={"detail": "Not authenticated"})

    user = lookup_session(raw_cookie)
    if user is None:
        return JSONResponse(status_code=401, content={"detail": "Not authenticated"})

    return {"id": user["id"], "email": user["email"], "display_name": user["display_name"]}
