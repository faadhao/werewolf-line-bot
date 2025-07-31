from enum import Enum
from typing import Dict, Any

class RoleType(Enum):
    VILLAGER = "平民"
    WEREWOLF = "狼人"
    SEER = "預言家"
    WITCH = "女巫"
    HUNTER = "獵人"
    WOLF_KING = "狼王"  # 新增角色
    GUARD = "守衛"      # 新增角色

class Role:
    def __init__(self, role_type: RoleType):
        self.role_type = role_type
        self.is_alive = True
        self.skill_used = False
        self.protected_by_guard = False
        self.special_effects = {}  # 存儲特殊效果

    def use_skill(self) -> bool:
        if not self.can_use_skill():
            return False
        if self.role_type in [RoleType.WITCH, RoleType.HUNTER]:
            self.skill_used = True
        return True

    def can_use_skill(self) -> bool:
        if not self.is_alive:
            return False
        if self.role_type in [RoleType.WITCH, RoleType.HUNTER] and self.skill_used:
            return False
        return True

    def add_effect(self, effect_name: str, duration: int):
        self.special_effects[effect_name] = {
            "duration": duration,
            "applied_at": 0
        }

    def process_effects(self, current_turn: int):
        expired_effects = []
        for effect, data in self.special_effects.items():
            if current_turn - data["applied_at"] >= data["duration"]:
                expired_effects.append(effect)
        
        for effect in expired_effects:
            del self.special_effects[effect]