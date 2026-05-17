from datetime import timezone
from flask import url_for


def _to_iso(dt):
    if not dt:
        return None
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")


def format_percentage(value):
    rounded = round(float(value), 1)
    if rounded.is_integer():
        return f"{int(rounded)}%"
    return f"{rounded:.1f}%"


def build_profile_image_url(image_id):
    if not image_id:
        return None
    return url_for("profile.get_profile_image_content", image_id=image_id, _external=True)


def serialize_level_item(level):
    return {
        "id": level.id,
        "name": level.name,
        "difficulty": level.difficulty,
        "goal": level.goal,
        "intro": level.scene,
        "maxTurns": level.max_turns,
        "status": level.status,
    }


def serialize_level_detail(level):
    return {
        "id": level.id,
        "name": level.name,
        "difficulty": level.difficulty,
        "goal": level.goal,
        "intro": level.scene,
        "scene": level.scene,
        "maxTurns": level.max_turns,
        "openingMessage": level.opening_message,
    }


def serialize_message(message):
    payload = {
        "role": message.role,
        "content": message.content,
        "createdAt": _to_iso(message.created_at),
    }
    if getattr(message, "turn_index", None) is not None:
        payload["turnIndex"] = message.turn_index
    if getattr(message, "shake_delta", None) is not None:
        payload["shakeDelta"] = message.shake_delta
    return payload


def serialize_run_state(game_run, messages, opening_message=None):
    data = {
        "runId": str(game_run.id),
        "status": game_run.status,
        "remainingTurns": game_run.remaining_turns,
        "shakeValue": game_run.shake_value,
        "passed": game_run.passed,
        "score": game_run.score,
        "bestLine": game_run.best_line or "",
        "finalReply": game_run.final_reply or "",
        "messages": [serialize_message(message) for message in messages],
        "sourceType": game_run.source_type or "level",
    }
    if game_run.level_id is not None:
        data["levelId"] = game_run.level_id
    if opening_message is not None:
        data["openingMessage"] = opening_message
    if game_run.custom_npc_id is not None:
        data["npcId"] = (
            game_run.custom_npc.external_npc_id
            if game_run.custom_npc is not None
            else str(game_run.custom_npc_id)
        )
    if game_run.source_type == "custom_npc" and game_run.snapshot_name:
        data["npcName"] = game_run.snapshot_name
    return data


def serialize_ranking_item(item):
    return {
        "nickname": item["nickname"],
        "score": item["score"],
        "levelId": item.get("levelId"),
        "rank": item.get("rank"),
    }


def serialize_challenge(challenge, include_creator=False):
    data = {
        "code": challenge.code,
        "title": challenge.title,
        "targetLevelId": challenge.target_level_id,
        "description": challenge.description,
        "shareTitle": challenge.share_title,
        "sourceScore": challenge.source_score,
    }
    if include_creator:
        data["creatorNickname"] = challenge.creator_nickname
        data["expiresAt"] = _to_iso(challenge.expires_at)
    return data


def serialize_profile(profile):
    recent_runs = []
    for item in profile.get("recent_runs", []):
        recent_runs.append(
            {
                "runId": item["runId"],
                "levelName": item["levelName"],
                "result": item["result"],
                "score": item["score"],
                "createdAt": _to_iso(item.get("createdAt")),
            }
        )
    return {
        "deviceId": profile["device_id"],
        "nickname": profile["nickname"] or "匿名玩家",
        "avatarUrl": profile.get("avatar_url"),
        "rankText": profile.get("rank_text"),
        "passedCount": profile["passed_count"],
        "totalScore": profile["total_score"],
        "passRate": profile["pass_rate"],
        "achievements": profile.get("achievements", []),
        "recentRuns": recent_runs,
    }


def serialize_profile_avatar_update(player, avatar_url):
    return {
        "deviceId": player.device_id,
        "avatarUrl": avatar_url,
        "updatedAt": _to_iso(player.updated_at),
    }


def serialize_profile_nickname_update(player):
    return {
        "deviceId": player.device_id,
        "nickname": player.nickname or "匿名玩家",
        "updatedAt": _to_iso(player.updated_at),
    }


def serialize_custom_npc(custom_npc):
    return {
        "npcId": custom_npc.external_npc_id,
        "name": custom_npc.name,
        "avatarUrl": custom_npc.avatar_url,
        "role": custom_npc.role,
        "personality": custom_npc.personality,
        "openingMessage": custom_npc.opening_message,
        "goal": custom_npc.goal,
        "maxTurns": custom_npc.max_turns,
        "difficulty": custom_npc.difficulty,
        "createdAt": _to_iso(custom_npc.created_at),
    }
