# View/Scenes/StartMenu.py
import pygame

class StartMenu:
    def __init__(self, screen):
        self.screen = screen

        # Base design dimensions for menu box
        self.base_width = 509
        self.base_height = 622
        self.vertical_offset = 30  # Lower menu box by 30px

        # Load background and menu box
        self.background = pygame.image.load("assets/scenery/start_bg.png").convert()
        self.menu_box_original = pygame.image.load("assets/menu options/menu_box.jpeg").convert_alpha()

        # Load button images with associated actions
        self.buttons = [
            {"image": pygame.image.load("assets/menu options/start_btn.jpeg").convert_alpha(), "action": "start"},
            {"image": pygame.image.load("assets/menu options/continue_btn.jpeg").convert_alpha(), "action": "continue"},
            {"image": pygame.image.load("assets/menu options/options_btn.jpeg").convert_alpha(), "action": "options"},
            {"image": pygame.image.load("assets/menu options/credits_btn.jpeg").convert_alpha(), "action": "credits"},
            {"image": pygame.image.load("assets/menu options/exit_btn.jpeg").convert_alpha(), "action": "exit"},
        ]

        # Layout state
        self.menu_box = None
        self.menu_box_rect = None
        self.button_rects = []
        self.selected_index = None

        self._create_layout()

    def _create_layout(self):
        """Scale menu box and buttons based on window size."""
        screen_width, screen_height = self.screen.get_size()

        # Fit background to screen
        self.background_scaled = pygame.transform.smoothscale(self.background, (screen_width, screen_height))

        # Scale factor relative to window
        scale_factor = min(screen_width / self.base_width, screen_height / self.base_height)

        # Apply scale, cap at original size, then shrink by 20%
        new_width = int(min(int(self.base_width * scale_factor), self.base_width) * 0.8)
        new_height = int(min(int(self.base_height * scale_factor), self.base_height) * 0.8)

        # Scale menu box and apply vertical offset
        self.menu_box = pygame.transform.smoothscale(self.menu_box_original, (new_width, new_height))
        self.menu_box_rect = self.menu_box.get_rect(
            center=(screen_width // 2, (screen_height // 2) + self.vertical_offset)
        )

        # Position buttons inside menu box
        spacing = new_height // (len(self.buttons) + 1)
        center_x = self.menu_box_rect.centerx
        start_y = self.menu_box_rect.top + spacing

        self.button_rects.clear()
        for i, button in enumerate(self.buttons):
            btn_width = int(new_width * 0.6)
            btn_height = int(new_height * 0.1)
            scaled_btn = pygame.transform.smoothscale(button["image"], (btn_width, btn_height))
            rect = scaled_btn.get_rect(center=(center_x, start_y + i * spacing))
            self.button_rects.append((scaled_btn, rect, button["action"]))

    def draw(self):
        """Render background, menu box, and buttons."""
        self.screen.blit(self.background_scaled, (0, 0))
        self.screen.blit(self.menu_box, self.menu_box_rect)

        mouse_pos = pygame.mouse.get_pos()
        for i, (image, rect, action) in enumerate(self.button_rects):
            if rect.collidepoint(mouse_pos) or self.selected_index == i:
                # Slightly enlarge on hover/selection
                scaled = pygame.transform.smoothscale(image, (int(rect.width * 1.1), int(rect.height * 1.1)))
                scaled_rect = scaled.get_rect(center=rect.center)
                self.screen.blit(scaled, scaled_rect)
            else:
                self.screen.blit(image, rect)

    def handle_input(self, event):
        """Handle mouse clicks and keyboard navigation."""
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            for _, rect, action in self.button_rects:
                if rect.collidepoint(event.pos):
                    self.selected_index = None
                    return action

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_DOWN:
                self.selected_index = 0 if self.selected_index is None else (self.selected_index + 1) % len(self.button_rects)
            elif event.key == pygame.K_UP:
                self.selected_index = 0 if self.    selected_index is None else (self.selected_index - 1) % len(self.button_rects)
            elif event.key == pygame.K_RETURN and self.selected_index is not None:
                _, _, action = self.button_rects[self.selected_index]
                return action

        return None

    def update(self):
        """Recalculate layout if window size changes."""
        self._create_layout()

    def render(self):
        """Draw everything to the screen."""
        self.draw()
