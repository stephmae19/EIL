# Model/Room.py
import pygame

class Room:
    def __init__(self, name="Room"):
        self.name = name
        self.color = (100, 100, 150)  # Default background color
        self.rect = pygame.Rect(0, 0, 800, 600)  # Full screen room area

    def update(self):
        """Update room state each frame (placeholder)."""
        pass

    def render(self, screen):
        """Draw the room background."""
        screen.fill(self.color)
