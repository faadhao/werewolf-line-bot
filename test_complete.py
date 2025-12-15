"""
測試腳本 - 驗證所有補完的功能
"""
import sys
import os

# 添加 src 到路徑
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_imports():
    """測試所有模組是否可以正確導入"""
    print("測試模組導入...")
    
    try:
        from game.room import GameRoom
        from game.player import Player
        from game.role import Role, RoleType
        from game.state import GameState
        from game.errors import GameError
        from utils.config import Config, GameConfig
        from utils.logger import GameLogger
        from utils.statistics import PlayerStats
        from utils.timer import GameTimer
        from utils.storage import GameStorage
        print("✓ 所有模組導入成功")
        return True
    except Exception as e:
        print(f"✗ 模組導入失敗: {e}")
        return False

def test_game_room():
    """測試 GameRoom 的新功能"""
    print("\n測試 GameRoom 功能...")
    
    try:
        from game.room import GameRoom
        from game.player import Player
        
        room = GameRoom("test_room")
        
        # 測試屬性是否存在
        assert hasattr(room, 'night_action_count'), "缺少 night_action_count 屬性"
        assert hasattr(room, 'is_werewolf_action_time'), "缺少 is_werewolf_action_time 屬性"
        assert hasattr(room, 'config'), "缺少 config 屬性"
        assert hasattr(room, 'votes'), "缺少 votes 屬性"
        
        # 測試新方法是否存在
        assert hasattr(room, 'check_night_complete'), "缺少 check_night_complete 方法"
        assert hasattr(room, 'check_voting_complete'), "缺少 check_voting_complete 方法"
        assert hasattr(room, 'start_day_phase'), "缺少 start_day_phase 方法"
        assert hasattr(room, 'get_vote_results'), "缺少 get_vote_results 方法"
        assert hasattr(room, 'handle_guard_protect'), "缺少 handle_guard_protect 方法"
        
        print("✓ GameRoom 所有新功能都存在")
        return True
    except Exception as e:
        print(f"✗ GameRoom 測試失敗: {e}")
        return False

def test_role():
    """測試 Role 的新功能"""
    print("\n測試 Role 功能...")
    
    try:
        from game.role import Role, RoleType
        
        role = Role(RoleType.WEREWOLF)
        
        # 測試新方法是否存在
        assert hasattr(role, 'kill'), "缺少 kill 方法"
        assert hasattr(role, 'get_role_name'), "缺少 get_role_name 方法"
        
        # 測試方法功能
        assert role.is_alive == True, "角色應該是存活的"
        role.kill()
        assert role.is_alive == False, "角色應該已死亡"
        
        role_name = role.get_role_name()
        assert role_name == "狼人", f"角色名稱應該是 '狼人'，但得到 '{role_name}'"
        
        print("✓ Role 所有新功能都正常")
        return True
    except Exception as e:
        print(f"✗ Role 測試失敗: {e}")
        return False

def test_message():
    """測試 Message 的新功能"""
    print("\n測試 GameMessage 功能...")
    
    try:
        from bot.message import GameMessage
        
        # 測試新方法是否存在
        assert hasattr(GameMessage, 'get_night_phase'), "缺少 get_night_phase 方法"
        assert hasattr(GameMessage, 'get_role_notice'), "缺少 get_role_notice 方法"
        assert hasattr(GameMessage, 'get_day_phase'), "缺少 get_day_phase 方法"
        
        # 測試方法是否可以調用
        night_msg = GameMessage.get_night_phase(1)
        role_msg = GameMessage.get_role_notice("測試玩家", "狼人")
        day_msg = GameMessage.get_day_phase(1)
        
        print("✓ GameMessage 所有新功能都正常")
        return True
    except Exception as e:
        print(f"✗ GameMessage 測試失敗: {e}")
        return False

def test_handler_imports():
    """測試 Handler 的導入是否正確"""
    print("\n測試 MessageHandler 導入...")
    
    try:
        # 注意：這裡只測試導入，不測試功能（因為需要 LINE Bot API）
        import bot.handler
        
        # 檢查是否導入了所需的模組
        from game.errors import GameError
        
        print("✓ MessageHandler 導入正常")
        return True
    except Exception as e:
        print(f"✗ MessageHandler 導入失敗: {e}")
        return False

def test_game_flow():
    """測試完整的遊戲流程"""
    print("\n測試遊戲流程...")
    
    try:
        from game.room import GameRoom
        from game.state import GameState
        
        room = GameRoom("test_room")
        
        # 添加玩家
        for i in range(6):
            room.add_player(f"user_{i}", f"玩家{i}")
        
        # 準備玩家
        for player in room.players.values():
            player.toggle_ready()
        
        # 開始遊戲
        success = room.start_game()
        assert success, "遊戲應該成功開始"
        assert room.game_state == GameState.NIGHT, "遊戲狀態應該是夜晚"
        
        # 檢查角色是否已分配
        for player in room.players.values():
            assert player.role is not None, "每個玩家都應該有角色"
        
        print("✓ 遊戲流程測試通過")
        return True
    except Exception as e:
        print(f"✗ 遊戲流程測試失敗: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """執行所有測試"""
    print("=" * 50)
    print("開始測試補完的功能")
    print("=" * 50)
    
    results = []
    
    results.append(("模組導入", test_imports()))
    results.append(("GameRoom", test_game_room()))
    results.append(("Role", test_role()))
    results.append(("GameMessage", test_message()))
    results.append(("Handler導入", test_handler_imports()))
    results.append(("遊戲流程", test_game_flow()))
    
    print("\n" + "=" * 50)
    print("測試結果總結")
    print("=" * 50)
    
    passed = 0
    failed = 0
    
    for name, result in results:
        status = "✓ 通過" if result else "✗ 失敗"
        print(f"{name}: {status}")
        if result:
            passed += 1
        else:
            failed += 1
    
    print(f"\n總計: {passed} 通過, {failed} 失敗")
    
    if failed == 0:
        print("\n🎉 所有測試通過！功能補完成功！")
    else:
        print(f"\n⚠️ 有 {failed} 個測試失敗，請檢查相關功能")
    
    return failed == 0

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
