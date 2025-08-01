"""
Main Game Engine for Corporate Crusader
Orchestrates all game systems and manages game state
"""
import random
from typing import Dict, List, Optional, Tuple

# Import all entities and systems - but handle pygame gracefully
from .entities import Player, Enemy, get_random_enemy, create_enemy, Item, ITEMS_CATALOG

# Import systems with error handling
try:
    from .systems.combat import CombatState
    from .systems.save_manager import SaveManager
except ImportError as e:
    print(f"Warning: Some systems may not work: {e}")
    CombatState = None
    SaveManager = None

class GameState:
    def __init__(self):
        self.current_scene = "main_menu"  # main_menu, exploration, combat, inventory, etc.
        self.player: Optional[Player] = None
        self.current_combat: Optional[CombatState] = None
        self.save_manager = SaveManager()
        
        # Game progression
        self.story_chapter = 1
        self.current_floor = 1  # Office building floor
        self.encounters_on_floor = 0
        self.max_encounters_per_floor = 5
        
        # Random events and encounters
        self.available_encounters = []
        self.special_events = []
        
        # Shop and services
        self.shop_items = []
        self.initialize_shop()
        
        # Game stats
        self.total_enemies_defeated = 0
        self.total_coffee_consumed = 0
        self.total_meetings_survived = 0
        
    def initialize_shop(self):
        """Initialize the office supply shop"""
        shop_items = [
            "instant_coffee", "energy_drink", "donut", "energy_bar",
            "stress_ball", "cheap_suit", "calculator", "plastic_watch"
        ]
        
        for item_id in shop_items:
            if item_id in ITEMS_CATALOG:
                self.shop_items.append(ITEMS_CATALOG[item_id])
    
    def start_new_game(self, player_name: str = "Corporate Climber"):
        """Start a new game"""
        self.player = Player(player_name)
        self.current_scene = "exploration"
        self.story_chapter = 1
        self.current_floor = 1
        self.encounters_on_floor = 0
        
        # Give player starting items
        starting_items = ["donut", "instant_coffee", "cheap_suit"]
        for item_id in starting_items:
            if item_id in ITEMS_CATALOG:
                item = Item.from_save_data(ITEMS_CATALOG[item_id].save_data())
                self.player.add_item(item)
        
        # Equip the cheap suit
        suit = None
        for item in self.player.inventory:
            if item.item_type == "suit":
                suit = item
                break
        if suit:
            self.player.equip_item(suit)
        
        return self.get_exploration_options()
    
    def get_exploration_options(self) -> Dict:
        """Get available actions during exploration"""
        if not self.player:
            return {"error": "No active game"}
        
        options = {
            "scene": "exploration",
            "floor": self.current_floor,
            "encounters_left": self.max_encounters_per_floor - self.encounters_on_floor,
            "actions": []
        }
        
        # Random encounter
        if self.encounters_on_floor < self.max_encounters_per_floor:
            options["actions"].append({
                "id": "random_encounter",
                "name": "Navigate the Office",
                "description": "Explore and potentially encounter corporate wildlife"
            })
        
        # Go to next floor
        if self.encounters_on_floor >= self.max_encounters_per_floor:
            options["actions"].append({
                "id": "next_floor",
                "name": "Take the Elevator",
                "description": f"Ascend to floor {self.current_floor + 1}"
            })
        
        # Visit shop
        options["actions"].append({
            "id": "shop",
            "name": "Office Supply Closet",
            "description": "Buy items with office supplies"
        })
        
        # Rest area
        options["actions"].append({
            "id": "rest",
            "name": "Break Room",
            "description": "Restore health and reduce stress"
        })
        
        # Character management
        options["actions"].append({
            "id": "inventory",
            "name": "Manage Equipment",
            "description": "View inventory and manage equipment"
        })
        
        # Save game
        options["actions"].append({
            "id": "save",
            "name": "Save Progress",
            "description": "Save your corporate climb"
        })
        
        return options
    
    def process_exploration_action(self, action_id: str) -> Dict:
        """Process an exploration action"""
        if not self.player:
            return {"error": "No active game"}
        
        result = {"success": False, "message": "", "new_scene": None}
        
        if action_id == "random_encounter":
            return self._handle_random_encounter()
        elif action_id == "next_floor":
            return self._advance_floor()
        elif action_id == "shop":
            result["new_scene"] = "shop"
            result["success"] = True
            return result
        elif action_id == "rest":
            return self._handle_rest()
        elif action_id == "inventory":
            result["new_scene"] = "inventory"
            result["success"] = True
            return result
        elif action_id == "save":
            return self._handle_save()
        else:
            result["message"] = "Invalid action"
            return result
    
    def _handle_random_encounter(self) -> Dict:
        """Handle a random encounter"""
        encounter_type = random.choices(
            ["combat", "event", "loot"],
            weights=[0.6, 0.2, 0.2]
        )[0]
        
        result = {"success": True, "encounter_type": encounter_type}
        
        if encounter_type == "combat":
            # Create enemy based on current floor
            enemy_level = max(1, self.current_floor + random.randint(-1, 1))
            enemy = get_random_enemy(enemy_level)
            
            self.current_combat = CombatState(self.player, enemy)
            self.current_scene = "combat"
            
            result["new_scene"] = "combat"
            result["enemy_name"] = enemy.name
            result["message"] = f"You encounter {enemy.name}!"
            
        elif encounter_type == "event":
            result.update(self._handle_random_event())
            
        elif encounter_type == "loot":
            result.update(self._handle_loot_find())
        
        self.encounters_on_floor += 1
        return result
    
    def _handle_random_event(self) -> Dict:
        """Handle a random story event"""
        events = [
            {
                "message": "You overhear office gossip about layoffs in the next quarter.",
                "effect": "stress",
                "value": 10
            },
            {
                "message": "You find an abandoned coffee that's still warm. Score!",
                "effect": "caffeine",
                "value": 15
            },
            {
                "message": "A motivational poster catches your eye: 'Hang in There!'",
                "effect": "stress_reduction",
                "value": 5
            },
            {
                "message": "You discover a shortcut through the supply closet.",
                "effect": "experience",
                "value": 10
            },
            {
                "message": "The printer jams just as you approach. Classic.",
                "effect": "stress",
                "value": 5
            },
            {
                "message": "You spot $5 someone dropped by the vending machine.",
                "effect": "office_supplies",
                "value": 5
            }
        ]
        
        event = random.choice(events)
        
        # Apply event effect
        if event["effect"] == "stress":
            self.player.stress = min(self.player.stress + event["value"], self.player.max_stress)
        elif event["effect"] == "caffeine":
            self.player.restore_caffeine(event["value"])
        elif event["effect"] == "stress_reduction":
            self.player.reduce_stress(event["value"])
        elif event["effect"] == "experience":
            self.player.add_experience(event["value"])
        elif event["effect"] == "office_supplies":
            self.player.office_supplies += event["value"]
        
        return {
            "message": event["message"],
            "effect_description": f"({event['effect'].replace('_', ' ').title()}: {event['value']})"
        }
    
    def _handle_loot_find(self) -> Dict:
        """Handle finding random loot"""
        # Determine loot quality based on floor
        rarity_weights = {"common": 0.7, "uncommon": 0.25, "rare": 0.05}
        if self.current_floor >= 5:
            rarity_weights = {"common": 0.5, "uncommon": 0.35, "rare": 0.13, "legendary": 0.02}
        
        from .entities.item import get_random_item
        found_item = get_random_item(rarity_weights)
        
        if self.player.add_item(found_item):
            return {
                "message": f"You found a {found_item.name}!",
                "item_description": found_item.description,
                "item_rarity": found_item.rarity
            }
        else:
            return {
                "message": f"You found a {found_item.name}, but your inventory is full!",
                "item_lost": True
            }
    
    def _advance_floor(self) -> Dict:
        """Advance to the next floor"""
        self.current_floor += 1
        self.encounters_on_floor = 0
        
        # Increase difficulty slightly
        if self.current_floor % 5 == 0:
            self.max_encounters_per_floor += 1
        
        # Story progression
        floor_messages = {
            2: "You take the elevator to the second floor. The carpet is slightly nicer here.",
            5: "Fifth floor - middle management territory. The suits get more expensive.",
            10: "Tenth floor - you can smell the executive privilege from here.",
            15: "Fifteenth floor - the air tastes like stock options and broken dreams.",
            20: "Top floor - the CEO's domain. Time to face the final boss of corporate hierarchy."
        }
        
        message = floor_messages.get(
            self.current_floor,
            f"Floor {self.current_floor} - another level in the corporate ladder."
        )
        
        return {
            "success": True,
            "message": message,
            "new_floor": self.current_floor
        }
    
    def _handle_rest(self) -> Dict:
        """Handle resting in the break room"""
        health_restored = min(30, self.player.max_health - self.player.health)
        stress_reduced = min(25, self.player.stress)
        caffeine_restored = min(20, self.player.max_caffeine - self.player.caffeine)
        
        self.player.heal(health_restored)
        self.player.reduce_stress(stress_reduced)
        self.player.restore_caffeine(caffeine_restored)
        
        rest_messages = [
            "You take a power nap under your desk.",
            "A quick meditation session by the water cooler helps.",
            "You steal a few minutes of peace in the bathroom.",
            "The break room microwave hums soothingly as you decompress."
        ]
        
        return {
            "success": True,
            "message": random.choice(rest_messages),
            "health_restored": health_restored,
            "stress_reduced": stress_reduced,
            "caffeine_restored": caffeine_restored
        }
    
    def _handle_save(self) -> Dict:
        """Handle saving the game"""
        game_state = {
            "story_chapter": self.story_chapter,
            "current_floor": self.current_floor,
            "encounters_on_floor": self.encounters_on_floor,
            "total_enemies_defeated": self.total_enemies_defeated,
            "total_coffee_consumed": self.total_coffee_consumed,
            "total_meetings_survived": self.total_meetings_survived
        }
        
        if self.save_manager: # Only save if SaveManager is available
            if self.save_manager.quick_save(self.player, game_state):
                return {
                    "success": True,
                    "message": "Game saved successfully!"
                }
            else:
                return {
                    "success": False,
                    "message": "Failed to save game."
                }
        else:
            return {
                "success": False,
                "message": "Save functionality not available."
            }
    
    def start_combat(self, enemy: Enemy) -> Dict:
        """Start combat with an enemy"""
        if not CombatState:
            return {"error": "Combat system not available"}
        self.current_combat = CombatState(self.player, enemy)
        self.current_scene = "combat"
        return self.current_combat.get_combat_state()
    
    def process_combat_action(self, action: str, **kwargs) -> Dict:
        """Process a combat action"""
        if not CombatState:
            return {"error": "Combat system not available"}
        if not self.current_combat or not self.current_combat.is_active:
            return {"error": "No active combat"}
        
        result = self.current_combat.process_turn(action, **kwargs)
        
        # Check if combat ended
        if not self.current_combat.is_active:
            if self.current_combat.victory == 'player':
                self.total_enemies_defeated += 1
            
            self.current_scene = "exploration"
            result["combat_ended"] = True
            result["victory"] = self.current_combat.victory
        
        return result
    
    def get_shop_items(self) -> List[Dict]:
        """Get available shop items"""
        shop_data = []
        for item in self.shop_items:
            shop_data.append({
                "name": item.name,
                "description": item.description,
                "price": item.value,
                "rarity": item.rarity,
                "item_type": item.item_type
            })
        return shop_data
    
    def buy_item(self, item_name: str) -> Dict:
        """Buy an item from the shop"""
        if not self.player:
            return {"error": "No active game"}
        
        # Find item in shop
        item_to_buy = None
        for item in self.shop_items:
            if item.name == item_name:
                item_to_buy = item
                break
        
        if not item_to_buy:
            return {"error": "Item not found in shop"}
        
        if self.player.office_supplies < item_to_buy.value:
            return {"error": "Not enough office supplies"}
        
        # Create new instance of item
        new_item = Item.from_save_data(item_to_buy.save_data())
        
        if not self.player.add_item(new_item):
            return {"error": "Inventory full"}
        
        self.player.office_supplies -= item_to_buy.value
        
        return {
            "success": True,
            "message": f"Purchased {item_to_buy.name}",
            "item": new_item.save_data()
        }
    
    def load_game(self, save_name: str) -> Dict:
        """Load a saved game"""
        if not SaveManager:
            return {"error": "Save functionality not available"}
        save_data = self.save_manager.load_game(save_name)
        
        if not save_data:
            return {"error": "Failed to load save"}
        
        try:
            # Create new player and load data
            self.player = Player()
            self.player.load_data(save_data["player_data"])
            
            # Load game state
            game_state = save_data["game_state"]
            self.story_chapter = game_state.get("story_chapter", 1)
            self.current_floor = game_state.get("current_floor", 1)
            self.encounters_on_floor = game_state.get("encounters_on_floor", 0)
            self.total_enemies_defeated = game_state.get("total_enemies_defeated", 0)
            self.total_coffee_consumed = game_state.get("total_coffee_consumed", 0)
            self.total_meetings_survived = game_state.get("total_meetings_survived", 0)
            
            self.current_scene = "exploration"
            
            return {
                "success": True,
                "message": f"Loaded game: {self.player.name}",
                "player_name": self.player.name,
                "level": self.player.level,
                "floor": self.current_floor
            }
            
        except Exception as e:
            return {"error": f"Corrupted save file: {e}"}
    
    def get_player_stats(self) -> Dict:
        """Get detailed player statistics"""
        if not self.player:
            return {}
        
        return {
            "name": self.player.name,
            "level": self.player.level,
            "experience": self.player.experience,
            "experience_to_next": self.player.experience_to_next,
            "health": self.player.health,
            "max_health": self.player.max_health,
            "caffeine": self.player.caffeine,
            "max_caffeine": self.player.max_caffeine,
            "stress": self.player.stress,
            "max_stress": self.player.max_stress,
            "charisma": self.player.get_total_stat('charisma'),
            "competence": self.player.get_total_stat('competence'),
            "networking": self.player.get_total_stat('networking'),
            "cynicism": self.player.get_total_stat('cynicism'),
            "office_supplies": self.player.office_supplies,
            "influence": self.player.influence,
            "department": self.player.department,
            "job_title": self.player.job_title,
            "current_floor": self.current_floor,
            "enemies_defeated": self.total_enemies_defeated
        }