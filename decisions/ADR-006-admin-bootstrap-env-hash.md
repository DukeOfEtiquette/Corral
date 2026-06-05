---
schema_version: 1
adr: 6
title: "Admin user seeded from an env-supplied password hash, never from source"
status: "accepted"
date: "2026-06-05"
related_adrs: [3, 7, 11]
supersedes: []
superseded_by: null
---

# ADR-006: Admin user seeded from an env-supplied password hash, never from source

## Context

The app must ship with a built-in admin user who has access to an admin-only page (user invites, future administration). The admin password cannot appear in the source tree for security reasons. The user's initial idea was to generate the password hash locally and paste it into a settings file built with the project.

## Alternatives considered

### Option A: Gitignored .env with ADMIN_EMAIL and ADMIN_PASSWORD_HASH, seeded at first boot

The operator generates a password hash locally (bcrypt or argon2; finalized with ADR-011), places it in a gitignored `.env` file alongside `ADMIN_EMAIL`, and docker compose injects it. On startup the server seeds the admin row if and only if no admin exists.

**Selected because:** it keeps the same spirit as the user's idea (hash generated locally, never plaintext in the deployment) while using the compose-native `.env` mechanism, keeping the secret out of any built artifact and out of git by a single ignore rule. Confirmed with the user on 2026-06-05.

### Option B: Hash pasted into a settings file built with the project (original idea)

**Rejected because:** functionally similar but riskier; the settings file must be carefully excluded from version control and rebuilt per deployment, and a file that ships inside the build artifact is easier to leak than runtime-injected environment.

### Option C: First-run setup page (no seed; first visitor creates the admin)

**Rejected because:** cleanest for sharing, but adds an unauthenticated bootstrap flow that must itself be built and secured; more surface than the project needs at this stage. Worth revisiting if central-server deployment makes `.env` handling awkward.

## Decision

Admin credentials are supplied via a gitignored `.env` file (`ADMIN_EMAIL`, `ADMIN_PASSWORD_HASH`) read by docker compose. The server seeds the admin account on first boot when absent. No credential material ever enters the source tree; a committed `.env.example` documents the variable names only.

## Consequences

- `.gitignore` must exclude `.env` and variants before any other file lands (done in this iteration).
- The hash algorithm and verification flow are finalized with the auth mechanism decision (ADR-011).
- Operators of new deployments have a one-time local step: generate hash, write `.env`.
- Agents are barred from writing secrets or hashes into tracked files (rule recorded in `./CLAUDE.md`).
