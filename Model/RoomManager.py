# Model/RoomManager.py
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
            # Example Chapter 1: Library Mystery
            library = Room("Library")
            hallway = Room("Hallway")
            secret_chamber = Room("Secret Chamber")

            # Add interactive elements
            library.add_whisper(Whisper("The shelves hide secrets...", (300, 200)))
            clue = Clue("A torn page with strange symbols", (400, 250))
            library.add_clue(clue)
            library.add_puzzle(Puzzle("What word unlocks the door?", "knowledge", clues_required=[clue]))

            # Register rooms
            self.add_room(library)
            self.add_room(hallway)
            self.add_room(secret_chamber)

            self.set_current_room("Library")

        elif chapter_id == 2:
            # Example Chapter 2: Haunted Garden
            garden = Room("Garden")
            fountain = Room("Fountain")
            crypt = Room("Crypt")

            garden.add_whisper(Whisper("The roses whisper of sorrow...", (500, 300)))
            clue = Clue("Rusty key with strange markings", (600, 350))
            garden.add_clue(clue)
            garden.add_puzzle(Puzzle("Which flower blooms at midnight?", "rose", clues_required=[clue]))

            self.add_room(garden)
            self.add_room(fountain)
            self.add_room(crypt)

            self.set_current_room("Garden")

        else:
            print(f"Chapter {chapter_id} not defined.")
