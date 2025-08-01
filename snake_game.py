import pygame
import random
import json
import os
import sys
from enum import Enum

# Initialize Pygame
pygame.init()

# Constants
WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600
GRID_SIZE = 20
GRID_WIDTH = WINDOW_WIDTH // GRID_SIZE
GRID_HEIGHT = (WINDOW_HEIGHT - 100) // GRID_SIZE  # Leave space for UI
FPS = 10

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (74, 222, 128)
DARK_GREEN = (34, 197, 94)
RED = (239, 68, 68)
BLUE = (59, 130, 246)
PURPLE = (147, 51, 234)
GRAY = (107, 114, 128)
LIGHT_GRAY = (229, 231, 235)
GOLD = (255, 215, 0)

class Direction(Enum):
    UP = (0, -1)
    DOWN = (0, 1)
    LEFT = (-1, 0)
    RIGHT = (1, 0)

class GameState(Enum):
    MENU = 1
    PLAYING = 2
    GAME_OVER = 3
    PAUSED = 4

class SnakeGame:
    def __init__(self):
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption("🐍 Snake Game - Python Edition")
        self.clock = pygame.time.Clock()
        
        # Fonts
        self.title_font = pygame.font.Font(None, 72)
        self.large_font = pygame.font.Font(None, 48)
        self.medium_font = pygame.font.Font(None, 36)
        self.small_font = pygame.font.Font(None, 24)
        
        # Game state
        self.state = GameState.MENU
        self.score = 0
        self.high_score = self.load_high_score()
        
        # Snake
        self.snake = [(GRID_WIDTH // 2, GRID_HEIGHT // 2)]
        self.direction = Direction.RIGHT
        self.next_direction = Direction.RIGHT
        
        # Food
        self.food = self.generate_food()
        
        # Game settings
        self.game_speed = FPS
        
    def load_high_score(self):
        """Load high score from file"""
        try:
            if os.path.exists('high_score.json'):
                with open('high_score.json', 'r') as f:
                    data = json.load(f)
                    return data.get('high_score', 0)
        except:
            pass
        return 0
    
    def save_high_score(self):
        """Save high score to file"""
        try:
            with open('high_score.json', 'w') as f:
                json.dump({'high_score': self.high_score}, f)
        except:
            pass
    
    def generate_food(self):
        """Generate food at random position not on snake"""
        while True:
            food = (random.randint(0, GRID_WIDTH - 1), random.randint(0, GRID_HEIGHT - 1))
            if food not in self.snake:
                return food
    
    def handle_events(self):
        """Handle pygame events"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            
            if event.type == pygame.KEYDOWN:
                if self.state == GameState.MENU:
                    if event.key in [pygame.K_SPACE, pygame.K_RETURN]:
                        self.start_game()
                
                elif self.state == GameState.PLAYING:
                    if event.key == pygame.K_UP or event.key == pygame.K_w:
                        if self.direction != Direction.DOWN:
                            self.next_direction = Direction.UP
                    elif event.key == pygame.K_DOWN or event.key == pygame.K_s:
                        if self.direction != Direction.UP:
                            self.next_direction = Direction.DOWN
                    elif event.key == pygame.K_LEFT or event.key == pygame.K_a:
                        if self.direction != Direction.RIGHT:
                            self.next_direction = Direction.LEFT
                    elif event.key == pygame.K_RIGHT or event.key == pygame.K_d:
                        if self.direction != Direction.LEFT:
                            self.next_direction = Direction.RIGHT
                    elif event.key == pygame.K_ESCAPE:
                        self.state = GameState.PAUSED
                
                elif self.state == GameState.GAME_OVER:
                    if event.key in [pygame.K_SPACE, pygame.K_RETURN]:
                        self.start_game()
                    elif event.key == pygame.K_ESCAPE:
                        self.state = GameState.MENU
                
                elif self.state == GameState.PAUSED:
                    if event.key == pygame.K_ESCAPE:
                        self.state = GameState.PLAYING
                    elif event.key in [pygame.K_SPACE, pygame.K_RETURN]:
                        self.state = GameState.PLAYING
        
        return True
    
    def start_game(self):
        """Initialize/restart the game"""
        self.state = GameState.PLAYING
        self.score = 0
        self.snake = [(GRID_WIDTH // 2, GRID_HEIGHT // 2)]
        self.direction = Direction.RIGHT
        self.next_direction = Direction.RIGHT
        self.food = self.generate_food()
        self.game_speed = FPS
    
    def update_game(self):
        """Update game logic"""
        if self.state != GameState.PLAYING:
            return
        
        # Update direction
        self.direction = self.next_direction
        
        # Move snake
        head_x, head_y = self.snake[0]
        dx, dy = self.direction.value
        new_head = (head_x + dx, head_y + dy)
        
        # Check wall collision
        if (new_head[0] < 0 or new_head[0] >= GRID_WIDTH or 
            new_head[1] < 0 or new_head[1] >= GRID_HEIGHT):
            self.game_over()
            return
        
        # Check self collision
        if new_head in self.snake:
            self.game_over()
            return
        
        # Add new head
        self.snake.insert(0, new_head)
        
        # Check food collision
        if new_head == self.food:
            self.score += 10
            if self.score > self.high_score:
                self.high_score = self.score
                self.save_high_score()
            self.food = self.generate_food()
            # Increase speed slightly
            if self.game_speed < 15:
                self.game_speed += 0.2
        else:
            # Remove tail if no food eaten
            self.snake.pop()
    
    def game_over(self):
        """Handle game over"""
        self.state = GameState.GAME_OVER
    
    def draw_gradient_rect(self, surface, color1, color2, rect):
        """Draw a rectangle with gradient effect"""
        for y in range(rect.height):
            ratio = y / rect.height
            r = int(color1[0] * (1 - ratio) + color2[0] * ratio)
            g = int(color1[1] * (1 - ratio) + color2[1] * ratio)
            b = int(color1[2] * (1 - ratio) + color2[2] * ratio)
            pygame.draw.line(surface, (r, g, b), 
                           (rect.x, rect.y + y), (rect.x + rect.width, rect.y + y))
    
    def draw_text_with_shadow(self, text, font, color, shadow_color, x, y, center=True):
        """Draw text with shadow effect"""
        # Draw shadow
        shadow_surf = font.render(text, True, shadow_color)
        if center:
            shadow_rect = shadow_surf.get_rect(center=(x + 2, y + 2))
        else:
            shadow_rect = (x + 2, y + 2)
        self.screen.blit(shadow_surf, shadow_rect)
        
        # Draw main text
        text_surf = font.render(text, True, color)
        if center:
            text_rect = text_surf.get_rect(center=(x, y))
        else:
            text_rect = (x, y)
        self.screen.blit(text_surf, text_rect)
    
    def draw_menu(self):
        """Draw the main menu"""
        # Background gradient
        self.draw_gradient_rect(self.screen, PURPLE, BLUE, 
                               pygame.Rect(0, 0, WINDOW_WIDTH, WINDOW_HEIGHT))
        
        # Title
        self.draw_text_with_shadow("🐍 SNAKE GAME", self.title_font, GOLD, BLACK,
                                  WINDOW_WIDTH // 2, 150)
        
        # Subtitle
        self.draw_text_with_shadow("Python Edition", self.medium_font, WHITE, GRAY,
                                  WINDOW_WIDTH // 2, 200)
        
        # Instructions
        instructions = [
            "WASD or Arrow Keys to move",
            "ESC to pause",
            "SPACE to start/restart",
            "",
            f"High Score: {self.high_score}"
        ]
        
        for i, instruction in enumerate(instructions):
            self.draw_text_with_shadow(instruction, self.small_font, WHITE, BLACK,
                                      WINDOW_WIDTH // 2, 300 + i * 30)
        
        # Start prompt
        self.draw_text_with_shadow("Press SPACE to Start!", self.large_font, WHITE, BLACK,
                                  WINDOW_WIDTH // 2, 500)
    
    def draw_game(self):
        """Draw the game screen"""
        # Background
        self.screen.fill(BLACK)
        
        # Game area border
        game_area = pygame.Rect(0, 100, WINDOW_WIDTH, WINDOW_HEIGHT - 100)
        pygame.draw.rect(self.screen, DARK_GREEN, game_area, 3)
        
        # Snake
        for i, segment in enumerate(self.snake):
            x, y = segment
            rect = pygame.Rect(x * GRID_SIZE, y * GRID_SIZE + 100, 
                              GRID_SIZE - 1, GRID_SIZE - 1)
            
            if i == 0:  # Head
                pygame.draw.rect(self.screen, DARK_GREEN, rect)
                pygame.draw.rect(self.screen, WHITE, rect, 2)
                # Eyes
                eye_size = 3
                pygame.draw.circle(self.screen, BLACK, 
                                 (rect.x + 5, rect.y + 5), eye_size)
                pygame.draw.circle(self.screen, BLACK, 
                                 (rect.x + rect.width - 5, rect.y + 5), eye_size)
            else:  # Body
                pygame.draw.rect(self.screen, GREEN, rect)
                pygame.draw.rect(self.screen, DARK_GREEN, rect, 1)
        
        # Food
        food_x, food_y = self.food
        food_center = (food_x * GRID_SIZE + GRID_SIZE // 2, 
                      food_y * GRID_SIZE + 100 + GRID_SIZE // 2)
        pygame.draw.circle(self.screen, RED, food_center, GRID_SIZE // 2 - 1)
        pygame.draw.circle(self.screen, WHITE, food_center, GRID_SIZE // 2 - 1, 2)
        
        # UI
        self.draw_ui()
    
    def draw_ui(self):
        """Draw the user interface"""
        # Background for UI
        ui_rect = pygame.Rect(0, 0, WINDOW_WIDTH, 100)
        self.draw_gradient_rect(self.screen, BLUE, PURPLE, ui_rect)
        
        # Score
        score_text = f"Score: {self.score}"
        self.draw_text_with_shadow(score_text, self.medium_font, WHITE, BLACK, 100, 30, False)
        
        # High Score
        high_score_text = f"High Score: {self.high_score}"
        self.draw_text_with_shadow(high_score_text, self.medium_font, GOLD, BLACK, 100, 60, False)
        
        # Game title
        self.draw_text_with_shadow("🐍 SNAKE", self.large_font, WHITE, BLACK,
                                  WINDOW_WIDTH // 2, 50)
        
        # Controls hint
        controls_text = "ESC: Pause"
        self.draw_text_with_shadow(controls_text, self.small_font, WHITE, BLACK,
                                  WINDOW_WIDTH - 100, 50)
    
    def draw_game_over(self):
        """Draw the game over screen"""
        # Semi-transparent overlay
        overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT))
        overlay.set_alpha(180)
        overlay.fill(BLACK)
        self.screen.blit(overlay, (0, 0))
        
        # Game Over box
        box_width, box_height = 400, 300
        box_x = (WINDOW_WIDTH - box_width) // 2
        box_y = (WINDOW_HEIGHT - box_height) // 2
        box_rect = pygame.Rect(box_x, box_y, box_width, box_height)
        
        self.draw_gradient_rect(self.screen, RED, PURPLE, box_rect)
        pygame.draw.rect(self.screen, WHITE, box_rect, 3)
        
        # Game Over text
        self.draw_text_with_shadow("GAME OVER", self.large_font, WHITE, BLACK,
                                  WINDOW_WIDTH // 2, box_y + 60)
        
        # Final score
        score_text = f"Final Score: {self.score}"
        self.draw_text_with_shadow(score_text, self.medium_font, WHITE, BLACK,
                                  WINDOW_WIDTH // 2, box_y + 120)
        
        # High score
        if self.score == self.high_score and self.score > 0:
            self.draw_text_with_shadow("NEW HIGH SCORE!", self.medium_font, GOLD, BLACK,
                                      WINDOW_WIDTH // 2, box_y + 160)
        else:
            high_score_text = f"High Score: {self.high_score}"
            self.draw_text_with_shadow(high_score_text, self.medium_font, GOLD, BLACK,
                                      WINDOW_WIDTH // 2, box_y + 160)
        
        # Instructions
        self.draw_text_with_shadow("SPACE - Play Again", self.small_font, WHITE, BLACK,
                                  WINDOW_WIDTH // 2, box_y + 220)
        self.draw_text_with_shadow("ESC - Main Menu", self.small_font, WHITE, BLACK,
                                  WINDOW_WIDTH // 2, box_y + 250)
    
    def draw_paused(self):
        """Draw the paused screen"""
        # Semi-transparent overlay
        overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT))
        overlay.set_alpha(150)
        overlay.fill(BLACK)
        self.screen.blit(overlay, (0, 0))
        
        # Paused text
        self.draw_text_with_shadow("PAUSED", self.title_font, WHITE, BLACK,
                                  WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 - 50)
        
        self.draw_text_with_shadow("Press ESC or SPACE to continue", self.medium_font, WHITE, BLACK,
                                  WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2 + 20)
    
    def draw(self):
        """Main draw function"""
        if self.state == GameState.MENU:
            self.draw_menu()
        elif self.state == GameState.PLAYING:
            self.draw_game()
        elif self.state == GameState.GAME_OVER:
            self.draw_game()  # Draw game in background
            self.draw_game_over()
        elif self.state == GameState.PAUSED:
            self.draw_game()  # Draw game in background
            self.draw_paused()
        
        pygame.display.flip()
    
    def run(self):
        """Main game loop"""
        running = True
        
        while running:
            running = self.handle_events()
            self.update_game()
            self.draw()
            self.clock.tick(self.game_speed if self.state == GameState.PLAYING else 60)
        
        pygame.quit()
        sys.exit()

def main():
    """Main function"""
    game = SnakeGame()
    game.run()

if __name__ == "__main__":
    main()