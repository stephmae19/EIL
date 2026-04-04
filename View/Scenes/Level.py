# View/Scenes/Level.py
import pygame
from Game.Game import Game

class Level:
    def __init__(self, screen, chapter_id=1):
        self.screen = screen
        self.game = Game(chapter_id)  # initialize game state for chosen chapter
        self.font = pygame.font.Font(None, 36)

    def handle_input(self, event):
        """Delegate input to the game logic."""
        self.game.handle_input(event)

    def update(self):
        """Run the game loop logic."""
        self.game.run_loop()

    def render(self):
        """Render the game state."""
        self.screen.fill((30, 30, 30))  # dark background
        self.game.render(self.screen)

        # Example overlay: score and timer
        score_text = self.font.render(f"Score: {self.game.score}", True, (255, 255, 255))
        timer_text = self.font.render(f"Time: {self.game.timer.get_time()}", True, (255, 255, 255))
        self.screen.blit(score_text, (20, 20))
        self.screen.blit(timer_text, (20, 60))
