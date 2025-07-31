import unittest
from unittest.mock import Mock, patch
from linebot.models import MessageEvent, TextMessage, Source
from src.bot.handler import MessageHandler
from src.game.room import GameRoom
from src.game.state import GameState
from src.game.role import RoleType

class TestMessageHandler(unittest.TestCase):
    def setUp(self):
        self.line_bot_api = Mock()
        self.handler = MessageHandler(self.line_bot_api)
        self.group_id = "test_group"
        self.user_id = "test_user"
        
    def create_test_event(self, message_text: str) -> MessageEvent:
        return MessageEvent(
            message=TextMessage(text=message_text),
            source=Source(group_id=self.group_id, user_id=self.user_id, type='group')
        )

    def test_help_command(self):
        event = self.create_test_event("/help")
        self.handler.handle_text_message(event)
        self.line_bot_api.reply_message.assert_called_once()

    def test_join_game(self):
        event = self.create_test_event("/join")
        self.line_bot_api.get_group_member_profile.return_value.display_name = "Test Player"
        
        self.handler.handle_text_message(event)
        
        self.assertIn(self.group_id, self.handler.rooms)
        room = self.handler.rooms[self.group_id]
        self.assertIn(self.user_id, room.players)
        self.line_bot_api.reply_message.assert_called_once()

    def test_ready_command(self):
        # 設置遊戲房間和玩家
        room = GameRoom(self.group_id)
        room.add_player(self.user_id, "Test Player")
        self.handler.rooms[self.group_id] = room
        
        event = self.create_test_event("/ready")
        self.handler.handle_text_message(event)
        
        self.assertTrue(room.players[self.user_id].is_ready)
        self.line_bot_api.reply_message.assert_called_once()

    @patch('random.shuffle')  # 防止角色隨機分配
    def test_start_game(self, mock_shuffle):
        # 創建足夠的測試玩家
        room = GameRoom(self.group_id)
        for i in range(6):
            user_id = f"test_user_{i}"
            room.add_player(user_id, f"Player {i}")
            room.players[user_id].toggle_ready()
        
        self.handler.rooms[self.group_id] = room
        
        event = self.create_test_event("/start")
        self.handler.handle_text_message(event)
        
        self.assertEqual(room.game_state, GameState.NIGHT)
        self.assertEqual(room.day_count, 1)

    def test_invalid_command_in_wrong_phase(self):
        room = GameRoom(self.group_id)
        room.game_state = GameState.NIGHT
        self.handler.rooms[self.group_id] = room
        
        event = self.create_test_event("/join")
        self.handler.handle_text_message(event)
        
        self.line_bot_api.reply_message.assert_called_with(
            event.reply_token,
            unittest.mock.ANY  # 驗證錯誤訊息被發送
        )

if __name__ == '__main__':
    unittest.main()