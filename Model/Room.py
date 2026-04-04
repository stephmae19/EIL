# Model/Room.py
import pygame
from Model.Whisper import Whisper
from Model.Clue import Clue
from Model.Puzzle import Puzzle

class Room:
    def __init__(self, name="Room", width=800, height=600, color=(100, 100, 150)):
        self.name = name
        self.color = color
        self.rect = pygame.Rect(0, 0, width, height)

        # Interactive elements
        self.whispers = []
        self.clues = []
        self.puzzles = []
        self.objects = []  # walls, exits, enemies, etc.

    # --- Management Methods ---
    def add_whisper(self, whisper: Whisper):
        self.whispers.append(whisper)

    def add_clue(self, clue: Clue):
        self.clues.append(clue)

    def add_puzzle(self, puzzle: Puzzle):
        self.puzzles.append(puzzle)

    def remove_object(self, obj):
        if obj in self.objects:
            self.objects.remove(obj)

    # --- Update Logic ---
    def update(self, player):
        """
        Update room state each frame.
        - Check whispers
        - Check clue collection
        - Check puzzle attempts
        """
        # Trigger whispers
        for whisper in self.whispers:
            if whisper.check_trigger(player.position):
                text = whisper.reveal()
                if text:
                    print(f"Whisper: {text}")

        # Collect clues
        for clue in self.clues:
            if not clue.collected and player.rect.colliderect(clue.rect):
                clue.collect(player)
                print(f"Collected clue: {clue.description}")

        # Check puzzles (optional: triggered by player interaction)
        for puzzle in self.puzzles:
            if puzzle.is_solved():
                continue
            # Example: auto-check if player has all clues
            if puzzle.clues_required and all(c in player.inventory for c in puzzle.clues_required):
                print(f"Puzzle ready: {puzzle.question}")

    # --- Rendering ---
    def render(self, screen):
        """Draw the room background and interactive elements."""
        screen.fill(self.color)

        # Draw clues
        for clue in self.clues:
            clue.draw(screen)

        # Draw whispers (optional visual indicator)
        for whisper in self.whispers:
            whisper.draw(screen)

        # Puzzles are usually abstract, but you could draw markers
        for puzzle in self.puzzles:
            if not puzzle.is_solved():
                # Placeholder: draw a puzzle marker
                pygame.draw.circle(screen, (255, 255, 0), (100, 100), 10)
