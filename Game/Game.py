import pygame
from Model.Timer import Timer
from Model.Player import Player
from Model.RoomManager import RoomManager
from Controller.InputHandler import InputHandler

class Game:
    def __init__(self, chapter_id=1, level_id=1, player=None):
        # Core state
        self.score = 0
        self.timer = Timer()
        self.game_state = "running"  # could be "running", "paused", "won", "lost"

        # RoomManager handles TMX maps and interactive objects
        self.room_manager = RoomManager()
        self.room_manager.load_map(chapter_id, level_id)

        # Initialize player
        if player:
            self.player = player
        else:
            spawn_x, spawn_y = self._get_spawn_point()
            self.player = Player(
                x=spawn_x,
                y=spawn_y,
                sprite_path="Assets/Characters/player.png"
            )

        # Input handler
        self.input_handler = InputHandler(self.player)

    def _get_spawn_point(self):
        """Look for a 'spawn' object in the TMX map."""
        if self.room_manager.current_room and self.room_manager.current_room.tmx_data:
            if hasattr(self.room_manager.current_room, "spawn_point") and self.room_manager.current_room.spawn_point:
                return self.room_manager.current_room.spawn_point
            for obj in self.room_manager.current_room.tmx_data.objects:
                if obj.type == "spawn":
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
        self.room_manager.render(screen)
        self.player.render(screen)

    def handle_input(self, event):
        if self.game_state == "running":
            self.input_handler.process_event(event)

        # Pause toggle
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            self.game_state = "paused" if self.game_state == "running" else "running"

    def check_win_condition(self):
        """Check if the player has met win conditions."""
        if self.score >= 100:
            self.game_state = "won"
