# Model/Room.py
import pygame

class Room:
    def __init__(self, name="Room", tmx_data=None, color=(100, 100, 150)):
        """
        Room can be initialized with TMX map data (from pytmx).
        """
        self.name = name
        self.color = color
        self.tmx_data = tmx_data

        # Interactive elements
        self.whispers = []
        self.clues = []
        self.puzzles = []
        self.objects = []  # walls, exits, enemies, etc.

        # Pre-render map layers if TMX provided
        if self.tmx_data:
            self.map_surface = pygame.Surface(
                (self.tmx_data.width * self.tmx_data.tilewidth,
                 self.tmx_data.height * self.tmx_data.tileheight)
            )
            self._render_layers()
        else:
            self.map_surface = None

    # --- Management Methods ---
    def add_whisper(self, whisper):
        self.whispers.append(whisper)

    def add_clue(self, clue):
        self.clues.append(clue)

    def add_puzzle(self, puzzle):
        self.puzzles.append(puzzle)

    def remove_object(self, obj):
        if obj in self.objects:
            self.objects.remove(obj)

    # --- Internal TMX Rendering ---
    def _render_layers(self):
        """Draw TMX layers in correct order: ground → wall → objects."""
        self.map_surface.fill(self.color)

        # Render each layer by name
        for layer in self.tmx_data.visible_layers:
            if hasattr(layer, "tiles"):
                # Draw tiles layer
                for x, y, tile in layer.tiles():
                    if tile:
                        self.map_surface.blit(
                            tile,
                            (x * self.tmx_data.tilewidth, y * self.tmx_data.tileheight)
                        )
            elif hasattr(layer, "name"):
                # You can add special handling per layer name if needed
                if layer.name.lower() == "objects":
                    # Objects layer can be drawn separately or skipped if handled via tmx_data.objects
                    pass

    # --- Update Logic ---
    def update(self, player):
        """Update room state each frame."""
        for whisper in self.whispers:
            if whisper.check_trigger(player.position):
                text = whisper.reveal()
                if text:
                    print(f"Whisper: {text}")

        for clue in self.clues:
            if not clue.collected and player.rect.colliderect(clue.rect):
                clue.collect(player)
                print(f"Collected clue: {clue.description}")

        for puzzle in self.puzzles:
            if puzzle.is_solved():
                continue
            if puzzle.clues_required and all(c in player.inventory for c in puzzle.clues_required):
                print(f"Puzzle ready: {puzzle.question}")

    # --- Rendering ---
    def render(self, screen):
        """Draw the TMX map layers and interactive elements."""
        if self.map_surface:
            screen.blit(self.map_surface, (0, 0))
        else:
            screen.fill(self.color)

        # Draw clues
        for clue in self.clues:
            clue.draw(screen)

        # Draw whispers (optional visual indicator)
        for whisper in self.whispers:
            whisper.draw(screen)

        # Draw puzzle markers (optional)
        for puzzle in self.puzzles:
            if not puzzle.is_solved():
                pygame.draw.circle(screen, (255, 255, 0), (100, 100), 10)
