# Model/Whisper.py
import pygame

class Whisper:
    def __init__(self, text, position, trigger_radius=50):
        """
        Represents a mysterious whisper entity in the game.
        :param text: The message or hint the whisper conveys
        :param position: (x, y) tuple for location in the room
        :param trigger_radius: Distance at which player hears the whisper
        """
        self.text = text
        self.position = position
        self.trigger_radius = trigger_radius
        self.active = True

    def check_trigger(self, player_pos):
        """Return True if player is within trigger radius."""
        dx = player_pos[0] - self.position[0]
        dy = player_pos[1] - self.position[1]
        distance = (dx**2 + dy**2) ** 0.5
        return distance <= self.trigger_radius and self.active

    def reveal(self):
        """Activate the whisper and return its text."""
        if self.active:
            self.active = False
            return self.text
        return None

    def draw(self, surface):
        """Optional: draw a subtle visual indicator for debugging."""
        pygame.draw.circle(surface, (100, 100, 255), self.position, 5)
