# Controller/SceneManager.py
import pygame
from View.Scenes.StartMenu import StartMenu
from View.Scenes.ChapterSelect import ChapterSelect
from View.Scenes.Level import Level

class SceneManager:
    def __init__(self, screen):
        self.screen = screen
        self.current_scene = None

    def set_scene(self, scene):
        """Switch to a new scene."""
        self.current_scene = scene

    def handle_input(self, event):
        """Delegate input events to the current scene and handle transitions."""
        if not self.current_scene:
            return None

        result = self.current_scene.handle_input(event)

        # --- Scene transitions ---
        # From StartMenu → ChapterSelect
        if isinstance(self.current_scene, StartMenu):
            if result == "start":
                self.set_scene(ChapterSelect(self.screen))

        # From ChapterSelect → Level or back
        elif isinstance(self.current_scene, ChapterSelect):
            if result == "back":
                self.set_scene(StartMenu(self.screen))
            elif result and "CHAPTER 1: THE BEGINNING - Level 1" in result:
                # Launch Level scene with Chapter 1 Level 1
                self.set_scene(Level(self.screen, chapter_id=1, character="default"))

        return result

    def update(self):
        """Update the current scene logic."""
        if self.current_scene:
            self.current_scene.update()

    def render(self):
        """Render the current scene to the screen."""
        if self.current_scene:
            self.current_scene.render()
        pygame.display.flip()
