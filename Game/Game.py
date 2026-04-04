# Game/Game.py
import pygame
from Model.Timer import Timer
from Model.Player import Player
from Model.Room import Room

class Game:
    def __init__(self, chapter_id=1):
        # Core state
        self.score = 0
        self.timer = Timer()
        self.game_state = "running"  # could be "running", "paused", "won", "lost"

        # Initialize rooms and player
        self.rooms = self._load_rooms(chapter_id)
        self.player = Player(start_room=self.rooms[0])

    def _load_rooms(self, chapter_id):
        """Load rooms for the given chapter. Placeholder for now."""
        # In a real game, you’d load chapter-specific room data here
        return [Room("Room 1"), Room("Room 2")]

    def run_loop(self):
        """Update game logic each frame."""
        if self.game_state == "running":
            self.timer.update()
            self.player.update()
            self.check_win_condition()

    def render(self, screen):
        """Draw the game state to the screen."""
        # Example: fill background
        screen.fill((50, 50, 80))

        # Render rooms and player
        for room in self.rooms:
            room.render(screen)
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
        # Placeholder: win if score reaches 100
        if self.score >= 100:
            self.game_state = "won"
