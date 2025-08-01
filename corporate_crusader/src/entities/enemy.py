"""
Enemy system for Corporate Crusader
Various corporate stereotypes as opponents
"""
import random
from typing import Dict, List, Optional
from .ability import Ability, ABILITIES
from .item import Item, get_random_item

class Enemy:
    def __init__(self, name: str, enemy_type: str, level: int = 1):
        self.name = name
        self.enemy_type = enemy_type  # micromanager, karen, intern, etc.
        self.level = level
        
        # Base stats scaled by level
        self.max_health = 50 + (level * 10)
        self.health = self.max_health
        self.max_stress = 100
        self.stress = random.randint(10, 30)  # Enemies start with some stress
        
        # Add caffeine for compatibility with ability system
        self.max_caffeine = 30 + (level * 5)
        self.caffeine = self.max_caffeine
        
        # Stats
        self.charisma = 5 + level
        self.competence = 5 + level  
        self.networking = 5 + level
        self.cynicism = 5 + level
        
        # Add missing attributes for ability compatibility
        self.influence = 0  # Enemies don't normally gain influence
        self.office_supplies = 0  # Enemies don't use office supplies
        
        # Combat stats
        self.attack_power = 10 + (level * 3)
        self.defense = 5 + level
        
        # AI behavior
        self.aggression = 50  # How likely to attack vs use abilities
        self.intelligence = 50  # How likely to use smart moves
        
        # Abilities
        self.abilities: List[Ability] = []
        
        # Loot
        self.loot_table = []
        self.experience_reward = 25 + (level * 5)
        self.office_supplies_reward = 10 + (level * 3)
        self.influence_reward = 1 if level >= 3 else 0
        
        # Special traits
        self.immunities = set()  # Immune to certain status effects
        self.weaknesses = set()  # Takes extra damage from certain types
        
        # Dialogue
        self.dialogue = {
            'intro': [f"A {enemy_type} blocks your path!"],
            'attack': ["Ugh!", "How dare you!", "This is unacceptable!"],
            'defeated': ["I'll be back!", "This isn't over!", "You haven't seen the last of me!"]
        }
        
        self.description = f"A level {level} {enemy_type}"
        
    def take_damage(self, amount: int, damage_type: str = "normal") -> bool:
        """Take damage and return if enemy is defeated"""
        # Apply defense
        actual_damage = max(1, amount - self.defense)
        
        # Check for weaknesses/resistances
        if damage_type in self.weaknesses:
            actual_damage = int(actual_damage * 1.5)
        elif damage_type in self.immunities:
            actual_damage = 0
        
        if damage_type == "stress":
            self.stress = min(self.stress + actual_damage, self.max_stress)
            if self.stress >= self.max_stress:
                # Stress overflow damages health
                overflow = self.stress - self.max_stress
                self.health -= overflow // 2
        else:
            self.health -= actual_damage
        
        self.health = max(0, self.health)
        return self.health <= 0
    
    def heal(self, amount: int):
        """Restore health"""
        self.health = min(self.health + amount, self.max_health)
    
    def reduce_stress(self, amount: int):
        """Reduce stress levels"""
        self.stress = max(0, self.stress - amount)
    
    def choose_action(self, player) -> Dict:
        """AI chooses what action to take"""
        available_actions = []
        
        # Basic attack is always available
        available_actions.append(('attack', 100))
        
        # Check available abilities
        for ability in self.abilities:
            if ability.can_use(self):
                priority = self._calculate_ability_priority(ability, player)
                available_actions.append(('ability', priority, ability))
        
        # Choose action based on weights and AI personality
        if available_actions:
            # Weighted random selection
            total_weight = sum(action[1] for action in available_actions)
            choice = random.uniform(0, total_weight)
            
            current_weight = 0
            for action in available_actions:
                current_weight += action[1]
                if choice <= current_weight:
                    if action[0] == 'attack':
                        return self._basic_attack(player)
                    else:
                        return self._use_ability(action[2], player)
        
        # Fallback to basic attack
        return self._basic_attack(player)
    
    def _calculate_ability_priority(self, ability: Ability, player) -> int:
        """Calculate how likely the AI is to use this ability"""
        priority = 50
        
        # Health-based decisions
        health_percent = self.health / self.max_health
        if health_percent < 0.3 and ability.target_type == "self" and ability.healing > 0:
            priority += 40  # Prioritize healing when low
        
        # Stress-based decisions
        if self.stress > 60 and ability.stress_reduction > 0:
            priority += 30
        
        # Offensive abilities when player is healthy
        player_health_percent = player.health / player.max_health
        if player_health_percent > 0.5 and ability.base_damage > 0:
            priority += 20
        
        # Intelligence affects ability usage
        intelligence_bonus = (self.intelligence - 50) // 10
        priority += intelligence_bonus
        
        return max(10, priority)
    
    def _basic_attack(self, player) -> Dict:
        """Perform a basic attack"""
        damage = random.randint(self.attack_power - 3, self.attack_power + 3)
        
        # Add some flavor based on enemy type
        attack_messages = self.dialogue.get('attack', ["Attacks!"])
        message = random.choice(attack_messages)
        
        return {
            'action': 'attack',
            'damage': damage,
            'message': f"{self.name} {message}",
            'target': 'player'
        }
    
    def _use_ability(self, ability: Ability, player) -> Dict:
        """Use a specific ability"""
        target = player if ability.target_type == "enemy" else self
        result = ability.use(self, target)
        
        return {
            'action': 'ability',
            'ability_name': ability.name,
            'result': result,
            'message': f"{self.name} uses {ability.name}! {result.get('message', '')}"
        }
    
    def get_loot(self) -> List[Item]:
        """Generate loot drops"""
        loot = []
        
        # Random chance for item drops
        if random.random() < 0.4:  # 40% chance for item
            rarity_weights = {
                "common": 0.6,
                "uncommon": 0.3, 
                "rare": 0.08,
                "legendary": 0.02
            }
            # Higher level enemies have better loot
            if self.level >= 5:
                rarity_weights["uncommon"] += 0.1
                rarity_weights["common"] -= 0.1
            if self.level >= 10:
                rarity_weights["rare"] += 0.1
                rarity_weights["uncommon"] -= 0.1
                
            item = get_random_item(rarity_weights)
            loot.append(item)
        
        return loot
    
    def get_dialogue(self, situation: str) -> str:
        """Get appropriate dialogue for the situation"""
        if situation in self.dialogue:
            return random.choice(self.dialogue[situation])
        return f"The {self.enemy_type} makes corporate noises."

# Enemy Templates
ENEMY_TEMPLATES = {
    "micromanager": {
        "names": ["Chad the Micromanager", "Brenda the Overbearing", "Kyle the Controlling"],
        "base_stats": {"charisma": 3, "competence": 8, "networking": 5, "cynicism": 9},
        "abilities": ["micromanage", "passive_aggressive", "blame_redirect"],
        "weaknesses": ["stress"],
        "dialogue": {
            "intro": [
                "I need to see all your work before you submit it!",
                "Are you working efficiently? Let me check your progress every 5 minutes.",
                "I don't think you understand the company procedures..."
            ],
            "attack": [
                "This isn't following the 47-step process!",
                "I'm going to need you to redo this entirely!",
                "Have you been tracking your time correctly?"
            ],
            "defeated": [
                "I'll be reviewing your performance metrics!",
                "This will be noted in your permanent record!",
                "My supervisor will hear about this!"
            ]
        }
    },
    
    "karen": {
        "names": ["Karen the Complainer", "Susan the Demanding", "Linda the Entitled"],
        "base_stats": {"charisma": 7, "competence": 3, "networking": 6, "cynicism": 8},
        "abilities": ["small_talk", "passive_aggressive", "buzzword_bingo"],
        "weaknesses": ["competence"],
        "dialogue": {
            "intro": [
                "I want to speak to your manager!",
                "This is completely unacceptable service!",
                "Do you know who I am? I have connections!"
            ],
            "attack": [
                "I'm leaving a negative review!",
                "I know people in corporate!",
                "This is going straight to HR!"
            ],
            "defeated": [
                "I'll be calling your supervisor!",
                "You haven't heard the last of this!",
                "I'm never doing business here again!"
            ]
        }
    },
    
    "intern": {
        "names": ["Brad the Overachiever", "Emma the Eager", "Tyler the Tryhard"],
        "base_stats": {"charisma": 6, "competence": 4, "networking": 7, "cynicism": 2},
        "abilities": ["small_talk", "networking", "coffee_break"],
        "immunities": ["cynicism"],
        "dialogue": {
            "intro": [
                "I'm going to prove myself and get hired full-time!",
                "This internship is my chance to make it big!",
                "I've already connected with everyone on LinkedIn!"
            ],
            "attack": [
                "I'm more qualified than you think!",
                "I have so many ideas for improvement!",
                "My college professor said I was exceptional!"
            ],
            "defeated": [
                "This was supposed to be my big break...",
                "I'll just have to try harder next time!",
                "Maybe I should have picked a different major..."
            ]
        }
    },
    
    "executive": {
        "names": ["Richard the Ruthless", "Margaret the Merciless", "Steven the Soulless"],
        "base_stats": {"charisma": 9, "competence": 7, "networking": 10, "cynicism": 10},
        "abilities": ["corporate_restructure", "hostile_takeover", "inspirational_speech"],
        "immunities": ["stress", "guilt"],
        "dialogue": {
            "intro": [
                "Time to optimize human resources... starting with you.",
                "I didn't claw my way to the top to be stopped by the likes of you.",
                "Your position has been deemed... redundant."
            ],
            "attack": [
                "Nothing personal, it's just business.",
                "Quarterly projections demand sacrifice!",
                "Shareholders must be appeased!"
            ],
            "defeated": [
                "This is merely a strategic repositioning...",
                "The board will hear about this setback!",
                "I'll be back with a better severance package!"
            ]
        }
    },
    
    "it_guy": {
        "names": ["Dave the Disconnected", "Steve the Sarcastic", "Bob the Burnt-Out"],
        "base_stats": {"charisma": 4, "competence": 10, "networking": 3, "cynicism": 9},
        "abilities": ["passive_aggressive", "blame_redirect", "coffee_break"],
        "immunities": ["buzzwords"],
        "weaknesses": ["social"],
        "dialogue": {
            "intro": [
                "Have you tried turning it off and on again?",
                "Let me guess, you forgot your password... again.",
                "The problem exists between keyboard and chair."
            ],
            "attack": [
                "Your technical literacy is... concerning.",
                "Maybe try reading the manual first?",
                "I'll add this to the growing list of user errors."
            ],
            "defeated": [
                "Fine, I'll create another ticket...",
                "This will take me away from actual important work.",
                "Next time, Google it first."
            ]
        }
    },
    
    "hr_representative": {
        "names": ["Janet the Judge", "Robert the Recorder", "Patricia the Punisher"],
        "base_stats": {"charisma": 8, "competence": 6, "networking": 8, "cynicism": 7},
        "abilities": ["buzzword_bingo", "networking", "corporate_restructure"],
        "immunities": ["legal"],
        "dialogue": {
            "intro": [
                "We need to have a conversation about your recent behavior.",
                "I'm here to ensure compliance with company policies.",
                "This is a documented performance discussion."
            ],
            "attack": [
                "That's a violation of section 4.2.7 of the employee handbook!",
                "I'm making a note of this in your permanent file!",
                "We may need to discuss a performance improvement plan!"
            ],
            "defeated": [
                "This meeting will be scheduled for follow-up...",
                "I'll be consulting with legal about next steps.",
                "Your manager will be receiving a full report."
            ]
        }
    }
}

def create_enemy(enemy_type: str, level: int = 1) -> Enemy:
    """Create an enemy of the specified type and level"""
    if enemy_type not in ENEMY_TEMPLATES:
        enemy_type = "micromanager"  # Default fallback
    
    template = ENEMY_TEMPLATES[enemy_type]
    
    # Choose random name
    name = random.choice(template["names"])
    
    # Create enemy
    enemy = Enemy(name, enemy_type, level)
    
    # Apply template stats
    for stat, value in template["base_stats"].items():
        current_value = getattr(enemy, stat)
        setattr(enemy, stat, current_value + value)
    
    # Add abilities
    for ability_name in template["abilities"]:
        if ability_name in ABILITIES:
            enemy.abilities.append(ABILITIES[ability_name])
    
    # Set immunities and weaknesses
    enemy.immunities = set(template.get("immunities", []))
    enemy.weaknesses = set(template.get("weaknesses", []))
    
    # Set dialogue
    enemy.dialogue.update(template.get("dialogue", {}))
    
    # Adjust AI personality based on type
    if enemy_type == "micromanager":
        enemy.aggression = 30  # Prefers control abilities
        enemy.intelligence = 60
    elif enemy_type == "karen":
        enemy.aggression = 70  # Very aggressive
        enemy.intelligence = 40
    elif enemy_type == "intern":
        enemy.aggression = 40  # Balanced
        enemy.intelligence = 70  # Smart but inexperienced
    elif enemy_type == "executive":
        enemy.aggression = 50
        enemy.intelligence = 90  # Very strategic
    elif enemy_type == "it_guy":
        enemy.aggression = 20  # Passive aggressive
        enemy.intelligence = 80
    elif enemy_type == "hr_representative":
        enemy.aggression = 60
        enemy.intelligence = 75
    
    return enemy

def get_random_enemy(level: int = 1) -> Enemy:
    """Get a random enemy appropriate for the level"""
    enemy_types = list(ENEMY_TEMPLATES.keys())
    
    # Weight enemy types by level appropriateness
    weights = []
    for enemy_type in enemy_types:
        if enemy_type == "intern":
            weight = max(1, 5 - level)  # More common at low levels
        elif enemy_type == "executive":
            weight = max(1, level - 3)  # Only appear at higher levels
        else:
            weight = 3  # Standard weight
        weights.append(weight)
    
    chosen_type = random.choices(enemy_types, weights=weights)[0]
    return create_enemy(chosen_type, level)