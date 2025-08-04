from linebot import LineBotApi
from linebot.models import MessageEvent, TextMessage
from typing import Dict, List
from ..game.room import GameRoom
from ..game.state import GameState
from .message import GameMessage
from ..utils.storage import GameStorage
from ..utils.logger import GameLogger
from ..utils.statistics import PlayerStats
from ..utils.timer import GameTimer

class MessageHandler:
    def __init__(self, line_bot_api: LineBotApi):
        self.line_bot_api = line_bot_api
        self.rooms: Dict[str, GameRoom] = {}
        self.storage = GameStorage()
        self.logger = GameLogger()
        self.spectators: Dict[str, List[str]] = {}  # group_id -> List[user_id]
        self.player_stats = PlayerStats()
        self.timer = GameTimer()

    def handle_text_message(self, event: MessageEvent):
        # 區分群組訊息和私聊訊息
        if event.source.type == 'user':  # 私聊訊息
            self.handle_private_message(event)
            return
            
        # 群組訊息處理
        if not hasattr(event.source, 'group_id'):
            self.line_bot_api.reply_message(
                event.reply_token,
                TextMessage(text="此遊戲只能在群組中進行！")
            )
            return

        group_id = event.source.group_id
        user_id = event.source.user_id
        message = event.message.text

        if message.startswith('/'):
            self.handle_command(message, group_id, user_id, event.reply_token)

    def handle_command(self, message: str, group_id: str, user_id: str, reply_token: str):
        # 嘗試讀取已存在的遊戲
        if group_id not in self.rooms:
            loaded_room = self.storage.load_game(group_id)
            if loaded_room:
                self.rooms[group_id] = loaded_room

        command = message.lower().split()[0]

        if command == '/help':
            self.line_bot_api.reply_message(
                reply_token,
                GameMessage.get_game_help()
            )
            return

        if command == '/join':
            if group_id not in self.rooms:
                self.rooms[group_id] = GameRoom(group_id)

            room = self.rooms[group_id]
            user_profile = self.line_bot_api.get_group_member_profile(group_id, user_id)
            
            if room.add_player(user_id, user_profile.display_name):
                self.line_bot_api.reply_message(
                    reply_token,
                    GameMessage.get_join_success(user_profile.display_name)
                )
            return

        if command == '/ready':
            if group_id in self.rooms:
                room = self.rooms[group_id]
                if user_id in room.players:
                    room.players[user_id].toggle_ready()
                    self.update_game_status(room, reply_token)
            return

        if command == '/start':
            if group_id in self.rooms:
                room = self.rooms[group_id]
                if room.start_game():
                    self.start_game(room, reply_token)
            return

        if command == '/skill':
            if group_id in self.rooms:
                room = self.rooms[group_id]
                # 解析目標玩家
                target_id = self.parse_target_user_id(message)
                if target_id:
                    self.handle_skill_usage(room, user_id, target_id, reply_token)
            return

        if command == '/vote':
            if group_id in self.rooms:
                room = self.rooms[group_id]
                if room.game_state == GameState.VOTING:
                    target_id = self.parse_target_user_id(message)
                    if target_id:
                        self.handle_voting(room, user_id, target_id, reply_token)
            return

        if command == '/spectate':
            if group_id in self.rooms:
                if group_id not in self.spectators:
                    self.spectators[group_id] = []
                if user_id not in self.spectators[group_id]:
                    self.spectators[group_id].append(user_id)
                    self.line_bot_api.reply_message(
                        reply_token,
                        TextMessage(text="已加入觀戰模式！")
                    )
            return

        if command == '/history':
            if group_id in self.rooms:
                history = self.logger.get_game_history(group_id)
                if history:
                    self.line_bot_api.reply_message(
                        reply_token,
                        TextMessage(text="".join(history[-10:]))  # 只顯示最近10條記錄
                    )
            return

        if command == '/stats':
            user_profile = self.line_bot_api.get_group_member_profile(group_id, user_id)
            stats = self.player_stats.get_player_stats(user_id)
            self.line_bot_api.reply_message(
                reply_token,
                GameMessage.get_player_stats(stats, user_profile.display_name)
            )
            return

        if command == '/tip':
            self.line_bot_api.reply_message(
                reply_token,
                GameMessage.get_daily_tip()
            )
            return

        if command == '/time':
            if group_id in self.rooms:
                room = self.rooms[group_id]
                remaining = self.timer.get_remaining_time(room.room_id)
                self.line_bot_api.reply_message(
                    reply_token,
                    GameMessage.get_timer_message(room.game_state.value, remaining)
                )
            return

        # 在每次重要操作後保存遊戲狀態
        if group_id in self.rooms:
            self.storage.save_game(self.rooms[group_id])

    def parse_target_user_id(self, message: str) -> str:
        # 從 @提及中提取用戶ID
        parts = message.split()
        if len(parts) > 1 and parts[1].startswith('@'):
            return parts[1][1:]  # 移除 @ 符號
        return None

    def log_and_broadcast(self, room: GameRoom, message: str):
        """記錄遊戲事件並廣播給玩家和觀戰者"""
        self.logger.log_game_event(room.room_id, message)
        
        for group_id, game_room in self.rooms.items():
            if game_room == room:
                # 發送給群組
                self.line_bot_api.push_message(
                    group_id,
                    TextMessage(text=message)
                )
                
                # 發送給觀戰者
                if group_id in self.spectators:
                    for spectator_id in self.spectators[group_id]:
                        self.line_bot_api.push_message(
                            spectator_id,
                            TextMessage(text=f"[觀戰] {message}")
                        )
                break

    def handle_skill_usage(self, room: GameRoom, user_id: str, target_id: str, reply_token: str):
        try:
            if user_id not in room.players:
                raise GameError("not_in_game")
            
            player = room.players[user_id]
            target = room.players.get(target_id)
            
            if not player.is_alive():
                raise GameError("already_dead")
                
            if not target:
                raise GameError("invalid_target")
                
            if room.game_state != GameState.NIGHT:
                raise GameError("wrong_phase")
                
            result = room.use_skill(player, target)
            room.night_action_count += 1
            
            # 檢查夜晚階段是否結束
            if room.check_night_complete():
                self.start_day_phase(room)
            
        except GameError as e:
            self.line_bot_api.reply_message(
                reply_token,
                GameMessage.get_error_message(str(e))
            )

    def handle_voting(self, room: GameRoom, voter_id: str, target_id: str, reply_token: str):
        if voter_id not in room.players or target_id not in room.players:
            return

        voter = room.players[voter_id]
        target = room.players[target_id]

        if not voter.is_alive():
            return

        room.cast_vote(voter_id, target_id)
        self.line_bot_api.reply_message(
            reply_token,
            TextSendMessage(text=f"{voter.display_name} 投票給了 {target.display_name}")
        )

        self.log_and_broadcast(
            room,
            f"{voter.display_name} 投票給了 {target.display_name}"
        )

        if room.check_voting_complete():
            self.handle_voting_result(room)

    def update_game_status(self, room: GameRoom, reply_token: str):
        # 準備玩家列表資訊
        players_info = "\n".join([
            f"{'✅' if player.is_ready else '❌'} {player.display_name}" + 
            (f" (已死亡)" if not player.is_alive() and room.game_state != GameState.WAITING else "")
            for player in room.players.values()
        ])
        
        # 發送遊戲狀態
        self.line_bot_api.reply_message(
            reply_token,
            GameMessage.get_game_status(
                room.game_state,
                players_info,
                room.day_count
            )
        )

    def start_game(self, room: GameRoom, reply_token: str):
        # 發送遊戲開始通知
        self.line_bot_api.reply_message(
            reply_token,
            GameMessage.get_night_phase(room.day_count)
        )
        
        # 私下通知每個玩家他們的角色
        for player in room.players.values():
            self.line_bot_api.push_message(
                player.user_id,
                GameMessage.get_role_notice(
                    player.display_name,
                    player.role.get_role_name()
                )
            )

    def start_day_phase(self, room: GameRoom):
        # 處理夜晚行動結果
        room.start_day_phase()
        
        # 檢查遊戲是否結束
        winner = room.check_game_end()
        if winner:
            self.announce_winner(room, winner)
            return

        # 通知所有玩家進入白天
        for group_id, game_room in self.rooms.items():
            if game_room == room:
                self.line_bot_api.multicast(
                    [p.user_id for p in room.players.values()],
                    [GameMessage.get_day_phase(room.day_count)]
                )
                break

        # 開始投票階段
        self.start_voting_phase(room)

    def start_voting_phase(self, room: GameRoom):
        room.game_state = GameState.VOTING
        
        # 設置投票計時器
        def voting_timeout():
            self.handle_voting_result(room)
            
        self.timer.start_timer(
            room.room_id,
            room.config.config["vote_timeout"],
            voting_timeout,
            "vote"
        )
        
        # 設置30秒警告
        def warning_callback():
            self.line_bot_api.push_message(
                group_id,
                GameMessage.get_timeout_warning("vote")
            )
            
        warning_time = room.config.config["vote_timeout"] - 30
        if warning_time > 0:
            threading.Timer(warning_time, warning_callback).start()

    def handle_voting_result(self, room: GameRoom):
        eliminated_player = room.process_votes()
        
        for group_id, game_room in self.rooms.items():
            if game_room == room:
                if eliminated_player:
                    self.line_bot_api.push_message(
                        group_id,
                        TextSendMessage(text=f"{eliminated_player.display_name} 被投票處決了！")
                    )
                
                # 檢查遊戲是否結束
                winner = room.check_game_end()
                if winner:
                    self.announce_winner(room, winner)
                else:
                    room.start_night_phase()
                    self.line_bot_api.push_message(
                        group_id,
                        GameMessage.get_night_phase(room.day_count)
                    )
                break

    def announce_winner(self, room: GameRoom, winner: str):
        for group_id, game_room in self.rooms.items():
            if game_room == room:
                self.line_bot_api.push_message(
                    group_id,
                    TextSendMessage(text=f"遊戲結束！{winner}獲勝！")
                )
                del self.rooms[group_id]
                break

    def end_game(self, room: GameRoom, winner: str):
        # 更新玩家統計
        for player in room.players.values():
            self.player_stats.update_player_stats(
                player.user_id,
                {
                    "won": (
                        (winner == "好人陣營" and player.role.role_type != RoleType.WEREWOLF) or
                        (winner == "狼人陣營" and player.role.role_type == RoleType.WEREWOLF)
                    ),
                    "role": player.role.get_role_name()
                }
            )

    def handle_private_message(self, event: MessageEvent):
        user_id = event.source.user_id
        message = event.message.text
        
        # 尋找玩家所在的遊戲房間
        current_room = None
        for room in self.rooms.values():
            if user_id in room.players:
                current_room = room
                break
        
        if not current_room:
            self.line_bot_api.reply_message(
                event.reply_token,
                GameMessage.get_error_message("not_in_game")
            )
            return

        player = current_room.players[user_id]

        if message.startswith('/skill'):
            # 檢查是否是死亡玩家（獵人或狼王可以死後使用技能）
            if not player.is_alive() and player.role.role_type not in [RoleType.HUNTER, RoleType.WOLF_KING]:
                self.line_bot_api.reply_message(
                    event.reply_token,
                    GameMessage.get_error_message("already_dead")
                )
                return

            # 檢查是否在正確的遊戲階段
            if current_room.game_state != GameState.NIGHT:
                self.line_bot_api.reply_message(
                    event.reply_token,
                    GameMessage.get_error_message("wrong_phase")
                )
                return

            # 檢查是否已經使用過技能
            if player.role.skill_used and player.role.role_type in [RoleType.WITCH, RoleType.SEER]:
                self.line_bot_api.reply_message(
                    event.reply_token,
                    GameMessage.get_error_message("skill_used")
                )
                return

            # 檢查是否是狼人團隊成員且不是單獨行動的時間
            if (player.role.role_type == RoleType.WEREWOLF and 
                not current_room.is_werewolf_action_time):
                self.line_bot_api.reply_message(
                    event.reply_token,
                    GameMessage.get_error_message("not_your_turn")
                )
                return
                 
            # 解析目標玩家
            target_id = self.parse_target_user_id(message)
            if target_id:
                self.handle_skill_usage(current_room, user_id, target_id, event.reply_token)
        else:
            # 其他私訊命令的處理
            self.line_bot_api.reply_message(
                event.reply_token,
                GameMessage.get_error_message("invalid_command")
            )