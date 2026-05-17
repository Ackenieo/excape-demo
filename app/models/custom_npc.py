import uuid
from datetime import datetime, timezone

from sqlalchemy.dialects.postgresql import JSONB

from app.extensions import db


class CustomNpc(db.Model):
    __tablename__ = "custom_npcs"

    id = db.Column(db.Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    public_id = db.Column(db.String(32), nullable=False, unique=True, index=True)
    player_id = db.Column(
        db.Uuid(as_uuid=True),
        db.ForeignKey("players.id"),
        nullable=False,
        index=True,
    )
    name = db.Column(db.String(64), nullable=False)
    avatar_url = db.Column(db.String(255), nullable=True)
    role = db.Column(db.String(128), nullable=False)
    personality = db.Column(db.Text, nullable=False)
    opening_message = db.Column(db.Text, nullable=False)
    goal = db.Column(db.Text, nullable=False)
    max_turns = db.Column(db.Integer, nullable=False)
    difficulty = db.Column(db.Integer, nullable=False, default=3)
    raw_system_prompt = db.Column(db.Text, nullable=True)
    scene = db.Column(db.Text, nullable=False)
    compiled_system_prompt = db.Column(db.Text, nullable=False)
    npc_checkpoints = db.Column(JSONB, nullable=False, default=list)
    pass_threshold = db.Column(db.Integer, nullable=False)
    success_token = db.Column(db.String(32), nullable=False)
    base_score = db.Column(db.Integer, nullable=False, default=200)
    status = db.Column(db.String(16), nullable=False, default="active")
    moderation_status = db.Column(db.String(16), nullable=False, default="approved")
    created_at = db.Column(
        db.DateTime,
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )
    updated_at = db.Column(
        db.DateTime,
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    player = db.relationship("Player", backref=db.backref("custom_npcs", lazy=True))

    @property
    def external_npc_id(self):
        return self.public_id or str(self.id)

    def __repr__(self):
        return f"<CustomNpc {self.external_npc_id} {self.name}>"
