"""
Audio Manager for Corporate Crusader
Handles sound effects and background music
"""
import pygame
import os
import random
from typing import Dict, Optional

class AudioManager:
    def __init__(self):
        # Initialize pygame mixer
        try:
            pygame.mixer.init(frequency=22050, size=-16, channels=2, buffer=512)
            self.audio_enabled = True
        except pygame.error:
            print("Warning: Could not initialize audio")
            self.audio_enabled = False
            return
        
        # Audio settings
        self.master_volume = 0.7
        self.sfx_volume = 0.8
        self.music_volume = 0.6
        
        # Audio caches
        self.sounds: Dict[str, pygame.mixer.Sound] = {}
        self.current_music = None
        
        # Load corporate-themed sound effects (generated programmatically)
        self._create_corporate_sounds()
    
    def _create_corporate_sounds(self):
        """Create simple sound effects programmatically"""
        if not self.audio_enabled:
            return
        
        try:
            # Create simple sound effects using sine waves
            sample_rate = 22050
            
            # Coffee slurp sound (low frequency gurgle)
            coffee_duration = 0.3
            coffee_samples = int(sample_rate * coffee_duration)
            coffee_wave = []
            for i in range(coffee_samples):
                t = float(i) / sample_rate
                # Mix of frequencies for gurgle effect
                wave = (
                    0.3 * math.sin(2 * math.pi * 80 * t) +
                    0.2 * math.sin(2 * math.pi * 120 * t) +
                    0.1 * math.sin(2 * math.pi * 200 * t)
                ) * (1 - t / coffee_duration)  # Fade out
                coffee_wave.append([int(wave * 32767), int(wave * 32767)])
            
            if coffee_wave:
                self.sounds['coffee'] = pygame.sndarray.make_sound(coffee_wave)
            
            # Keyboard typing sound (high frequency clicks)
            typing_duration = 0.1
            typing_samples = int(sample_rate * typing_duration)
            typing_wave = []
            for i in range(typing_samples):
                t = float(i) / sample_rate
                if i % 100 < 50:  # Square wave for click effect
                    wave = 0.2
                else:
                    wave = -0.2
                wave *= (1 - t / typing_duration)  # Fade out
                typing_wave.append([int(wave * 32767), int(wave * 32767)])
            
            if typing_wave:
                self.sounds['typing'] = pygame.sndarray.make_sound(typing_wave)
            
            # Success sound (ascending notes)
            success_duration = 0.5
            success_samples = int(sample_rate * success_duration)
            success_wave = []
            for i in range(success_samples):
                t = float(i) / sample_rate
                # Ascending frequency
                freq = 440 + (t / success_duration) * 220
                wave = 0.3 * math.sin(2 * math.pi * freq * t)
                wave *= (1 - t / success_duration)  # Fade out
                success_wave.append([int(wave * 32767), int(wave * 32767)])
            
            if success_wave:
                self.sounds['success'] = pygame.sndarray.make_sound(success_wave)
            
            # Error sound (harsh buzz)
            error_duration = 0.2
            error_samples = int(sample_rate * error_duration)
            error_wave = []
            for i in range(error_samples):
                t = float(i) / sample_rate
                # Harsh buzz with distortion
                wave = 0.4 * math.sin(2 * math.pi * 150 * t)
                if wave > 0.2:
                    wave = 0.2
                elif wave < -0.2:
                    wave = -0.2
                error_wave.append([int(wave * 32767), int(wave * 32767)])
            
            if error_wave:
                self.sounds['error'] = pygame.sndarray.make_sound(error_wave)
        
        except ImportError:
            # numpy/sndarray not available, create silent sounds
            print("Note: Audio effects disabled (numpy not available)")
            for sound_name in ['coffee', 'typing', 'success', 'error']:
                self.sounds[sound_name] = None
    
    def play_sound(self, sound_name: str, volume: float = 1.0):
        """Play a sound effect"""
        if not self.audio_enabled:
            return
        
        if sound_name in self.sounds and self.sounds[sound_name]:
            try:
                sound = self.sounds[sound_name]
                sound.set_volume(volume * self.sfx_volume * self.master_volume)
                sound.play()
            except pygame.error:
                pass  # Sound failed to play
    
    def play_corporate_sound(self, action: str):
        """Play appropriate sound for corporate actions"""
        sound_mapping = {
            'coffee_break': 'coffee',
            'attack': 'typing',
            'level_up': 'success',
            'damage': 'error',
            'ability_use': 'typing',
            'item_use': 'coffee',
            'victory': 'success',
            'defeat': 'error'
        }
        
        if action in sound_mapping:
            self.play_sound(sound_mapping[action])
    
    def set_master_volume(self, volume: float):
        """Set master volume (0.0 to 1.0)"""
        self.master_volume = max(0.0, min(1.0, volume))
    
    def set_sfx_volume(self, volume: float):
        """Set sound effects volume (0.0 to 1.0)"""
        self.sfx_volume = max(0.0, min(1.0, volume))
    
    def set_music_volume(self, volume: float):
        """Set music volume (0.0 to 1.0)"""
        self.music_volume = max(0.0, min(1.0, volume))
        if pygame.mixer.music.get_busy():
            pygame.mixer.music.set_volume(self.music_volume * self.master_volume)
    
    def play_ambient_music(self):
        """Play ambient office music (if available)"""
        if not self.audio_enabled:
            return
        
        # This would load actual music files if available
        # For now, we'll create a simple tone
        try:
            # Create a simple ambient tone
            self._create_ambient_music()
        except:
            pass  # No music available
    
    def _create_ambient_music(self):
        """Create simple ambient background tones"""
        # This would create or load ambient office sounds
        # Like air conditioning, distant typing, etc.
        pass
    
    def stop_music(self):
        """Stop background music"""
        if self.audio_enabled:
            pygame.mixer.music.stop()
    
    def cleanup(self):
        """Clean up audio resources"""
        if self.audio_enabled:
            pygame.mixer.quit()

# Import math for sound generation
try:
    import math
except ImportError:
    # Fallback if math is not available
    class MockMath:
        @staticmethod
        def sin(x):
            return 0
        
        @staticmethod
        def pi():
            return 3.14159
        
        pi = 3.14159
    
    math = MockMath()