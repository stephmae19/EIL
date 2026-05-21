import pygame

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

    def update(self, player):
        if not self.collected and player.rect.colliderect(self.rect):
            self.collected = True
            player.add_item(self.description)
            print(f"Collected clue: {self.description}")

    def draw(self, surface, camera_offset):
        if not self.collected:
            pygame.draw.rect(surface, (0, 0, 255),
                             self.rect.move(-camera_offset[0], -camera_offset[1]))


class Whisper(Entity):
    def __init__(self, text, position, radius=10):
        self.text = text
        self.rect = pygame.Rect(position[0], position[1], 32, 32)
        self.radius = radius
        self.triggered = False

    def update(self, player):
        if player.rect.colliderect(self.rect) and not self.triggered:
            print(f"Whisper: {self.text}")
            self.triggered = True

    def draw(self, surface, camera_offset):
        pygame.draw.circle(surface, (200, 200, 200),
                           (self.rect.x - camera_offset[0], self.rect.y - camera_offset[1]),
                           self.radius)


class Puzzle(Entity):
    def __init__(self, question, solution, clues_required=None):
        self.question = question
        self.solution = solution
        self.clues_required = clues_required or []
        self.solved = False

    def update(self, player):
        if not self.solved and all(c in player.inventory for c in self.clues_required):
            print(f"Puzzle ready: {self.question}")

    def draw(self, surface, camera_offset):
        if not self.solved:
            pygame.draw.circle(surface, (255, 255, 0),
                               (100 - camera_offset[0], 100 - camera_offset[1]), 10)
