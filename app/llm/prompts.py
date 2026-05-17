import os
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

def get_chat_prompt_template():
    return ChatPromptTemplate.from_messages([
        ("system", """{system_prompt}

你现在的动摇度是：{shake_value}/100。
剩余可以对话的次数：{remaining_turns}次。
当前已经通过的检查点数量：{passed_checkpoint_count}/{pass_threshold}。

下面是当前仍未通过的检查点，请只基于这些检查点判断本轮是否命中：
{pending_checkpoints_text}

下面是当前会话中后端整理出的短期记忆，请把它当成高优先级上下文：
{session_memory_text}

当前是否处于“追问刚才记住了什么”的场景：{memory_recall_mode}

注意：
1. 必须根据玩家的话语进行回应，保持角色设定。
2. `hit_checkpoint_ids` 只能填写上方“仍未通过的检查点”中的 id；如果没有命中，返回空数组。
3. 当你判断“当前已通过数量 + 本轮命中数量 >= 阈值”时，说明玩家已经说服你放行，你的 `reply` 必须自然表达放行，并包含指定成功词：{success_token}。
4. 不要在 `reply` 中直接提到“检查点”“阈值”“命中”等系统术语。
5. 即使你很动摇，也不要轻易放行；只有玩家给出足够充分、符合剩余检查点的内容时才放行。
6. 如果用户正在追问此前让你记住的内容，你必须优先根据“短期记忆”准确复述；如果没有记忆，不要编造。
"""),
        MessagesPlaceholder(variable_name="history"),
        ("human", "{input}")
    ])
