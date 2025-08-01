"""
Player class for Corporate Crusader
Represents the player character navigating corporate life
"""
import json
from typing import Dict, List, Optional
from .item import Item
from .ability import Ability

class Player:
    def __init__(self, name: str = "New Hire"):
        self.name = name
        self.level = 1
        self.experience = 0
        self.experience_to_next = 100
        
        # Corporate-themed stats
        self.max_health = 100
        self.health = 100
        self.max_caffeine = 50  # Mana equivalent
        self.caffeine = 50
        self.stress = 0  # Negative status
        self.max_stress = 100
        
        # Primary stats
        self.charisma = 10  # Social interactions, negotiations
        self.competence = 10  # Technical skills, problem solving
        self.networking = 10  # Information gathering, allies
        self.cynicism = 5   # Resistance to corporate BS
        
        # Secondary stats (calculated)
        self.influence = 0  # Currency for special actions
        self.office_supplies = 0  # Basic currency
        
        # Equipment slots
        self.equipment = {
            'suit': None,
            'accessory': None,
            'gadget': None,
            'drink': None
        }
        
        # Inventory
        self.inventory: List[Item] = []
        self.max_inventory_size = 20
        
        # Abilities
        self.abilities: List[Ability] = []
        self.learn_basic_abilities()
        
        # Story progress
        self.department = "Intern Pool"
        self.job_title = "Unpaid Intern"
        self.story_flags = set()
        self.completed_quests = []
        
    def learn_basic_abilities(self):
        """Learn starting abilities"""
        from .ability import ABILITIES
        self.abilities = [
            ABILITIES['small_talk'],
            ABILITIES['coffee_break'],
            ABILITIES['blame_redirect']
        ]
    
    def add_experience(self, amount: int):
        """Add experience and handle level ups"""
        self.experience += amount
        while self.experience >= self.experience_to_next:
            self.level_up()
    
    def level_up(self):
        """Handle level up mechanics"""
        self.experience -= self.experience_to_next
        self.level += 1
        self.experience_to_next = int(self.experience_to_next * 1.2)
        
        # Stat increases
        self.max_health += 10
        self.health = self.max_health
        self.max_caffeine += 5
        self.caffeine = self.max_caffeine
        
        # Random stat boost
        import random
        stat_choices = ['charisma', 'competence', 'networking', 'cynicism']
        chosen_stat = random.choice(stat_choices)
        setattr(self, chosen_stat, getattr(self, chosen_stat) + 2)
        
        return f"Level Up! {chosen_stat.title()} increased!"
    
    def take_damage(self, amount: int, damage_type: str = "stress"):
        """Take damage from various sources"""
        if damage_type == "stress":
            self.stress = min(self.stress + amount, self.max_stress)
            if self.stress >= self.max_stress:
                self.health -= amount // 2  # Stress overflow damages health
        else:
            self.health -= amount
        
        self.health = max(0, self.health)
        return self.health <= 0
    
    def heal(self, amount: int):
        """Restore health"""
        self.health = min(self.health + amount, self.max_health)
    
    def restore_caffeine(self, amount: int):
        """Restore caffeine (mana)"""
        self.caffeine = min(self.caffeine + amount, self.max_caffeine)
    
    def reduce_stress(self, amount: int):
        """Reduce stress levels"""
        self.stress = max(0, self.stress - amount)
    
    def can_use_ability(self, ability: Ability) -> bool:
        """Check if player can use an ability"""
        return (self.caffeine >= ability.caffeine_cost and 
                self.stress <= ability.max_stress_to_use)
    
    def use_ability(self, ability: Ability) -> bool:
        """Use an ability, consuming resources"""
        if self.can_use_ability(ability):
            self.caffeine -= ability.caffeine_cost
            return True
        return False
    
    def add_item(self, item: Item) -> bool:
        """Add item to inventory"""
        if len(self.inventory) < self.max_inventory_size:
            self.inventory.append(item)
            return True
        return False
    
    def remove_item(self, item: Item) -> bool:
        """Remove item from inventory"""
        if item in self.inventory:
            self.inventory.remove(item)
            return True
        return False
    
    def equip_item(self, item: Item) -> bool:
        """Equip an item"""
        if item.item_type in self.equipment and item in self.inventory:
            # Unequip current item
            current_item = self.equipment[item.item_type]
            if current_item:
                self.unequip_item(current_item)
            
            # Equip new item
            self.equipment[item.item_type] = item
            self.remove_item(item)
            self.apply_item_effects(item, equip=True)
            return True
        return False
    
    def unequip_item(self, item: Item) -> bool:
        """Unequip an item"""
        for slot, equipped_item in self.equipment.items():
            if equipped_item == item:
                self.equipment[slot] = None
                self.add_item(item)
                self.apply_item_effects(item, equip=False)
                return True
        return False
    
    def apply_item_effects(self, item: Item, equip: bool = True):
        """Apply or remove item stat effects"""
        multiplier = 1 if equip else -1
        for stat, value in item.stat_bonuses.items():
            if hasattr(self, stat):
                current_value = getattr(self, stat)
                setattr(self, stat, current_value + (value * multiplier))
    
    def get_total_stat(self, stat_name: str) -> int:
        """Get stat including equipment bonuses"""
        base_stat = getattr(self, stat_name, 0)
        equipment_bonus = sum(
            item.stat_bonuses.get(stat_name, 0) 
            for item in self.equipment.values() 
            if item
        )
        return base_stat + equipment_bonus
    
    def save_data(self) -> Dict:
        """Export player data for saving"""
        return {
            'name': self.name,
            'level': self.level,
            'experience': self.experience,
            'experience_to_next': self.experience_to_next,
            'health': self.health,
            'max_health': self.max_health,
            'caffeine': self.caffeine,
            'max_caffeine': self.max_caffeine,
            'stress': self.stress,
            'charisma': self.charisma,
            'competence': self.competence,
            'networking': self.networking,
            'cynicism': self.cynicism,
            'influence': self.influence,
            'office_supplies': self.office_supplies,
            'department': self.department,
            'job_title': self.job_title,
            'story_flags': list(self.story_flags),
            'completed_quests': self.completed_quests,
            'inventory': [item.save_data() for item in self.inventory],
            'equipment': {slot: item.save_data() if item else None 
                        for slot, item in self.equipment.items()},
            'abilities': [ability.name for ability in self.abilities]
        }
    
    def load_data(self, data: Dict):
        """Load player data from save file"""
        for key, value in data.items():
            if key in ['story_flags']:
                setattr(self, key, set(value))
            elif key in ['inventory']:
                self.inventory = [Item.from_save_data(item_data) for item_data in value]
            elif key in ['equipment']:
                self.equipment = {
                    slot: Item.from_save_data(item_data) if item_data else None
                    for slot, item_data in value.items()
                }
            elif key in ['abilities']:
                from .ability import ABILITIES
                self.abilities = [ABILITIES.get(name) for name in value if name in ABILITIES]
                self.abilities = [a for a in self.abilities if a]  # Filter None values
            else:
                setattr(self, key, value)