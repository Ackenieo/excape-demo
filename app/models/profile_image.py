import uuid
from datetime import datetime, timezone

from app.extensions import db


class ProfileImage(db.Model):
    __tablename__ = "profile_images"

    id = db.Column(db.Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    storage_key = db.Column(db.String(64), nullable=True, unique=True)
    storage_kind = db.Column(db.String(16), nullable=False)
    binary_data = db.Column(db.LargeBinary, nullable=False)
    mime_type = db.Column(db.String(64), nullable=False)
    byte_size = db.Column(db.Integer, nullable=False)
    checksum = db.Column(db.String(64), nullable=False)
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

    def __repr__(self):
        return f"<ProfileImage {self.id} {self.storage_kind}>"
