# Model/Player.py
import pygame

class Player:
    def __init__(self, start_room=None):
        # Position and movement
        self.x = 100
        self.y = 100
        self.speed = 5

        # Visual representation
        self.color = (0, 200, 0)  # Green
        self.size = 40

        # Room reference
        self.current_room = start_room

        # Stats
        self.health = 100
        self.inventory = []

    def handle_input(self, event):
        """Process keyboard input for movement."""
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_LEFT:
                self.x -= self.speed
            elif event.key == pygame.K_RIGHT:
                self.x += self.speed
            elif event.key == pygame.K_UP:
                self.y -= self.speed
            elif event.key == pygame.K_DOWN:
                self.y += self.speed

    def update(self):
        """Update player state each frame."""
        # Clamp position to screen bounds (example: 800x600 window)
        self.x = max(0, min(self.x, 800 - self.size))
        self.y = max(0, min(self.y, 600 - self.size))

    def render(self, screen):
        """Draw the player as a rectangle."""
        pygame.draw.rect(screen, self.color, (self.x, self.y, self.size, self.size))

    def add_item(self, item):
        """Add an item to inventory."""
        self.inventory.append(item)

    def remove_item(self, item):
        """Remove an item from inventory if present."""
        if item in self.inventory:
            self.inventory.remove(item)
