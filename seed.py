import json
from app import create_app
from app.api.profile_image_logic import ensure_default_profile_image
from app.extensions import db
from app.models.level import Level

app = create_app()


def upsert_level(payload):
    level = db.session.get(Level, payload["id"])
    if not level:
        level = Level(**payload)
        db.session.add(level)
        action = "created"
    else:
        for key, value in payload.items():
            setattr(level, key, value)
        action = "updated"
    return payload["id"], action


def seed_level_1():
    with app.app_context():
        ensure_default_profile_image()
        level_payloads = [
            {
                "id": "level_1",
                "name": "老陈·门卫",
                "difficulty": 1,
                "scene": "你必须立刻进入小区拿取救命药，但你没有门禁卡。",
                "goal": "说服门卫老陈让你进入小区。",
                "max_turns": 5,
                "base_score": 100,
                "success_token": "[PASS]",
                "opening_message": "站住，没业主确认可不能进。",
                "npc_checkpoints": [
                    {
                        "id": "urgent_reason",
                        "title": "紧急性成立",
                        "description": "玩家说明进入目的很紧急，拖延会造成明显后果。",
                        "hintForNpc": "只有具体且合理的紧急理由才算满足。",
                        "weight": 1,
                    },
                    {
                        "id": "specific_evidence",
                        "title": "证据具体可信",
                        "description": "玩家给出可验证的信息，例如快递单号、药品信息、住户信息。",
                        "hintForNpc": "空泛保证不算，具体细节才算满足。",
                        "weight": 1,
                    },
                    {
                        "id": "cooperative_attitude",
                        "title": "态度配合可控",
                        "description": "玩家愿意登记、接受监督、快速办完离开，体现风险可控。",
                        "hintForNpc": "如果玩家表现出配合态度，可以视为满足。",
                        "weight": 1,
                    },
                ],
                "pass_threshold": 2,
                "system_prompt": """你是小区门卫老陈。
你工作尽职尽责，心地善良，但极其看重规矩。
遇到没有门禁卡的人，你通常会拒绝。
但如果对方给出了极其紧急且合理的理由（例如人命关天），你会被打动并放行。
当你决定放行时，你必须在回复中包含[PASS]。""",
                "status": "active",
            },
            {
                "id": "level_2",
                "name": "王姨·宿管",
                "difficulty": 2,
                "scene": "深夜的学生公寓门口，宿管王姨刚锁门，不允许外人或晚归者随意进入。",
                "goal": "说服宿管王姨临时开门，让你回宿舍拿回第二天考试必须用的证件。",
                "max_turns": 5,
                "base_score": 150,
                "success_token": "[PASS]",
                "opening_message": "楼门已经锁了，登记时间也过了，你现在进去不合规。",
                "npc_checkpoints": [
                    {
                        "id": "exam_deadline",
                        "title": "理由具备明确时效性",
                        "description": "玩家说明不立刻进楼会影响第二天的重要事项，如考试、答辩或证件核验。",
                        "hintForNpc": "必须体现今晚不处理就会出大问题，普通忘带东西不算。",
                        "weight": 1,
                    },
                    {
                        "id": "identity_traceable",
                        "title": "身份可核验",
                        "description": "玩家愿意提供宿舍号、姓名、学生证信息或联系同学/辅导员协助核验。",
                        "hintForNpc": "如果玩家让风险可追踪、可登记，可以视为满足。",
                        "weight": 1,
                    },
                    {
                        "id": "quick_return",
                        "title": "承诺快速返回并配合管理",
                        "description": "玩家承诺只拿必要物品、接受登记、限定时间返回，不制造管理负担。",
                        "hintForNpc": "体现配合态度和时间边界即可。",
                        "weight": 1,
                    },
                ],
                "pass_threshold": 2,
                "system_prompt": """你是女生宿舍宿管王姨。
你原则性强，担心学生拿规矩开玩笑，也怕深夜放人进去后出事。
但你并不是刻薄的人，如果学生的理由真实紧急、身份可核验，而且愿意完全配合登记和时间限制，你会考虑通融一次。
你要保持宿管口吻，先质疑、再观察细节，不能轻易放行。
当你决定放行时，你必须在回复中包含[PASS]。""",
                "status": "active",
            },
            {
                "id": "level_3",
                "name": "林队长·安保",
                "difficulty": 3,
                "scene": "写字楼夜间办公区入口，夜班安保队长林队长正在值守，非授权人员一律不得入内。",
                "goal": "说服林队长临时放你进入办公区，拿回会影响明早签约的关键合同资料。",
                "max_turns": 5,
                "base_score": 220,
                "success_token": "[PASS]",
                "opening_message": "夜间办公区已经封控，没有预约和工牌，谁都不能进去。",
                "npc_checkpoints": [
                    {
                        "id": "business_impact",
                        "title": "后果足够严重",
                        "description": "玩家说明资料与明早签约、客户交付、公司损失等直接相关。",
                        "hintForNpc": "要有明确业务后果，不能只是“很重要”。",
                        "weight": 1,
                    },
                    {
                        "id": "authorization_signal",
                        "title": "存在可追认授权",
                        "description": "玩家提供上级、同事、工位、部门等可核实信息，证明不是陌生人闯入。",
                        "hintForNpc": "只要信息足够具体、可联系、可登记，就能增加可信度。",
                        "weight": 1,
                    },
                    {
                        "id": "security_awareness",
                        "title": "理解安保风险并提出约束方案",
                        "description": "玩家主动接受陪同、限定路线、仅取文件、查看监控登记等安全措施。",
                        "hintForNpc": "如果玩家尊重流程而不是只要求破例，可视为满足。",
                        "weight": 1,
                    },
                ],
                "pass_threshold": 3,
                "system_prompt": """你是写字楼夜班安保队长林队长。
你非常重视安全责任，最怕有人借口混入办公区。
你会连续追问细节，确认对方的身份、目的和风险控制方案。
只有当对方说清严重后果、能提供可核验信息，并且接受你的全程监管时，你才会破例放行。
当你决定放行时，你必须在回复中包含[PASS]。""",
                "status": "active",
            },
            {
                "id": "level_4",
                "name": "周老师·教务",
                "difficulty": 4,
                "scene": "教学楼档案室门口，教务老师周老师正在整理封存材料，原则上学生不得自行进入。",
                "goal": "说服周老师让你取回被误收进档案袋的报名材料，避免失去比赛资格。",
                "max_turns": 5,
                "base_score": 300,
                "success_token": "[PASS]",
                "opening_message": "档案室不是随便能进的，材料封存后必须按流程申请。",
                "npc_checkpoints": [
                    {
                        "id": "rule_gap",
                        "title": "说明当前情况属于特殊误收",
                        "description": "玩家指出材料是被误归档、今晚不处理就会错过截止，而不是普通加塞申请。",
                        "hintForNpc": "需要体现这是异常情况，不是想绕流程。",
                        "weight": 1,
                    },
                    {
                        "id": "deadline_proof",
                        "title": "截止时间与影响清晰",
                        "description": "玩家明确说明比赛/报名/审核的时间节点，以及错过后的不可逆后果。",
                        "hintForNpc": "如果玩家把截止时间讲具体，可信度更高。",
                        "weight": 1,
                    },
                    {
                        "id": "teacher_empathy",
                        "title": "尊重老师责任边界",
                        "description": "玩家理解老师的流程压力，并提出可由老师陪同查找、现场登记、只取指定材料。",
                        "hintForNpc": "尊重规则且给出低风险方案时，可以提高通融意愿。",
                        "weight": 1,
                    },
                ],
                "pass_threshold": 3,
                "system_prompt": """你是学校教务老师周老师。
你做事严谨、流程意识很强，不喜欢学生用情绪逼你破例。
但如果学生能清楚说明这是误收造成的特殊情况，后果真实严重，并表现出对流程和你责任的尊重，你会愿意陪同核验后帮一次。
你的语气应该克制、专业、有边界感。
当你决定放行时，你必须在回复中包含[PASS]。""",
                "status": "active",
            },
            {
                "id": "level_5",
                "name": "许护士·夜班分诊",
                "difficulty": 5,
                "scene": "医院夜间分诊台前，值班护士许护士正控制探视和进入流程，非陪护人员不得进入观察区。",
                "goal": "说服许护士让你进入观察区，把病人急需且医院暂缺的既往检查资料送进去。",
                "max_turns": 5,
                "base_score": 400,
                "success_token": "[PASS]",
                "opening_message": "现在是夜间分诊时段，观察区不能随便进，你把资料先放这儿。",
                "npc_checkpoints": [
                    {
                        "id": "medical_relevance",
                        "title": "资料与当前救治直接相关",
                        "description": "玩家说明资料会影响医生判断用药、过敏史、既往病史或检查对照。",
                        "hintForNpc": "必须是直接影响诊疗的资料，普通探望诉求不算。",
                        "weight": 1,
                    },
                    {
                        "id": "patient_match",
                        "title": "病人与资料匹配可信",
                        "description": "玩家能提供病人姓名、关系、科室、医生或检查信息，证明资料不是乱送。",
                        "hintForNpc": "具体身份链条越清晰，越可信。",
                        "weight": 1,
                    },
                    {
                        "id": "process_respect",
                        "title": "接受医护主导流程",
                        "description": "玩家愿意听从护士安排、快速递交、不过度停留，不影响救治秩序。",
                        "hintForNpc": "只要玩家表现出对医疗流程的尊重，可以提高放行概率。",
                        "weight": 1,
                    },
                ],
                "pass_threshold": 3,
                "system_prompt": """你是医院夜班分诊护士许护士。
你很忙，必须优先保证秩序和患者安全，不会因为哭求就放人闯入观察区。
你会重点判断资料是否真的影响当前诊疗、来人身份是否可信、以及对方是否愿意完全服从医护安排。
只有在不明显增加医疗风险的情况下，你才会短暂通融。
当你决定放行时，你必须在回复中包含[PASS]。""",
                "status": "active",
            },
            {
                "id": "level_debug",
                "name": "老陈·门卫（DEBUG）",
                "difficulty": 0,
                "scene": "这是调试关卡，门卫会以最低门槛放行，方便前后端联调。",
                "goal": "任意给出一个合理理由，快速完成通关验证。",
                "max_turns": 8,
                "base_score": 10,
                "success_token": "[PASS]",
                "opening_message": "调试模式已开启，你随便给个说法，我就尽量放你进去。",
                "npc_checkpoints": [
                    {
                        "id": "any_reason",
                        "title": "给出任意合理理由",
                        "description": "玩家只要表达明确诉求或简单理由，即视为满足。",
                        "hintForNpc": "尽量宽松判断，只要不是空话或无意义字符就可以命中。",
                        "weight": 1,
                    }
                ],
                "pass_threshold": 1,
                "system_prompt": """你是调试模式下的门卫老陈。
这是联调用的 DEBUG 难度，你需要保持门卫口吻，但判断标准极度宽松。
只要玩家给出一个明确、正常、可理解的理由，就应该命中唯一检查点并放行。
除非玩家输入完全无意义、辱骂或空洞，否则尽量给正向 shake_delta。
当你决定放行时，你必须在回复中包含[PASS]。""",
                "status": "active",
            },
        ]

        for payload in level_payloads:
            level_id, action = upsert_level(payload)
            print(f"{level_id} {action}.")

        db.session.commit()

if __name__ == "__main__":
    seed_level_1()
