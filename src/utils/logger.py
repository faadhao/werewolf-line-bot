import os
from datetime import datetime
from typing import List

class GameLogger:
    def __init__(self, log_dir: str = "game_logs"):
        self.log_dir = log_dir
        os.makedirs(log_dir, exist_ok=True)

    def log_game_event(self, room_id: str, event: str):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_file = os.path.join(self.log_dir, f"{room_id}_{datetime.now().strftime('%Y%m%d')}.log")
        
        with open(log_file, 'a', encoding='utf-8') as f:
            f.write(f"[{timestamp}] {event}\n")

    def get_game_history(self, room_id: str) -> List[str]:
        log_file = os.path.join(self.log_dir, f"{room_id}_{datetime.now().strftime('%Y%m%d')}.log")
        if not os.path.exists(log_file):
            return []
            
        with open(log_file, 'r', encoding='utf-8') as f:
            return f.readlines()