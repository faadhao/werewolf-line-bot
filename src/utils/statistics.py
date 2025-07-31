import json
import os
from typing import Dict, Any
from datetime import datetime

class PlayerStats:
    def __init__(self, stats_file: str = "player_stats.json"):
        self.stats_file = stats_file
        self.stats = self._load_stats()

    def _load_stats(self) -> Dict[str, Any]:
        if os.path.exists(self.stats_file):
            with open(self.stats_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {}

    def _save_stats(self):
        with open(self.stats_file, 'w', encoding='utf-8') as f:
            json.dump(self.stats, f, ensure_ascii=False, indent=2)

    def update_player_stats(self, user_id: str, game_result: Dict[str, Any]):
        if user_id not in self.stats:
            self.stats[user_id] = {
                "games_played": 0,
                "wins": 0,
                "losses": 0,
                "roles_played": {},
                "last_played": None
            }

        stats = self.stats[user_id]
        stats["games_played"] += 1
        stats["last_played"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        if game_result["won"]:
            stats["wins"] += 1
        else:
            stats["losses"] += 1

        role = game_result["role"]
        if role not in stats["roles_played"]:
            stats["roles_played"][role] = 0
        stats["roles_played"][role] += 1

        self._save_stats()

    def get_player_stats(self, user_id: str) -> Dict[str, Any]:
        return self.stats.get(user_id, {
            "games_played": 0,
            "wins": 0,
            "losses": 0,
            "roles_played": {},
            "last_played": None
        })