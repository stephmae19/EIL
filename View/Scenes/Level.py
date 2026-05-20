# View/Scenes/Level.py
import pygame
from Game.Game import Game
from Model.Player import Player
from Model.Room import Room
from Model.Clue import Clue   # example interactive object

class Level:
    def __init__(self, screen, chapter_id, character):
        self.screen = screen
        self.chapter_id = chapter_id
        self.character = character

        # Create player
        self.player = Player(x=100, y=100, sprite_path="assets/Characters/player.png")

        # Create a room (environment)
        self.room = Room("Chapter Room", background="assets/Maps/chapter_bg.png")

        # Add an interactive object (example: chest)
        chest = Clue(x=300, y=200, sprite_path="assets/Objects-Items/chest.png", description="A mysterious chest")
        self.room.add_object(chest)

        # Game orchestrator
        self.game = Game(player=self.player, rooms=[self.room])

    def handle_input(self, event):
        """Pass input to game logic."""
        self.game.handle_input(event)

    def update(self):
        """Update game state each frame."""
        self.game.run_loop()

    def render(self):
        """Draw everything."""
        self.game.render(self.screen)
