from dataclasses import dataclass
from typing import Optional
from urllib.parse import urlparse


SUCCESS_TOKEN = "[PASS]"
DEFAULT_DIFFICULTY = 3
DEFAULT_BASE_SCORE = {
    1: 100,
    2: 150,
    3: 200,
    4: 300,
    5: 400,
}
DEFAULT_PASS_THRESHOLD = {
    1: 1,
    2: 2,
    3: 2,
    4: 3,
    5: 3,
}
DISALLOWED_CONTENT_MARKERS = [
    "[PASS]",
    "ignore previous",
    "system prompt",
    "system_prompt",
    "developer message",
    "忽略之前",
    "忽略上面的规则",
    "无视规则",
]


@dataclass
class CustomNpcValidationResult:
    payload: Optional[dict]
    error_code: Optional[int] = None
    error_message: Optional[str] = None


def _normalize_text(value):
    return str(value or "").strip()


def _normalize_optional_url(value):
    text = _normalize_text(value)
    if not text:
        return None
    parsed = urlparse(text)
    if parsed.scheme != "https" or not parsed.netloc:
        return None
    return text


def _contains_disallowed_content(*values):
    haystack = " ".join(_normalize_text(value).lower() for value in values if value is not None)
    return any(marker in haystack for marker in DISALLOWED_CONTENT_MARKERS)


def validate_custom_npc_payload(data, param_error_code, content_error_code):
    device_id = _normalize_text(data.get("deviceId"))
    name = _normalize_text(data.get("name"))
    role = _normalize_text(data.get("role"))
    personality = _normalize_text(data.get("personality"))
    opening_message = _normalize_text(data.get("openingMessage"))
    goal = _normalize_text(data.get("goal"))
    system_prompt = _normalize_text(data.get("systemPrompt")) or None
    avatar_url = data.get("avatarUrl")

    if not all([device_id, name, role, personality, opening_message, goal]):
        return CustomNpcValidationResult(
            None,
            param_error_code,
            "自定义 NPC 缺少必填字段",
        )

    try:
        max_turns = int(data.get("maxTurns"))
    except (TypeError, ValueError):
        return CustomNpcValidationResult(None, param_error_code, "maxTurns 必须为整数")

    if max_turns < 3 or max_turns > 10:
        return CustomNpcValidationResult(None, param_error_code, "maxTurns 必须在 3 到 10 之间")

    difficulty = data.get("difficulty", DEFAULT_DIFFICULTY)
    try:
        difficulty = int(difficulty)
    except (TypeError, ValueError):
        return CustomNpcValidationResult(None, param_error_code, "difficulty 必须为整数")

    if difficulty < 1 or difficulty > 5:
        return CustomNpcValidationResult(None, param_error_code, "difficulty 必须在 1 到 5 之间")

    normalized_avatar_url = _normalize_optional_url(avatar_url)
    if avatar_url is not None and normalized_avatar_url is None:
        return CustomNpcValidationResult(None, param_error_code, "avatarUrl 必须为 HTTPS 图片地址")

    if len(name) > 64 or len(role) > 128:
        return CustomNpcValidationResult(None, param_error_code, "name 或 role 超出长度限制")

    for field_name, field_value, max_length in [
        ("personality", personality, 500),
        ("openingMessage", opening_message, 500),
        ("goal", goal, 500),
        ("systemPrompt", system_prompt or "", 1000),
    ]:
        if len(field_value) > max_length:
            return CustomNpcValidationResult(
                None,
                param_error_code,
                f"{field_name} 超出长度限制",
            )

    if _contains_disallowed_content(name, role, personality, opening_message, goal, system_prompt):
        return CustomNpcValidationResult(
            None,
            content_error_code,
            "自定义 NPC 内容不符合要求",
        )

    return CustomNpcValidationResult(
        {
            "device_id": device_id,
            "name": name,
            "avatar_url": normalized_avatar_url,
            "role": role,
            "personality": personality,
            "opening_message": opening_message,
            "goal": goal,
            "max_turns": max_turns,
            "difficulty": difficulty,
            "raw_system_prompt": system_prompt,
        }
    )


def build_custom_npc_runtime_fields(payload):
    difficulty = payload["difficulty"]
    pass_threshold = DEFAULT_PASS_THRESHOLD[difficulty]
    checkpoint_templates = [
        {
            "id": "clear_intent",
            "title": "说明来意明确",
            "description": f"玩家需要清楚说明为什么要完成“{payload['goal']}”。",
            "hintForNpc": "如果玩家的目标明确且理由具体，可以视为命中。",
            "weight": 1,
        },
        {
            "id": "credible_reason",
            "title": "理由可信具体",
            "description": f"玩家需要给出足以说服 {payload['role']} 的具体信息、背景或证据。",
            "hintForNpc": "空泛表态不算，具体细节或证据才算命中。",
            "weight": 1,
        },
        {
            "id": "risk_control",
            "title": "风险可控",
            "description": "玩家需要表现出愿意配合、接受核验或降低风险的态度。",
            "hintForNpc": "如果玩家提出登记、验证、陪同、限时行动等方案，可以视为命中。",
            "weight": 1,
        },
    ]
    if difficulty >= 4:
        checkpoint_templates.append(
            {
                "id": "emotional_or_value_alignment",
                "title": "触发情理或价值认同",
                "description": f"玩家需要进一步打动 {payload['role']}，让对方在规矩之外看到合理性。",
                "hintForNpc": "只有在理由充分的前提下，情理说服才算命中。",
                "weight": 1,
            }
        )

    scene = f"你正在扮演{payload['name']}，身份是{payload['role']}。玩家的目标是：{payload['goal']}。"
    compiled_prompt_lines = [
        f"你是{payload['name']}。",
        f"你的身份是：{payload['role']}。",
        f"你的性格特点是：{payload['personality']}。",
        f"当前场景：{scene}",
        f"开场白参考：{payload['opening_message']}",
        "你必须始终保持角色一致，只根据玩家的话做出自然回应。",
        "除非玩家提供了足够充分、具体、可信且风险可控的理由，否则不要轻易放行。",
    ]
    if payload.get("raw_system_prompt"):
        compiled_prompt_lines.append(
            f"补充设定（需要在不违反系统规则的前提下参考）：{payload['raw_system_prompt']}"
        )

    return {
        "scene": scene,
        "compiled_system_prompt": "\n".join(compiled_prompt_lines),
        "npc_checkpoints": checkpoint_templates,
        "pass_threshold": pass_threshold,
        "success_token": SUCCESS_TOKEN,
        "base_score": DEFAULT_BASE_SCORE[difficulty],
    }
