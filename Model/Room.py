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

        # Interactive elements
        self.entities = []        # Clue, Whisper, Puzzle, etc.
        self.objects = []         # exits, doors, etc.
        self.collision_rects = [] # walls/obstacles parsed from TMX

        if self.tmx_data:
            self.map_surface = pygame.Surface(
                (self.tmx_data.width * self.tmx_data.tilewidth,
                 self.tmx_data.height * self.tmx_data.tileheight)
            )
            self._render_layers()
            self._parse_collision_objects()
        else:
            self.map_surface = None

    # --- Management Methods ---
    def add_entity(self, entity):
        self.entities.append(entity)

    def remove_entity(self, entity):
        if entity in self.entities:
            self.entities.remove(entity)

    def add_object(self, obj):
        self.objects.append(obj)

    def remove_object(self, obj):
        if obj in self.objects:
            self.objects.remove(obj)

    # --- Method Overloading Examples ---
    def describe(self, detail_level=None):
        """Describe the room with optional detail level."""
        if detail_level == "short":
            print(f"You are in {self.name}.")
        elif detail_level == "long":
            print(f"This is {self.name}, containing {len(self.entities)} entities and {len(self.objects)} objects.")
        else:
            print(f"Room: {self.name} (default description).")

    def interact(self, target=None):
        """Interact with the room itself or a specific target."""
        if target:
            print(f"You interact with {target} inside {self.name}.")
        else:
            print(f"You explore the room {self.name}.")

    def move(self, destination=None):
        """Move to another room or just wander inside."""
        if destination:
            print(f"You move from {self.name} to {destination}.")
        else:
            print(f"You wander around inside {self.name}.")

    # --- Internal TMX Rendering ---
    def _render_layers(self):
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

    def _parse_collision_objects(self):
        for obj in self.tmx_data.objects:
            if obj.type == "collision":
                rect = pygame.Rect(obj.x, obj.y, obj.width, obj.height)
                self.collision_rects.append(rect)

    # --- Update Logic ---
    def update(self, player):
        for entity in self.entities:
            entity.update(player)

    # --- Rendering ---
    def render(self, renderer, camera_offset=(0, 0)):
        if self.map_surface:
            renderer.virtual_surface.blit(self.map_surface, (-camera_offset[0], -camera_offset[1]))
        else:
            renderer.virtual_surface.fill(self.color)

        for entity in self.entities:
            entity.draw(renderer.virtual_surface, camera_offset)
