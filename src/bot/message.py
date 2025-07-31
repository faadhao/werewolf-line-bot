from linebot.models import TextSendMessage, TemplateSendMessage, ButtonsTemplate, MessageAction
from ..game.state import GameState
from ..game.role import RoleType
import random
from typing import List, Dict, Any

class GameMessage:
    @staticmethod
    def get_game_help() -> TextSendMessage:
        help_text = (
            "🐺 狼人殺遊戲指令說明 🐺\n\n"
            "📋 基本指令：\n"
            "/help - 顯示說明\n"
            "/join - 加入遊戲\n"
            "/ready - 準備開始\n"
            "/start - 開始遊戲\n"
            "/exit - 離開遊戲\n\n"
            "🎮 遊戲中指令：\n"
            "/vote [@玩家] - 投票處決\n"
            "/skill [@玩家] - 使用技能\n"
            "/status - 查看遊戲狀態"
        )
        return TextSendMessage(text=help_text)

    @staticmethod
    def get_error_message(error_type: str) -> TextSendMessage:
        error_messages = {
            "not_in_game": "您還未加入遊戲！",
            "game_started": "遊戲已經開始，無法加入！",
            "not_enough_players": "玩家人數不足，至少需要6人！",
            "wrong_phase": "現在不是使用此指令的時機！",
            "already_dead": "您已經死亡，無法執行此操作！",
            "invalid_target": "無效的目標玩家！",
            "skill_used": "您已經使用過技能了！",
            "not_your_turn": "現在不是您的回合！"
        }
        return TextSendMessage(text=error_messages.get(error_type, "發生未知錯誤！"))

    @staticmethod
    def get_role_instructions(role_type: RoleType) -> TextSendMessage:
        instructions = {
            RoleType.VILLAGER: "您是平民，請在白天積極發言找出狼人！",
            RoleType.WEREWOLF: "您是狼人，每晚可以殺死一名玩家。請小心隱藏身份！",
            RoleType.SEER: "您是預言家，每晚可以查驗一名玩家的身份。",
            RoleType.WITCH: "您是女巫，擁有一瓶解藥和一瓶毒藥。每種藥只能使用一次！",
            RoleType.HUNTER: "您是獵人，死亡時可以開槍帶走一名玩家。"
        }
        return TextSendMessage(text=instructions.get(role_type, "未知角色"))

    @staticmethod
    def get_night_action_prompt(role_type: RoleType) -> TextSendMessage:
        prompts = {
            RoleType.WEREWOLF: "請選擇要殺害的對象：\n使用 /skill @玩家名稱",
            RoleType.SEER: "請選擇要查驗的對象：\n使用 /skill @玩家名稱",
            RoleType.WITCH: "請選擇要使用藥水的對象：\n使用 /skill @玩家名稱",
            RoleType.HUNTER: "您可以選擇帶走一名玩家：\n使用 /skill @玩家名稱"
        }
        return TextSendMessage(text=prompts.get(role_type, ""))

    @staticmethod
    def get_death_announcement(player_name: str, role_name: str) -> TextSendMessage:
        return TextSendMessage(text=f"😱 {player_name} 死亡了！\n他的身份是：{role_name}")

    @staticmethod
    def get_game_summary(alive_players: list, day_count: int) -> TextSendMessage:
        summary = (
            f"第 {day_count} 天\n"
            f"存活玩家：{len(alive_players)}人\n"
            "玩家列表：\n" + 
            "\n".join([f"- {player.display_name}" for player in alive_players])
        )
        return TextSendMessage(text=summary)

    @staticmethod
    def get_voting_start() -> TextSendMessage:
        return TextSendMessage(text="投票環節開始！\n請使用 /vote @玩家名稱 進行投票")

    @staticmethod
    def get_voting_result(player_name: str, vote_count: int) -> TextSendMessage:
        return TextSendMessage(text=f"{player_name} 獲得了 {vote_count} 票，被處決！")

    @staticmethod
    def get_game_over(winner: str) -> TextSendMessage:
        return TextSendMessage(text=f"遊戲結束！{winner}獲得勝利！🎉")

    @staticmethod
    def get_spectator_help() -> TextSendMessage:
        help_text = (
            "🔍 觀戰模式指令：\n"
            "/spectate - 加入觀戰\n"
            "/history - 查看遊戲記錄\n"
            "/status - 查看當前遊戲狀態"
        )
        return TextSendMessage(text=help_text)

    @staticmethod
    def get_game_log(log_entries: List[str]) -> TextSendMessage:
        return TextSendMessage(text="📜 遊戲記錄：\n" + "".join(log_entries))

    @staticmethod
    def get_player_stats(stats: Dict[str, Any], player_name: str) -> TextSendMessage:
        win_rate = (stats["wins"] / stats["games_played"] * 100) if stats["games_played"] > 0 else 0
        
        stats_text = (
            f"📊 {player_name} 的遊戲統計\n\n"
            f"總場次：{stats['games_played']} 場\n"
            f"勝場：{stats['wins']} 場\n"
            f"敗場：{stats['losses']} 場\n"
            f"勝率：{win_rate:.1f}%\n\n"
            "🎭 角色統計：\n"
        )
        
        for role, count in stats["roles_played"].items():
            stats_text += f"{role}: {count} 次\n"
        
        if stats["last_played"]:
            stats_text += f"\n最後遊玩時間：\n{stats['last_played']}"
        
        return TextSendMessage(text=stats_text)

    @staticmethod
    def get_daily_tip() -> TextSendMessage:
        tips = [
            "💡 好人陣營要多觀察發言，找出破綻！",
            "💡 狼人要懂得互相掩護，避免露出馬腳。",
            "💡 預言家不要太早暴露身份。",
            "💡 女巫的解藥要謹慎使用。",
            "💡 獵人臨死前的一槍可能扭轉局勢！"
        ]
        return TextSendMessage(text=random.choice(tips))

    @staticmethod
    def get_config_status(config: Dict[str, Any]) -> TextSendMessage:
        config_text = (
            "🎮 遊戲配置\n\n"
            f"最小玩家數：{config['min_players']}\n"
            f"最大玩家數：{config['max_players']}\n"
            f"投票時間：{config['vote_timeout']}秒\n"
            f"討論時間：{config['discussion_time']}秒\n"
            f"夜晚時間：{config['night_timeout']}秒\n"
            f"特殊角色：{'開啟' if config['enable_special_roles'] else '關閉'}\n\n"
            "🎭 特殊效果：\n"
            f"女巫毒藥延遲：{config['special_effects']['witch_poison_delay']}回合\n"
            f"守衛連續守護：{'允許' if config['special_effects']['guard_self_protect'] else '禁止'}\n"
            f"預言家干擾率：{config['special_effects']['seer_fake_result_chance']*100}%"
        )
        return TextSendMessage(text=config_text)

    @staticmethod
    def get_timer_message(phase: str, remaining: int) -> TextSendMessage:
        return TextSendMessage(text=f"⏰ {phase}階段還剩 {remaining} 秒")

    @staticmethod
    def get_timeout_warning(phase: str) -> TextSendMessage:
        warnings = {
            "vote": "⚠️ 投票時間剩下30秒！還沒投票的玩家請盡快！",
            "night": "⚠️ 夜晚時間剩下30秒！請盡快使用技能！",
            "discussion": "⚠️ 討論時間剩下30秒！請總結發言！"
        }
        return TextSendMessage(text=warnings.get(phase, "時間即將結束！"))

    @staticmethod
    def get_join_success(player_name: str) -> TextSendMessage:
        """
        產生玩家成功加入遊戲的訊息
        
        Args:
            player_name (str): 玩家名稱
            
        Returns:
            TextSendMessage: Line 訊息物件
        """
        return TextSendMessage(text=f"{player_name} 成功加入遊戲！")
