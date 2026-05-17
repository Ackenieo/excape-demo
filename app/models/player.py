import uuid
from datetime import datetime, timezone
from app.extensions import db


class Player(db.Model):
    __tablename__ = "players"

    id = db.Column(db.Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    device_id = db.Column(db.String(64), nullable=False, unique=True)
    nickname = db.Column(db.String(32), nullable=True)
    avatar_url = db.Column(db.String(255), nullable=True)
    avatar_image_id = db.Column(
        db.Uuid(as_uuid=True),
        db.ForeignKey("profile_images.id"),
        nullable=True,
    )
    created_at = db.Column(db.DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(
        db.DateTime,
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )
    avatar_image = db.relationship("ProfileImage", foreign_keys=[avatar_image_id])

    def __repr__(self):
        return f"<Player {self.device_id}>"
