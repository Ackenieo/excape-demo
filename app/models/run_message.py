import uuid
from app.extensions import db
from app.api.game_logic import utc_now


class RunMessage(db.Model):
    __tablename__ = "run_messages"

    id = db.Column(db.Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    run_id = db.Column(db.Uuid(as_uuid=True), db.ForeignKey("game_runs.id"), nullable=False, index=True)
    role = db.Column(db.String(16), nullable=False)
    content = db.Column(db.Text, nullable=False)
    turn_index = db.Column(db.Integer, nullable=True)
    shake_delta = db.Column(db.Integer, nullable=True)
    created_at = db.Column(db.DateTime, nullable=False, default=utc_now)

    run = db.relationship("GameRun", backref=db.backref("run_messages", lazy=True, order_by="RunMessage.created_at"))

    def __repr__(self):
        return f"<RunMessage {self.run_id} {self.role}>"
