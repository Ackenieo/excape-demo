import uuid

from flask import Blueprint, request

from app.extensions import db
from app.models.custom_npc import CustomNpc
from app.models.level import Level
from app.models.player import Player
from app.models.game_run import GameRun
from app.models.run_message import RunMessage
from app.api.game_logic import (
    DEFAULT_FAIL_REPLY,
    build_custom_npc_conversation_config,
    build_level_conversation_config,
    build_run_conversation_config,
    compute_score,
    utc_now,
)
from app.api.responses import (
    CUSTOM_NPC_INVALID,
    LEVEL_NOT_FOUND,
    PARAM_ERROR,
    RUN_NOT_FOUND,
    error_response,
    success_response,
)
from app.api.serializers import serialize_run_state

run_bp = Blueprint("run", __name__, url_prefix="/api/v1/runs")


def _get_run_messages(run_id):
    return (
        RunMessage.query.filter_by(run_id=run_id)
        .order_by(RunMessage.created_at.asc(), RunMessage.id.asc())
        .all()
    )


def _get_or_create_player(device_id):
    player = Player.query.filter_by(device_id=device_id).first()
    if player:
        return player

    player = Player(device_id=device_id)
    db.session.add(player)
    db.session.flush()
    return player


def _parse_uuid(value):
    try:
        return uuid.UUID(str(value))
    except (TypeError, ValueError, AttributeError):
        return None


def _find_custom_npc(player_id, npc_id):
    npc_id = str(npc_id).strip()
    base_query = CustomNpc.query.filter_by(
        player_id=player_id,
        status="active",
        moderation_status="approved",
    )
    custom_npc = base_query.filter_by(public_id=npc_id).first()
    if custom_npc is not None:
        return custom_npc

    parsed_npc_id = _parse_uuid(npc_id)
    if parsed_npc_id is None:
        return None
    return base_query.filter_by(id=parsed_npc_id).first()


def _apply_run_snapshot(game_run, config):
    game_run.source_type = config.source_type
    game_run.snapshot_name = config.name
    game_run.snapshot_role = config.role
    game_run.snapshot_personality = config.personality
    game_run.snapshot_scene = config.scene
    game_run.snapshot_opening_message = config.opening_message
    game_run.snapshot_goal = config.goal
    game_run.snapshot_system_prompt = config.system_prompt
    game_run.snapshot_checkpoints = config.npc_checkpoints
    game_run.snapshot_pass_threshold = config.pass_threshold
    game_run.snapshot_success_token = config.success_token
    game_run.snapshot_max_turns = config.max_turns
    game_run.snapshot_difficulty = config.difficulty
    game_run.snapshot_base_score = config.base_score


@run_bp.post("")
def create_run():
    data = request.get_json() or {}
    device_id = data.get("deviceId")
    level_id = data.get("levelId")
    npc_id = data.get("npcId")

    if not device_id:
        return error_response(PARAM_ERROR, "缺少 deviceId")

    if bool(level_id) == bool(npc_id):
        return error_response(PARAM_ERROR, "levelId 与 npcId 必须且只能传一个")

    player = _get_or_create_player(device_id)
    level = None
    custom_npc = None
    if level_id:
        level = Level.query.get(level_id)
        if not level or level.status != "active":
            return error_response(LEVEL_NOT_FOUND, "关卡不存在或不可用", status=404)
        config = build_level_conversation_config(level)
    else:
        custom_npc = _find_custom_npc(player.id, npc_id)
        if not custom_npc:
            return error_response(CUSTOM_NPC_INVALID, "自定义 NPC 不存在或不可用", status=404)
        config = build_custom_npc_conversation_config(custom_npc)

    game_run = GameRun(
        player_id=player.id,
        level_id=level.id if level else None,
        custom_npc_id=custom_npc.id if custom_npc else None,
        remaining_turns=config.max_turns,
    )
    _apply_run_snapshot(game_run, config)
    db.session.add(game_run)
    db.session.flush()

    opening_message = RunMessage(
        run_id=game_run.id,
        role="npc",
        content=config.opening_message,
        turn_index=0,
    )
    db.session.add(opening_message)
    db.session.commit()

    return success_response(
        serialize_run_state(game_run, [opening_message], opening_message=config.opening_message),
        status=201,
    )


@run_bp.get("/<uuid:run_id>")
def get_run(run_id):
    game_run = GameRun.query.get(run_id)
    if not game_run:
        return error_response(RUN_NOT_FOUND, "对局不存在", status=404)

    messages = _get_run_messages(run_id)
    config = build_run_conversation_config(game_run)
    return success_response(serialize_run_state(game_run, messages, opening_message=config.opening_message))


@run_bp.post("/<uuid:run_id>/finish")
def finish_run(run_id):
    game_run = GameRun.query.get(run_id)
    if not game_run:
        return error_response(RUN_NOT_FOUND, "对局不存在", status=404)

    if game_run.status in {"success", "fail", "finished"}:
        messages = _get_run_messages(run_id)
        config = build_run_conversation_config(game_run)
        return success_response(serialize_run_state(game_run, messages, opening_message=config.opening_message))

    config = build_run_conversation_config(game_run)
    game_run.status = "finished"
    game_run.score = compute_score(config, game_run.remaining_turns, game_run.passed)
    if not game_run.final_reply:
        game_run.final_reply = DEFAULT_FAIL_REPLY
    game_run.finished_at = utc_now()
    db.session.commit()

    messages = _get_run_messages(run_id)
    return success_response(serialize_run_state(game_run, messages, opening_message=config.opening_message))
