from flask import Blueprint, Response, request

from app.api.game_logic import utc_now
from app.api.profile_image_logic import (
    get_profile_image_by_id,
    resolve_player_avatar_url,
)
from app.api.profile_logic import (
    build_achievements,
    build_profile_stats,
    build_rank_text,
    build_recent_runs,
    get_player_by_device_id,
    normalize_nickname,
)
from app.api.responses import (
    AVATAR_INVALID,
    NICKNAME_INVALID,
    PARAM_ERROR,
    USER_NOT_FOUND,
    error_response,
    success_response,
)
from app.api.serializers import (
    build_profile_image_url,
    format_percentage,
    serialize_profile,
    serialize_profile_avatar_update,
    serialize_profile_nickname_update,
)
from app.api.upload_logic import is_allowed_avatar_url
from app.extensions import db


profile_bp = Blueprint("profile", __name__, url_prefix="/api/v1/profile")

@profile_bp.get("")
def get_profile():
    device_id = request.args.get("deviceId")
    if not device_id:
        return error_response(PARAM_ERROR, "缺少 deviceId")

    player = get_player_by_device_id(device_id)
    if not player:
        return error_response(USER_NOT_FOUND, "用户不存在或 deviceId 无效", status=404)

    stats = build_profile_stats(player.id)
    pass_rate = (stats["passed_count"] / stats["play_count"] * 100.0) if stats["play_count"] else 0.0
    total_score = stats["total_score"]
    payload = serialize_profile(
        {
            "device_id": player.device_id,
            "nickname": player.nickname,
            "avatar_url": resolve_player_avatar_url(player, build_profile_image_url),
            "rank_text": build_rank_text(player.id),
            "passed_count": stats["passed_count"],
            "total_score": total_score,
            "pass_rate": format_percentage(pass_rate),
            "achievements": build_achievements(player.id, total_score),
            "recent_runs": build_recent_runs(player.id),
        }
    )
    return success_response(payload)


@profile_bp.get("/images/<uuid:image_id>/content")
def get_profile_image_content(image_id):
    image = get_profile_image_by_id(image_id)
    if not image:
        return error_response(AVATAR_INVALID, "头像不存在", status=404)

    response = Response(image.binary_data, mimetype=image.mime_type)
    response.headers["Content-Length"] = str(image.byte_size)
    response.headers["Cache-Control"] = "public, max-age=3600"
    response.set_etag(image.checksum)
    return response


@profile_bp.post("/avatar")
def update_profile_avatar():
    data = request.get_json() or {}
    device_id = (data.get("deviceId") or "").strip()
    avatar_url = (data.get("avatarUrl") or "").strip()

    if not device_id:
        return error_response(PARAM_ERROR, "缺少 deviceId", status=400)
    if not avatar_url:
        return error_response(PARAM_ERROR, "缺少 avatarUrl", status=400)

    player = get_player_by_device_id(device_id)
    if not player:
        return error_response(USER_NOT_FOUND, "用户不存在或 deviceId 无效", status=404)

    if not is_allowed_avatar_url(avatar_url):
        return error_response(AVATAR_INVALID, "头像地址非法或不受支持", status=400)

    player.avatar_url = avatar_url
    player.updated_at = utc_now()
    db.session.commit()
    return success_response(serialize_profile_avatar_update(player, avatar_url))


@profile_bp.post("/nickname")
def update_profile_nickname():
    data = request.get_json() or {}
    device_id = data.get("deviceId")
    nickname = data.get("nickname")

    if not device_id or nickname is None:
        return error_response(PARAM_ERROR, "缺少 deviceId 或 nickname")

    player = get_player_by_device_id(device_id)
    if not player:
        return error_response(USER_NOT_FOUND, "用户不存在或 deviceId 无效", status=404)

    normalized_nickname = normalize_nickname(nickname)
    if normalized_nickname is None:
        return error_response(NICKNAME_INVALID, "昵称不符合要求", status=400)

    player.nickname = normalized_nickname
    player.updated_at = utc_now()
    db.session.commit()
    return success_response(serialize_profile_nickname_update(player))
