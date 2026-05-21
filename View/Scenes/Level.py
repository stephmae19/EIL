# View/Scenes/Level.py
import pygame
from Game.Game import Game
from Model.Player import Player
from Model.RoomManager import RoomManager
from View.Renderer import Renderer

class Level:
    def __init__(self, screen, chapter_id, character):
        self.screen = screen
        self.chapter_id = chapter_id
        self.character = character

        # Create player
        self.player = Player(x=100, y=100, sprite_path="Assets/Characters/player_walk.jpeg")

        # RoomManager handles TMX maps and interactive objects
        self.room_manager = RoomManager()
        self.room_manager.load_chapter(chapter_id)

        # Game orchestrator: connects player + rooms
        self.game = Game(chapter_id=chapter_id, player=self.player)

        # Renderer with fixed viewport (35 tiles wide × 20 tiles tall)
        self.renderer = Renderer(screen, tile_width=32, tile_height=32,
                                 view_tiles_w=35, view_tiles_h=20)

    def handle_input(self, event):
        """Pass input to game logic."""
        self.game.handle_input(event)

    def update(self):
        """Update game state each frame."""
        self.game.run_loop()
        self.room_manager.update(self.player)

        # Update camera to follow player
        if self.room_manager.current_room and self.room_manager.current_room.tmx_data:
            map_width = self.room_manager.current_room.tmx_data.width * self.room_manager.current_room.tmx_data.tilewidth
            map_height = self.room_manager.current_room.tmx_data.height * self.room_manager.current_room.tmx_data.tileheight
            self.renderer.set_camera(self.player.rect, map_width, map_height)

    def render(self):
        """Draw everything: map + player + UI."""
        self.renderer.clear()

        # Draw current room (delegates to Room.render)
        self.room_manager.render(self.screen)

        # Draw player
        if self.player.sprite:
            self.renderer.draw_sprite(self.player.sprite, self.player.rect)
        else:
            self.renderer.draw_rect(self.player.color, self.player.rect)

        # Optional: draw UI (health, inventory, etc.)
        self.renderer.draw_text(f"Health: {self.player.health}", (20, 20), size=24, color=(255, 0, 0))

        # Scale and update display
        self.renderer.update_display()
