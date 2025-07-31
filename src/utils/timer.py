import threading
import time
from typing import Callable, Dict, Any

class GameTimer:
    def __init__(self):
        self.timers: Dict[str, threading.Timer] = {}
        self.start_times: Dict[str, float] = {}

    def start_timer(self, room_id: str, duration: int, callback: Callable, phase: str):
        # 取消該房間現有的計時器
        self.cancel_timer(room_id)
        
        # 設置新的計時器
        timer = threading.Timer(duration, callback)
        timer.start()
        
        self.timers[room_id] = timer
        self.start_times[room_id] = time.time()

    def cancel_timer(self, room_id: str):
        if room_id in self.timers:
            self.timers[room_id].cancel()
            del self.timers[room_id]
            del self.start_times[room_id]

    def get_remaining_time(self, room_id: str) -> int:
        if room_id in self.start_times:
            elapsed = time.time() - self.start_times[room_id]
            total_duration = self.timers[room_id].interval
            remaining = max(0, total_duration - elapsed)
            return int(remaining)
        return 0