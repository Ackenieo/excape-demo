import uuid
from datetime import timedelta
from app.extensions import db
from app.api.game_logic import utc_now


def _default_expires_at():
    return utc_now() + timedelta(days=14)


class Challenge(db.Model):
    __tablename__ = "challenges"

    id = db.Column(db.Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    code = db.Column(db.String(64), nullable=False, unique=True, index=True)
    run_id = db.Column(db.Uuid(as_uuid=True), db.ForeignKey("game_runs.id"), nullable=False)
    target_level_id = db.Column(db.String(32), db.ForeignKey("levels.id"), nullable=False)
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text, nullable=False)
    share_title = db.Column(db.String(255), nullable=True)
    creator_nickname = db.Column(db.String(64), nullable=True)
    source_score = db.Column(db.Integer, nullable=False, default=0)
    expires_at = db.Column(db.DateTime, nullable=True, default=_default_expires_at)
    created_at = db.Column(db.DateTime, nullable=False, default=utc_now)

    run = db.relationship("GameRun", backref=db.backref("challenges", lazy=True))
    level = db.relationship("Level", backref=db.backref("challenges", lazy=True))

    def __repr__(self):
        return f"<Challenge {self.code}>"
