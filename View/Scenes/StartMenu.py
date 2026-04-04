# View/Scenes/StartMenu.py
import pygame

class StartMenu:
    def __init__(self, screen):
        self.screen = screen
        self.font = pygame.font.Font(None, 48)

        # Define buttons
        self.buttons = [
            {"label": "START GAME", "action": "start"},
            {"label": "CONTINUE", "action": "continue"},
            {"label": "OPTIONS", "action": "options"},
            {"label": "CREDITS", "action": "credits"},
            {"label": "EXIT GAME", "action": "exit"},
        ]

        # Button layout
        self.button_rects = []
        self._create_layout()

        # Track keyboard selection
        self.selected_index = None  # None means no keyboard selection

    def _create_layout(self):
        """Create button rectangles centered on screen."""
        screen_width, screen_height = self.screen.get_size()
        spacing = 70
        start_y = screen_height // 3

        for i, button in enumerate(self.buttons):
            rect = self.font.render(button["label"], True, (255, 255, 255)).get_rect(
                center=(screen_width // 2, start_y + i * spacing)
            )
            self.button_rects.append((button["label"], rect, button["action"]))

    def draw(self):
        """Render menu buttons with hover and keyboard highlight."""
        self.screen.fill((0, 0, 0))  # Black background
        mouse_pos = pygame.mouse.get_pos()

        for i, (label, rect, action) in enumerate(self.button_rects):
            # Highlight if hovered OR keyboard-selected
            if rect.collidepoint(mouse_pos):
                text_surface = self.font.render(label, True, (255, 215, 0))  # Gold hover
            elif self.selected_index == i:
                text_surface = self.font.render(label, True, (173, 216, 230))  # Light blue keyboard highlight
            else:
                text_surface = self.font.render(label, True, (255, 255, 255))
            self.screen.blit(text_surface, rect)

    def handle_input(self, event):
        """Check if a button is clicked or selected with keyboard."""
        # Mouse click
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mouse_pos = event.pos
            for i, (label, rect, action) in enumerate(self.button_rects):
                if rect.collidepoint(mouse_pos):
                    self.selected_index = None  # clear keyboard selection
                    return action

        # Keyboard navigation
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_DOWN:
                if self.selected_index is None:
                    self.selected_index = 0
                else:
                    self.selected_index = (self.selected_index + 1) % len(self.button_rects)
            elif event.key == pygame.K_UP:
                if self.selected_index is None:
                    self.selected_index = 0
                else:
                    self.selected_index = (self.selected_index - 1) % len(self.button_rects)
            elif event.key == pygame.K_RETURN and self.selected_index is not None:
                _, _, action = self.button_rects[self.selected_index]
                return action

        return None

    def update(self):
        pass

    def render(self):
        self.draw()
