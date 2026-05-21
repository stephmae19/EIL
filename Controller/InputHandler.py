# Controller/InputHandler.py
import pygame

class InputHandler:
    def __init__(self, player=None):
        self.player = player

    def process_event(self, event):
        if self.player:
            if event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_a, pygame.K_LEFT):
                    self.player.move_left()
                elif event.key in (pygame.K_d, pygame.K_RIGHT):
                    self.player.move_right()
            elif event.type == pygame.KEYUP:
                if event.key in (pygame.K_a, pygame.K_LEFT, pygame.K_d, pygame.K_RIGHT):
                    self.player.stop_movement()

    def _handle_keyup(self, key):
        """Stop movement when keys are released."""
        if key in (pygame.K_w, pygame.K_UP, pygame.K_s, pygame.K_DOWN,
                   pygame.K_a, pygame.K_LEFT, pygame.K_d, pygame.K_RIGHT):
            self.player.stop_movement()
        return None
