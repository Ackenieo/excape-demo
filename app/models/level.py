from sqlalchemy.dialects.postgresql import JSONB
from app.extensions import db

class Level(db.Model):
    __tablename__ = 'levels'

    id = db.Column(db.String(32), primary_key=True)
    name = db.Column(db.String(64), nullable=False)
    difficulty = db.Column(db.Integer, nullable=False)
    scene = db.Column(db.Text, nullable=False)
    goal = db.Column(db.Text, nullable=False)
    max_turns = db.Column(db.Integer, nullable=False)
    base_score = db.Column(db.Integer, nullable=False)
    success_token = db.Column(db.String(32), nullable=False)
    opening_message = db.Column(db.Text, nullable=False)
    system_prompt = db.Column(db.Text, nullable=False)
    npc_checkpoints = db.Column(JSONB, nullable=False, default=list)
    pass_threshold = db.Column(db.Integer, nullable=False, default=1)
    status = db.Column(db.String(16), nullable=False, default='active')

    def __repr__(self):
        return f"<Level {self.id}: {self.name}>"
