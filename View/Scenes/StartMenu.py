import pygame
import os

class StartMenu:
    def __init__(self, screen):
        self.screen = screen

        # Base design dimensions
        self.base_width = 509
        self.base_height = 622
        self.vertical_offset = 30

        # Load background and menu box
        self.background = pygame.image.load("Assets/Scenery/start_bg.png").convert()
        self.menu_box_original = pygame.image.load("Assets/Menu Options/menu_box.jpeg").convert_alpha()

        # Load main menu buttons
        self.main_buttons = [
            {"image": pygame.image.load("Assets/Menu Options/start_btn.jpeg").convert_alpha(), "action": "start"},
            {"image": pygame.image.load("Assets/Menu Options/continue_btn.jpeg").convert_alpha(), "action": "continue"},
            {"image": pygame.image.load("Assets/Menu Options/options_btn.jpeg").convert_alpha(), "action": "options"},
            {"image": pygame.image.load("Assets/Menu Options/credits_btn.jpeg").convert_alpha(), "action": "credits"},
            {"image": pygame.image.load("Assets/Menu Options/exit_btn.jpeg").convert_alpha(), "action": "exit"},
        ]

        # Load volume sprites safely (music_1.png … music_8.png)
        self.volume_images = []
        for i in range(1, 9):  # include 1 through 8
            path = f"Assets/Sprite/Music/music_{i}.png"
            if os.path.exists(path):
                self.volume_images.append(pygame.image.load(path).convert_alpha())
            else:
                print(f"Warning: {path} not found, skipping.")

        self.volume_level = 4  # start mid-level (1–8)

        # Back button for options menu
        self.back_btn = pygame.image.load("Assets/Menu Options/back_btn.png").convert_alpha()

        # Current button set
        self.current_buttons = self.main_buttons
        self.button_rects = []
        self.menu_box = None
        self.menu_box_rect = None
        self.selected_index = None

        # Hover sound
        self.hover_sound = pygame.mixer.Sound("sounds/button_hover.mp3")
        self.last_hovered_index = None

        self._create_layout()

    def _create_layout(self):
        screen_width, screen_height = self.screen.get_size()
        self.background_scaled = pygame.transform.smoothscale(self.background, (screen_width, screen_height))

        scale_factor = min(screen_width / self.base_width, screen_height / self.base_height)
        new_width = int(min(int(self.base_width * scale_factor), self.base_width) * 0.8)
        new_height = int(min(int(self.base_height * scale_factor), self.base_height) * 0.8)

        self.menu_box = pygame.transform.smoothscale(self.menu_box_original, (new_width, new_height))
        self.menu_box_rect = self.menu_box.get_rect(center=(screen_width // 2, (screen_height // 2) + self.vertical_offset))

        spacing = new_height // (len(self.current_buttons) + 1)
        center_x = self.menu_box_rect.centerx
        start_y = self.menu_box_rect.top + spacing

        self.button_rects.clear()

        if self.current_buttons == self.main_buttons:
            # Layout main buttons
            for i, button in enumerate(self.current_buttons):
                btn_width = int(new_width * 0.6)
                btn_height = int(new_height * 0.1)
                scaled_btn = pygame.transform.smoothscale(button["image"], (btn_width, btn_height))
                rect = scaled_btn.get_rect(center=(center_x, start_y + i * spacing))
                self.button_rects.append((scaled_btn, rect, button["action"]))
        else:
            # Layout options menu: volume + back
            vol_width = int(new_width * 0.6)
            vol_height = int(new_height * 0.15)
            vol_image = pygame.transform.smoothscale(self.volume_images[self.volume_level - 1], (vol_width, vol_height))
            vol_rect = vol_image.get_rect(center=(center_x, start_y))
            self.button_rects.append((vol_image, vol_rect, "volume"))

            back_width = int(new_width * 0.4)
            back_height = int(new_height * 0.1)
            back_scaled = pygame.transform.smoothscale(self.back_btn, (back_width, back_height))
            back_rect = back_scaled.get_rect(center=(center_x, start_y + spacing * 2))
            self.button_rects.append((back_scaled, back_rect, "back"))

    def draw(self):
        self.screen.blit(self.background_scaled, (0, 0))
        self.screen.blit(self.menu_box, self.menu_box_rect)

        mouse_pos = pygame.mouse.get_pos()
        hovered_index = None

        for i, (image, rect, action) in enumerate(self.button_rects):
            if rect.collidepoint(mouse_pos) or self.selected_index == i:
                hovered_index = i
                scaled = pygame.transform.smoothscale(image, (int(rect.width * 1.1), int(rect.height * 1.1)))
                scaled_rect = scaled.get_rect(center=rect.center)
                self.screen.blit(scaled, scaled_rect)
            else:
                self.screen.blit(image, rect)

        if hovered_index is not None and hovered_index != self.last_hovered_index:
            self.hover_sound.play()
        self.last_hovered_index = hovered_index

    def handle_input(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            for _, rect, action in self.button_rects:
                if rect.collidepoint(event.pos):
                    if action == "options":
                        # Switch to options menu
                        self.current_buttons = "options"
                        self._create_layout()
                        return "options"
                    elif action == "back" and self.current_buttons == "options":
                        # Return to main menu
                        self.current_buttons = self.main_buttons
                        self._create_layout()
                        return "back"
                    elif action == "volume":
                        # Adjust volume based on click position
                        if event.pos[0] > rect.centerx and self.volume_level < len(self.volume_images):
                            self.volume_level += 1
                        elif event.pos[0] < rect.centerx and self.volume_level > 1:
                            self.volume_level -= 1
                        pygame.mixer.music.set_volume(self.volume_level / len(self.volume_images))
                        self._create_layout()
                        return "volume"
                    else:
                        return action

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_DOWN:
                self.selected_index = 0 if self.selected_index is None else (self.selected_index + 1) % len(self.button_rects)
            elif event.key == pygame.K_UP:
                self.selected_index = 0 if self.selected_index is None else (self.selected_index - 1) % len(self.button_rects)
            elif event.key == pygame.K_RETURN and self.selected_index is not None:
                _, _, action = self.button_rects[self.selected_index]
                return action

        return None

    def update(self):
        self._create_layout()

    def render(self):
        self.draw()
