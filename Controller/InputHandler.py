# Controller/InputHandler.py
import pygame

class InputHandler:
    def __init__(self, player=None, ui_elements=None):
        """
        Handles raw input events for both gameplay and UI.
        :param player: Player object (optional, for gameplay scenes)
        :param ui_elements: List of UI elements (e.g., buttons) for menus
        """
        self.player = player
        self.ui_elements = ui_elements if ui_elements else []

    def process_event(self, event):
        """
        Process a single pygame event.
        """
        # Handle UI clicks first
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            for element in self.ui_elements:
                if hasattr(element, "is_clicked") and element.is_clicked(event):
                    return element.text  # Return the button label as action

        # Handle gameplay input if player exists
        if self.player:
            if event.type == pygame.KEYDOWN:
                return self._handle_keydown(event.key)
            elif event.type == pygame.KEYUP:
                return self._handle_keyup(event.key)

        return None

    def _handle_keydown(self, key):
        """Handle key press events for gameplay."""
        if key in (pygame.K_w, pygame.K_UP):
            self.player.move_up()
        elif key in (pygame.K_s, pygame.K_DOWN):
            self.player.move_down()
        elif key in (pygame.K_a, pygame.K_LEFT):
            self.player.move_left()
        elif key in (pygame.K_d, pygame.K_RIGHT):
            self.player.move_right()
        elif key == pygame.K_SPACE:
            self.player.attack()
        elif key == pygame.K_e:
            self.player.interact()
        elif key == pygame.K_ESCAPE:
            return "pause"  # Example: trigger pause menu
        return None

    def _handle_keyup(self, key):
        """Stop movement when keys are released."""
        if key in (pygame.K_w, pygame.K_UP, pygame.K_s, pygame.K_DOWN,
                   pygame.K_a, pygame.K_LEFT, pygame.K_d, pygame.K_RIGHT):
            self.player.stop_movement()
        return None
