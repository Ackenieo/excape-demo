import os
import json
from datetime import datetime, timezone
from app.llm.parsers import NPCResponse

try:
    from langchain_deepseek import ChatDeepSeek
except Exception:
    ChatDeepSeek = None


MAX_CONTEXT_MESSAGES = 100
_history_store = {}
_session_memory_store = {}


class RuleBasedConversationChain:
    def invoke(self, payload):
        pending_checkpoints = _parse_pending_checkpoints(payload.get("pending_checkpoints_text"))
        hit_checkpoint_ids = _match_checkpoints(payload.get("input", ""), pending_checkpoints)
        pass_threshold = int(payload.get("pass_threshold", 1))
        passed_checkpoint_count = int(payload.get("passed_checkpoint_count", 0))
        success_token = payload.get("success_token", "[PASS]")
        will_pass = passed_checkpoint_count + len(hit_checkpoint_ids) >= pass_threshold
        shake_delta = _estimate_shake_delta(hit_checkpoint_ids, payload.get("input", ""))

        if will_pass:
            reply = f"你这次说得有理，我可以通融一次。{success_token}"
            judgement = f"规则兜底命中 {len(hit_checkpoint_ids)} 个检查点，达到放行阈值。"
        elif hit_checkpoint_ids:
            reply = "我听明白了，你这次的说法比刚才更像样，但还差最后一点。"
            judgement = f"规则兜底命中检查点：{', '.join(hit_checkpoint_ids)}。"
        else:
            reply = "你的理由还不够充分，我现在还不能放你进去。"
            judgement = "规则兜底未命中新的检查点。"

        return NPCResponse(
            reply=reply,
            hit_checkpoint_ids=hit_checkpoint_ids,
            shake_delta=shake_delta,
            judgement=judgement,
            best_line_hit=will_pass or len(hit_checkpoint_ids) >= 2,
        )

def _session_key(session_id: str) -> str:
    return str(session_id)

def get_llm():
    api_key = os.environ.get('deepseek_api_key')
    if not api_key:
        raise ValueError("deepseek_api_key environment variable not set")
    if ChatDeepSeek is None:
        raise ImportError("langchain_deepseek 不可用")
    
    return ChatDeepSeek(
        model="deepseek-chat",
        api_key=api_key,
        temperature=0.7,
        max_tokens=1024
    )

def get_chain():
    try:
        llm = get_llm()
        from app.llm.prompts import get_chat_prompt_template

        prompt = get_chat_prompt_template()
        structured_llm = llm.with_structured_output(NPCResponse)
        return prompt | structured_llm
    except Exception:
        return RuleBasedConversationChain()


def get_history_messages(session_id: str):
    messages = list(_history_store.get(_session_key(session_id), []))
    try:
        from langchain_core.messages import AIMessage, HumanMessage
    except Exception:
        return messages

    converted = []
    for item in messages:
        if isinstance(item, dict):
            message_cls = HumanMessage if item.get("role") == "human" else AIMessage
            converted.append(message_cls(content=item.get("content", "")))
        else:
            converted.append(item)
    return converted


def append_history_messages(session_id: str, user_input: str, assistant_reply: str):
    session_key = _session_key(session_id)
    messages = _history_store.setdefault(session_key, [])
    messages.extend(
        [
            {"role": "human", "content": user_input},
            {"role": "ai", "content": assistant_reply},
        ]
    )
    if len(messages) > MAX_CONTEXT_MESSAGES:
        del messages[:-MAX_CONTEXT_MESSAGES]


def store_session_memory(
    session_id: str,
    kind: str,
    value: str,
    source_text: str,
    turn_index: int,
):
    session_key = _session_key(session_id)
    items = _session_memory_store.setdefault(session_key, [])
    items.append(
        {
            "kind": kind,
            "value": value,
            "source_text": source_text,
            "turn_index": turn_index,
            "created_at": datetime.now(timezone.utc).isoformat(),
        }
    )
    return items[-1]


def get_session_memories(session_id: str):
    return list(_session_memory_store.get(_session_key(session_id), []))


def get_latest_session_memory(session_id: str):
    items = _session_memory_store.get(_session_key(session_id), [])
    if not items:
        return None
    return items[-1]


def format_session_memory_text(session_id: str, recall_mode: bool = False, memory_items=None):
    items = list(memory_items) if memory_items is not None else get_session_memories(session_id)
    if not items:
        return "当前没有已记录的会话记忆。"

    lines = []
    for item in items[-5:]:
        lines.append(
            f"- 第{item['turn_index']}轮记录的{item['kind']}：{item['value']}"
        )

    if recall_mode:
        latest = items[-1]
        lines.append(
            f"当前用户正在追问记忆内容，请优先准确复述最近一条：{latest['value']}"
        )

    return "\n".join(lines)


def get_conversational_chain():
    return get_chain()


def _parse_pending_checkpoints(raw_text):
    try:
        data = json.loads(raw_text or "[]")
    except json.JSONDecodeError:
        return []
    if not isinstance(data, list):
        return []
    return [item for item in data if isinstance(item, dict) and item.get("id")]


def _match_checkpoints(user_input, pending_checkpoints):
    text = str(user_input or "").strip().lower()
    if not text:
        return []

    hits = []
    for checkpoint in pending_checkpoints:
        checkpoint_id = str(checkpoint.get("id", ""))
        title = str(checkpoint.get("title", ""))
        description = str(checkpoint.get("description", ""))
        merged = f"{checkpoint_id} {title} {description}".lower()
        if _checkpoint_matches(text, merged):
            hits.append(checkpoint_id)
    return hits


def _checkpoint_matches(text, checkpoint_text):
    keyword_groups = {
        "intent": ["要", "需要", "为了", "想", "必须", "来意", "进去", "进入"],
        "evidence": ["证", "预约", "登记", "工牌", "单号", "号码", "记录", "证明", "核验"],
        "risk": ["配合", "监督", "陪同", "马上", "很快", "登记", "核验", "离开", "风险"],
        "emotion": ["拜托", "求您", "通融", "理解", "真的", "着急", "帮帮", "情理"],
    }

    if "any_reason" in checkpoint_text:
        return len(text) >= 4
    if any(key in checkpoint_text for key in ["intent", "来意", "目标", "紧急"]):
        return any(word in text for word in keyword_groups["intent"] + keyword_groups["emotion"])
    if any(key in checkpoint_text for key in ["credible", "evidence", "证据", "具体", "可信"]):
        return any(word in text for word in keyword_groups["evidence"]) or any(char.isdigit() for char in text)
    if any(key in checkpoint_text for key in ["risk", "配合", "可控"]):
        return any(word in text for word in keyword_groups["risk"])
    if any(key in checkpoint_text for key in ["emotion", "情理", "价值"]):
        return any(word in text for word in keyword_groups["emotion"])
    return len(text) >= 8


def _estimate_shake_delta(hit_checkpoint_ids, user_input):
    if not hit_checkpoint_ids:
        return 0 if len(str(user_input or "").strip()) >= 4 else -5
    return min(40, 10 + 8 * len(hit_checkpoint_ids))
