"""store profile images in postgresql

Revision ID: 20260516_0004
Revises: 20260516_0003
Create Date: 2026-05-16 11:40:00.000000

"""

import base64
import hashlib

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision = "20260516_0004"
down_revision = "20260516_0003"
branch_labels = None
depends_on = None


DEFAULT_PROFILE_IMAGE_ID = "11111111-1111-1111-1111-111111111111"
DEFAULT_PROFILE_IMAGE_STORAGE_KEY = "default-avatar-01"
DEFAULT_PROFILE_IMAGE_MIME_TYPE = "image/png"
DEFAULT_PROFILE_IMAGE_BASE64 = (
    "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVQIHWP4////fwAJ+wP9"
    "KobjigAAAABJRU5ErkJggg=="
)


def upgrade():
    op.create_table(
        "profile_images",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("storage_key", sa.String(length=64), nullable=True),
        sa.Column("storage_kind", sa.String(length=16), nullable=False),
        sa.Column("binary_data", sa.LargeBinary(), nullable=False),
        sa.Column("mime_type", sa.String(length=64), nullable=False),
        sa.Column("byte_size", sa.Integer(), nullable=False),
        sa.Column("checksum", sa.String(length=64), nullable=False),
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
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("storage_key"),
    )
    op.add_column(
        "players",
        sa.Column("avatar_image_id", postgresql.UUID(as_uuid=True), nullable=True),
    )
    op.create_foreign_key(
        "fk_players_avatar_image_id",
        "players",
        "profile_images",
        ["avatar_image_id"],
        ["id"],
    )

    binary_data = base64.b64decode(DEFAULT_PROFILE_IMAGE_BASE64)
    profile_images = sa.table(
        "profile_images",
        sa.column("id", postgresql.UUID(as_uuid=False)),
        sa.column("storage_key", sa.String(length=64)),
        sa.column("storage_kind", sa.String(length=16)),
        sa.column("binary_data", sa.LargeBinary()),
        sa.column("mime_type", sa.String(length=64)),
        sa.column("byte_size", sa.Integer()),
        sa.column("checksum", sa.String(length=64)),
    )
    op.bulk_insert(
        profile_images,
        [
            {
                "id": DEFAULT_PROFILE_IMAGE_ID,
                "storage_key": DEFAULT_PROFILE_IMAGE_STORAGE_KEY,
                "storage_kind": "default",
                "binary_data": binary_data,
                "mime_type": DEFAULT_PROFILE_IMAGE_MIME_TYPE,
                "byte_size": len(binary_data),
                "checksum": hashlib.sha256(binary_data).hexdigest(),
            }
        ],
    )

    op.alter_column("profile_images", "created_at", server_default=None)
    op.alter_column("profile_images", "updated_at", server_default=None)


def downgrade():
    op.drop_constraint("fk_players_avatar_image_id", "players", type_="foreignkey")
    op.drop_column("players", "avatar_image_id")
    op.drop_table("profile_images")
