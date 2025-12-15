import json
import os
from typing import Dict
from ..game.room import GameRoom
from ..game.player import Player
from ..game.role import Role, RoleType
from ..game.state import GameState

class GameStorage:
    def __init__(self, storage_dir: str = "game_data"):
        self.storage_dir = storage_dir
        os.makedirs(storage_dir, exist_ok=True)

    def save_game(self, room: GameRoom) -> bool:
        try:
            game_data = {
                "room_id": room.room_id,
                "game_state": room.game_state.value,
                "day_count": room.day_count,
                "players": [
                    {
                        "user_id": player.user_id,
                        "display_name": player.display_name,
                        "role": player.role.role_type.value if player.role else None,
                        "is_alive": player.is_alive(),
                        "is_ready": player.is_ready
                    }
                    for player in room.players.values()
                ],
                "witch_potion": room.witch_potion,
                "night_actions": room.night_actions
            }
            
            file_path = os.path.join(self.storage_dir, f"{room.room_id}.json")
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(game_data, f, ensure_ascii=False, indent=2)
            return True
            
        except Exception as e:
            print(f"保存遊戲失敗: {str(e)}")
            return False

    def load_game(self, room_id: str) -> GameRoom:
        try:
            file_path = os.path.join(self.storage_dir, f"{room_id}.json")
            if not os.path.exists(file_path):
                return None

            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)

            room = GameRoom(room_id)
            room.game_state = GameState(data["game_state"])
            room.day_count = data["day_count"]
            room.witch_potion = data["witch_potion"]
            room.night_actions = data["night_actions"]

            for player_data in data["players"]:
                player = Player(player_data["user_id"], player_data["display_name"])
                player.is_ready = player_data["is_ready"]
                if player_data["role"]:
                    role = Role(RoleType(player_data["role"]))
                    if not player_data["is_alive"]:
                        role.kill()
                    player.set_role(role)
                room.players[player.user_id] = player

            return room

        except Exception as e:
            print(f"讀取遊戲失敗: {str(e)}")
            return None