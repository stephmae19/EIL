# Game/Game.py
import pygame
from Model.Timer import Timer
from Model.Player import Player
from Model.RoomManager import RoomManager

class Game:
    def __init__(self, chapter_id=1, player=None):
        # Core state
        self.score = 0
        self.timer = Timer()
        self.game_state = "running"  # could be "running", "paused", "won", "lost"

        # RoomManager handles TMX maps and interactive objects
        self.room_manager = RoomManager()
        self.room_manager.load_chapter(chapter_id)

        # Initialize player
        if player:
            self.player = player
        else:
            # Try to spawn player from TMX "spawn" layer
            spawn_x, spawn_y = self._get_spawn_point()
            self.player = Player(
                x=spawn_x,
                y=spawn_y,
                sprite_path="assets/Characters/player.png"
            )

    def _get_spawn_point(self):
        """Look for an object with class 'player' in the TMX spawn layer."""
        if self.room_manager.current_room and self.room_manager.current_room.tmx_data:
            for obj in self.room_manager.current_room.tmx_data.objects:
                if obj.type == "player":  # class field in Tiled
                    return obj.x, obj.y
        # Fallback if no spawn found
        return 100, 100

    def run_loop(self):
        """Update game logic each frame."""
        if self.game_state == "running":
            self.timer.update()
            self.player.update()
            self.room_manager.update(self.player)
            self.check_win_condition()

    def render(self, screen):
        """Draw the game state to the screen."""
        # Render current room (TMX map + interactive objects)
        self.room_manager.render(screen)
        # Render player
        self.player.render(screen)

    def handle_input(self, event):
        """Process player input."""
        if self.game_state == "running":
            self.player.handle_input(event)

        # Example pause toggle
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            self.game_state = "paused" if self.game_state == "running" else "running"

    def check_win_condition(self):
        """Check if the player has met win conditions."""
        # Example: win if score reaches 100
        if self.score >= 100:
            self.game_state = "won"
