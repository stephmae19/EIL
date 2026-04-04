# Model/Clue.py
import pygame

class Clue:
    def __init__(self, description, position, collected=False):
        """
        Represents a collectible clue in the game.
        :param description: Text describing the clue
        :param position: (x, y) tuple for location in the room
        :param collected: Whether the clue has been collected
        """
        self.description = description
        self.position = position
        self.collected = collected
        self.rect = pygame.Rect(position[0], position[1], 32, 32)  # default size

    def collect(self, player):
        """Mark clue as collected and add to player inventory."""
        if not self.collected:
            self.collected = True
            player.inventory.append(self)

    def draw(self, surface):
        """Draw clue if not collected."""
        if not self.collected:
            pygame.draw.rect(surface, (0, 255, 0), self.rect)
