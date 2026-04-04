# View/Scenes/PauseMenu.py
import pygame

class PauseMenu:
    def __init__(self, screen):
        self.screen = screen
        self.font = pygame.font.Font(None, 48)

        # Define pause menu options
        self.options = [
            {"label": "RESUME", "action": "resume"},
            {"label": "OPTIONS", "action": "options"},
            {"label": "QUIT TO MENU", "action": "menu"},
            {"label": "EXIT GAME", "action": "exit"},
        ]

        # Button layout
        self.option_rects = []
        self._create_layout()

        # Track keyboard selection
        self.selected_index = None

    def _create_layout(self):
        """Create option rectangles centered on screen."""
        screen_width, screen_height = self.screen.get_size()
        spacing = 70
        start_y = screen_height // 3

        for i, option in enumerate(self.options):
            rect = self.font.render(option["label"], True, (255, 255, 255)).get_rect(
                center=(screen_width // 2, start_y + i * spacing)
            )
            self.option_rects.append((option["label"], rect, option["action"]))

    def draw(self):
        """Render pause menu options with hover and keyboard highlight."""
        self.screen.fill((40, 40, 40))  # Dark gray background
        mouse_pos = pygame.mouse.get_pos()

        for i, (label, rect, action) in enumerate(self.option_rects):
            if rect.collidepoint(mouse_pos):
                text_surface = self.font.render(label, True, (255, 215, 0))  # Gold hover
            elif self.selected_index == i:
                text_surface = self.font.render(label, True, (173, 216, 230))  # Light blue keyboard highlight
            else:
                text_surface = self.font.render(label, True, (255, 255, 255))
            self.screen.blit(text_surface, rect)

    def handle_input(self, event):
        """Check if an option is clicked or selected with keyboard."""
        # Mouse click
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mouse_pos = event.pos
            for i, (label, rect, action) in enumerate(self.option_rects):
                if rect.collidepoint(mouse_pos):
                    self.selected_index = None
                    return action

        # Keyboard navigation
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_DOWN:
                if self.selected_index is None:
                    self.selected_index = 0
                else:
                    self.selected_index = (self.selected_index + 1) % len(self.option_rects)
            elif event.key == pygame.K_UP:
                if self.selected_index is None:
                    self.selected_index = 0
                else:
                    self.selected_index = (self.selected_index - 1) % len(self.option_rects)
            elif event.key == pygame.K_RETURN and self.selected_index is not None:
                _, _, action = self.option_rects[self.selected_index]
                return action

        return None

    def update(self):
        pass

    def render(self):
        self.draw()
