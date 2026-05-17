from sqlalchemy import case, func
from flask import Blueprint, request
from app.extensions import db
from app.models.game_run import GameRun
from app.models.player import Player
from app.models.level import Level
from app.api.responses import (
    PARAM_ERROR,
    LEVEL_NOT_FOUND,
    error_response,
    success_response,
)
from app.api.serializers import format_percentage, serialize_ranking_item


ranking_bp = Blueprint("ranking", __name__, url_prefix="/api/v1")


def _build_rankings(scope, level_id=None):
    query = (
        db.session.query(
            Player.nickname.label("nickname"),
            GameRun.score.label("score"),
            GameRun.level_id.label("level_id"),
        )
        .join(Player, Player.id == GameRun.player_id)
        .filter(GameRun.status.in_(["success", "fail", "finished"]))
        .order_by(GameRun.score.desc(), GameRun.created_at.asc())
    )

    if scope == "level":
        query = query.filter(GameRun.level_id == level_id)

    rows = query.limit(50).all()
    items = []
    for index, row in enumerate(rows, start=1):
        items.append(
            serialize_ranking_item(
                {
                    "nickname": row.nickname or "匿名玩家",
                    "score": row.score,
                    "levelId": row.level_id,
                    "rank": index,
                }
            )
        )
    return items


def _build_stats(level_id=None):
    query = db.session.query(
        func.count(GameRun.id),
        func.sum(case((GameRun.passed.is_(True), 1), else_=0)),
        func.avg(GameRun.score),
        func.max(GameRun.score),
    ).filter(GameRun.status.in_(["success", "fail", "finished"]))

    if level_id:
        query = query.filter(GameRun.level_id == level_id)

    play_count, pass_count, avg_score, best_score = query.one()
    play_count = int(play_count or 0)
    pass_count = int(pass_count or 0)
    pass_rate = (pass_count / play_count * 100.0) if play_count else 0.0
    return {
        "playCount": play_count,
        "passCount": pass_count,
        "passRate": format_percentage(pass_rate),
        "avgScore": round(float(avg_score or 0), 1),
        "bestScore": int(best_score or 0),
    }


@ranking_bp.get("/rankings")
def get_rankings():
    scope = request.args.get("scope", "overall")
    level_id = request.args.get("levelId")

    if scope not in {"overall", "level"}:
        return error_response(PARAM_ERROR, "scope 必须为 overall 或 level")

    if scope == "level":
        if not level_id:
            return error_response(PARAM_ERROR, "缺少 levelId")
        level = db.session.get(Level, level_id)
        if not level:
            return error_response(LEVEL_NOT_FOUND, "关卡不存在", status=404)

    items = _build_rankings(scope, level_id)
    stats = _build_stats(level_id if scope == "level" else None)
    return success_response({"overall": items, "stats": {
        "playCount": stats["playCount"],
        "passRate": stats["passRate"],
        "bestScore": stats["bestScore"],
    }})


@ranking_bp.get("/stats/<level_id>")
def get_level_stats(level_id):
    level = db.session.get(Level, level_id)
    if not level:
        return error_response(LEVEL_NOT_FOUND, "关卡不存在", status=404)

    stats = _build_stats(level_id)
    return success_response(
        {
            "levelId": level_id,
            "playCount": stats["playCount"],
            "passCount": stats["passCount"],
            "passRate": stats["passRate"],
            "avgScore": stats["avgScore"],
            "bestScore": stats["bestScore"],
        }
    )
