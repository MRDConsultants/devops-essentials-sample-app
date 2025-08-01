#!/usr/bin/env python3
"""
Corporate Crusader - Main Entry Point
A satirical RPG about climbing the corporate ladder

Welcome to the world of corporate warfare, where your weapons are buzzwords,
your armor is a cheap suit, and your enemies are every annoying office stereotype
you've ever encountered.

Controls:
- Arrow Keys / Mouse: Navigate menus
- Enter/Space: Select options
- Escape: Go back/Exit
- Number Keys (1-4): Combat actions

Features:
- Turn-based corporate combat
- Equipment and inventory system
- Hilarious corporate-themed abilities
- Progression through office floors
- Save/Load system
- Multiple enemy types with unique AI

Author: AI Assistant
Version: 1.0
"""

import sys
import os

# Add src directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

try:
    from src.ui.ui_manager import UIManager
except ImportError as e:
    print(f"Failed to import game modules: {e}")
    print("Make sure pygame is installed: pip install pygame")
    sys.exit(1)

def main():
    """Main entry point"""
    print("=" * 60)
    print("🏢 CORPORATE CRUSADER 🏢")
    print("Climb the Corporate Ladder of Success!")
    print("=" * 60)
    print()
    print("Starting game...")
    
    try:
        # Create and run the UI manager
        ui_manager = UIManager(width=1200, height=800)
        ui_manager.run()
    
    except KeyboardInterrupt:
        print("\n\nGame interrupted by user. Thanks for playing!")
    
    except Exception as e:
        print(f"\nAn error occurred: {e}")
        print("Please check that all dependencies are installed.")
        return 1
    
    return 0

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)