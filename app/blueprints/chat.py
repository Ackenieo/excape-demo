import json
import re
import traceback
from flask import Blueprint, request
from app.extensions import db
from app.models.game_run import GameRun
from app.models.run_message import RunMessage
from app.api.game_logic import (
    DEFAULT_FAIL_REPLY,
    build_run_conversation_config,
    compute_score,
    utc_now,
)
from app.api.responses import (
    CONTENT_INVALID,
    PARAM_ERROR,
    RUN_NOT_FOUND,
    RUN_NOT_PLAYABLE,
    SERVER_ERROR,
    error_response,
    success_response,
)
from app.api.serializers import serialize_message
from app.llm.chains import (
    append_history_messages,
    format_session_memory_text,
    get_conversational_chain,
    get_history_messages,
    get_session_memories,
    store_session_memory,
)
from app.llm.parsers import NPCResponse

chat_bp = Blueprint("chat", __name__, url_prefix="/api/v1/chat")
MEMORY_INTENT_PATTERNS = [
    "记住",
    "记一下",
    "帮我记",
    "等会我会问你",
    "稍后问你",
    "关键词",
    "暗号",
    "密码",
]
MEMORY_RECALL_PATTERNS = [
    "我刚刚让你记住了什么",
    "我刚才让你记住了什么",
    "刚刚让你记住了什么",
    "刚才让你记住了什么",
    "你记住了什么",
    "刚才那个关键词是什么",
    "刚刚那个关键词是什么",
    "我的暗号是什么",
    "我的密码是什么",
]


def _normalize_checkpoints(raw_checkpoints):
    checkpoints = []

    if not isinstance(raw_checkpoints, list):
        return checkpoints

    for item in raw_checkpoints:
        if not isinstance(item, dict):
            continue

        checkpoint_id = str(item.get("id", "")).strip()
        if not checkpoint_id:
            continue

        checkpoints.append(
            {
                "id": checkpoint_id,
                "title": str(item.get("title", checkpoint_id)).strip(),
                "description": str(item.get("description", "")).strip(),
                "hintForNpc": str(item.get("hintForNpc", "")).strip(),
                "weight": item.get("weight", 1),
            }
        )

    return checkpoints


def _format_pending_checkpoints(checkpoints):
    if not checkpoints:
        return "[]"

    prompt_items = []
    for checkpoint in checkpoints:
        prompt_items.append(
            {
                "id": checkpoint["id"],
                "title": checkpoint["title"],
                "description": checkpoint["description"],
                "hintForNpc": checkpoint["hintForNpc"],
            }
        )

    return json.dumps(prompt_items, ensure_ascii=False, indent=2)


def _merge_checkpoint_ids(existing_ids, new_ids, valid_ids):
    merged = []
    seen = set()

    for checkpoint_id in existing_ids + new_ids:
        if checkpoint_id not in valid_ids or checkpoint_id in seen:
            continue
        merged.append(checkpoint_id)
        seen.add(checkpoint_id)

    return merged


def _inspect_memory_content(content):
    normalized = content.strip()
    has_memory_intent = any(pattern in normalized for pattern in MEMORY_INTENT_PATTERNS)
    has_memory_recall_query = any(pattern in normalized for pattern in MEMORY_RECALL_PATTERNS)
    extracted_value = None
    memory_kind = "fact"

    keyword_match = re.search(r"(?:关键词|暗号|密码)[：:\s]+(.+?)(?:[。！？!?,，]|$)", normalized)
    if keyword_match:
        extracted_value = keyword_match.group(1).strip()
        if "暗号" in normalized:
            memory_kind = "暗号"
        elif "密码" in normalized:
            memory_kind = "密码"
        else:
            memory_kind = "关键词"
    elif "记住" in normalized:
        remember_match = re.search(r"记住(?:一个)?(?:关键词)?[：:\s]+(.+?)(?:[。！？!?,，]|$)", normalized)
        if remember_match:
            extracted_value = remember_match.group(1).strip()
            memory_kind = "关键词" if "关键词" in normalized else "内容"

    return {
        "has_memory_intent": has_memory_intent,
        "has_memory_recall_query": has_memory_recall_query,
        "extracted_value": extracted_value or "",
        "memory_kind": memory_kind,
    }


def _build_candidate_memory(memory_inspection, turn_index, content):
    if not memory_inspection["has_memory_intent"] or not memory_inspection["extracted_value"]:
        return None

    return {
        "kind": memory_inspection["memory_kind"],
        "value": memory_inspection["extracted_value"],
        "source_text": content,
        "turn_index": turn_index,
        "created_at": "pending",
    }


def _build_memory_recall_response(memory_items):
    latest_memory = memory_items[-1] if memory_items else None
    if latest_memory:
        reply = f"你刚刚让我记住的是“{latest_memory['value']}”。我已经记下了。"
        judgement = f"命中记忆追问，直接返回最近一条会话记忆：{latest_memory['value']}"
    else:
        reply = "你之前还没有让我记住明确的内容。"
        judgement = "命中记忆追问，但当前会话内没有可用记忆，明确说明为空。"

    return NPCResponse(
        reply=reply,
        hit_checkpoint_ids=[],
        shake_delta=0,
        judgement=judgement,
        best_line_hit=False,
    )


def _coerce_npc_response(response):
    if isinstance(response, NPCResponse):
        return response
    if isinstance(response, dict):
        return NPCResponse(
            reply=str(response.get("reply", "")),
            hit_checkpoint_ids=list(response.get("hit_checkpoint_ids", []) or []),
            shake_delta=int(response.get("shake_delta", 0) or 0),
            judgement=str(response.get("judgement", "")),
            best_line_hit=bool(response.get("best_line_hit", False)),
        )
    raise TypeError(f"unsupported NPC response type: {type(response)!r}")


def _print_memory_debug(run_id, content, memory_inspection, memory_context_text, stored_count):
    print(
        "[memory-debug]",
        json.dumps(
            {
                "runId": str(run_id),
                "content": content,
                "hasMemoryIntent": memory_inspection["has_memory_intent"],
                "hasMemoryRecallQuery": memory_inspection["has_memory_recall_query"],
                "memoryKind": memory_inspection["memory_kind"],
                "extractedValue": memory_inspection["extracted_value"],
                "storedMemoryCount": stored_count,
                "memoryContextText": memory_context_text,
            },
            ensure_ascii=False,
        ),
        flush=True,
    )


@chat_bp.post("/send")
def send_message():
    data = request.get_json() or {}
    run_id = data.get("runId")
    content = (data.get("content") or "").strip()

    if not run_id or not content:
        return error_response(PARAM_ERROR, "缺少 runId 或 content")

    if len(content) > 500:
        return error_response(CONTENT_INVALID, "文本不能为空且长度不能超过 500")

    game_run = GameRun.query.get(run_id)
    if not game_run:
        return error_response(RUN_NOT_FOUND, "对局不存在", status=404)

    if game_run.status != "playing":
        return error_response(RUN_NOT_PLAYABLE, "对局已结束，不能继续发送", status=400)

    if game_run.remaining_turns <= 0:
        return error_response(RUN_NOT_PLAYABLE, "对局已结束，不能继续发送", status=400)

    config = build_run_conversation_config(game_run)
    level_checkpoints = _normalize_checkpoints(config.npc_checkpoints)
    all_checkpoint_ids = {checkpoint["id"] for checkpoint in level_checkpoints}
    existing_passed_ids = list(game_run.passed_checkpoint_ids or [])
    pending_checkpoints = [
        checkpoint for checkpoint in level_checkpoints
        if checkpoint["id"] not in existing_passed_ids
    ]

    session_id = str(game_run.id)
    current_turn_index = config.max_turns - game_run.remaining_turns + 1
    memory_inspection = _inspect_memory_content(content)
    existing_memories = get_session_memories(session_id)
    candidate_memory = _build_candidate_memory(memory_inspection, current_turn_index, content)
    effective_memories = list(existing_memories)
    if candidate_memory:
        effective_memories.append(candidate_memory)
    memory_context_text = format_session_memory_text(
        session_id,
        recall_mode=memory_inspection["has_memory_recall_query"],
        memory_items=effective_memories,
    )
    _print_memory_debug(
        run_id,
        content,
        memory_inspection,
        memory_context_text,
        len(existing_memories),
    )

    chain = get_conversational_chain()
    history_messages = get_history_messages(session_id)

    if memory_inspection["has_memory_recall_query"]:
        response = _build_memory_recall_response(existing_memories)
    else:
        try:
            response = chain.invoke(
                {
                    "system_prompt": config.system_prompt,
                    "shake_value": game_run.shake_value,
                    "remaining_turns": game_run.remaining_turns,
                    "passed_checkpoint_count": game_run.passed_checkpoint_count,
                    "pass_threshold": config.pass_threshold,
                    "pending_checkpoints_text": _format_pending_checkpoints(pending_checkpoints),
                    "session_memory_text": memory_context_text,
                    "memory_recall_mode": "是" if memory_inspection["has_memory_recall_query"] else "否",
                    "history": history_messages,
                    "success_token": config.success_token,
                    "input": content,
                },
            )
        except Exception as e:
            traceback.print_exc()
            return error_response(SERVER_ERROR, f"AI 调用失败: {str(e)}", status=500)

    response = _coerce_npc_response(response)
    game_run.remaining_turns -= 1

    new_hit_ids = [
        checkpoint_id for checkpoint_id in response.hit_checkpoint_ids
        if checkpoint_id in {checkpoint["id"] for checkpoint in pending_checkpoints}
    ]
    merged_checkpoint_ids = _merge_checkpoint_ids(
        existing_passed_ids,
        new_hit_ids,
        all_checkpoint_ids,
    )
    game_run.passed_checkpoint_ids = merged_checkpoint_ids
    game_run.passed_checkpoint_count = len(merged_checkpoint_ids)

    new_shake = game_run.shake_value + response.shake_delta
    game_run.shake_value = max(0, min(100, new_shake))

    assistant_reply = response.reply

    if game_run.passed_checkpoint_count >= config.pass_threshold:
        game_run.passed = True
        if config.success_token not in assistant_reply:
            assistant_reply = f"{assistant_reply.rstrip()} 好吧，这次我给你进去。{config.success_token}"

    if response.best_line_hit:
        game_run.best_line = content

    game_run.final_reply = assistant_reply

    turn_index = config.max_turns - game_run.remaining_turns
    player_message = RunMessage(
        run_id=game_run.id,
        role="player",
        content=content,
        turn_index=turn_index,
    )
    npc_message = RunMessage(
        run_id=game_run.id,
        role="npc",
        content=assistant_reply,
        turn_index=turn_index,
        shake_delta=response.shake_delta,
    )
    db.session.add(player_message)
    db.session.add(npc_message)
    if candidate_memory:
        store_session_memory(
            session_id,
            candidate_memory["kind"],
            candidate_memory["value"],
            candidate_memory["source_text"],
            candidate_memory["turn_index"],
        )

    if game_run.passed:
        game_run.status = "success"
        game_run.score = compute_score(config, game_run.remaining_turns, True)
        game_run.finished_at = utc_now()
    elif game_run.remaining_turns <= 0:
        game_run.status = "fail"
        if not game_run.final_reply:
            game_run.final_reply = DEFAULT_FAIL_REPLY
        game_run.score = 0
        game_run.finished_at = utc_now()
    else:
        game_run.status = "playing"

    db.session.commit()
    append_history_messages(session_id, content, assistant_reply)

    return success_response(
        {
            "runId": str(game_run.id),
            "status": game_run.status,
            "remainingTurns": game_run.remaining_turns,
            "shakeValue": game_run.shake_value,
            "shakeDelta": response.shake_delta,
            "passed": game_run.passed,
            "score": game_run.score,
            "bestLine": game_run.best_line or "",
            "bestLineUpdated": response.best_line_hit,
            "assistantReply": assistant_reply,
            "finalReply": game_run.final_reply or "",
            "messages": [serialize_message(player_message), serialize_message(npc_message)],
            "hitCheckpointIds": new_hit_ids,
            "passedCheckpointIds": game_run.passed_checkpoint_ids,
            "passedCheckpointCount": game_run.passed_checkpoint_count,
            "passThreshold": config.pass_threshold,
        }
    )
