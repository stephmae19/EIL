# Model/RoomManager.py
import os
from pytmx.util_pygame import load_pygame
from Model.Room import Room
from Model.Whisper import Whisper
from Model.Clue import Clue
from Model.Puzzle import Puzzle

class RoomManager:
    def __init__(self):
        """
        Manages multiple rooms and transitions between them.
        """
        self.rooms = {}          # Dictionary of room_name -> Room
        self.current_room = None
        self.tmx_data = None     # Store TMX data for later use

        self.setup()

    def setup(self):
        """
        Initial setup: load the default map if available.
        """
        map_file = os.path.join("Assets", "MAPS", "chapter 1", "level 1", "ch1_lvl1.tmx")

        if not os.path.exists(map_file):
            print("Map file not found:", map_file)
            return

        # Load TMX data
        self.tmx_data = load_pygame(map_file)
        print("Loaded map:", self.tmx_data)

        # Create a Room linked to TMX
        level1 = Room("Chapter1_Level1", self.tmx_data)

        # Parse objects from TMX
        for obj in self.tmx_data.objects:
            obj_pos = (obj.x, obj.y)
            if obj.type == "book":
                level1.add_clue(Clue(obj.name, obj_pos))
            elif obj.type == "puzzle":
                level1.add_puzzle(Puzzle(obj.name, "solution", clues_required=[]))
            elif obj.type == "door":
                level1.add_whisper(Whisper("The door creaks ominously...", obj_pos))
            elif obj.type == "light":
                level1.add_whisper(Whisper("A flickering lamp lights the way...", obj_pos))
            elif obj.type == "manuscript":
                level1.add_clue(Clue(f"Manuscript: {obj.name}", obj_pos))
            elif obj.type == "web":
                level1.add_whisper(Whisper("Cobwebs cling to the corners...", obj_pos))
            elif obj.type == "table":
                level1.add_whisper(Whisper(f"A sturdy {obj.name} stands here.", obj_pos))
            # Extend with other object types as needed

        self.add_room(level1)
        self.set_current_room("Chapter1_Level1")

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

    def render(self, screen):
        """Render the current room."""
        if self.current_room:
            self.current_room.render(screen)

    # --- Chapter Loader ---
    def load_chapter(self, chapter_id: int):
        """
        Build and load a sequence of rooms for a given chapter.
        :param chapter_id: Numeric ID of the chapter
        """
        self.rooms.clear()
        self.current_room = None

        if chapter_id == 1:
            map_file = os.path.join("Assets", "MAPS", "chapter 1", "level 1", "ch1_lvl1.tmx")
            if not os.path.exists(map_file):
                print("Chapter 1 map not found:", map_file)
                return

            tmx_data = load_pygame(map_file)
            level1 = Room("Chapter1_Level1", tmx_data)

            for obj in tmx_data.objects:
                obj_pos = (obj.x, obj.y)
                if obj.type == "book":
                    level1.add_clue(Clue(obj.name, obj_pos))
                elif obj.type == "puzzle":
                    level1.add_puzzle(Puzzle(obj.name, "solution", clues_required=[]))
                elif obj.type == "door":
                    level1.add_whisper(Whisper("The door creaks ominously...", obj_pos))
                elif obj.type == "light":
                    level1.add_whisper(Whisper("A flickering lamp lights the way...", obj_pos))
                elif obj.type == "manuscript":
                    level1.add_clue(Clue(f"Manuscript: {obj.name}", obj_pos))
                elif obj.type == "web":
                    level1.add_whisper(Whisper("Cobwebs cling to the corners...", obj_pos))
                elif obj.type == "table":
                    level1.add_whisper(Whisper(f"A sturdy {obj.name} stands here.", obj_pos))

            self.add_room(level1)
            self.set_current_room("Chapter1_Level1")

        elif chapter_id == 2:
            map_file = os.path.join("Assets", "MAPS", "chapter 2", "level 1", "ch2_lvl1.tmx")
            if os.path.exists(map_file):
                tmx_data = load_pygame(map_file)
                level2 = Room("Chapter2_Level1", tmx_data)
                self.add_room(level2)
                self.set_current_room("Chapter2_Level1")
            else:
                print("Chapter 2 map not found.")

        else:
            print(f"Chapter {chapter_id} not defined.")
