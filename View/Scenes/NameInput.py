# View/Scenes/NameInput

import pygame
import sys
import os
from View.Scenes.ChapterSelect import ChapterSelect

# --- Config ---
NAMEBOX_FILE = "Assets/SCENERY/name_box.png"

class NameInput:
    def __init__(self, screen, scene_manager, chosen_character):
        self.screen = screen
        self.scene_manager = scene_manager
        self.chosen_character = chosen_character
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont("arial", 32, bold=True)

        # Load name box UI
        if os.path.exists(NAMEBOX_FILE):
            self.name_box = pygame.image.load(NAMEBOX_FILE).convert_alpha()
        else:
            print("⚠️ name_box.png not found at:", os.path.abspath(NAMEBOX_FILE))
            self.name_box = pygame.Surface((400, 100), pygame.SRCALPHA)
            self.name_box.fill((50, 50, 50, 200))

        # Center the name box
        self.box_rect = self.name_box.get_rect(center=(screen.get_width() // 2,
                                                       screen.get_height() // 2))

        self.input_text = ""

    def handle_input(self, event):
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN:
                player_name = self.input_text.strip() if self.input_text.strip() else "Player"
                self.scene_manager.set_scene(
                    ChapterSelect(self.screen, self.chosen_character, player_name)
                )
                return "confirm"
            elif event.key == pygame.K_BACKSPACE:
                self.input_text = self.input_text[:-1]
            else:
                if len(self.input_text) < 12:
                    self.input_text += event.unicode
        return None

    def update(self):
        pass

    def render(self):
        self.screen.fill((0, 0, 0))  # black background
        self.screen.blit(self.name_box, self.box_rect)

        # Render typed text INSIDE the box
        text_surface = self.font.render(self.input_text, True, (255, 255, 255))
        text_rect = text_surface.get_rect(center=self.box_rect.center)
        self.screen.blit(text_surface, text_rect)

        pygame.display.flip()
        self.clock.tick(60)
