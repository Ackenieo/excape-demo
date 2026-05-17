import uuid
from datetime import datetime, timezone
from sqlalchemy.dialects.postgresql import JSONB
from app.extensions import db

class GameRun(db.Model):
    __tablename__ = 'game_runs'

    id = db.Column(db.Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4)
    player_id = db.Column(db.Uuid(as_uuid=True), db.ForeignKey('players.id'), nullable=False)
    level_id = db.Column(db.String(32), db.ForeignKey('levels.id'), nullable=True)
    source_type = db.Column(db.String(16), nullable=False, default='level')
    custom_npc_id = db.Column(db.Uuid(as_uuid=True), db.ForeignKey('custom_npcs.id'), nullable=True)
    status = db.Column(db.String(16), nullable=False, default='playing')
    remaining_turns = db.Column(db.Integer, nullable=False)
    shake_value = db.Column(db.Integer, nullable=False, default=0)
    passed = db.Column(db.Boolean, nullable=False, default=False)
    passed_checkpoint_ids = db.Column(JSONB, nullable=False, default=list)
    passed_checkpoint_count = db.Column(db.Integer, nullable=False, default=0)
    score = db.Column(db.Integer, nullable=False, default=0)
    best_line = db.Column(db.Text, nullable=True)
    final_reply = db.Column(db.Text, nullable=True)
    snapshot_name = db.Column(db.String(64), nullable=True)
    snapshot_role = db.Column(db.String(128), nullable=True)
    snapshot_personality = db.Column(db.Text, nullable=True)
    snapshot_scene = db.Column(db.Text, nullable=True)
    snapshot_opening_message = db.Column(db.Text, nullable=True)
    snapshot_goal = db.Column(db.Text, nullable=True)
    snapshot_system_prompt = db.Column(db.Text, nullable=True)
    snapshot_checkpoints = db.Column(JSONB, nullable=True)
    snapshot_pass_threshold = db.Column(db.Integer, nullable=True)
    snapshot_success_token = db.Column(db.String(32), nullable=True)
    snapshot_max_turns = db.Column(db.Integer, nullable=True)
    snapshot_difficulty = db.Column(db.Integer, nullable=True)
    snapshot_base_score = db.Column(db.Integer, nullable=True)
    created_at = db.Column(db.DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))
    finished_at = db.Column(db.DateTime, nullable=True)

    # Relationships
    player = db.relationship('Player', backref=db.backref('game_runs', lazy=True))
    level = db.relationship('Level', backref=db.backref('game_runs', lazy=True))
    custom_npc = db.relationship('CustomNpc', backref=db.backref('game_runs', lazy=True))

    def __repr__(self):
        return f"<GameRun {self.id} - Level {self.level_id} - Status {self.status}>"
