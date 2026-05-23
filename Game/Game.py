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

        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            self.game_state = "paused" if self.game_state == "running" else "running"

    def check_win_condition(self):
        """Default win condition: score reaches 100."""
        if self.score >= 100:
            self.game_state = "won"


# --- Method Overriding Examples ---
class PuzzleGame(Game):
    """PuzzleGame overrides win condition to check if all puzzles are solved."""
    def check_win_condition(self):
        if all(entity.solved for entity in self.room_manager.current_room.entities if hasattr(entity, "solved")):
            print("All puzzles solved! You win!")
            self.game_state = "won"


class TimedGame(Game):
    """TimedGame overrides run_loop to enforce a countdown timer."""
    def run_loop(self):
        if self.game_state == "running":
            self.timer.update()
            self.player.update()
            self.room_manager.update(self.player)

            if self.timer.remaining_time <= 0:
                print("Time's up! You lost.")
                self.game_state = "lost"
            else:
                self.check_win_condition()


class ExplorationGame(Game):
    """ExplorationGame overrides render to show exploration-specific HUD."""
    def render(self, screen):
        super().render(screen)
        # Add exploration HUD overlay
        font = pygame.font.SysFont("Arial", 24)
        text = font.render(f"Exploring: {self.room_manager.current_room.name}", True, (255, 255, 255))
        screen.blit(text, (20, 20))
