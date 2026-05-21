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
        Check collisions between the player and:
        - Ground/platform tiles (stop vertical falling only)
        - Interactive objects (clues, exits, etc.)
        - Collision rectangles defined in TMX (walls/obstacles)
        """
        current_room = self.room_manager.current_room
        if not current_room or not current_room.tmx_data:
            return

        # --- Ground collision (platformer style) ---
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
                            # Only snap if falling onto the tile from above
                            if self.player.vel_y >= 0 and self.player.rect.bottom <= tile_rect.top + 10:
                                self.player.rect.bottom = tile_rect.top
                                self.player.vel_y = 0
                                self.player.on_ground = True
                                break
                else:
                    # No ground collision detected → airborne
                    self.player.on_ground = False

        # --- Collision objects (walls/obstacles) ---
        if hasattr(current_room, "collision_rects"):
            for rect in current_room.collision_rects:
                if self.player.rect.colliderect(rect):
                    # Simple resolution: push player back horizontally
                    if self.player.vel_x > 0:  # moving right
                        self.player.rect.right = rect.left
                    elif self.player.vel_x < 0:  # moving left
                        self.player.rect.left = rect.right

        # --- Interactive objects (clues, exits, etc.) ---
        if hasattr(current_room, "objects"):
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
            self.player.collect_clue(obj)
            current_room = self.room_manager.current_room
            current_room.remove_object(obj)

        elif obj.type == "enemy":
            self.player.take_damage(obj.damage)

        elif obj.type == "exit":
            self.player.move_to_next_room(obj.target_room)

        # Walls are handled separately via collision_rects
