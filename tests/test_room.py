import unittest
from src.game.room import Room
from src.game.state import GameState
from src.game.role import RoleType

class TestRoom(unittest.TestCase):
    def setUp(self):
        self.room = Room("test_room")
        
    def create_test_players(self, count: int):
        """創建指定數量的測試玩家"""
        for i in range(count):
            self.room.add_player(f"user_{i}", f"Player {i}")
            self.room.players[f"user_{i}"].toggle_ready()

    def test_add_player(self):
        result = self.room.add_player("test_user", "Test Player")
        self.assertTrue(result)
        self.assertIn("test_user", self.room.players)
        self.assertEqual(self.room.players["test_user"].display_name, "Test Player")

    def test_add_player_to_started_game(self):
        self.create_test_players(6)
        self.room.start_game()
        result = self.room.add_player("late_user", "Late Player")
        self.assertFalse(result)

    def test_assign_roles(self):
        self.create_test_players(6)
        result = self.room.assign_roles()
        self.assertTrue(result)
        
        # 檢查角色分配
        roles = [p.role.role_type for p in self.room.players.values()]
        self.assertIn(RoleType.WEREWOLF, roles)
        self.assertIn(RoleType.SEER, roles)
        self.assertIn(RoleType.WITCH, roles)
        self.assertIn(RoleType.HUNTER, roles)

    def test_start_game(self):
        self.create_test_players(6)
        result = self.room.start_game()
        self.assertTrue(result)
        self.assertEqual(self.room.game_state, GameState.NIGHT)
        self.assertEqual(self.room.day_count, 1)

    def test_start_game_with_insufficient_players(self):
        self.create_test_players(5)  # 少於最小人數
        result = self.room.start_game()
        self.assertFalse(result)
        self.assertEqual(self.room.game_state, GameState.WAITING)

    def test_vote_system(self):
        self.create_test_players(6)
        self.room.start_game()
        
        # 模擬投票
        voter_id = "user_0"
        target_id = "user_1"
        self.room.cast_vote(voter_id, target_id)
        
        target = self.room.players[target_id]
        self.assertEqual(target.get_vote_count(), 1)
        self.assertIn(voter_id, target.voted_by)

    def test_process_night_actions(self):
        self.create_test_players(6)
        self.room.start_game()
        
        # 模擬狼人殺人
        self.room.night_actions["werewolf_kill"] = "user_0"
        self.room.process_night_actions()
        
        # 檢查目標是否死亡
        target = self.room.players["user_0"]
        self.assertFalse(target.is_alive())

if __name__ == '__main__':
    unittest.main()