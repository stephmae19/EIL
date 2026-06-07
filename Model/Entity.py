# Model/Entity.py

import pygame
import os

class Entity:
    """Base class for all interactive entities in a room."""
    def update(self, player):
        raise NotImplementedError("Subclasses must implement update()")

    def draw(self, surface, camera_offset):
        raise NotImplementedError("Subclasses must implement draw()")


class Clue(Entity):
    def __init__(self, description, position, size=(32, 32)):
        self.description = description
        self.rect = pygame.Rect(position[0], position[1], *size)
        self.collected = False
        self.color = (0, 0, 255)

    def update(self, player):
        if not self.collected and player.rect.colliderect(self.rect):
            self.collected = True
            player.add_item(self.description)
            print(f"Collected clue: {self.description}")

    def draw(self, surface, camera_offset):
        if not self.collected:
            pygame.draw.rect(surface, self.color,
                             self.rect.move(-camera_offset[0], -camera_offset[1]))


class Whisper(Entity):
    def __init__(self, text, position, radius=10):
        self.text = text
        self.rect = pygame.Rect(position[0], position[1], 32, 32)
        self.radius = radius
        self.triggered = False
        self.color = (200, 200, 200)

    def update(self, player):
        if player.rect.colliderect(self.rect) and not self.triggered:
            print(f"Whisper: {self.text}")
            self.triggered = True

    def draw(self, surface, camera_offset):
        pygame.draw.circle(surface, self.color,
                           (self.rect.x - camera_offset[0], self.rect.y - camera_offset[1]),
                           self.radius)


class Puzzle(Entity):
    def __init__(self, question, solution, clues_required=None):
        self.question = question
        self.solution = solution
        self.clues_required = clues_required or []
        self.solved = False
        self.color = (255, 255, 0)

    def update(self, player):
        if not self.solved and all(c in player.inventory for c in self.clues_required):
            print(f"Puzzle ready: {self.question}")

    def draw(self, surface, camera_offset):
        if not self.solved:
            pygame.draw.circle(surface, self.color,
                               (100 - camera_offset[0], 100 - camera_offset[1]), 10)


class Projectile(Entity):
    """Borrowed from general.py: glowing blue blast."""
    def __init__(self, x, y, facing_right):
        self.image = pygame.Surface((35, 12), pygame.SRCALPHA)
        self.image.fill((100, 200, 255, 200))  # glowing blue
        self.rect = self.image.get_rect(center=(x, y))
        self.speed = 12
        self.facing_right = facing_right

    def update(self, player=None):
        if self.facing_right:
            self.rect.x += self.speed
        else:
            self.rect.x -= self.speed

    def draw(self, surface, camera_offset):
        surface.blit(self.image, self.rect.move(-camera_offset[0], -camera_offset[1]))
