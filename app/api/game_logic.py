from dataclasses import dataclass
from datetime import datetime, timezone


DEFAULT_FAIL_REPLY = "不行，规矩不能破，你还是回去吧。"


@dataclass
class ConversationConfig:
    source_type: str
    level_id: str | None
    custom_npc_id: str | None
    name: str
    role: str | None
    personality: str | None
    scene: str | None
    goal: str
    opening_message: str
    system_prompt: str
    npc_checkpoints: list
    pass_threshold: int
    success_token: str
    max_turns: int
    difficulty: int
    base_score: int


def utc_now():
    return datetime.now(timezone.utc)


def compute_score(config, remaining_turns, passed):
    turns_used = max(0, config.max_turns - remaining_turns)
    multiplier = 0.0

    if passed:
        if turns_used <= 1:
            multiplier = 4.0
        elif turns_used == 2:
            multiplier = 3.0
        elif turns_used == 3:
            multiplier = 2.0
        elif turns_used == 4:
            multiplier = 1.2
        else:
            multiplier = 1.0

    return int(config.base_score * multiplier)


def build_level_conversation_config(level):
    return ConversationConfig(
        source_type="level",
        level_id=level.id,
        custom_npc_id=None,
        name=level.name,
        role=None,
        personality=None,
        scene=level.scene,
        goal=level.goal,
        opening_message=level.opening_message,
        system_prompt=level.system_prompt,
        npc_checkpoints=list(level.npc_checkpoints or []),
        pass_threshold=level.pass_threshold,
        success_token=level.success_token,
        max_turns=level.max_turns,
        difficulty=level.difficulty,
        base_score=level.base_score,
    )


def build_custom_npc_conversation_config(custom_npc):
    return ConversationConfig(
        source_type="custom_npc",
        level_id=None,
        custom_npc_id=custom_npc.external_npc_id,
        name=custom_npc.name,
        role=custom_npc.role,
        personality=custom_npc.personality,
        scene=custom_npc.scene,
        goal=custom_npc.goal,
        opening_message=custom_npc.opening_message,
        system_prompt=custom_npc.compiled_system_prompt,
        npc_checkpoints=list(custom_npc.npc_checkpoints or []),
        pass_threshold=custom_npc.pass_threshold,
        success_token=custom_npc.success_token,
        max_turns=custom_npc.max_turns,
        difficulty=custom_npc.difficulty,
        base_score=custom_npc.base_score,
    )


def build_run_conversation_config(game_run):
    if game_run.snapshot_system_prompt:
        return ConversationConfig(
            source_type=game_run.source_type or "level",
            level_id=game_run.level_id,
            custom_npc_id=str(game_run.custom_npc_id) if game_run.custom_npc_id else None,
            name=game_run.snapshot_name or "",
            role=game_run.snapshot_role,
            personality=game_run.snapshot_personality,
            scene=game_run.snapshot_scene,
            goal=game_run.snapshot_goal or "",
            opening_message=game_run.snapshot_opening_message or "",
            system_prompt=game_run.snapshot_system_prompt,
            npc_checkpoints=list(game_run.snapshot_checkpoints or []),
            pass_threshold=game_run.snapshot_pass_threshold or 1,
            success_token=game_run.snapshot_success_token or "[PASS]",
            max_turns=game_run.snapshot_max_turns or game_run.remaining_turns,
            difficulty=game_run.snapshot_difficulty or 1,
            base_score=game_run.snapshot_base_score or 100,
        )

    if game_run.source_type == "custom_npc" and game_run.custom_npc:
        return build_custom_npc_conversation_config(game_run.custom_npc)

    if game_run.level:
        return build_level_conversation_config(game_run.level)

    raise ValueError("对局缺少可用的运行时配置")


def normalize_run_status(run_status, passed):
    if run_status in {"playing", "success", "fail", "finished"}:
        return run_status

    if passed:
        return "success"

    return "playing"
