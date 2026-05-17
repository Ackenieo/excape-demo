from sqlalchemy import case, func

from app.extensions import db
from app.models.game_run import GameRun
from app.models.level import Level
from app.models.player import Player


TERMINAL_RUN_STATUSES = {"success", "fail", "finished"}
RECENT_RUN_LIMIT = 5
ACHIEVEMENT_SCORE_THRESHOLD = 500
INVALID_NICKNAME_VALUES = {"", "null", "undefined", "none", "匿名玩家", "游客"}

ACHIEVEMENT_DEFINITIONS = [
    {
        "id": "ach_first_pass",
        "title": "初出茅庐",
        "description": "首次通关任意关卡",
    },
    {
        "id": "ach_two_turns",
        "title": "一针见血",
        "description": "2 句话内通关任意关卡",
    },
    {
        "id": "ach_score_breaker",
        "title": "分数破局者",
        "description": f"累计总分达到 {ACHIEVEMENT_SCORE_THRESHOLD} 分",
    },
    {
        "id": "ach_debug_master",
        "title": "真实潜入者",
        "description": "在非调试关卡完成至少一次通关",
    },
]


def get_player_by_device_id(device_id):
    return Player.query.filter_by(device_id=device_id).first()


def normalize_nickname(value):
    if value is None or not isinstance(value, str):
        return None
    normalized = value.strip()
    if not normalized:
        return None
    if len(normalized) < 2 or len(normalized) > 16:
        return None
    if normalized.lower() in INVALID_NICKNAME_VALUES or normalized in INVALID_NICKNAME_VALUES:
        return None
    return normalized


def build_profile_stats(player_id):
    play_count, pass_count, total_score = (
        db.session.query(
            func.count(GameRun.id),
            func.sum(case((GameRun.passed.is_(True), 1), else_=0)),
            func.sum(GameRun.score),
        )
        .filter(
            GameRun.player_id == player_id,
            GameRun.status.in_(TERMINAL_RUN_STATUSES),
        )
        .one()
    )
    play_count = int(play_count or 0)
    pass_count = int(pass_count or 0)
    total_score = int(total_score or 0)
    return {
        "play_count": play_count,
        "passed_count": pass_count,
        "total_score": total_score,
    }


def build_recent_runs(player_id):
    rows = (
        db.session.query(
            GameRun.id.label("run_id"),
            Level.name.label("level_name"),
            GameRun.status.label("status"),
            GameRun.passed.label("passed"),
            GameRun.score.label("score"),
            GameRun.created_at.label("created_at"),
        )
        .join(Level, Level.id == GameRun.level_id)
        .filter(
            GameRun.player_id == player_id,
            GameRun.status.in_(TERMINAL_RUN_STATUSES),
        )
        .order_by(GameRun.created_at.desc())
        .limit(RECENT_RUN_LIMIT)
        .all()
    )
    items = []
    for row in rows:
        result = "success" if row.status == "success" or row.passed else "fail"
        items.append(
            {
                "runId": str(row.run_id),
                "levelName": row.level_name,
                "result": result,
                "score": int(row.score or 0),
                "createdAt": row.created_at,
            }
        )
    return items


def build_rank_text(player_id):
    total_score_expr = func.coalesce(func.sum(GameRun.score), 0)
    passed_count_expr = func.coalesce(
        func.sum(case((GameRun.passed.is_(True), 1), else_=0)),
        0,
    )
    first_terminal_expr = func.min(func.coalesce(GameRun.finished_at, GameRun.created_at))
    rows = (
        db.session.query(
            Player.id.label("player_id"),
            total_score_expr.label("total_score"),
            passed_count_expr.label("passed_count"),
            first_terminal_expr.label("first_terminal_at"),
            Player.created_at.label("player_created_at"),
        )
        .join(GameRun, GameRun.player_id == Player.id)
        .filter(GameRun.status.in_(TERMINAL_RUN_STATUSES))
        .group_by(Player.id, Player.created_at)
        .order_by(
            total_score_expr.desc(),
            passed_count_expr.desc(),
            first_terminal_expr.asc(),
            Player.created_at.asc(),
        )
        .all()
    )
    for index, row in enumerate(rows, start=1):
        if row.player_id == player_id:
            return f"全球第 {index} 名"
    return None


def build_achievements(player_id, total_score):
    success_rows = (
        db.session.query(
            GameRun.level_id,
            GameRun.remaining_turns,
            Level.max_turns,
        )
        .join(Level, Level.id == GameRun.level_id)
        .filter(
            GameRun.player_id == player_id,
            GameRun.status == "success",
        )
        .all()
    )
    has_success = bool(success_rows)
    has_fast_success = any(
        (row.max_turns - row.remaining_turns) <= 2 for row in success_rows
    )
    has_formal_success = any(row.level_id != "level_debug" for row in success_rows)

    active_map = {
        "ach_first_pass": has_success,
        "ach_two_turns": has_fast_success,
        "ach_score_breaker": total_score >= ACHIEVEMENT_SCORE_THRESHOLD,
        "ach_debug_master": has_formal_success,
    }
    return [
        {
            "id": definition["id"],
            "title": definition["title"],
            "description": definition["description"],
            "active": active_map.get(definition["id"], False),
        }
        for definition in ACHIEVEMENT_DEFINITIONS
    ]
