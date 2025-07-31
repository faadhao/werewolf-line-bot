from enum import Enum

class GameState(Enum):
    WAITING = "等待中"
    NIGHT = "夜晚"
    DAY = "白天"
    VOTING = "投票中"
    ENDED = "遊戲結束"