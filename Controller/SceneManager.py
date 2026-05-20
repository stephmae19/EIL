# Controller/SceneManager.py
import pygame

class SceneManager:
    def __init__(self, screen):
        self.screen = screen
        self.current_scene = None

    def set_scene(self, scene):
        """Switch to a new scene."""
        self.current_scene = scene

    def handle_input(self, event):
        """Delegate input events to the current scene and return any action."""
        if self.current_scene:
            return self.current_scene.handle_input(event)
        return None

    def update(self):
        """Update the current scene logic."""
        if self.current_scene:
            self.current_scene.update()

    def render(self):
        """Render the current scene to the screen."""
        if self.current_scene:
            self.current_scene.render()
        pygame.display.flip()
