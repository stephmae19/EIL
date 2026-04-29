# View/Scenes/CharacterSelection.py
import pygame
import os

class CharacterSelection:
    def __init__(self, screen):
        self.screen = screen
        font_path = os.path.join("assets", "font", "VCR_OSD_MONO_1.001.ttf")
        self.font = pygame.font.Font(font_path, 48)

        # Load background
        self.background = pygame.image.load("assets/scenery/plain_bg.png").convert()
        self.background_scaled = None

        # Define available characters
        self.characters = [
            {"label": "WARRIOR", "id": "warrior"},
            {"label": "MAGE", "id": "mage"},
            {"label": "ROGUE", "id": "rogue"},
            {"label": "BACK TO MENU", "id": "menu"},
        ]

        # Button layout
        self.character_rects = []
        self._create_layout()

        # Track keyboard selection
        self.selected_index = None

    def _create_layout(self):
        """Create character option rectangles centered on screen."""
        screen_width, screen_height = self.screen.get_size()

        # Scale background to fit screen
        self.background_scaled = pygame.transform.smoothscale(self.background, (screen_width, screen_height))

        spacing = 70
        start_y = screen_height // 3

        self.character_rects.clear()
        for i, character in enumerate(self.characters):
            rect = self.font.render(character["label"], True, (255, 255, 255)).get_rect(
                center=(screen_width // 2, start_y + i * spacing)
            )
            self.character_rects.append((character["label"], rect, character["id"]))

    def draw(self):
        """Render background and character options with hover and keyboard highlight."""
        # Draw background
        self.screen.blit(self.background_scaled, (0, 0))

        mouse_pos = pygame.mouse.get_pos()

        for i, (label, rect, char_id) in enumerate(self.character_rects):
            if rect.collidepoint(mouse_pos):
                text_surface = self.font.render(label, True, (255, 215, 0))  # Gold hover
            elif self.selected_index == i:
                text_surface = self.font.render(label, True, (173, 216, 230))  # Light blue keyboard highlight
            else:
                text_surface = self.font.render(label, True, (255, 255, 255))
            self.screen.blit(text_surface, rect)

    def handle_input(self, event):
        """Check if a character is clicked or selected with keyboard."""
        # Mouse click
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mouse_pos = event.pos
            for i, (label, rect, char_id) in enumerate(self.character_rects):
                if rect.collidepoint(mouse_pos):
                    self.selected_index = None
                    return char_id

        # Keyboard navigation
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_DOWN:
                if self.selected_index is None:
                    self.selected_index = 0
                else:
                    self.selected_index = (self.selected_index + 1) % len(self.character_rects)
            elif event.key == pygame.K_UP:
                if self.selected_index is None:
                    self.selected_index = 0
                else:
                    self.selected_index = (self.selected_index - 1) % len(self.character_rects)
            elif event.key == pygame.K_RETURN and self.selected_index is not None:
                _, _, char_id = self.character_rects[self.selected_index]
                return char_id

        return None

    def update(self):
        # Recalculate layout if window size changes
        self._create_layout()

    def render(self):
        self.draw()
