#!/usr/bin/env python3
"""
Simple test script for Corporate Crusader
Tests core game logic without requiring pygame
"""

import sys
import os

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_game_core():
    """Test core game functionality"""
    print("🏢 Corporate Crusader - Core System Test 🏢")
    print("=" * 50)
    
    try:
        # Test entity imports
        from src.entities.player import Player
        from src.entities.enemy import Enemy, get_random_enemy
        from src.entities.item import Item, ITEMS_CATALOG
        from src.entities.ability import Ability, ABILITIES
        print("✅ Entity classes imported successfully")
        
        # Test player creation
        player = Player("Test Executive")
        print(f"✅ Player created: {player.name} (Level {player.level})")
        
        # Test enemy creation
        enemy = get_random_enemy(1)
        print(f"✅ Enemy created: {enemy.name} ({enemy.enemy_type})")
        
        # Test items
        print(f"✅ Items loaded: {len(ITEMS_CATALOG)} different items")
        
        # Test abilities
        print(f"✅ Abilities loaded: {len(ABILITIES)} corporate skills")
        
        # Test combat system
        from src.systems.combat import CombatState
        combat = CombatState(player, enemy)
        print(f"✅ Combat system initialized (Turn {combat.turn_count})")
        
        # Test save system
        from src.systems.save_manager import SaveManager
        save_manager = SaveManager()
        print("✅ Save system initialized")
        
        # Test game engine
        from src.game import GameState
        game = GameState()
        print("✅ Game engine initialized")
        
        print("\n🎉 All core systems working!")
        print("The game is ready to run with: python main.py")
        print("(Requires pygame for the graphical interface)")
        
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_game_logic():
    """Test game logic without UI"""
    print("\n🔧 Testing Game Logic...")
    
    try:
        from src.entities.player import Player
        from src.entities.enemy import get_random_enemy
        from src.systems.combat import CombatState
        
        # Create test scenario
        player = Player("Corporate Warrior")
        enemy = get_random_enemy(1)
        
        print(f"Player: {player.name} vs {enemy.name}")
        print(f"Player Stats: H:{player.health} C:{player.caffeine} S:{player.stress}")
        
        # Test combat
        combat = CombatState(player, enemy)
        
        # Simulate a turn
        result = combat.process_turn("attack")
        print(f"Attack result: {result.get('success', False)}")
        
        # Test ability usage
        if player.abilities:
            ability = player.abilities[0]
            result = combat.process_turn("ability", ability=ability)
            print(f"Ability '{ability.name}' result: {result.get('success', False)}")
        
        print("✅ Game logic test completed successfully!")
        return True
        
    except Exception as e:
        print(f"❌ Game logic error: {e}")
        return False

if __name__ == "__main__":
    print("Starting Corporate Crusader test suite...\n")
    
    core_test = test_game_core()
    logic_test = test_game_logic()
    
    if core_test and logic_test:
        print("\n🚀 All tests passed! The game is ready to play!")
        exit_code = 0
    else:
        print("\n💥 Some tests failed. Check the errors above.")
        exit_code = 1
    
    sys.exit(exit_code)