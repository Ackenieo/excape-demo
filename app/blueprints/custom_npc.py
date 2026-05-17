from flask import Blueprint, request

from app.api.custom_npc_logic import (
    build_custom_npc_runtime_fields,
    validate_custom_npc_payload,
)
from app.api.game_logic import utc_now
from app.api.responses import (
    CUSTOM_NPC_CONTENT_INVALID,
    CUSTOM_NPC_INVALID,
    error_response,
    success_response,
)
from app.api.serializers import serialize_custom_npc
from app.extensions import db
from app.models.custom_npc import CustomNpc
from app.models.player import Player


custom_npc_bp = Blueprint("custom_npc", __name__, url_prefix="/api/v1/custom-npcs")


def _get_or_create_player(device_id):
    player = Player.query.filter_by(device_id=device_id).first()
    if player:
        return player

    player = Player(device_id=device_id)
    db.session.add(player)
    db.session.flush()
    return player


def _generate_public_npc_id(created_at):
    date_part = created_at.strftime("%Y%m%d")
    prefix = f"npc_custom_{date_part}_"
    latest_row = (
        db.session.query(CustomNpc.public_id)
        .filter(CustomNpc.public_id.like(f"{prefix}%"))
        .order_by(CustomNpc.public_id.desc())
        .first()
    )
    latest_public_id = latest_row[0] if latest_row else None
    next_sequence = 1
    if latest_public_id:
        suffix = latest_public_id.removeprefix(prefix)
        if suffix.isdigit():
            next_sequence = int(suffix) + 1
    return f"{prefix}{next_sequence:03d}"


@custom_npc_bp.post("")
def create_custom_npc():
    data = request.get_json() or {}
    validation_result = validate_custom_npc_payload(
        data,
        CUSTOM_NPC_INVALID,
        CUSTOM_NPC_CONTENT_INVALID,
    )
    if validation_result.payload is None:
        return error_response(
            validation_result.error_code,
            validation_result.error_message,
            status=400,
        )

    payload = validation_result.payload
    player = _get_or_create_player(payload["device_id"])
    runtime_fields = build_custom_npc_runtime_fields(payload)
    now = utc_now()
    custom_npc = CustomNpc(
        public_id=_generate_public_npc_id(now),
        player_id=player.id,
        name=payload["name"],
        avatar_url=payload["avatar_url"],
        role=payload["role"],
        personality=payload["personality"],
        opening_message=payload["opening_message"],
        goal=payload["goal"],
        max_turns=payload["max_turns"],
        difficulty=payload["difficulty"],
        raw_system_prompt=payload["raw_system_prompt"],
        scene=runtime_fields["scene"],
        compiled_system_prompt=runtime_fields["compiled_system_prompt"],
        npc_checkpoints=runtime_fields["npc_checkpoints"],
        pass_threshold=runtime_fields["pass_threshold"],
        success_token=runtime_fields["success_token"],
        base_score=runtime_fields["base_score"],
        status="active",
        moderation_status="approved",
        created_at=now,
        updated_at=now,
    )
    db.session.add(custom_npc)
    db.session.commit()
    return success_response(serialize_custom_npc(custom_npc), status=201)
