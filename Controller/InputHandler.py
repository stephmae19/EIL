# Controller/InputHandler.py

import pygame

class InputHandler:
    def __init__(self, player=None):
        self.player = player

    # --- Method Overloading Example ---
    def process_event(self, event, context=None):
        """
        Handle input events differently depending on arguments.
        - event only → normal gameplay input
        - event + "menu" → menu navigation
        - event + "puzzle" → puzzle interaction
        """
        if self.player:
            if context == "menu":
                self._handle_menu_event(event)
            elif context == "puzzle":
                self._handle_puzzle_event(event)
            else:
                # Default: forward to player
                self.player.handle_input(event)

    def _handle_menu_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                print("Menu: Move selection up")
            elif event.key == pygame.K_DOWN:
                print("Menu: Move selection down")
            elif event.key == pygame.K_RETURN:
                print("Menu: Confirm selection")

    def _handle_puzzle_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                print("Puzzle: Attempt solution")
            elif event.key == pygame.K_h:
                print("Puzzle: Request hint")
