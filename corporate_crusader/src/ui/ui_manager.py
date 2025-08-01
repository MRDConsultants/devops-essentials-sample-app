"""
UI Manager for Corporate Crusader
Handles all pygame-based user interface elements
"""
import pygame
import sys
from typing import Dict, List, Optional, Tuple, Any
from .colors import *
from ..game import GameState

class UIManager:
    def __init__(self, width: int = 1200, height: int = 800):
        # Initialize pygame
        pygame.init()
        
        self.width = width
        self.height = height
        self.screen = pygame.display.set_mode((width, height))
        pygame.display.set_caption("Corporate Crusader - Climb the Corporate Ladder")
        
        # Clock for FPS control
        self.clock = pygame.time.Clock()
        self.fps = 60
        
        # Fonts
        self.fonts = self._load_fonts()
        
        # Game state
        self.game = GameState()
        self.current_menu = "main_menu"
        
        # UI state
        self.selected_button = 0
        self.scroll_offset = 0
        self.animation_time = 0
        
        # Input handling
        self.keys_pressed = set()
        self.mouse_pos = (0, 0)
        self.mouse_clicked = False
        
        # UI elements cache
        self.buttons = []
        self.text_elements = []
        
    def _load_fonts(self) -> Dict[str, pygame.font.Font]:
        """Load fonts with fallbacks"""
        fonts = {}
        
        try:
            # Try to load system fonts
            fonts['title'] = pygame.font.Font(None, 48)
            fonts['large'] = pygame.font.Font(None, 32)
            fonts['medium'] = pygame.font.Font(None, 24)
            fonts['small'] = pygame.font.Font(None, 18)
            fonts['tiny'] = pygame.font.Font(None, 14)
        except:
            # Fallback to default font
            fonts['title'] = pygame.font.Font(None, 48)
            fonts['large'] = pygame.font.Font(None, 32)
            fonts['medium'] = pygame.font.Font(None, 24)
            fonts['small'] = pygame.font.Font(None, 18)
            fonts['tiny'] = pygame.font.Font(None, 14)
        
        return fonts
    
    def run(self):
        """Main game loop"""
        running = True
        
        while running:
            # Handle events
            running = self._handle_events()
            
            # Update game state
            self._update()
            
            # Render frame
            self._render()
            
            # Control FPS
            self.clock.tick(self.fps)
        
        pygame.quit()
        sys.exit()
    
    def _handle_events(self) -> bool:
        """Handle pygame events"""
        self.mouse_clicked = False
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            
            elif event.type == pygame.KEYDOWN:
                self.keys_pressed.add(event.key)
                self._handle_keydown(event.key)
            
            elif event.type == pygame.KEYUP:
                self.keys_pressed.discard(event.key)
            
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Left click
                    self.mouse_clicked = True
                    self._handle_mouse_click(event.pos)
            
            elif event.type == pygame.MOUSEMOTION:
                self.mouse_pos = event.pos
        
        return True
    
    def _handle_keydown(self, key: int):
        """Handle key press events"""
        if self.current_menu == "main_menu":
            if key == pygame.K_RETURN or key == pygame.K_SPACE:
                self._activate_selected_button()
            elif key == pygame.K_UP:
                self.selected_button = max(0, self.selected_button - 1)
            elif key == pygame.K_DOWN:
                self.selected_button = min(len(self.buttons) - 1, self.selected_button + 1)
        
        elif self.current_menu == "combat":
            if key == pygame.K_1:
                self._combat_action("attack")
            elif key == pygame.K_2:
                self._combat_action("ability")
            elif key == pygame.K_3:
                self._combat_action("item")
            elif key == pygame.K_4:
                self._combat_action("flee")
        
        # Global keys
        if key == pygame.K_ESCAPE:
            if self.current_menu != "main_menu":
                self.current_menu = "main_menu"
            else:
                return False
    
    def _handle_mouse_click(self, pos: Tuple[int, int]):
        """Handle mouse click events"""
        # Check button clicks
        for i, button in enumerate(self.buttons):
            if self._point_in_rect(pos, button['rect']):
                self.selected_button = i
                self._activate_selected_button()
                break
    
    def _point_in_rect(self, point: Tuple[int, int], rect: pygame.Rect) -> bool:
        """Check if point is inside rectangle"""
        return rect.collidepoint(point)
    
    def _activate_selected_button(self):
        """Activate the currently selected button"""
        if 0 <= self.selected_button < len(self.buttons):
            button = self.buttons[self.selected_button]
            action = button.get('action')
            
            if action:
                self._execute_action(action)
    
    def _execute_action(self, action: str):
        """Execute a UI action"""
        if action == "new_game":
            result = self.game.start_new_game("Corporate Climber")
            self.current_menu = "exploration"
        
        elif action == "load_game":
            self.current_menu = "load_menu"
        
        elif action == "quit":
            pygame.quit()
            sys.exit()
        
        elif action == "back":
            self.current_menu = "main_menu"
        
        elif action.startswith("explore_"):
            exploration_action = action[8:]  # Remove "explore_" prefix
            result = self.game.process_exploration_action(exploration_action)
            
            if result.get("new_scene"):
                self.current_menu = result["new_scene"]
            elif result.get("new_scene") == "combat":
                self.current_menu = "combat"
        
        elif action == "inventory":
            self.current_menu = "inventory"
        
        elif action == "character":
            self.current_menu = "character"
    
    def _combat_action(self, action: str):
        """Handle combat actions"""
        if self.game.current_combat:
            result = self.game.process_combat_action(action)
            
            if result.get("combat_ended"):
                self.current_menu = "exploration"
    
    def _update(self):
        """Update game state and animations"""
        self.animation_time += self.clock.get_time() / 1000.0
        
        # Update buttons based on current menu
        self._update_buttons()
    
    def _update_buttons(self):
        """Update button list based on current menu"""
        self.buttons = []
        
        if self.current_menu == "main_menu":
            self.buttons = [
                {"text": "New Game", "action": "new_game"},
                {"text": "Load Game", "action": "load_game"},
                {"text": "Quit", "action": "quit"}
            ]
        
        elif self.current_menu == "exploration":
            options = self.game.get_exploration_options()
            if "actions" in options:
                for action in options["actions"]:
                    self.buttons.append({
                        "text": action["name"],
                        "action": f"explore_{action['id']}",
                        "description": action["description"]
                    })
        
        elif self.current_menu == "combat":
            if self.game.current_combat:
                actions = self.game.current_combat.get_available_actions()
                self.buttons = [
                    {"text": "Attack (1)", "action": "attack"},
                    {"text": "Abilities (2)", "action": "ability"},
                    {"text": "Items (3)", "action": "item"},
                    {"text": "Flee (4)", "action": "flee"}
                ]
        
        # Add rect positions to buttons
        self._position_buttons()
    
    def _position_buttons(self):
        """Calculate button positions"""
        button_height = 60
        button_width = 300
        start_y = self.height // 2 - (len(self.buttons) * button_height) // 2
        
        for i, button in enumerate(self.buttons):
            x = self.width // 2 - button_width // 2
            y = start_y + i * (button_height + 10)
            button['rect'] = pygame.Rect(x, y, button_width, button_height)
    
    def _render(self):
        """Render the current frame"""
        # Clear screen
        self.screen.fill(OFFICE_BEIGE)
        
        # Render based on current menu
        if self.current_menu == "main_menu":
            self._render_main_menu()
        elif self.current_menu == "exploration":
            self._render_exploration()
        elif self.current_menu == "combat":
            self._render_combat()
        elif self.current_menu == "inventory":
            self._render_inventory()
        elif self.current_menu == "character":
            self._render_character()
        elif self.current_menu == "shop":
            self._render_shop()
        
        # Update display
        pygame.display.flip()
    
    def _render_main_menu(self):
        """Render the main menu"""
        # Title
        title_text = self.fonts['title'].render("CORPORATE CRUSADER", True, CORPORATE_BLUE)
        title_rect = title_text.get_rect(center=(self.width // 2, 150))
        self.screen.blit(title_text, title_rect)
        
        # Subtitle
        subtitle_text = self.fonts['medium'].render("Climb the Corporate Ladder", True, CORPORATE_GRAY)
        subtitle_rect = subtitle_text.get_rect(center=(self.width // 2, 200))
        self.screen.blit(subtitle_text, subtitle_rect)
        
        # Render buttons
        self._render_buttons()
    
    def _render_exploration(self):
        """Render exploration interface"""
        # Header
        if self.game.player:
            stats = self.game.get_player_stats()
            
            # Player info
            player_text = f"{stats['name']} - Level {stats['level']} {stats['job_title']}"
            player_surface = self.fonts['large'].render(player_text, True, CORPORATE_BLUE)
            self.screen.blit(player_surface, (20, 20))
            
            # Floor info
            floor_text = f"Floor {stats['current_floor']}"
            floor_surface = self.fonts['medium'].render(floor_text, True, CORPORATE_GRAY)
            self.screen.blit(floor_surface, (20, 60))
            
            # Status bars
            self._render_status_bars(100, 100, stats)
        
        # Action buttons
        self._render_buttons()
        
        # Recent messages (if any)
        # This would show exploration results
    
    def _render_combat(self):
        """Render combat interface"""
        if not self.game.current_combat:
            return
        
        combat_state = self.game.current_combat.get_combat_state()
        
        # Combat header
        header_text = f"Combat - Turn {combat_state['turn_count']}"
        header_surface = self.fonts['large'].render(header_text, True, CORPORATE_BLUE)
        self.screen.blit(header_surface, (20, 20))
        
        # Player status (left side)
        player_data = combat_state['player']
        self._render_combat_entity(50, 100, "You", player_data, True)
        
        # Enemy status (right side)
        enemy_data = combat_state['enemy']
        self._render_combat_entity(self.width - 350, 100, enemy_data['name'], enemy_data, False)
        
        # Combat log
        self._render_combat_log(50, 400)
        
        # Action buttons
        self._render_buttons()
    
    def _render_inventory(self):
        """Render inventory interface"""
        # Title
        title_text = self.fonts['large'].render("Inventory & Equipment", True, CORPORATE_BLUE)
        self.screen.blit(title_text, (20, 20))
        
        if self.game.player:
            # Equipment slots
            self._render_equipment_slots(50, 80)
            
            # Inventory grid
            self._render_inventory_grid(50, 300)
        
        # Back button
        back_button = {"text": "Back", "action": "back", "rect": pygame.Rect(50, self.height - 80, 100, 50)}
        self._render_button(back_button, 0, False)
    
    def _render_character(self):
        """Render character stats interface"""
        if not self.game.player:
            return
        
        stats = self.game.get_player_stats()
        
        # Title
        title_text = self.fonts['large'].render(f"Character: {stats['name']}", True, CORPORATE_BLUE)
        self.screen.blit(title_text, (20, 20))
        
        # Stats display
        y_offset = 80
        stat_names = ['charisma', 'competence', 'networking', 'cynicism']
        
        for stat in stat_names:
            stat_text = f"{stat.title()}: {stats[stat]}"
            stat_surface = self.fonts['medium'].render(stat_text, True, TEXT_DARK)
            self.screen.blit(stat_surface, (50, y_offset))
            y_offset += 40
        
        # Resources
        y_offset += 20
        resources = [
            f"Office Supplies: {stats['office_supplies']}",
            f"Influence: {stats['influence']}",
            f"Enemies Defeated: {stats['enemies_defeated']}"
        ]
        
        for resource in resources:
            resource_surface = self.fonts['medium'].render(resource, True, TEXT_DARK)
            self.screen.blit(resource_surface, (50, y_offset))
            y_offset += 30
        
        # Back button
        back_button = {"text": "Back", "action": "back", "rect": pygame.Rect(50, self.height - 80, 100, 50)}
        self._render_button(back_button, 0, False)
    
    def _render_shop(self):
        """Render shop interface"""
        # Title
        title_text = self.fonts['large'].render("Office Supply Closet", True, CORPORATE_BLUE)
        self.screen.blit(title_text, (20, 20))
        
        # Player money
        if self.game.player:
            money_text = f"Office Supplies: {self.game.player.office_supplies}"
            money_surface = self.fonts['medium'].render(money_text, True, CORPORATE_GRAY)
            self.screen.blit(money_surface, (20, 60))
        
        # Shop items
        shop_items = self.game.get_shop_items()
        y_offset = 120
        
        for item in shop_items:
            # Item name and price
            item_text = f"{item['name']} - {item['price']} supplies"
            item_surface = self.fonts['medium'].render(item_text, True, TEXT_DARK)
            self.screen.blit(item_surface, (50, y_offset))
            
            # Item description
            desc_surface = self.fonts['small'].render(item['description'], True, TEXT_MUTED)
            self.screen.blit(desc_surface, (50, y_offset + 25))
            
            y_offset += 60
        
        # Back button
        back_button = {"text": "Back", "action": "back", "rect": pygame.Rect(50, self.height - 80, 100, 50)}
        self._render_button(back_button, 0, False)
    
    def _render_buttons(self):
        """Render all buttons"""
        for i, button in enumerate(self.buttons):
            selected = (i == self.selected_button)
            self._render_button(button, i, selected)
    
    def _render_button(self, button: Dict, index: int, selected: bool):
        """Render a single button"""
        rect = button['rect']
        
        # Button background
        bg_color = BUTTON_PRIMARY if selected else BUTTON_SECONDARY
        if self._point_in_rect(self.mouse_pos, rect):
            bg_color = BUTTON_HOVER if not selected else bg_color
        
        pygame.draw.rect(self.screen, bg_color, rect)
        pygame.draw.rect(self.screen, CORPORATE_BLUE, rect, 2)
        
        # Button text
        text_color = TEXT_LIGHT if selected else TEXT_DARK
        text_surface = self.fonts['medium'].render(button['text'], True, text_color)
        text_rect = text_surface.get_rect(center=rect.center)
        self.screen.blit(text_surface, text_rect)
        
        # Description (if available)
        if 'description' in button and selected:
            desc_y = rect.bottom + 10
            desc_surface = self.fonts['small'].render(button['description'], True, TEXT_MUTED)
            desc_rect = desc_surface.get_rect(centerx=rect.centerx, top=desc_y)
            self.screen.blit(desc_surface, desc_rect)
    
    def _render_status_bars(self, x: int, y: int, stats: Dict):
        """Render health, caffeine, and stress bars"""
        bar_width = 200
        bar_height = 20
        
        # Health bar
        health_ratio = stats['health'] / stats['max_health']
        health_rect = pygame.Rect(x, y, bar_width, bar_height)
        health_fill = pygame.Rect(x, y, bar_width * health_ratio, bar_height)
        
        pygame.draw.rect(self.screen, CORPORATE_GRAY, health_rect)
        pygame.draw.rect(self.screen, HEALTH_GREEN, health_fill)
        pygame.draw.rect(self.screen, TEXT_DARK, health_rect, 2)
        
        health_text = f"Health: {stats['health']}/{stats['max_health']}"
        health_surface = self.fonts['small'].render(health_text, True, TEXT_DARK)
        self.screen.blit(health_surface, (x, y - 20))
        
        # Caffeine bar
        y += 40
        caffeine_ratio = stats['caffeine'] / stats['max_caffeine']
        caffeine_rect = pygame.Rect(x, y, bar_width, bar_height)
        caffeine_fill = pygame.Rect(x, y, bar_width * caffeine_ratio, bar_height)
        
        pygame.draw.rect(self.screen, CORPORATE_GRAY, caffeine_rect)
        pygame.draw.rect(self.screen, CAFFEINE_BROWN, caffeine_fill)
        pygame.draw.rect(self.screen, TEXT_DARK, caffeine_rect, 2)
        
        caffeine_text = f"Caffeine: {stats['caffeine']}/{stats['max_caffeine']}"
        caffeine_surface = self.fonts['small'].render(caffeine_text, True, TEXT_DARK)
        self.screen.blit(caffeine_surface, (x, y - 20))
        
        # Stress bar
        y += 40
        stress_ratio = stats['stress'] / stats['max_stress']
        stress_rect = pygame.Rect(x, y, bar_width, bar_height)
        stress_fill = pygame.Rect(x, y, bar_width * stress_ratio, bar_height)
        
        pygame.draw.rect(self.screen, CORPORATE_GRAY, stress_rect)
        pygame.draw.rect(self.screen, STRESS_RED, stress_fill)
        pygame.draw.rect(self.screen, TEXT_DARK, stress_rect, 2)
        
        stress_text = f"Stress: {stats['stress']}/{stats['max_stress']}"
        stress_surface = self.fonts['small'].render(stress_text, True, TEXT_DARK)
        self.screen.blit(stress_surface, (x, y - 20))
    
    def _render_combat_entity(self, x: int, y: int, name: str, data: Dict, is_player: bool):
        """Render combat entity status"""
        # Name
        name_surface = self.fonts['medium'].render(name, True, CORPORATE_BLUE)
        self.screen.blit(name_surface, (x, y))
        
        # Health bar
        y += 30
        health_ratio = data['health'] / data['max_health']
        health_rect = pygame.Rect(x, y, 200, 20)
        health_fill = pygame.Rect(x, y, 200 * health_ratio, 20)
        
        pygame.draw.rect(self.screen, CORPORATE_GRAY, health_rect)
        pygame.draw.rect(self.screen, HEALTH_GREEN, health_fill)
        pygame.draw.rect(self.screen, TEXT_DARK, health_rect, 2)
        
        health_text = f"{data['health']}/{data['max_health']}"
        health_surface = self.fonts['small'].render(health_text, True, TEXT_DARK)
        self.screen.blit(health_surface, (x + 210, y))
        
        # Additional stats for player
        if is_player:
            # Caffeine
            y += 40
            caffeine_ratio = data['caffeine'] / data['max_caffeine']
            caffeine_rect = pygame.Rect(x, y, 200, 20)
            caffeine_fill = pygame.Rect(x, y, 200 * caffeine_ratio, 20)
            
            pygame.draw.rect(self.screen, CORPORATE_GRAY, caffeine_rect)
            pygame.draw.rect(self.screen, CAFFEINE_BROWN, caffeine_fill)
            pygame.draw.rect(self.screen, TEXT_DARK, caffeine_rect, 2)
            
            caffeine_text = f"Caffeine: {data['caffeine']}/{data['max_caffeine']}"
            caffeine_surface = self.fonts['small'].render(caffeine_text, True, TEXT_DARK)
            self.screen.blit(caffeine_surface, (x, y - 20))
        else:
            # Enemy level and type
            y += 40
            enemy_info = f"Level {data['level']} {data['enemy_type'].replace('_', ' ').title()}"
            enemy_surface = self.fonts['small'].render(enemy_info, True, TEXT_MUTED)
            self.screen.blit(enemy_surface, (x, y))
    
    def _render_combat_log(self, x: int, y: int):
        """Render combat log messages"""
        if not self.game.current_combat:
            return
        
        log_entries = self.game.current_combat.get_recent_log(5)
        
        log_title = self.fonts['medium'].render("Combat Log:", True, CORPORATE_BLUE)
        self.screen.blit(log_title, (x, y))
        
        y += 30
        for entry in log_entries:
            entry_surface = self.fonts['small'].render(entry, True, TEXT_DARK)
            self.screen.blit(entry_surface, (x, y))
            y += 25
    
    def _render_equipment_slots(self, x: int, y: int):
        """Render equipment slots"""
        if not self.game.player:
            return
        
        equipment_title = self.fonts['medium'].render("Equipment:", True, CORPORATE_BLUE)
        self.screen.blit(equipment_title, (x, y))
        
        y += 40
        slot_names = ["Suit", "Accessory", "Gadget", "Drink"]
        
        for i, slot_name in enumerate(slot_names):
            slot_key = slot_name.lower()
            equipped_item = self.game.player.equipment.get(slot_key)
            
            slot_text = f"{slot_name}: "
            if equipped_item:
                slot_text += equipped_item.name
                color = TEXT_SUCCESS
            else:
                slot_text += "None"
                color = TEXT_MUTED
            
            slot_surface = self.fonts['small'].render(slot_text, True, color)
            self.screen.blit(slot_surface, (x, y + i * 30))
    
    def _render_inventory_grid(self, x: int, y: int):
        """Render inventory grid"""
        if not self.game.player:
            return
        
        inventory_title = self.fonts['medium'].render("Inventory:", True, CORPORATE_BLUE)
        self.screen.blit(inventory_title, (x, y))
        
        y += 40
        for i, item in enumerate(self.game.player.inventory):
            item_text = f"• {item.name}"
            
            # Color by rarity
            if item.rarity == "common":
                color = COMMON_WHITE
            elif item.rarity == "uncommon":
                color = UNCOMMON_GREEN
            elif item.rarity == "rare":
                color = RARE_BLUE
            elif item.rarity == "legendary":
                color = LEGENDARY_ORANGE
            else:
                color = TEXT_DARK
            
            item_surface = self.fonts['small'].render(item_text, True, color)
            self.screen.blit(item_surface, (x, y + i * 25))