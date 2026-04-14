"""Initial AVERT schema."""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa


revision = "20260407_0001"
down_revision = None
branch_labels = None
depends_on = None


def _has_table(table_name: str) -> bool:
    return table_name in sa.inspect(op.get_bind()).get_table_names()


def _has_index(table_name: str, index_name: str) -> bool:
    if not _has_table(table_name):
        return False
    indexes = sa.inspect(op.get_bind()).get_indexes(table_name)
    return any(index["name"] == index_name for index in indexes)


def _drop_index_if_exists(table_name: str, index_name: str) -> None:
    if _has_index(table_name, index_name):
        op.drop_index(index_name, table_name=table_name)


def _drop_table_if_exists(table_name: str) -> None:
    if _has_table(table_name):
        op.drop_table(table_name)


def upgrade() -> None:
    if not _has_table("narratives"):
        op.create_table(
            "narratives",
            sa.Column("id", sa.String(length=64), nullable=False),
            sa.Column("name", sa.String(length=255), nullable=False),
            sa.Column("state", sa.String(length=32), nullable=False),
            sa.Column("thesis", sa.Text(), nullable=False),
            sa.Column("topic_rank", sa.Integer(), nullable=False),
            sa.Column("rank_delta", sa.Integer(), nullable=False),
            sa.Column("internal_velocity", sa.Integer(), nullable=False),
            sa.Column("flow_acceleration", sa.Integer(), nullable=False),
            sa.Column("breadth", sa.Integer(), nullable=False),
            sa.Column("price_expansion", sa.Integer(), nullable=False),
            sa.Column("persistence", sa.Integer(), nullable=False),
            sa.Column("risk_heat", sa.Integer(), nullable=False),
            sa.Column("capital_demand", sa.Integer(), nullable=False),
            sa.Column("token_strip", sa.JSON(), nullable=False),
            sa.Column("stage_bias", sa.String(length=24), nullable=False),
            sa.Column("evidence", sa.JSON(), nullable=False),
            sa.Column(
                "created_at",
                sa.DateTime(timezone=True),
                server_default=sa.text("CURRENT_TIMESTAMP"),
                nullable=False,
            ),
            sa.Column(
                "updated_at",
                sa.DateTime(timezone=True),
                server_default=sa.text("CURRENT_TIMESTAMP"),
                nullable=False,
            ),
            sa.PrimaryKeyConstraint("id"),
        )

    if not _has_table("candidate_tokens"):
        op.create_table(
            "candidate_tokens",
            sa.Column("id", sa.String(length=64), nullable=False),
            sa.Column("narrative_id", sa.String(length=64), nullable=False),
            sa.Column("symbol", sa.String(length=32), nullable=False),
            sa.Column("name", sa.String(length=255), nullable=False),
            sa.Column("investability_score", sa.Integer(), nullable=False),
            sa.Column("leadership_score", sa.Integer(), nullable=False),
            sa.Column("liquidity_score", sa.Integer(), nullable=False),
            sa.Column("toxicity_penalty", sa.Integer(), nullable=False),
            sa.Column("scout_size", sa.String(length=32), nullable=False),
            sa.Column("overlap_narratives", sa.JSON(), nullable=False),
            sa.Column("price_expansion_5m", sa.String(length=32), nullable=False),
            sa.Column("breadth_signal", sa.Text(), nullable=False),
            sa.Column("protected_exit", sa.JSON(), nullable=False),
            sa.Column("note", sa.Text(), nullable=False),
            sa.PrimaryKeyConstraint("id"),
        )
    if not _has_index("candidate_tokens", "ix_candidate_tokens_narrative_id"):
        op.create_index("ix_candidate_tokens_narrative_id", "candidate_tokens", ["narrative_id"], unique=False)

    if not _has_table("allocation_plans"):
        op.create_table(
            "allocation_plans",
            sa.Column("narrative_id", sa.String(length=64), nullable=False),
            sa.Column("budget", sa.JSON(), nullable=False),
            sa.Column("gates", sa.JSON(), nullable=False),
            sa.Column("protected_exit", sa.JSON(), nullable=False),
            sa.PrimaryKeyConstraint("narrative_id"),
        )

    if not _has_table("positions"):
        op.create_table(
            "positions",
            sa.Column("id", sa.String(length=64), nullable=False),
            sa.Column("narrative_id", sa.String(length=64), nullable=False),
            sa.Column("symbol", sa.String(length=32), nullable=False),
            sa.Column("stage", sa.String(length=24), nullable=False),
            sa.Column("size", sa.String(length=32), nullable=False),
            sa.Column("average_basis", sa.String(length=32), nullable=False),
            sa.Column("pnl", sa.String(length=32), nullable=False),
            sa.Column("status_note", sa.Text(), nullable=False),
            sa.Column("next_action", sa.Text(), nullable=False),
            sa.Column("stage_progress", sa.JSON(), nullable=False),
            sa.Column("protected_exit", sa.JSON(), nullable=False),
            sa.PrimaryKeyConstraint("id"),
        )
    if not _has_index("positions", "ix_positions_narrative_id"):
        op.create_index("ix_positions_narrative_id", "positions", ["narrative_id"], unique=False)

    if not _has_table("policy_evaluations"):
        op.create_table(
            "policy_evaluations",
            sa.Column("id", sa.String(length=64), nullable=False),
            sa.Column("narrative_id", sa.String(length=64), nullable=False),
            sa.Column("candidate_id", sa.String(length=64), nullable=False),
            sa.Column("target_stage", sa.String(length=24), nullable=False),
            sa.Column("allowed", sa.String(length=8), nullable=False),
            sa.Column("gates", sa.JSON(), nullable=False),
            sa.Column(
                "created_at",
                sa.DateTime(timezone=True),
                server_default=sa.text("CURRENT_TIMESTAMP"),
                nullable=False,
            ),
            sa.PrimaryKeyConstraint("id"),
        )
    if not _has_index("policy_evaluations", "ix_policy_evaluations_candidate_id"):
        op.create_index("ix_policy_evaluations_candidate_id", "policy_evaluations", ["candidate_id"], unique=False)
    if not _has_index("policy_evaluations", "ix_policy_evaluations_narrative_id"):
        op.create_index("ix_policy_evaluations_narrative_id", "policy_evaluations", ["narrative_id"], unique=False)

    if not _has_table("execution_intents"):
        op.create_table(
            "execution_intents",
            sa.Column("id", sa.String(length=64), nullable=False),
            sa.Column("candidate_id", sa.String(length=64), nullable=False),
            sa.Column("mode", sa.String(length=16), nullable=False),
            sa.Column("provider", sa.String(length=64), nullable=False),
            sa.Column("status", sa.String(length=24), nullable=False),
            sa.Column("protected_exit", sa.JSON(), nullable=False),
            sa.Column("message", sa.Text(), nullable=False),
            sa.Column(
                "created_at",
                sa.DateTime(timezone=True),
                server_default=sa.text("CURRENT_TIMESTAMP"),
                nullable=False,
            ),
            sa.PrimaryKeyConstraint("id"),
        )
    if not _has_index("execution_intents", "ix_execution_intents_candidate_id"):
        op.create_index("ix_execution_intents_candidate_id", "execution_intents", ["candidate_id"], unique=False)

    if not _has_table("execution_requests"):
        op.create_table(
            "execution_requests",
            sa.Column("id", sa.String(length=64), nullable=False),
            sa.Column("app_mode", sa.String(length=16), nullable=False),
            sa.Column("narrative_id", sa.String(length=64), nullable=False),
            sa.Column("candidate_id", sa.String(length=64), nullable=False),
            sa.Column("target_stage", sa.String(length=24), nullable=False),
            sa.Column("decision", sa.String(length=255), nullable=False),
            sa.Column("execution_mode", sa.String(length=32), nullable=False),
            sa.Column("lifecycle_phase", sa.String(length=24), nullable=False),
            sa.Column("lifecycle_status", sa.String(length=24), nullable=False),
            sa.Column("provider", sa.String(length=64), nullable=False),
            sa.Column("route", sa.String(length=64), nullable=False),
            sa.Column("slippage", sa.String(length=32), nullable=False),
            sa.Column("protected_exit", sa.JSON(), nullable=False),
            sa.Column("message", sa.Text(), nullable=False),
            sa.Column("failure_reason", sa.Text(), nullable=True),
            sa.Column("request_payload", sa.JSON(), nullable=False),
            sa.Column("response_payload", sa.JSON(), nullable=False),
            sa.Column(
                "created_at",
                sa.DateTime(timezone=True),
                server_default=sa.text("CURRENT_TIMESTAMP"),
                nullable=False,
            ),
            sa.Column(
                "updated_at",
                sa.DateTime(timezone=True),
                server_default=sa.text("CURRENT_TIMESTAMP"),
                nullable=False,
            ),
            sa.PrimaryKeyConstraint("id"),
        )
    if not _has_index("execution_requests", "ix_execution_requests_candidate_id"):
        op.create_index("ix_execution_requests_candidate_id", "execution_requests", ["candidate_id"], unique=False)
    if not _has_index("execution_requests", "ix_execution_requests_narrative_id"):
        op.create_index("ix_execution_requests_narrative_id", "execution_requests", ["narrative_id"], unique=False)

    if not _has_table("execution_events"):
        op.create_table(
            "execution_events",
            sa.Column("id", sa.String(length=64), nullable=False),
            sa.Column("execution_request_id", sa.String(length=64), nullable=False),
            sa.Column("lifecycle_phase", sa.String(length=24), nullable=False),
            sa.Column("lifecycle_status", sa.String(length=24), nullable=False),
            sa.Column("message", sa.Text(), nullable=False),
            sa.Column("payload", sa.JSON(), nullable=False),
            sa.Column(
                "created_at",
                sa.DateTime(timezone=True),
                server_default=sa.text("CURRENT_TIMESTAMP"),
                nullable=False,
            ),
            sa.PrimaryKeyConstraint("id"),
        )
    if not _has_index("execution_events", "ix_execution_events_execution_request_id"):
        op.create_index(
            "ix_execution_events_execution_request_id",
            "execution_events",
            ["execution_request_id"],
            unique=False,
        )

    if not _has_table("journal_entries"):
        op.create_table(
            "journal_entries",
            sa.Column("id", sa.String(length=64), nullable=False),
            sa.Column("timestamp", sa.String(length=32), nullable=False),
            sa.Column("narrative_id", sa.String(length=64), nullable=False),
            sa.Column("title", sa.String(length=255), nullable=False),
            sa.Column("stage", sa.String(length=24), nullable=False),
            sa.Column("verdict", sa.String(length=16), nullable=False),
            sa.Column("summary", sa.Text(), nullable=False),
            sa.Column("evidence", sa.JSON(), nullable=False),
            sa.PrimaryKeyConstraint("id"),
        )
    if not _has_index("journal_entries", "ix_journal_entries_narrative_id"):
        op.create_index("ix_journal_entries_narrative_id", "journal_entries", ["narrative_id"], unique=False)

    if not _has_table("replay_sessions"):
        op.create_table(
            "replay_sessions",
            sa.Column("id", sa.String(length=64), nullable=False),
            sa.Column("narrative_id", sa.String(length=64), nullable=False),
            sa.Column("title", sa.String(length=255), nullable=False),
            sa.Column("result", sa.String(length=255), nullable=False),
            sa.Column("snapshots", sa.JSON(), nullable=False),
            sa.PrimaryKeyConstraint("id"),
        )
    if not _has_index("replay_sessions", "ix_replay_sessions_narrative_id"):
        op.create_index("ix_replay_sessions_narrative_id", "replay_sessions", ["narrative_id"], unique=False)


def downgrade() -> None:
    _drop_index_if_exists("replay_sessions", "ix_replay_sessions_narrative_id")
    _drop_table_if_exists("replay_sessions")
    _drop_index_if_exists("journal_entries", "ix_journal_entries_narrative_id")
    _drop_table_if_exists("journal_entries")
    _drop_index_if_exists("execution_events", "ix_execution_events_execution_request_id")
    _drop_table_if_exists("execution_events")
    _drop_index_if_exists("execution_requests", "ix_execution_requests_narrative_id")
    _drop_index_if_exists("execution_requests", "ix_execution_requests_candidate_id")
    _drop_table_if_exists("execution_requests")
    _drop_index_if_exists("execution_intents", "ix_execution_intents_candidate_id")
    _drop_table_if_exists("execution_intents")
    _drop_index_if_exists("policy_evaluations", "ix_policy_evaluations_narrative_id")
    _drop_index_if_exists("policy_evaluations", "ix_policy_evaluations_candidate_id")
    _drop_table_if_exists("policy_evaluations")
    _drop_index_if_exists("positions", "ix_positions_narrative_id")
    _drop_table_if_exists("positions")
    _drop_table_if_exists("allocation_plans")
    _drop_index_if_exists("candidate_tokens", "ix_candidate_tokens_narrative_id")
    _drop_table_if_exists("candidate_tokens")
    _drop_table_if_exists("narratives")
