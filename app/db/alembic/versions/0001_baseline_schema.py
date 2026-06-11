"""Baseline v1 schema: eleven tables

Revision ID: 0001
Revises:
Create Date: 2026-06-11

Sources:
  ADR-012: core tables (issues, labels, issue_labels, views, view_labels,
           issue_comments, issue_events, minimal users)
  ADR-025: epic columns (issues.type, issues.parent_id)
  ADR-011: auth delta (users.email/password_hash, invites, sessions)
  ADR-026: machine-user identity (users.kind discriminator, agent_credentials)
  ADR-014: Alembic with hand-written migrations, single baseline revision,
           no ORM, no autogenerate

DDL is fully pinned by the kickoff. Invariants for epics (at-most-one parent,
children-are-tasks, epics-not-nested) and machine/human user column rules are
API-enforced (ADR-010), not DB-enforced. No triggers, no cross-table CHECKs.
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import JSONB

# revision identifiers, used by Alembic.
revision: str = "0001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # -------------------------------------------------------------------------
    # users
    # ADR-012 minimal + ADR-011 auth delta + ADR-026 kind discriminator
    # -------------------------------------------------------------------------
    op.create_table(
        "users",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("display_name", sa.Text(), nullable=False),
        sa.Column("kind", sa.Text(), nullable=False),
        sa.Column("email", sa.Text(), nullable=True),
        sa.Column("password_hash", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.CheckConstraint("kind in ('human', 'machine')", name=None),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("email"),
    )

    # -------------------------------------------------------------------------
    # agent_credentials (ADR-026: separate table, one row per machine user)
    # api_key_hash: hashed at rest (ADR-026 / ADR-011 hashed-at-rest posture)
    # -------------------------------------------------------------------------
    op.create_table(
        "agent_credentials",
        sa.Column("user_id", sa.BigInteger(), nullable=False),
        sa.Column("api_key_hash", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("user_id"),
    )

    # -------------------------------------------------------------------------
    # issues
    # ADR-012 DDL + ADR-025 epic columns (type, parent_id) folded into CREATE
    # status/priority/type use text + CHECK (no native Postgres ENUMs, ADR-012)
    # -------------------------------------------------------------------------
    op.create_table(
        "issues",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("title", sa.Text(), nullable=False),
        sa.Column("body", sa.Text(), nullable=True),
        sa.Column("status", sa.Text(), nullable=False),
        sa.Column("priority", sa.Text(), nullable=False),
        sa.Column("type", sa.Text(), server_default="task", nullable=False),
        sa.Column("parent_id", sa.BigInteger(), nullable=True),
        sa.Column("assignee_id", sa.BigInteger(), nullable=True),
        sa.Column("external_ref", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.CheckConstraint(
            "status in ('backlog', 'in-progress', 'blocked', 'done')",
            name=None,
        ),
        sa.CheckConstraint(
            "priority in ('P0', 'P1', 'P2', 'P3')",
            name=None,
        ),
        sa.CheckConstraint(
            "type in ('task', 'epic')",
            name=None,
        ),
        sa.ForeignKeyConstraint(["assignee_id"], ["users.id"]),
        sa.ForeignKeyConstraint(["parent_id"], ["issues.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("external_ref"),
    )

    # -------------------------------------------------------------------------
    # labels (ADR-012; taxonomy/reserved families owned by ADR-018, not here)
    # -------------------------------------------------------------------------
    op.create_table(
        "labels",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("name", sa.Text(), nullable=False),
        sa.Column("color", sa.Text(), nullable=True),
        sa.Column("description", sa.Text(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("name"),
    )

    # -------------------------------------------------------------------------
    # issue_labels join table (ADR-012)
    # -------------------------------------------------------------------------
    op.create_table(
        "issue_labels",
        sa.Column("issue_id", sa.BigInteger(), nullable=False),
        sa.Column("label_id", sa.BigInteger(), nullable=False),
        sa.ForeignKeyConstraint(["issue_id"], ["issues.id"]),
        sa.ForeignKeyConstraint(["label_id"], ["labels.id"]),
        sa.PrimaryKeyConstraint("issue_id", "label_id"),
    )

    # -------------------------------------------------------------------------
    # views (ADR-012; per-view column config deferred to ADR-017)
    # -------------------------------------------------------------------------
    op.create_table(
        "views",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("name", sa.Text(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("name"),
    )

    # -------------------------------------------------------------------------
    # view_labels join table (ADR-012; AND-match semantics, vacuous = all)
    # -------------------------------------------------------------------------
    op.create_table(
        "view_labels",
        sa.Column("view_id", sa.BigInteger(), nullable=False),
        sa.Column("label_id", sa.BigInteger(), nullable=False),
        sa.ForeignKeyConstraint(["label_id"], ["labels.id"]),
        sa.ForeignKeyConstraint(["view_id"], ["views.id"]),
        sa.PrimaryKeyConstraint("view_id", "label_id"),
    )

    # -------------------------------------------------------------------------
    # issue_comments (ADR-012; user comments + imported activity-log lines)
    # -------------------------------------------------------------------------
    op.create_table(
        "issue_comments",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("issue_id", sa.BigInteger(), nullable=False),
        sa.Column("author_id", sa.BigInteger(), nullable=False),
        sa.Column("body", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["author_id"], ["users.id"]),
        sa.ForeignKeyConstraint(["issue_id"], ["issues.id"]),
        sa.PrimaryKeyConstraint("id"),
    )

    # -------------------------------------------------------------------------
    # issue_events (ADR-012; structured app-generated activity; payload is jsonb)
    # -------------------------------------------------------------------------
    op.create_table(
        "issue_events",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("issue_id", sa.BigInteger(), nullable=False),
        sa.Column("actor_id", sa.BigInteger(), nullable=False),
        sa.Column("event_type", sa.Text(), nullable=False),
        sa.Column("payload", JSONB(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["actor_id"], ["users.id"]),
        sa.ForeignKeyConstraint(["issue_id"], ["issues.id"]),
        sa.PrimaryKeyConstraint("id"),
    )

    # -------------------------------------------------------------------------
    # invites (ADR-011: invite-token mechanics)
    # token_hash: hashed at rest (never plaintext, ADR-011)
    # -------------------------------------------------------------------------
    op.create_table(
        "invites",
        sa.Column("id", sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column("email", sa.Text(), nullable=False),
        sa.Column("token_hash", sa.Text(), nullable=False),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("consumed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_by", sa.BigInteger(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["created_by"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
    )

    # -------------------------------------------------------------------------
    # sessions (ADR-011: server-side session store)
    # session_id: stores the opaque identifier HASHED at rest (same
    #   bearer-secret posture as invite tokens and api keys, ADR-011)
    # Revocation is a row delete.
    # -------------------------------------------------------------------------
    op.create_table(
        "sessions",
        sa.Column("session_id", sa.Text(), nullable=False),
        sa.Column("user_id", sa.BigInteger(), nullable=False),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("session_id"),
    )

    # -------------------------------------------------------------------------
    # Indexes (exactly the seven pinned in the kickoff; named ix_{table}_{col})
    # PK, UNIQUE, and FK constraint indexes are created automatically above.
    # -------------------------------------------------------------------------
    op.create_index("ix_issues_status", "issues", ["status"])
    op.create_index("ix_issues_assignee_id", "issues", ["assignee_id"])
    op.create_index("ix_issues_parent_id", "issues", ["parent_id"])
    op.create_index("ix_issue_labels_label_id", "issue_labels", ["label_id"])
    op.create_index("ix_view_labels_label_id", "view_labels", ["label_id"])
    op.create_index("ix_issue_comments_issue_id", "issue_comments", ["issue_id"])
    op.create_index("ix_issue_events_issue_id", "issue_events", ["issue_id"])


def downgrade() -> None:
    # Drop in reverse dependency order (indexes first, then tables leaf-to-root)
    op.drop_index("ix_issue_events_issue_id", table_name="issue_events")
    op.drop_index("ix_issue_comments_issue_id", table_name="issue_comments")
    op.drop_index("ix_view_labels_label_id", table_name="view_labels")
    op.drop_index("ix_issue_labels_label_id", table_name="issue_labels")
    op.drop_index("ix_issues_parent_id", table_name="issues")
    op.drop_index("ix_issues_assignee_id", table_name="issues")
    op.drop_index("ix_issues_status", table_name="issues")

    op.drop_table("sessions")
    op.drop_table("invites")
    op.drop_table("issue_events")
    op.drop_table("issue_comments")
    op.drop_table("view_labels")
    op.drop_table("views")
    op.drop_table("issue_labels")
    op.drop_table("labels")
    op.drop_table("issues")
    op.drop_table("agent_credentials")
    op.drop_table("users")
