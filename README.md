# 🐍 Snake Game

A classic Snake game implementation available in both web and Python versions!

## Web Version (HTML/JavaScript)

Located in `src/index.html` - A modern, responsive Snake game that runs in any web browser.

### Features:
- **Responsive Design**: Works on desktop and mobile devices
- **Touch Controls**: Mobile-friendly directional buttons
- **Modern UI**: Glassmorphism design with gradient backgrounds
- **Persistent High Scores**: Saves your best score using localStorage
- **Smooth Gameplay**: 60fps canvas rendering

### How to Play (Web):
1. Open `src/index.html` in any web browser
2. Use WASD or Arrow keys to control the snake
3. Press SPACE to restart when game is over
4. On mobile, use the touch control buttons

## Python Version (Pygame)

Located in `snake_game.py` - A feature-rich desktop version with advanced graphics.

### Features:
- **Advanced Graphics**: Gradient backgrounds, shadows, and visual effects
- **Multiple Game States**: Menu, playing, paused, and game over screens
- **Progressive Difficulty**: Speed increases as you eat more food
- **File-based High Scores**: Persistent high score storage in JSON
- **Snake Eyes**: Detailed snake head with animated eyes
- **Pause Functionality**: Press ESC to pause/unpause

### Installation & Setup:
```bash
# Install pygame
pip install pygame==2.5.2

# Or install from requirements.txt
pip install -r requirements.txt
```

### How to Play (Python):
```bash
python snake_game.py
```

### Controls:
- **WASD** or **Arrow Keys**: Move the snake
- **SPACE**: Start game / Restart when game over
- **ESC**: Pause/unpause game, return to menu from game over
- **ENTER**: Alternative to SPACE for starting

### Game Rules:
1. Control the snake to eat red food items
2. Each food item increases your score by 10 points
3. The snake grows longer with each food eaten
4. Avoid hitting the walls or the snake's own body
5. Game speed increases slightly as you progress

### File Structure:
```
├── src/
│   └── index.html          # Web version
├── snake_game.py           # Python version
├── requirements.txt        # Python dependencies
├── high_score.json        # Auto-generated high score file
└── README.md              # This file
```

Both versions feature the same core gameplay with their own unique visual styles and platform-specific optimizations. Choose the version that best fits your environment!

## Screenshots
- Web version features a clean, modern glassmorphism design
- Python version includes detailed graphics with gradient effects and animations

Enjoy playing Snake! 🐍
