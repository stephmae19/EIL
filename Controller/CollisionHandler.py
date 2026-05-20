# Controller/CollisionHandler.py
import pygame

class CollisionHandler:
    def __init__(self, player, room_manager):
        """
        Handles collisions between the player and room objects.
        :param player: Player object
        :param room_manager: RoomManager instance (to access current room and TMX data)
        """
        self.player = player
        self.room_manager = room_manager

    def check_collisions(self):
        """
        Check collisions between the player and the ground/platform tiles,
        plus interactive objects in the current room.
        """
        current_room = self.room_manager.current_room
        if not current_room or not current_room.tmx_data:
            return

        # --- Ground collision (platformer style) ---
        # Ensure player stands on top of ground tiles
        for layer in current_room.tmx_data.visible_layers:
            if hasattr(layer, "tiles") and layer.name.lower() == "ground":
                for x, y, tile in layer.tiles():
                    if tile:
                        tile_rect = pygame.Rect(
                            x * current_room.tmx_data.tilewidth,
                            y * current_room.tmx_data.tileheight,
                            current_room.tmx_data.tilewidth,
                            current_room.tmx_data.tileheight
                        )
                        if self.player.rect.colliderect(tile_rect):
                            # Snap player to top of ground tile
                            self.player.rect.bottom = tile_rect.top
                            self.player.on_ground = True
                            break
                else:
                    # If no ground collision detected, player is airborne
                    self.player.on_ground = False

        # --- Interactive objects (clues, enemies, exits, etc.) ---
        for obj in current_room.objects:
            if self._collides(self.player.rect, obj.rect):
                self.handle_collision(obj)

    def _collides(self, rect1, rect2):
        """Return True if two rects overlap."""
        return rect1.colliderect(rect2)

    def handle_collision(self, obj):
        """
        Handle collision with a specific object.
        :param obj: Object collided with
        """
        if obj.type == "clue":
            # Collect clue
            self.player.collect_clue(obj)
            current_room = self.room_manager.current_room
            current_room.remove_object(obj)

        elif obj.type == "enemy":
            # Reduce player health
            self.player.take_damage(obj.damage)

        elif obj.type == "exit":
            # Trigger room transition
            self.player.move_to_next_room(obj.target_room)

        # Walls are treated as background only → no blocking
