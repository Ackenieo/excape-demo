"""add custom npcs and run snapshots

Revision ID: 20260516_0005
Revises: 20260516_0004
Create Date: 2026-05-16 13:20:00.000000

"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision = "20260516_0005"
down_revision = "20260516_0004"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "custom_npcs",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("player_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("name", sa.String(length=64), nullable=False),
        sa.Column("avatar_url", sa.String(length=255), nullable=True),
        sa.Column("role", sa.String(length=128), nullable=False),
        sa.Column("personality", sa.Text(), nullable=False),
        sa.Column("opening_message", sa.Text(), nullable=False),
        sa.Column("goal", sa.Text(), nullable=False),
        sa.Column("max_turns", sa.Integer(), nullable=False),
        sa.Column("difficulty", sa.Integer(), nullable=False),
        sa.Column("raw_system_prompt", sa.Text(), nullable=True),
        sa.Column("scene", sa.Text(), nullable=False),
        sa.Column("compiled_system_prompt", sa.Text(), nullable=False),
        sa.Column("npc_checkpoints", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("pass_threshold", sa.Integer(), nullable=False),
        sa.Column("success_token", sa.String(length=32), nullable=False),
        sa.Column("base_score", sa.Integer(), nullable=False),
        sa.Column("status", sa.String(length=16), nullable=False),
        sa.Column("moderation_status", sa.String(length=16), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(),
            nullable=False,
            server_default=sa.text("TIMEZONE('utc', NOW())"),
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(),
            nullable=False,
            server_default=sa.text("TIMEZONE('utc', NOW())"),
        ),
        sa.ForeignKeyConstraint(["player_id"], ["players.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_custom_npcs_player_id", "custom_npcs", ["player_id"], unique=False)

    op.add_column(
        "game_runs",
        sa.Column("source_type", sa.String(length=16), nullable=False, server_default="level"),
    )
    op.add_column(
        "game_runs",
        sa.Column("custom_npc_id", postgresql.UUID(as_uuid=True), nullable=True),
    )
    op.add_column("game_runs", sa.Column("snapshot_name", sa.String(length=64), nullable=True))
    op.add_column("game_runs", sa.Column("snapshot_role", sa.String(length=128), nullable=True))
    op.add_column("game_runs", sa.Column("snapshot_personality", sa.Text(), nullable=True))
    op.add_column("game_runs", sa.Column("snapshot_scene", sa.Text(), nullable=True))
    op.add_column("game_runs", sa.Column("snapshot_opening_message", sa.Text(), nullable=True))
    op.add_column("game_runs", sa.Column("snapshot_goal", sa.Text(), nullable=True))
    op.add_column("game_runs", sa.Column("snapshot_system_prompt", sa.Text(), nullable=True))
    op.add_column(
        "game_runs",
        sa.Column("snapshot_checkpoints", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
    )
    op.add_column("game_runs", sa.Column("snapshot_pass_threshold", sa.Integer(), nullable=True))
    op.add_column("game_runs", sa.Column("snapshot_success_token", sa.String(length=32), nullable=True))
    op.add_column("game_runs", sa.Column("snapshot_max_turns", sa.Integer(), nullable=True))
    op.add_column("game_runs", sa.Column("snapshot_difficulty", sa.Integer(), nullable=True))
    op.add_column("game_runs", sa.Column("snapshot_base_score", sa.Integer(), nullable=True))
    op.alter_column("game_runs", "level_id", existing_type=sa.String(length=32), nullable=True)
    op.create_foreign_key(
        "fk_game_runs_custom_npc_id",
        "game_runs",
        "custom_npcs",
        ["custom_npc_id"],
        ["id"],
    )
    op.alter_column("custom_npcs", "created_at", server_default=None)
    op.alter_column("custom_npcs", "updated_at", server_default=None)
    op.alter_column("game_runs", "source_type", server_default=None)


def downgrade():
    op.drop_constraint("fk_game_runs_custom_npc_id", "game_runs", type_="foreignkey")
    op.alter_column("game_runs", "level_id", existing_type=sa.String(length=32), nullable=False)
    op.drop_column("game_runs", "snapshot_base_score")
    op.drop_column("game_runs", "snapshot_difficulty")
    op.drop_column("game_runs", "snapshot_max_turns")
    op.drop_column("game_runs", "snapshot_success_token")
    op.drop_column("game_runs", "snapshot_pass_threshold")
    op.drop_column("game_runs", "snapshot_checkpoints")
    op.drop_column("game_runs", "snapshot_system_prompt")
    op.drop_column("game_runs", "snapshot_goal")
    op.drop_column("game_runs", "snapshot_opening_message")
    op.drop_column("game_runs", "snapshot_scene")
    op.drop_column("game_runs", "snapshot_personality")
    op.drop_column("game_runs", "snapshot_role")
    op.drop_column("game_runs", "snapshot_name")
    op.drop_column("game_runs", "custom_npc_id")
    op.drop_column("game_runs", "source_type")
    op.drop_index("ix_custom_npcs_player_id", table_name="custom_npcs")
    op.drop_table("custom_npcs")
