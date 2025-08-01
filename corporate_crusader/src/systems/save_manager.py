"""
Save/Load system for Corporate Crusader
Handles game state persistence
"""
import json
import os
from datetime import datetime
from typing import Dict, List, Optional

class SaveManager:
    def __init__(self, save_directory: str = "data/saves"):
        self.save_directory = save_directory
        self.ensure_save_directory()
    
    def ensure_save_directory(self):
        """Create save directory if it doesn't exist"""
        if not os.path.exists(self.save_directory):
            os.makedirs(self.save_directory)
    
    def save_game(self, player, game_state: Dict, save_name: str = None) -> bool:
        """Save the current game state"""
        try:
            if save_name is None:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                save_name = f"save_{timestamp}"
            
            save_data = {
                "version": "1.0",
                "timestamp": datetime.now().isoformat(),
                "player_data": player.save_data(),
                "game_state": game_state
            }
            
            save_path = os.path.join(self.save_directory, f"{save_name}.json")
            
            with open(save_path, 'w') as f:
                json.dump(save_data, f, indent=2)
            
            return True
            
        except Exception as e:
            print(f"Error saving game: {e}")
            return False
    
    def load_game(self, save_name: str) -> Optional[Dict]:
        """Load a saved game"""
        try:
            save_path = os.path.join(self.save_directory, f"{save_name}.json")
            
            if not os.path.exists(save_path):
                return None
            
            with open(save_path, 'r') as f:
                save_data = json.load(f)
            
            return save_data
            
        except Exception as e:
            print(f"Error loading game: {e}")
            return None
    
    def list_saves(self) -> List[Dict]:
        """List all available save files"""
        saves = []
        
        try:
            for filename in os.listdir(self.save_directory):
                if filename.endswith('.json'):
                    save_name = filename[:-5]  # Remove .json extension
                    save_path = os.path.join(self.save_directory, filename)
                    
                    try:
                        with open(save_path, 'r') as f:
                            save_data = json.load(f)
                        
                        saves.append({
                            "name": save_name,
                            "timestamp": save_data.get("timestamp", "Unknown"),
                            "player_name": save_data.get("player_data", {}).get("name", "Unknown"),
                            "level": save_data.get("player_data", {}).get("level", 1),
                            "department": save_data.get("player_data", {}).get("department", "Unknown")
                        })
                    except:
                        continue  # Skip corrupted saves
        
        except FileNotFoundError:
            pass  # No saves directory yet
        
        # Sort by timestamp, newest first
        saves.sort(key=lambda x: x["timestamp"], reverse=True)
        return saves
    
    def delete_save(self, save_name: str) -> bool:
        """Delete a save file"""
        try:
            save_path = os.path.join(self.save_directory, f"{save_name}.json")
            if os.path.exists(save_path):
                os.remove(save_path)
                return True
            return False
        except Exception as e:
            print(f"Error deleting save: {e}")
            return False
    
    def quick_save(self, player, game_state: Dict) -> bool:
        """Create a quick save (overwrites previous quick save)"""
        return self.save_game(player, game_state, "quicksave")
    
    def auto_save(self, player, game_state: Dict) -> bool:
        """Create an auto save"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M")
        return self.save_game(player, game_state, f"autosave_{timestamp}")