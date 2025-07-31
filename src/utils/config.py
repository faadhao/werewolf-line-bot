# src/utils/config.py
import os
from dotenv import load_dotenv
from typing import Dict, Any
import json

# 配置設定
LINE_CHANNEL_ACCESS_TOKEN = '你的_CHANNEL_ACCESS_TOKEN'
LINE_CHANNEL_SECRET = '你的_CHANNEL_SECRET'

class Config:
    def __init__(self):
        load_dotenv()
        self.CHANNEL_ACCESS_TOKEN = os.getenv('LINE_CHANNEL_ACCESS_TOKEN')
        self.CHANNEL_SECRET = os.getenv('LINE_CHANNEL_SECRET')

class GameConfig:
    DEFAULT_CONFIG = {
        "min_players": 6,
        "max_players": 12,
        "vote_timeout": 120,  # 秒
        "discussion_time": 180,  # 秒
        "night_timeout": 90,  # 秒
        "enable_special_roles": True,
        "role_distribution": {
            "6-7": {"werewolf": 2, "special_roles": 3},
            "8-9": {"werewolf": 3, "special_roles": 3},
            "10+": {"werewolf": 4, "special_roles": 4}
        },
        "special_effects": {
            "witch_poison_delay": 1,  # 女巫毒藥延遲生效回合
            "guard_self_protect": False,  # 守衛是否能連續守護同一人
            "seer_fake_result_chance": 0.1  # 預言家查驗結果被干擾的機率
        }
    }

    def __init__(self, config_file: str = "game_config.json"):
        self.config_file = config_file
        self.config = self._load_config()

    def _load_config(self) -> Dict[str, Any]:
        if os.path.exists(self.config_file):
            with open(self.config_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return self.DEFAULT_CONFIG.copy()

    def save_config(self):
        with open(self.config_file, 'w', encoding='utf-8') as f:
            json.dump(self.config, f, ensure_ascii=False, indent=2)

    def update_config(self, new_config: Dict[str, Any]):
        self.config.update(new_config)
        self.save_config()

    def get_role_distribution(self, player_count: int) -> Dict[str, int]:
        if player_count <= 7:
            return self.config["role_distribution"]["6-7"]
        elif player_count <= 9:
            return self.config["role_distribution"]["8-9"]
        return self.config["role_distribution"]["10+"]