"""
Item system for Corporate Crusader
Includes equipment, consumables, and office supplies
"""
from typing import Dict, List, Optional, Callable
import random

class Item:
    def __init__(self, name: str, description: str, item_type: str, 
                 value: int = 0, rarity: str = "common"):
        self.name = name
        self.description = description
        self.item_type = item_type  # suit, accessory, gadget, drink, consumable, quest
        self.value = value  # Office supplies cost
        self.rarity = rarity  # common, uncommon, rare, legendary
        
        # Equipment bonuses
        self.stat_bonuses: Dict[str, int] = {}
        
        # Consumable effects
        self.consumable_effects: Dict[str, int] = {}
        self.is_consumable = item_type == "consumable"
        
        # Special abilities or effects
        self.special_effect: Optional[Callable] = None
        self.flavor_text = ""
    
    def use(self, player) -> str:
        """Use the item (for consumables)"""
        if not self.is_consumable:
            return "This item cannot be consumed."
        
        results = []
        for effect, amount in self.consumable_effects.items():
            if effect == "health":
                player.heal(amount)
                results.append(f"Restored {amount} health")
            elif effect == "caffeine":
                player.restore_caffeine(amount)
                results.append(f"Restored {amount} caffeine")
            elif effect == "stress":
                player.reduce_stress(amount)
                results.append(f"Reduced stress by {amount}")
            elif effect == "experience":
                player.add_experience(amount)
                results.append(f"Gained {amount} experience")
        
        if self.special_effect:
            special_result = self.special_effect(player)
            if special_result:
                results.append(special_result)
        
        return ". ".join(results) if results else "Nothing happened."
    
    def get_rarity_color(self) -> str:
        """Get color code for rarity"""
        colors = {
            "common": "#FFFFFF",
            "uncommon": "#00FF00", 
            "rare": "#0080FF",
            "legendary": "#FF8000"
        }
        return colors.get(self.rarity, "#FFFFFF")
    
    def save_data(self) -> Dict:
        """Export item data for saving"""
        return {
            'name': self.name,
            'description': self.description,
            'item_type': self.item_type,
            'value': self.value,
            'rarity': self.rarity,
            'stat_bonuses': self.stat_bonuses,
            'consumable_effects': self.consumable_effects,
            'flavor_text': self.flavor_text
        }
    
    @classmethod
    def from_save_data(cls, data: Dict) -> 'Item':
        """Create item from save data"""
        item = cls(
            data['name'],
            data['description'], 
            data['item_type'],
            data.get('value', 0),
            data.get('rarity', 'common')
        )
        item.stat_bonuses = data.get('stat_bonuses', {})
        item.consumable_effects = data.get('consumable_effects', {})
        item.flavor_text = data.get('flavor_text', '')
        return item

# Special effect functions
def coffee_buzz_effect(player) -> str:
    """Special effect for premium coffee"""
    if random.random() < 0.3:  # 30% chance
        player.add_experience(5)
        return "The caffeine rush sparked an epiphany! (+5 XP)"
    return ""

def networking_lunch_effect(player) -> str:
    """Special effect for networking lunch"""
    player.influence += 1
    return "Made a valuable connection (+1 Influence)"

def stress_ball_effect(player) -> str:
    """Special effect for stress ball"""
    if player.stress > 50:
        extra_relief = 10
        player.reduce_stress(extra_relief)
        return f"Perfect timing! Extra stress relief (+{extra_relief})"
    return ""

# Pre-defined items catalog
ITEMS_CATALOG = {
    # Suits (armor equivalent)
    "cheap_suit": Item(
        "Cheap Polyester Suit",
        "It's shiny, uncomfortable, and screams 'I shop at discount stores'",
        "suit", 50, "common"
    ),
    "business_casual": Item(
        "Business Casual Ensemble", 
        "The uniform of the eternally middle-management",
        "suit", 150, "uncommon"
    ),
    "designer_suit": Item(
        "Designer Power Suit",
        "Intimidates interns and impresses executives",
        "suit", 500, "rare"
    ),
    "ceo_suit": Item(
        "Executive Armor",
        "Woven from the tears of laid-off employees and golden parachutes",
        "suit", 2000, "legendary"
    ),
    
    # Accessories
    "plastic_watch": Item(
        "Plastic Digital Watch",
        "Shows time in 3 time zones you'll never visit",
        "accessory", 25, "common"
    ),
    "bluetooth_headset": Item(
        "Bluetooth Headset", 
        "Makes you look important while you ignore your family",
        "accessory", 100, "uncommon"
    ),
    "gold_tie_clip": Item(
        "Golden Tie Clip",
        "Subtle flex that says 'I have more money than taste'",
        "accessory", 300, "rare"
    ),
    "ceo_watch": Item(
        "Swiss Chronometer of Oppression",
        "Each tick represents another worker's dream being crushed",
        "accessory", 5000, "legendary"
    ),
    
    # Gadgets
    "calculator": Item(
        "Basic Calculator",
        "Perfect for calculating your existential dread per hour",
        "gadget", 15, "common"
    ),
    "smartphone": Item(
        "Corporate Smartphone",
        "Leash disguised as connectivity",
        "gadget", 200, "uncommon"
    ),
    "laptop": Item(
        "High-End Laptop",
        "Powerful enough to run your dreams into the ground",
        "gadget", 800, "rare"
    ),
    "ai_assistant": Item(
        "Corporate AI Assistant",
        "It knows your deepest fears and reports them to HR",
        "gadget", 3000, "legendary"
    ),
    
    # Drinks
    "instant_coffee": Item(
        "Instant Coffee",
        "Brown water that technically contains caffeine",
        "drink", 5, "common"
    ),
    "energy_drink": Item(
        "Corporate Energy Drink",
        "Liquid anxiety in a can",
        "drink", 15, "uncommon"
    ),
    "premium_coffee": Item(
        "Artisanal Coffee Blend",
        "Ethically sourced from workers paid almost living wages",
        "drink", 50, "rare"
    ),
    "ceo_coffee": Item(
        "Executive Espresso",
        "Made from beans harvested by unpaid interns",
        "drink", 200, "legendary"
    ),
    
    # Consumables
    "donut": Item(
        "Stale Office Donut",
        "Sugar-coated despair from the break room",
        "consumable", 3, "common"
    ),
    "energy_bar": Item(
        "Protein Energy Bar",
        "Tastes like cardboard, provides actual nutrition",
        "consumable", 8, "common"
    ),
    "networking_lunch": Item(
        "Networking Lunch",
        "Overpriced salad with a side of empty promises",
        "consumable", 25, "uncommon"
    ),
    "stress_ball": Item(
        "Therapeutic Stress Ball",
        "Squeeze away your problems (spoiler: they remain)",
        "consumable", 20, "uncommon"
    ),
    "meditation_app": Item(
        "Premium Meditation App",
        "Mindfulness subscription to ignore your problems mindfully",
        "consumable", 100, "rare"
    )
}

# Set up item stats and effects
def initialize_items():
    """Initialize all item stats and effects"""
    
    # Suits - increase charisma and provide some protection
    ITEMS_CATALOG["cheap_suit"].stat_bonuses = {"charisma": 1, "max_health": 5}
    ITEMS_CATALOG["business_casual"].stat_bonuses = {"charisma": 3, "competence": 1, "max_health": 10}
    ITEMS_CATALOG["designer_suit"].stat_bonuses = {"charisma": 6, "networking": 2, "max_health": 20}
    ITEMS_CATALOG["ceo_suit"].stat_bonuses = {"charisma": 10, "networking": 5, "cynicism": 3, "max_health": 40}
    
    # Accessories - various bonuses
    ITEMS_CATALOG["plastic_watch"].stat_bonuses = {"competence": 1}
    ITEMS_CATALOG["bluetooth_headset"].stat_bonuses = {"networking": 2, "charisma": 1}
    ITEMS_CATALOG["gold_tie_clip"].stat_bonuses = {"charisma": 4, "networking": 2}
    ITEMS_CATALOG["ceo_watch"].stat_bonuses = {"charisma": 6, "competence": 4, "networking": 3}
    
    # Gadgets - boost competence and utility
    ITEMS_CATALOG["calculator"].stat_bonuses = {"competence": 2}
    ITEMS_CATALOG["smartphone"].stat_bonuses = {"competence": 3, "networking": 3}
    ITEMS_CATALOG["laptop"].stat_bonuses = {"competence": 6, "networking": 2}
    ITEMS_CATALOG["ai_assistant"].stat_bonuses = {"competence": 10, "networking": 5, "cynicism": 2}
    
    # Drinks - mainly caffeine and temporary boosts
    ITEMS_CATALOG["instant_coffee"].stat_bonuses = {"max_caffeine": 5}
    ITEMS_CATALOG["energy_drink"].stat_bonuses = {"max_caffeine": 10, "max_health": -5}  # Unhealthy
    ITEMS_CATALOG["premium_coffee"].stat_bonuses = {"max_caffeine": 15, "charisma": 1}
    ITEMS_CATALOG["premium_coffee"].special_effect = coffee_buzz_effect
    ITEMS_CATALOG["ceo_coffee"].stat_bonuses = {"max_caffeine": 25, "charisma": 3, "cynicism": 1}
    
    # Consumables - immediate effects
    ITEMS_CATALOG["donut"].consumable_effects = {"health": 5, "caffeine": 5, "stress": -5}
    ITEMS_CATALOG["energy_bar"].consumable_effects = {"health": 15, "caffeine": 10}
    ITEMS_CATALOG["networking_lunch"].consumable_effects = {"health": 20, "stress": 15}
    ITEMS_CATALOG["networking_lunch"].special_effect = networking_lunch_effect
    ITEMS_CATALOG["stress_ball"].consumable_effects = {"stress": 20}
    ITEMS_CATALOG["stress_ball"].special_effect = stress_ball_effect
    ITEMS_CATALOG["meditation_app"].consumable_effects = {"stress": 30, "health": 10}

# Initialize items when module is imported
initialize_items()

def get_random_item(rarity_weights: Dict[str, float] = None) -> Item:
    """Get a random item based on rarity weights"""
    if rarity_weights is None:
        rarity_weights = {"common": 0.5, "uncommon": 0.3, "rare": 0.15, "legendary": 0.05}
    
    # Filter items by rarity
    rarity_pools = {rarity: [] for rarity in rarity_weights.keys()}
    for item in ITEMS_CATALOG.values():
        if item.rarity in rarity_pools:
            rarity_pools[item.rarity].append(item)
    
    # Choose rarity based on weights
    rarities = list(rarity_weights.keys())
    weights = list(rarity_weights.values())
    chosen_rarity = random.choices(rarities, weights=weights)[0]
    
    # Choose random item from that rarity
    if rarity_pools[chosen_rarity]:
        chosen_item = random.choice(rarity_pools[chosen_rarity])
        # Create a copy so each instance is unique
        return Item.from_save_data(chosen_item.save_data())
    
    # Fallback to common item
    return Item.from_save_data(ITEMS_CATALOG["cheap_suit"].save_data())