"""
Corporate Crusader Systems Package
Contains all game systems: Combat, Audio, Save Management
"""

from .combat import CombatState
from .save_manager import SaveManager

# Try to import AudioManager, but don't fail if pygame isn't available
try:
    from .audio_manager import AudioManager
    __all__ = ['CombatState', 'SaveManager', 'AudioManager']
except ImportError:
    AudioManager = None
    __all__ = ['CombatState', 'SaveManager']