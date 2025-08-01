"""
Ability system for Corporate Crusader
Corporate-themed skills and special attacks
"""
from typing import Dict, List, Callable, Optional
import random

class Ability:
    def __init__(self, name: str, description: str, caffeine_cost: int = 0,
                 cooldown: int = 0, max_stress_to_use: int = 100):
        self.name = name
        self.description = description
        self.caffeine_cost = caffeine_cost
        self.cooldown = cooldown
        self.current_cooldown = 0
        self.max_stress_to_use = max_stress_to_use  # Can't use if too stressed
        
        # Damage and effects
        self.base_damage = 0
        self.stress_damage = 0
        self.healing = 0
        self.caffeine_restore = 0
        self.stress_reduction = 0
        
        # Special effects
        self.special_effect: Optional[Callable] = None
        self.target_type = "enemy"  # enemy, self, ally
        
        # Stat requirements
        self.required_stats: Dict[str, int] = {}
        
        # Flavor text for different outcomes
        self.success_messages = []
        self.failure_messages = []
        self.critical_messages = []
    
    def can_use(self, user) -> bool:
        """Check if ability can be used"""
        if self.current_cooldown > 0:
            return False
        if user.caffeine < self.caffeine_cost:
            return False
        if user.stress > self.max_stress_to_use:
            return False
        
        # Check stat requirements
        for stat, required_value in self.required_stats.items():
            if getattr(user, stat, 0) < required_value:
                return False
        
        return True
    
    def use(self, user, target=None) -> Dict:
        """Use the ability"""
        if not self.can_use(user):
            return {"success": False, "message": "Cannot use this ability right now"}
        
        # Consume resources
        user.caffeine -= self.caffeine_cost
        self.current_cooldown = self.cooldown
        
        result = {
            "success": True,
            "message": "",
            "damage": 0,
            "stress_damage": 0,
            "healing": 0,
            "effects": []
        }
        
        # Calculate effectiveness based on stats
        effectiveness = self._calculate_effectiveness(user, target)
        
        # Apply damage
        if self.base_damage > 0 and target:
            damage = int(self.base_damage * effectiveness)
            result["damage"] = damage
            if hasattr(target, 'take_damage'):
                target.take_damage(damage)
        
        # Apply stress damage
        if self.stress_damage > 0 and target:
            stress_dmg = int(self.stress_damage * effectiveness)
            result["stress_damage"] = stress_dmg
            if hasattr(target, 'take_damage'):
                target.take_damage(stress_dmg, "stress")
        
        # Apply healing
        if self.healing > 0:
            heal_amount = int(self.healing * effectiveness)
            result["healing"] = heal_amount
            if self.target_type == "self":
                user.heal(heal_amount)
            elif target and hasattr(target, 'heal'):
                target.heal(heal_amount)
        
        # Apply caffeine restoration
        if self.caffeine_restore > 0:
            if self.target_type == "self":
                user.restore_caffeine(self.caffeine_restore)
                result["effects"].append(f"Restored {self.caffeine_restore} caffeine")
        
        # Apply stress reduction
        if self.stress_reduction > 0:
            if self.target_type == "self":
                user.reduce_stress(self.stress_reduction)
                result["effects"].append(f"Reduced stress by {self.stress_reduction}")
        
        # Special effects
        if self.special_effect:
            special_result = self.special_effect(user, target, effectiveness)
            if special_result:
                result["effects"].extend(special_result)
        
        # Generate message
        result["message"] = self._generate_message(effectiveness, result)
        
        return result
    
    def _calculate_effectiveness(self, user, target=None) -> float:
        """Calculate ability effectiveness based on user stats"""
        base_effectiveness = 1.0
        
        # Add stat bonuses
        for stat, weight in self.required_stats.items():
            stat_value = getattr(user, stat, 0)
            bonus = (stat_value - weight) * 0.1  # 10% per point above requirement
            base_effectiveness += max(0, bonus)
        
        # Add some randomness
        random_factor = random.uniform(0.8, 1.2)
        final_effectiveness = base_effectiveness * random_factor
        
        return max(0.1, final_effectiveness)  # Minimum 10% effectiveness
    
    def _generate_message(self, effectiveness: float, result: Dict) -> str:
        """Generate appropriate message based on effectiveness"""
        if effectiveness >= 1.5:  # Critical success
            messages = self.critical_messages or self.success_messages
        elif effectiveness >= 0.9:  # Normal success
            messages = self.success_messages
        else:  # Poor performance
            messages = self.failure_messages or self.success_messages
        
        if messages:
            return random.choice(messages)
        return f"Used {self.name}"
    
    def reduce_cooldown(self):
        """Reduce cooldown by 1"""
        if self.current_cooldown > 0:
            self.current_cooldown -= 1

# Special effect functions
def small_talk_effect(user, target, effectiveness):
    """Small talk can sometimes gather information or reduce enemy stress"""
    effects = []
    if random.random() < 0.3:  # 30% chance
        if target and hasattr(target, 'stress'):
            stress_reduction = int(5 * effectiveness)
            target.stress = max(0, target.stress - stress_reduction)
            effects.append(f"Enemy stress reduced by {stress_reduction}")
        else:
            user.influence += 1
            effects.append("Gained valuable information (+1 Influence)")
    return effects

def blame_redirect_effect(user, target, effectiveness):
    """Blame redirect can cause confusion"""
    effects = []
    if target and random.random() < 0.4:  # 40% chance
        effects.append("Target is confused and may attack itself!")
        # This would be handled by the combat system
    return effects

def buzzword_bingo_effect(user, target, effectiveness):
    """Corporate buzzwords can be devastating"""
    effects = []
    buzzwords = ["synergy", "paradigm shift", "circle back", "move the needle", 
                 "low-hanging fruit", "think outside the box"]
    used_buzzword = random.choice(buzzwords)
    extra_damage = int(effectiveness * 5)
    if target and hasattr(target, 'take_damage'):
        target.take_damage(extra_damage, "stress")
        effects.append(f"'{used_buzzword.title()}!' deals {extra_damage} psychic damage!")
    return effects

def networking_effect(user, target, effectiveness):
    """Networking can provide various benefits"""
    effects = []
    user.networking += 1
    user.influence += int(effectiveness)
    effects.append(f"Gained connection (+1 Networking, +{int(effectiveness)} Influence)")
    return effects

def passive_aggressive_effect(user, target, effectiveness):
    """Passive aggressive attacks build up stress over time"""
    effects = []
    if target and hasattr(target, 'stress'):
        stress_buildup = int(effectiveness * 3)
        target.stress += stress_buildup
        effects.append(f"Target stress increases by {stress_buildup} (ongoing frustration)")
    return effects

# Pre-defined abilities
ABILITIES = {
    "small_talk": Ability(
        "Small Talk", 
        "Engage in meaningless conversation to lower guard",
        caffeine_cost=5, cooldown=0, max_stress_to_use=80
    ),
    
    "coffee_break": Ability(
        "Coffee Break",
        "Take a moment to restore caffeine and reduce stress",
        caffeine_cost=0, cooldown=3, max_stress_to_use=100
    ),
    
    "blame_redirect": Ability(
        "Blame Redirect",
        "Masterfully shift blame to confuse and damage enemy",
        caffeine_cost=10, cooldown=1, max_stress_to_use=70
    ),
    
    "buzzword_bingo": Ability(
        "Buzzword Bingo",
        "Unleash corporate speak to deal massive psychic damage",
        caffeine_cost=15, cooldown=2, max_stress_to_use=60
    ),
    
    "networking": Ability(
        "Strategic Networking",
        "Build connections for future advantages",
        caffeine_cost=20, cooldown=4, max_stress_to_use=50
    ),
    
    "passive_aggressive": Ability(
        "Passive Aggressive Comment",
        "Subtle attack that builds stress over time",
        caffeine_cost=8, cooldown=0, max_stress_to_use=90
    ),
    
    "micromanage": Ability(
        "Micromanagement",
        "Slowly crush enemy spirit with excessive oversight",
        caffeine_cost=12, cooldown=1, max_stress_to_use=50
    ),
    
    "corporate_restructure": Ability(
        "Corporate Restructure",
        "Devastating attack that can eliminate lower-level enemies",
        caffeine_cost=30, cooldown=5, max_stress_to_use=30
    ),
    
    "inspirational_speech": Ability(
        "Inspirational Speech",
        "Boost morale and restore team resources",
        caffeine_cost=25, cooldown=6, max_stress_to_use=20
    ),
    
    "hostile_takeover": Ability(
        "Hostile Takeover",
        "Ultimate ability that can instantly defeat some enemies",
        caffeine_cost=50, cooldown=10, max_stress_to_use=10
    )
}

def initialize_abilities():
    """Initialize all ability stats and effects"""
    
    # Small Talk
    ABILITIES["small_talk"].stress_damage = 5
    ABILITIES["small_talk"].special_effect = small_talk_effect
    ABILITIES["small_talk"].required_stats = {"charisma": 5}
    ABILITIES["small_talk"].success_messages = [
        "You discuss the weather with devastating effectiveness",
        "Your commentary on local sports strikes deep",
        "They're trapped in conversation about weekend plans"
    ]
    
    # Coffee Break
    ABILITIES["coffee_break"].target_type = "self"
    ABILITIES["coffee_break"].caffeine_restore = 20
    ABILITIES["coffee_break"].stress_reduction = 15
    ABILITIES["coffee_break"].success_messages = [
        "The caffeine flows through you like liquid motivation",
        "A moment of peace in the corporate chaos",
        "You feel refreshed and ready to face more meetings"
    ]
    
    # Blame Redirect
    ABILITIES["blame_redirect"].base_damage = 15
    ABILITIES["blame_redirect"].stress_damage = 10
    ABILITIES["blame_redirect"].special_effect = blame_redirect_effect
    ABILITIES["blame_redirect"].required_stats = {"cynicism": 3, "charisma": 5}
    ABILITIES["blame_redirect"].success_messages = [
        "You expertly deflect responsibility like a corporate ninja",
        "The blame bounces off you and sticks to them",
        "Your Teflon coating of denial is impenetrable"
    ]
    
    # Buzzword Bingo
    ABILITIES["buzzword_bingo"].base_damage = 20
    ABILITIES["buzzword_bingo"].stress_damage = 15
    ABILITIES["buzzword_bingo"].special_effect = buzzword_bingo_effect
    ABILITIES["buzzword_bingo"].required_stats = {"charisma": 8, "competence": 5}
    ABILITIES["buzzword_bingo"].success_messages = [
        "Your synergistic approach leverages core competencies",
        "You circle back to touch base on key deliverables",
        "Your paradigm-shifting ideation breaks their brain"
    ]
    
    # Networking
    ABILITIES["networking"].target_type = "self"
    ABILITIES["networking"].special_effect = networking_effect
    ABILITIES["networking"].required_stats = {"networking": 10, "charisma": 8}
    ABILITIES["networking"].success_messages = [
        "You make a valuable connection for future opportunities",
        "Your business card collection grows stronger",
        "Another LinkedIn connection in the bag"
    ]
    
    # Passive Aggressive
    ABILITIES["passive_aggressive"].stress_damage = 8
    ABILITIES["passive_aggressive"].special_effect = passive_aggressive_effect
    ABILITIES["passive_aggressive"].required_stats = {"cynicism": 5}
    ABILITIES["passive_aggressive"].success_messages = [
        "You deliver a backhanded compliment with surgical precision",
        "Your subtle dig hits harder than expected",
        "They'll be thinking about that comment for hours"
    ]
    
    # Micromanage
    ABILITIES["micromanage"].base_damage = 12
    ABILITIES["micromanage"].stress_damage = 20
    ABILITIES["micromanage"].required_stats = {"competence": 10, "cynicism": 8}
    ABILITIES["micromanage"].success_messages = [
        "You question every decision they've made today",
        "Your oversight is suffocatingly thorough", 
        "They feel their autonomy being slowly strangled"
    ]
    
    # Corporate Restructure
    ABILITIES["corporate_restructure"].base_damage = 40
    ABILITIES["corporate_restructure"].stress_damage = 30
    ABILITIES["corporate_restructure"].required_stats = {"networking": 15, "competence": 12}
    ABILITIES["corporate_restructure"].success_messages = [
        "You eliminate redundancies with extreme prejudice",
        "The org chart becomes a weapon of mass destruction",
        "They've been optimized out of existence"
    ]
    
    # Inspirational Speech
    ABILITIES["inspirational_speech"].target_type = "self"
    ABILITIES["inspirational_speech"].healing = 30
    ABILITIES["inspirational_speech"].caffeine_restore = 15
    ABILITIES["inspirational_speech"].stress_reduction = 25
    ABILITIES["inspirational_speech"].required_stats = {"charisma": 15, "networking": 10}
    ABILITIES["inspirational_speech"].success_messages = [
        "Your words inspire yourself to greatness",
        "You channel the spirit of motivational posters",
        "Even you believe your own corporate propaganda"
    ]
    
    # Hostile Takeover
    ABILITIES["hostile_takeover"].base_damage = 80
    ABILITIES["hostile_takeover"].stress_damage = 50
    ABILITIES["hostile_takeover"].required_stats = {"networking": 20, "competence": 15, "cynicism": 10}
    ABILITIES["hostile_takeover"].success_messages = [
        "You acquire their entire existence",
        "They are now a wholly-owned subsidiary of YOU",
        "The merger is complete. Resistance is futile."
    ]

# Initialize abilities when module is imported
initialize_abilities()