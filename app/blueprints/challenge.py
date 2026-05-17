import secrets
from datetime import timezone
from flask import Blueprint, request
from app.extensions import db
from app.models.challenge import Challenge
from app.models.game_run import GameRun
from app.api.game_logic import utc_now
from app.api.responses import (
    CHALLENGE_INVALID,
    PARAM_ERROR,
    RUN_NOT_FOUND,
    error_response,
    success_response,
)
from app.api.serializers import serialize_challenge


challenge_bp = Blueprint("challenge", __name__, url_prefix="/api/v1/challenges")


def _generate_code(level_id):
    suffix = secrets.token_hex(3).upper()
    return f"NPC-{level_id}-{suffix}"


def _normalize_datetime(dt):
    if not dt:
        return None
    if dt.tzinfo is None:
        return dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc)


@challenge_bp.post("")
def create_challenge():
    data = request.get_json() or {}
    run_id = data.get("runId")
    if not run_id:
        return error_response(PARAM_ERROR, "缺少 runId")

    game_run = db.session.get(GameRun, run_id)
    if not game_run:
        return error_response(RUN_NOT_FOUND, "对局不存在", status=404)

    if game_run.status not in {"success", "fail", "finished"}:
        return error_response(PARAM_ERROR, "只有已结束对局才能生成挑战")

    level = game_run.level
    player = game_run.player
    challenge = Challenge(
        code=_generate_code(level.id),
        run_id=game_run.id,
        target_level_id=level.id,
        title=f"你能用更少的话让 {level.name} 放你进去吗？",
        description="挑战模式已生成，分享给好友即可参与。",
        share_title=f"我拿到了 {game_run.score} 分，你敢来试试吗？",
        creator_nickname=(player.nickname or "匿名玩家"),
        source_score=game_run.score,
    )
    db.session.add(challenge)
    db.session.commit()

    return success_response(serialize_challenge(challenge))


@challenge_bp.get("/<code>")
def get_challenge(code):
    challenge = Challenge.query.filter_by(code=code).first()
    if not challenge:
        return error_response(CHALLENGE_INVALID, "挑战码不存在", status=404)

    expires_at = _normalize_datetime(challenge.expires_at)
    if expires_at and expires_at <= utc_now():
        return error_response(CHALLENGE_INVALID, "挑战已过期", status=404)

    return success_response(serialize_challenge(challenge, include_creator=True))
