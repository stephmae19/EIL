import os
from pytmx.util_pygame import load_pygame
from Model.Room import Room
from Model.Entity import Clue, Whisper, Puzzle   # imported from Entity.py

class RoomManager:
    # Factory mapping for TMX object types → entity classes
    ENTITY_MAP = {
        "book": lambda obj: Clue(obj.name, (obj.x, obj.y)),
        "manuscript": lambda obj: Clue(f"Manuscript: {obj.name}", (obj.x, obj.y)),
        "puzzle": lambda obj: Puzzle(obj.name, "solution", clues_required=[]),
        "door": lambda obj: Whisper("The door creaks ominously...", (obj.x, obj.y)),
        "light": lambda obj: Whisper("A flickering lamp lights the way...", (obj.x, obj.y)),
        "web": lambda obj: Whisper("Cobwebs cling to the corners...", (obj.x, obj.y)),
        "table": lambda obj: Whisper(f"A sturdy {obj.name} stands here.", (obj.x, obj.y)),
    }

    def __init__(self):
        """
        Manages multiple rooms and transitions between them.
        """
        self.rooms = {}          # Dictionary of room_name -> Room
        self.current_room = None
        self.tmx_data = None     # Store TMX data for later use

    # --- Generic Map Loader ---
    def load_map(self, chapter_id: int, level_id: int):
        """Load a specific map by chapter and level ID."""
        map_file = os.path.join(
            "Assets", "Maps", f"chapter{chapter_id}", f"level{level_id}", f"ch{chapter_id}_lvl{level_id}.tmx"
        )

        if not os.path.exists(map_file):
            print("Map file not found:", map_file)
            return None

        # Load TMX data
        tmx_data = load_pygame(map_file)
        print("Loaded map:", map_file)

        # Create a Room linked to TMX
        room_name = f"Chapter{chapter_id}_Level{level_id}"
        room = Room(room_name, tmx_data)

        # Parse objects from TMX using factory
        for obj in tmx_data.objects:
            if obj.type in RoomManager.ENTITY_MAP:
                entity = RoomManager.ENTITY_MAP[obj.type](obj)
                room.add_entity(entity)
            elif obj.type == "spawn":
                room.spawn_point = (obj.x, obj.y)
            elif obj.type == "collision":
                # Collision rects handled in Room
                rect = (obj.x, obj.y, obj.width, obj.height)
                room.collision_rects.append(rect)

        self.add_room(room)
        self.set_current_room(room_name)
        return room

    def add_room(self, room: Room):
        """Add a room to the manager."""
        self.rooms[room.name] = room
        if self.current_room is None:
            self.current_room = room  # First room added becomes default

    def set_current_room(self, room_name: str):
        """Switch to a specific room by name."""
        if room_name in self.rooms:
            self.current_room = self.rooms[room_name]
            print(f"Entered room: {room_name}")
        else:
            print(f"Room '{room_name}' not found.")

    def next_room(self, room_name: str):
        """Transition to the next room (e.g., when player reaches an exit)."""
        self.set_current_room(room_name)

    def update(self, player):
        """Update the current room state."""
        if self.current_room:
            self.current_room.update(player)

    def render(self, renderer):
        """Render the current room with camera offset."""
        if self.current_room:
            offset = renderer.get_camera_offset()
            self.current_room.render(renderer, offset)

    # --- Chapter Loader ---
    def load_chapter(self, chapter_id: int):
        """Load the first level of a given chapter."""
        self.rooms.clear()
        self.current_room = None
        self.load_map(chapter_id, 1)
