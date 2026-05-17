from dataclasses import dataclass, field
from typing import List


@dataclass
class NPCResponse:
    reply: str
    hit_checkpoint_ids: List[str] = field(default_factory=list)
    shake_delta: int = 0
    judgement: str = ""
    best_line_hit: bool = False
