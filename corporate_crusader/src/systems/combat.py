"""
Combat system for Corporate Crusader
Turn-based corporate warfare
"""
import random
from typing import Dict, List, Optional, Tuple
from ..entities.player import Player
from ..entities.enemy import Enemy
from ..entities.ability import Ability

class CombatState:
    def __init__(self, player: Player, enemy: Enemy):
        self.player = player
        self.enemy = enemy
        self.turn_count = 0
        self.player_turn = True
        self.combat_log = []
        self.is_active = True
        self.victory = None  # None, 'player', 'enemy'
        
        # Combat-specific effects
        self.status_effects = {
            'player': {},  # effect_name: turns_remaining
            'enemy': {}
        }
        
        # Initialize combat
        self._start_combat()
    
    def _start_combat(self):
        """Initialize combat encounter"""
        intro_message = self.enemy.get_dialogue('intro')
        self.add_to_log(intro_message)
        
        # Roll for initiative (who goes first)
        player_initiative = random.randint(1, 20) + self.player.get_total_stat('networking')
        enemy_initiative = random.randint(1, 20) + self.enemy.networking
        
        if enemy_initiative > player_initiative:
            self.player_turn = False
            self.add_to_log("The enemy acts first!")
    
    def add_to_log(self, message: str):
        """Add message to combat log"""
        self.combat_log.append(message)
    
    def get_recent_log(self, count: int = 5) -> List[str]:
        """Get recent combat log entries"""
        return self.combat_log[-count:]
    
    def process_turn(self, action: str, target=None, ability: Ability = None, item=None) -> Dict:
        """Process a combat turn"""
        if not self.is_active:
            return {"error": "Combat is not active"}
        
        result = {"success": False, "messages": [], "effects": []}
        
        if self.player_turn:
            result = self._process_player_turn(action, target, ability, item)
        else:
            result = self._process_enemy_turn()
        
        # Check for combat end conditions
        if self.player.health <= 0:
            self.victory = 'enemy'
            self.is_active = False
            defeat_message = "You have been corporately restructured... Game Over!"
            self.add_to_log(defeat_message)
            result["messages"].append(defeat_message)
        elif self.enemy.health <= 0:
            self.victory = 'player'
            self.is_active = False
            victory_message = f"{self.enemy.name} has been successfully managed!"
            defeat_dialogue = self.enemy.get_dialogue('defeated')
            self.add_to_log(victory_message)
            self.add_to_log(defeat_dialogue)
            result["messages"].extend([victory_message, defeat_dialogue])
            
            # Award experience and loot
            exp_gained = self.enemy.experience_reward
            supplies_gained = self.enemy.office_supplies_reward
            influence_gained = self.enemy.influence_reward
            
            self.player.add_experience(exp_gained)
            self.player.office_supplies += supplies_gained
            self.player.influence += influence_gained
            
            loot = self.enemy.get_loot()
            for item in loot:
                if self.player.add_item(item):
                    result["messages"].append(f"Found: {item.name}")
            
            result["rewards"] = {
                "experience": exp_gained,
                "office_supplies": supplies_gained,
                "influence": influence_gained,
                "loot": loot
            }
        
        # Process status effects and ability cooldowns
        self._process_status_effects()
        self._reduce_cooldowns()
        
        # Switch turns
        self.player_turn = not self.player_turn
        self.turn_count += 1
        
        # Add log messages to result
        result["combat_log"] = self.get_recent_log(3)
        
        return result
    
    def _process_player_turn(self, action: str, target=None, ability: Ability = None, item=None) -> Dict:
        """Process player's turn"""
        result = {"success": False, "messages": [], "effects": []}
        
        if action == "attack":
            result = self._player_attack()
        elif action == "ability" and ability:
            result = self._player_use_ability(ability)
        elif action == "item" and item:
            result = self._player_use_item(item)
        elif action == "flee":
            result = self._attempt_flee()
        else:
            result["messages"] = ["Invalid action!"]
            return result
        
        return result
    
    def _process_enemy_turn(self) -> Dict:
        """Process enemy's turn"""
        action_result = self.enemy.choose_action(self.player)
        result = {"success": True, "messages": [], "effects": []}
        
        if action_result['action'] == 'attack':
            damage = action_result['damage']
            is_defeated = self.player.take_damage(damage)
            
            message = f"{action_result['message']} Deals {damage} damage!"
            self.add_to_log(message)
            result["messages"].append(message)
            
        elif action_result['action'] == 'ability':
            ability_result = action_result['result']
            message = action_result['message']
            
            self.add_to_log(message)
            result["messages"].append(message)
            
            if ability_result.get('effects'):
                for effect in ability_result['effects']:
                    self.add_to_log(effect)
                    result["messages"].append(effect)
        
        return result
    
    def _player_attack(self) -> Dict:
        """Handle player basic attack"""
        result = {"success": True, "messages": [], "effects": []}
        
        # Calculate attack damage
        base_damage = 10 + self.player.get_total_stat('competence')
        damage_variance = random.randint(-3, 3)
        final_damage = max(1, base_damage + damage_variance)
        
        # Apply damage
        is_defeated = self.enemy.take_damage(final_damage)
        
        # Create message
        attack_messages = [
            f"You unleash a devastating spreadsheet attack for {final_damage} damage!",
            f"Your PowerPoint presentation hits for {final_damage} damage!",
            f"You email them into submission for {final_damage} damage!",
            f"Your meeting request causes {final_damage} points of scheduling anxiety!"
        ]
        
        message = random.choice(attack_messages)
        self.add_to_log(message)
        result["messages"].append(message)
        
        return result
    
    def _player_use_ability(self, ability: Ability) -> Dict:
        """Handle player ability usage"""
        result = {"success": False, "messages": [], "effects": []}
        
        if not self.player.can_use_ability(ability):
            message = "Cannot use that ability right now!"
            result["messages"].append(message)
            return result
        
        # Use the ability
        target = self.enemy if ability.target_type == "enemy" else self.player
        ability_result = ability.use(self.player, target)
        
        if ability_result["success"]:
            result["success"] = True
            message = f"You use {ability.name}! {ability_result['message']}"
            self.add_to_log(message)
            result["messages"].append(message)
            
            # Add effect messages
            for effect in ability_result.get("effects", []):
                self.add_to_log(effect)
                result["messages"].append(effect)
        else:
            result["messages"].append(ability_result.get("message", "Ability failed!"))
        
        return result
    
    def _player_use_item(self, item) -> Dict:
        """Handle player item usage"""
        result = {"success": False, "messages": [], "effects": []}
        
        if not item.is_consumable:
            result["messages"].append("That item cannot be used in combat!")
            return result
        
        if item not in self.player.inventory:
            result["messages"].append("You don't have that item!")
            return result
        
        # Use the item
        use_result = item.use(self.player)
        self.player.remove_item(item)
        
        message = f"You use {item.name}. {use_result}"
        self.add_to_log(message)
        result["messages"].append(message)
        result["success"] = True
        
        return result
    
    def _attempt_flee(self) -> Dict:
        """Handle flee attempt"""
        result = {"success": False, "messages": [], "effects": []}
        
        # Flee chance based on networking (social skills to extract yourself)
        flee_chance = 30 + self.player.get_total_stat('networking') * 2
        flee_chance = min(80, flee_chance)  # Max 80% chance
        
        if random.randint(1, 100) <= flee_chance:
            self.is_active = False
            self.victory = 'fled'
            message = "You successfully extract yourself from this corporate encounter!"
            self.add_to_log(message)
            result["messages"].append(message)
            result["success"] = True
        else:
            message = "You couldn't find an excuse to leave! The conversation continues..."
            self.add_to_log(message)
            result["messages"].append(message)
        
        return result
    
    def _process_status_effects(self):
        """Process ongoing status effects"""
        for target in ['player', 'enemy']:
            effects_to_remove = []
            
            for effect_name, turns_remaining in self.status_effects[target].items():
                # Apply effect
                self._apply_status_effect(target, effect_name)
                
                # Reduce duration
                turns_remaining -= 1
                if turns_remaining <= 0:
                    effects_to_remove.append(effect_name)
                else:
                    self.status_effects[target][effect_name] = turns_remaining
            
            # Remove expired effects
            for effect_name in effects_to_remove:
                del self.status_effects[target][effect_name]
    
    def _apply_status_effect(self, target: str, effect_name: str):
        """Apply a specific status effect"""
        target_obj = self.player if target == 'player' else self.enemy
        
        if effect_name == 'confused':
            # Confused entities might target themselves
            if random.random() < 0.3:
                self.add_to_log(f"{target_obj.name} is confused and hurts themselves!")
                target_obj.take_damage(5)
        elif effect_name == 'stressed':
            # Stress buildup over time
            target_obj.stress += 5
            self.add_to_log(f"{target_obj.name} feels increasingly stressed...")
        elif effect_name == 'motivated':
            # Temporary stat boost
            pass  # Handled by stat calculation
    
    def _reduce_cooldowns(self):
        """Reduce ability cooldowns"""
        for ability in self.player.abilities:
            ability.reduce_cooldown()
        
        for ability in self.enemy.abilities:
            ability.reduce_cooldown()
    
    def add_status_effect(self, target: str, effect_name: str, duration: int):
        """Add a status effect"""
        self.status_effects[target][effect_name] = duration
    
    def get_available_actions(self) -> Dict:
        """Get list of available actions for the player"""
        actions = {
            "attack": True,
            "flee": True,
            "abilities": [],
            "items": []
        }
        
        # Available abilities
        for ability in self.player.abilities:
            if self.player.can_use_ability(ability):
                actions["abilities"].append({
                    "name": ability.name,
                    "description": ability.description,
                    "caffeine_cost": ability.caffeine_cost,
                    "cooldown": ability.current_cooldown
                })
        
        # Available consumable items
        for item in self.player.inventory:
            if item.is_consumable:
                actions["items"].append({
                    "name": item.name,
                    "description": item.description,
                    "effects": item.consumable_effects
                })
        
        return actions
    
    def get_combat_state(self) -> Dict:
        """Get current combat state for UI"""
        return {
            "turn_count": self.turn_count,
            "player_turn": self.player_turn,
            "is_active": self.is_active,
            "victory": self.victory,
            "player": {
                "name": self.player.name,
                "health": self.player.health,
                "max_health": self.player.max_health,
                "caffeine": self.player.caffeine,
                "max_caffeine": self.player.max_caffeine,
                "stress": self.player.stress,
                "max_stress": self.player.max_stress
            },
            "enemy": {
                "name": self.enemy.name,
                "health": self.enemy.health,
                "max_health": self.enemy.max_health,
                "stress": self.enemy.stress,
                "max_stress": self.enemy.max_stress,
                "level": self.enemy.level,
                "enemy_type": self.enemy.enemy_type
            },
            "status_effects": self.status_effects,
            "available_actions": self.get_available_actions()
        }