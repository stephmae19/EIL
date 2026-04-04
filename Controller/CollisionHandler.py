# Controller/CollisionHandler.py
import pygame

class CollisionHandler:
    def __init__(self, player, rooms):
        """
        Handles collisions between the player and room objects.
        :param player: Player object
        :param rooms: List of Room objects
        """
        self.player = player
        self.rooms = rooms

    def check_collisions(self):
        """
        Check collisions between the player and all objects in the current room.
        """
        current_room = self.player.current_room
        if not current_room:
            return

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
        if obj.type == "wall":
            # Prevent player from moving through walls
            self.player.stop_movement()
        elif obj.type == "clue":
            # Collect clue
            self.player.collect_clue(obj)
            current_room = self.player.current_room
            current_room.remove_object(obj)
        elif obj.type == "enemy":
            # Reduce player health
            self.player.take_damage(obj.damage)
        elif obj.type == "exit":
            # Trigger room transition
            self.player.move_to_next_room(obj.target_room)
