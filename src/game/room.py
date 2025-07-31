from typing import Dict, List, Optional
import random
from .player import Player
from .role import Role, RoleType
from .state import GameState

class GameRoom:
    def __init__(self, room_id: str):
        self.room_id = room_id
        self.players: Dict[str, Player] = {}
        self.game_state = GameState.WAITING
        self.day_count = 0
        self.night_actions = {}  # 存儲夜晚行動
        self.witch_potion = {"heal": True, "poison": True}  # 女巫的藥水狀態
        self.current_turn = 0
        self.delayed_actions = []  # 延遲執行的動作

    def add_player(self, user_id: str, display_name: str) -> bool:
        if user_id not in self.players and self.game_state == GameState.WAITING:
            self.players[user_id] = Player(user_id, display_name)
            return True
        return False

    def remove_player(self, user_id: str) -> bool:
        if user_id in self.players and self.game_state == GameState.WAITING:
            del self.players[user_id]
            return True
        return False

    def assign_roles(self):
        players_count = len(self.players)
        if players_count < 6:
            return False

        # 根據玩家人數調整角色分配
        roles = []
        if players_count <= 7:
            # 6-7人局：2狼人
            roles = [RoleType.WEREWOLF] * 2
        elif players_count <= 9:
            # 8-9人局：3狼人
            roles = [RoleType.WEREWOLF] * 3
        else:
            # 10人以上：3狼人+1狼王
            roles = [RoleType.WEREWOLF] * 3 + [RoleType.WOLF_KING]

        # 神職配置
        roles.extend([
            RoleType.SEER,
            RoleType.WITCH,
            RoleType.HUNTER
        ])

        # 剩餘玩家為平民
        while len(roles) < players_count:
            roles.append(RoleType.VILLAGER)

        random.shuffle(roles)
        
        for player, role_type in zip(self.players.values(), roles):
            player.set_role(Role(role_type))

        return True

    def start_game(self) -> bool:
        if not all(player.is_ready for player in self.players.values()):
            return False
        
        if not self.assign_roles():
            return False

        self.game_state = GameState.NIGHT
        self.day_count = 1
        return True

    def get_alive_players(self) -> List[Player]:
        return [p for p in self.players.values() if p.is_alive()]

    def get_werewolves(self) -> List[Player]:
        return [p for p in self.players.values() 
                if p.is_alive() and p.role.role_type == RoleType.WEREWOLF]

    def use_skill(self, player: Player, target: Player) -> str:
        if player.role.role_type == RoleType.WEREWOLF:
            return self.handle_werewolf_kill(player, target)
        elif player.role.role_type == RoleType.SEER:
            return self.handle_seer_check(player, target)
        elif player.role.role_type == RoleType.WITCH:
            return self.handle_witch_action(player, target)
        elif player.role.role_type == RoleType.HUNTER:
            return self.handle_hunter_shoot(player, target)
        return "您沒有特殊技能可以使用"

    def handle_werewolf_kill(self, player: Player, target: Player) -> str:
        if target.role.role_type == RoleType.WEREWOLF:
            return "狼人不能殺死自己人！"
        
        self.night_actions["werewolf_kill"] = target.user_id
        return f"你選擇了要殺死 {target.display_name}"

    def handle_seer_check(self, player: Player, target: Player) -> str:
        is_werewolf = target.role.role_type == RoleType.WEREWOLF
        self.night_actions["seer_check"] = True
        return f"你查驗的結果是：{target.display_name} 是{'狼人' if is_werewolf else '好人'}"

    def handle_witch_action(self, player: Player, target: Player) -> str:
        if not self.witch_potion["heal"] and not self.witch_potion["poison"]:
            return "您已經沒有藥水可以使用了"
        
        # 這裡需要實作選擇使用解藥或毒藥的邏輯
        if self.night_actions.get("werewolf_kill") == target.user_id and self.witch_potion["heal"]:
            self.witch_potion["heal"] = False
            self.night_actions["witch_save"] = target.user_id
            return f"你使用解藥救活了 {target.display_name}"
        
        if self.witch_potion["poison"]:
            self.witch_potion["poison"] = False
            self.night_actions["witch_kill"] = target.user_id
            return f"你使用毒藥殺死了 {target.display_name}"
        
        return "無效的行動"

    def handle_hunter_shoot(self, player: Player, target: Player) -> str:
        if not player.is_alive():
            self.night_actions["hunter_shoot"] = target.user_id
            return f"你選擇射殺 {target.display_name}"
        return "獵人技能只能在死亡時使用"

    def process_night_actions(self):
        self.current_turn += 1
        
        # 處理守衛保護
        protected_id = self.night_actions.get("guard_protect")
        if protected_id:
            self.players[protected_id].role.protected_by_guard = True

        # 處理狼人擊殺
        if "werewolf_kill" in self.night_actions:
            target_id = self.night_actions["werewolf_kill"]
            target = self.players[target_id]
            
            # 檢查是否被守衛保護
            if not target.role.protected_by_guard:
                if "witch_save" not in self.night_actions or self.night_actions["witch_save"] != target_id:
                    target.role.kill()

        # 處理女巫毒藥
        if "witch_kill" in self.night_actions:
            if self.config.config["special_effects"]["witch_poison_delay"] > 0:
                self.delayed_actions.append({
                    "type": "poison",
                    "target": self.night_actions["witch_kill"],
                    "execute_turn": self.current_turn + self.config.config["special_effects"]["witch_poison_delay"]
                })
            else:
                self.players[self.night_actions["witch_kill"]].role.kill()

        # 處理延遲的動作
        self._process_delayed_actions()

        # 重置守衛保護狀態
        for player in self.players.values():
            player.role.protected_by_guard = False

        self.night_actions.clear()

    def _process_delayed_actions(self):
        remaining_actions = []
        for action in self.delayed_actions:
            if action["execute_turn"] <= self.current_turn:
                if action["type"] == "poison":
                    target = self.players[action["target"]]
                    target.role.kill()
            else:
                remaining_actions.append(action)
        self.delayed_actions = remaining_actions

    def cast_vote(self, voter_id: str, target_id: str):
        if voter_id in self.players and target_id in self.players:
            self.players[target_id].add_vote(voter_id)

    def process_votes(self) -> Optional[Player]:
        max_votes = 0
        eliminated_player = None
        
        for player in self.players.values():
            if player.get_vote_count() > max_votes:
                max_votes = player.get_vote_count()
                eliminated_player = player
            player.clear_votes()

        if eliminated_player:
            eliminated_player.role.kill()

        return eliminated_player

    def check_game_end(self) -> Optional[str]:
        werewolves = len([p for p in self.players.values() 
                          if p.is_alive() and p.role.role_type in 
                          [RoleType.WEREWOLF, RoleType.WOLF_KING]])
        villagers = len([p for p in self.players.values() 
                        if p.is_alive() and p.role.role_type not in 
                        [RoleType.WEREWOLF, RoleType.WOLF_KING]])
        
        # 特殊勝利條件：獵人復仇
        hunter_revenge = any(p for p in self.players.values()
                            if not p.is_alive() and 
                            p.role.role_type == RoleType.HUNTER and 
                            "hunter_shoot" in self.night_actions)

        if werewolves == 0 or hunter_revenge:
            return "好人陣營"
        elif werewolves >= villagers:
            return "狼人陣營"
        return None

    def check_night_phase_complete(self) -> bool:
        # 檢查是否所有角色都完成了夜晚行動
        required_actions = {"werewolf_kill", "seer_check"}
        return all(action in self.night_actions for action in required_actions)

    def start_night_phase(self):
        self.game_state = GameState.NIGHT
        self.day_count += 1
        self.night_actions.clear()