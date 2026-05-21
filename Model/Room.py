# Model/Room.py
import pygame

class Room:
    def __init__(self, name="Room", tmx_data=None, color=(100, 100, 150)):
        """
        Room initialized with TMX map data (from pytmx).
        """
        self.name = name
        self.color = color
        self.tmx_data = tmx_data

        # Interactive elements (all share update/draw polymorphism)
        self.entities = []   # Clue, Whisper, Puzzle, etc.
        self.objects = []    # walls, exits, enemies

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
    def add_entity(self, entity):
        """Add any interactive entity (Clue, Whisper, Puzzle)."""
        self.entities.append(entity)

    def remove_entity(self, entity):
        if entity in self.entities:
            self.entities.remove(entity)

    def add_object(self, obj):
        self.objects.append(obj)

    def remove_object(self, obj):
        if obj in self.objects:
            self.objects.remove(obj)

    # --- Internal TMX Rendering ---
    def _render_layers(self):
        """Pre-render TMX layers once: ground → walls → objects."""
        self.map_surface.fill(self.color)

        for layer in self.tmx_data.visible_layers:
            if hasattr(layer, "tiles"):
                for x, y, gid in layer:
                    tile = self.tmx_data.get_tile_image_by_gid(gid)
                    if tile:
                        self.map_surface.blit(
                            tile,
                            (x * self.tmx_data.tilewidth, y * self.tmx_data.tileheight)
                        )
        # Object layers handled separately via self.tmx_data.objects

    # --- Update Logic ---
    def update(self, player):
        """Update all entities in the room."""
        for entity in self.entities:
            entity.update(player)   # polymorphic call

    # --- Rendering ---
    def render(self, renderer, camera_offset=(0, 0)):
        """Draw the TMX map and all entities with camera offset."""
        if self.map_surface:
            renderer.virtual_surface.blit(self.map_surface, (-camera_offset[0], -camera_offset[1]))
        else:
            renderer.virtual_surface.fill(self.color)

        # Draw all entities polymorphically
        for entity in self.entities:
            entity.draw(renderer.virtual_surface, camera_offset)
