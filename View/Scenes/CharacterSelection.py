# View/Scenes/CharacterSelection.py
import pygame
import os
from View.Scenes.StartMenu import StartMenu
from View.Scenes.ChapterSelect import ChapterSelect

class CharacterSelection:
    def __init__(self, screen, scene_manager=None):
        self.screen = screen
        self.scene_manager = scene_manager
        font_path = os.path.join("assets", "font", "VCR_OSD_MONO_1.001.ttf")
        self.font = pygame.font.Font(font_path, 48)

        # Load full background
        self.background = pygame.image.load("assets/scenery/plain_bg.png").convert()
        self.background_scaled = None

        # Load centered window
        self.window_image = pygame.image.load("assets/scenery/chapter_select_window.png").convert_alpha()
        self.window_scaled = None
        self.window_rect = None

        # Load buttons
        self.back_btn_original = pygame.image.load("assets/menu options/back_btn.png").convert_alpha()
        self.confirm_btn_original = pygame.image.load("assets/menu options/confirm_btn.png").convert_alpha()
        self.back_btn = None
        self.confirm_btn = None
        self.back_btn_rect = None
        self.confirm_btn_rect = None

        # Load character images
        self.girl_image = pygame.image.load("assets/characters/girl_char.png").convert_alpha()
        self.boy_image = pygame.image.load("assets/characters/boy_char.png").convert_alpha()

        # Define available characters
        self.characters = [
            {"label": "GIRL", "id": "girl"},
            {"label": "BOY", "id": "boy"},
        ]

        self.selected_index = None
        self.chosen_character = None

        self._create_layout()

    def _create_layout(self):
        screen_width, screen_height = self.screen.get_size()
        self.background_scaled = pygame.transform.smoothscale(self.background, (screen_width, screen_height))

        # Square window
        square_size = int(min(screen_width, screen_height) * 0.6)
        self.window_scaled = pygame.transform.smoothscale(self.window_image, (square_size, square_size))
        self.window_rect = self.window_scaled.get_rect(center=(screen_width // 2, screen_height // 2))

        # Scale buttons
        btn_width = square_size // 3
        btn_height = int(btn_width * 0.4)
        self.back_btn = pygame.transform.smoothscale(self.back_btn_original, (btn_width, btn_height))
        self.confirm_btn = pygame.transform.smoothscale(self.confirm_btn_original, (btn_width, btn_height))

        button_y = self.window_rect.bottom - btn_height - 20
        spacing_x = 100
        self.back_btn_rect = self.back_btn.get_rect(center=(self.window_rect.centerx - spacing_x, button_y))
        self.confirm_btn_rect = self.confirm_btn.get_rect(center=(self.window_rect.centerx + spacing_x, button_y))

        # Character boxes inside window
        box_size = square_size // 3
        box_y = self.window_rect.top + 150
        self.girl_box = pygame.Rect(self.window_rect.centerx - box_size - 50, box_y, box_size, box_size)
        self.boy_box = pygame.Rect(self.window_rect.centerx + 50, box_y, box_size, box_size)

        # Scale character images to fit boxes
        self.girl_image_scaled = pygame.transform.smoothscale(self.girl_image, (box_size - 20, box_size - 20))
        self.boy_image_scaled = pygame.transform.smoothscale(self.boy_image, (box_size - 20, box_size - 20))

    def draw(self):
        self.screen.blit(self.background_scaled, (0, 0))
        self.screen.blit(self.window_scaled, self.window_rect)

        mouse_pos = pygame.mouse.get_pos()

        # Header text
        header_surface = self.font.render("SELECT YOUR EXPLORER", True, (255, 255, 255))
        header_rect = header_surface.get_rect(center=(self.window_rect.centerx, self.window_rect.top + 60))
        self.screen.blit(header_surface, header_rect)

        # Draw character boxes
        for box, image in [(self.girl_box, self.girl_image_scaled), (self.boy_box, self.boy_image_scaled)]:
            pygame.draw.rect(self.screen, (25, 16, 21), box)  # fill color #191015
            pygame.draw.rect(self.screen, (0, 0, 0), box, 2)  # thin black border
            img_rect = image.get_rect(center=box.center)
            self.screen.blit(image, img_rect)

        # Back button
        if self.back_btn_rect.collidepoint(mouse_pos):
            back_hover = pygame.transform.smoothscale(self.back_btn_original,
                                                      (self.back_btn_rect.width + 20, self.back_btn_rect.height + 10))
            back_rect = back_hover.get_rect(center=self.back_btn_rect.center)
            self.screen.blit(back_hover, back_rect)
        else:
            self.screen.blit(self.back_btn, self.back_btn_rect)

        # Confirm button
        if self.confirm_btn_rect.collidepoint(mouse_pos):
            confirm_hover = pygame.transform.smoothscale(self.confirm_btn_original,
                                                         (self.confirm_btn_rect.width + 20, self.confirm_btn_rect.height + 10))
            confirm_rect = confirm_hover.get_rect(center=self.confirm_btn_rect.center)
            self.screen.blit(confirm_hover, confirm_rect)
        else:
            self.screen.blit(self.confirm_btn, self.confirm_btn_rect)

    def handle_input(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mouse_pos = event.pos
            # Character box clicks
            if self.girl_box.collidepoint(mouse_pos):
                self.chosen_character = "girl"
                return "girl"
            if self.boy_box.collidepoint(mouse_pos):
                self.chosen_character = "boy"
                return "boy"
            # Back button
            if self.back_btn_rect.collidepoint(mouse_pos):
                if self.scene_manager:
                    self.scene_manager.set_scene(StartMenu(self.screen))
                return "back"
            # Confirm button
            if self.confirm_btn_rect.collidepoint(mouse_pos):
                if self.chosen_character and self.scene_manager:
                    self.scene_manager.set_scene(ChapterSelect(self.screen))
                return "confirm"

        return None

    def update(self):
        self._create_layout()

    def render(self):
        self.draw()
