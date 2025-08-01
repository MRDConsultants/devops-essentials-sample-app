#!/usr/bin/env python3
"""
Corporate Crusader - Text Mode
A text-based version for environments without pygame
"""

import sys
import os
import random

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.entities.player import Player
from src.entities.enemy import get_random_enemy
from src.entities.item import ITEMS_CATALOG
from src.systems.combat import CombatState
from src.game import GameState

class TextUI:
    def __init__(self):
        self.game = GameState()
        self.running = True
    
    def run(self):
        """Main text-based game loop"""
        self.print_header()
        self.main_menu()
    
    def print_header(self):
        """Print the game header"""
        print("=" * 60)
        print("🏢 CORPORATE CRUSADER 🏢")
        print("Text Mode - Climb the Corporate Ladder!")
        print("=" * 60)
        print()
    
    def main_menu(self):
        """Display main menu"""
        while self.running:
            print("\n📋 MAIN MENU")
            print("1. New Game")
            print("2. Quick Demo")
            print("3. Quit")
            
            choice = input("\nSelect option (1-3): ").strip()
            
            if choice == "1":
                self.new_game()
            elif choice == "2":
                self.quick_demo()
            elif choice == "3":
                print("Thanks for playing Corporate Crusader!")
                self.running = False
            else:
                print("Invalid choice. Please try again.")
    
    def new_game(self):
        """Start a new game"""
        print("\n🆕 NEW GAME")
        name = input("Enter your corporate climber name: ").strip()
        if not name:
            name = "Corporate Warrior"
        
        result = self.game.start_new_game(name)
        print(f"\nWelcome, {name}! You begin as an unpaid intern.")
        
        self.exploration_loop()
    
    def exploration_loop(self):
        """Main exploration loop"""
        while self.running and self.game.player and self.game.player.health > 0:
            self.display_player_status()
            options = self.game.get_exploration_options()
            
            print(f"\n🏢 Floor {options.get('floor', 1)} - {options.get('encounters_left', 0)} encounters remaining")
            print("\nAvailable actions:")
            
            for i, action in enumerate(options.get('actions', []), 1):
                print(f"{i}. {action['name']} - {action['description']}")
            
            print("0. Return to Main Menu")
            
            try:
                choice = int(input("\nSelect action: ").strip())
                
                if choice == 0:
                    break
                elif 1 <= choice <= len(options.get('actions', [])):
                    action = options['actions'][choice - 1]
                    self.handle_exploration_action(action['id'])
                else:
                    print("Invalid choice.")
            except ValueError:
                print("Please enter a number.")
    
    def handle_exploration_action(self, action_id):
        """Handle exploration actions"""
        result = self.game.process_exploration_action(action_id)
        
        if result.get('message'):
            print(f"\n📢 {result['message']}")
        
        if result.get('encounter_type') == 'combat':
            self.combat_loop()
        elif result.get('new_scene') == 'shop':
            self.shop_interface()
    
    def combat_loop(self):
        """Handle combat encounters"""
        combat = self.game.current_combat
        if not combat:
            return
        
        print("\n⚔️ COMBAT ENCOUNTER!")
        print(f"You face: {combat.enemy.name}")
        print(combat.enemy.get_dialogue('intro'))
        
        while combat.is_active:
            # Display combat status
            state = combat.get_combat_state()
            print(f"\n--- Turn {state['turn_count']} ---")
            print(f"YOU: Health {state['player']['health']}/{state['player']['max_health']}, "
                  f"Caffeine {state['player']['caffeine']}/{state['player']['max_caffeine']}")
            print(f"ENEMY: Health {state['enemy']['health']}/{state['enemy']['max_health']}")
            
            if state['player_turn']:
                print("\nYour turn!")
                print("1. Attack")
                print("2. Use Ability")
                print("3. Use Item")
                print("4. Flee")
                
                try:
                    choice = int(input("Choose action (1-4): ").strip())
                    
                    if choice == 1:
                        result = self.game.process_combat_action("attack")
                    elif choice == 2:
                        self.ability_menu()
                        continue
                    elif choice == 3:
                        self.item_menu()
                        continue
                    elif choice == 4:
                        result = self.game.process_combat_action("flee")
                    else:
                        print("Invalid choice.")
                        continue
                    
                    # Display results
                    for message in result.get('messages', []):
                        print(f"📣 {message}")
                
                except ValueError:
                    print("Please enter a number.")
                    continue
            else:
                print("\nEnemy's turn...")
                result = self.game.process_combat_action("attack")  # AI handles enemy turn
                for message in result.get('messages', []):
                    print(f"📣 {message}")
        
        # Combat ended
        if combat.victory == 'player':
            print("\n🎉 Victory! You have successfully managed the corporate encounter!")
            if 'rewards' in result:
                rewards = result['rewards']
                print(f"Gained: {rewards.get('experience', 0)} XP, {rewards.get('office_supplies', 0)} supplies")
        elif combat.victory == 'enemy':
            print("\n💀 Defeat! You have been corporately restructured...")
        elif combat.victory == 'fled':
            print("\n🏃 You successfully extracted yourself from the situation!")
    
    def ability_menu(self):
        """Show ability selection menu"""
        if not self.game.player.abilities:
            print("No abilities available.")
            return
        
        print("\n🎯 ABILITIES:")
        available_abilities = [a for a in self.game.player.abilities if self.game.player.can_use_ability(a)]
        
        if not available_abilities:
            print("No abilities can be used right now.")
            return
        
        for i, ability in enumerate(available_abilities, 1):
            print(f"{i}. {ability.name} (Cost: {ability.caffeine_cost} caffeine)")
            print(f"   {ability.description}")
        
        print("0. Back")
        
        try:
            choice = int(input("Select ability: ").strip())
            if choice == 0:
                return
            elif 1 <= choice <= len(available_abilities):
                ability = available_abilities[choice - 1]
                result = self.game.process_combat_action("ability", ability=ability)
                for message in result.get('messages', []):
                    print(f"📣 {message}")
        except ValueError:
            print("Invalid choice.")
    
    def item_menu(self):
        """Show item usage menu"""
        consumables = [item for item in self.game.player.inventory if item.is_consumable]
        
        if not consumables:
            print("No usable items.")
            return
        
        print("\n🎒 ITEMS:")
        for i, item in enumerate(consumables, 1):
            print(f"{i}. {item.name} - {item.description}")
        
        print("0. Back")
        
        try:
            choice = int(input("Select item: ").strip())
            if choice == 0:
                return
            elif 1 <= choice <= len(consumables):
                item = consumables[choice - 1]
                result = self.game.process_combat_action("item", item=item)
                for message in result.get('messages', []):
                    print(f"📣 {message}")
        except ValueError:
            print("Invalid choice.")
    
    def shop_interface(self):
        """Handle shop interactions"""
        print("\n🛒 OFFICE SUPPLY CLOSET")
        print(f"Your Office Supplies: {self.game.player.office_supplies}")
        
        shop_items = self.game.get_shop_items()
        
        for i, item in enumerate(shop_items, 1):
            print(f"{i}. {item['name']} - {item['price']} supplies")
            print(f"   {item['description']}")
        
        print("0. Leave shop")
        
        try:
            choice = int(input("Select item to buy: ").strip())
            if choice == 0:
                return
            elif 1 <= choice <= len(shop_items):
                item = shop_items[choice - 1]
                result = self.game.buy_item(item['name'])
                if result.get('success'):
                    print(f"✅ {result['message']}")
                else:
                    print(f"❌ {result.get('error', 'Purchase failed')}")
        except ValueError:
            print("Invalid choice.")
    
    def display_player_status(self):
        """Display current player status"""
        if not self.game.player:
            return
        
        stats = self.game.get_player_stats()
        print(f"\n👤 {stats['name']} - Level {stats['level']} {stats['job_title']}")
        print(f"❤️  Health: {stats['health']}/{stats['max_health']}")
        print(f"☕ Caffeine: {stats['caffeine']}/{stats['max_caffeine']}")
        print(f"😰 Stress: {stats['stress']}/{stats['max_stress']}")
        print(f"💼 Office Supplies: {stats['office_supplies']}")
        print(f"🎯 Influence: {stats['influence']}")
    
    def quick_demo(self):
        """Run a quick combat demo"""
        print("\n🎮 QUICK DEMO - Corporate Combat!")
        
        player = Player("Demo Player")
        enemy = get_random_enemy(1)
        
        print(f"\nYou face: {enemy.name} ({enemy.enemy_type})")
        print(f"Your stats: Health={player.health}, Caffeine={player.caffeine}")
        print(f"Enemy stats: Health={enemy.health}, Level={enemy.level}")
        
        combat = CombatState(player, enemy)
        
        # Simulate a few combat rounds
        for turn in range(3):
            if not combat.is_active:
                break
            
            print(f"\n--- Turn {turn + 1} ---")
            
            # Player attacks
            if combat.player_turn:
                result = combat.process_turn("attack")
                print("You attack!")
                for msg in result.get('messages', []):
                    print(f"  {msg}")
            
            # Enemy turn
            if combat.is_active and not combat.player_turn:
                result = combat.process_turn("attack")
                print("Enemy attacks!")
                for msg in result.get('messages', []):
                    print(f"  {msg}")
        
        if combat.victory == 'player':
            print("\n🎉 You won the demo combat!")
        elif combat.victory == 'enemy':
            print("\n💀 The enemy won the demo combat!")
        else:
            print("\n⏸️ Demo combat ended without resolution.")
        
        input("\nPress Enter to return to main menu...")

if __name__ == "__main__":
    try:
        ui = TextUI()
        ui.run()
    except KeyboardInterrupt:
        print("\n\nThanks for playing Corporate Crusader!")
    except Exception as e:
        print(f"\nError: {e}")
        print("If this persists, please check your installation.")