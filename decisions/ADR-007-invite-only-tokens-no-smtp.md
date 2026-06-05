---
schema_version: 1
adr: 7
title: "Invite-only users via admin-minted single-use tokens; no SMTP dependency"
status: "accepted"
date: "2026-06-05"
related_adrs: [6, 11]
supersedes: []
superseded_by: null
---

# ADR-007: Invite-only users via admin-minted single-use tokens; no SMTP dependency

## Context

The login system is invite-only, initiated by the web admin, with email as the invited user's identity. The open question was whether "invite by email" means the system must actually send email, which would add an SMTP dependency to every deployment of a tool whose portability is a hard requirement (ADR-003).

## Alternatives considered

### Option A: Invite links, no SMTP

The admin enters an email address on the admin page. The system mints a single-use invite token bound to that email, rendered as a link. The admin shares the link through any channel. Redeeming the link lets the invitee set a password for an account fixed to that email.

**Selected because:** email remains the identity anchor and the invite remains admin-initiated, with zero mail infrastructure. Confirmed with the user on 2026-06-05. Trade-off accepted: the admin manually delivers links.

### Option B: Real email delivery via SMTP

**Rejected for now because:** it requires SMTP configuration per deployment plus a dev mailcatcher service in compose; more moving parts than the use case needs. Designed to be addable later: delivery is a pluggable notifier on top of the same token flow, so adopting SMTP later changes delivery, not the invite model.

## Decision

User onboarding is by admin-minted, single-use, email-bound invite tokens shared manually as links. SMTP delivery is out of scope for v1 and is explicitly a pluggable later addition.

## Consequences

- No mail service in the compose topology (ADR-003 stays minimal).
- Token generation, expiry, and single-use enforcement become part of the auth design (ADR-011).
- The admin page (ADR-006) needs an invite-management view: mint, list, revoke.
- If SMTP is added later it wraps this flow; the token model does not change.
