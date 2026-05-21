# Controller/InputHandler.py
import pygame

class InputHandler:
    def __init__(self, player=None):
        self.player = player

    def process_event(self, event):
        """Forward input events directly to the Player class."""
        if self.player:
            self.player.handle_input(event)
