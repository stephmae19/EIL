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

        # Load volume spritesheet (music_volume.png, 3x3 grid)
        spritesheet = pygame.image.load("Assets/Sprite/Music/music_volume.png").convert_alpha()
        frame_width, frame_height = 340, 91
        cols, rows = 3, 3
        self.volume_frames = []
        for row in range(rows):
            for col in range(cols):
                rect = pygame.Rect(col * frame_width, row * frame_height, frame_width, frame_height)
                frame = spritesheet.subsurface(rect)
                self.volume_frames.append(frame)

        # Slider clickable offsets (original frame size)
        self.inner_x_offset = 53
        self.inner_y_offset = 32
        self.slider_width = 265
        self.slider_height = 33
        self.frame_width = frame_width
        self.frame_height = frame_height

        self.volume_level = 4
        self.dragging = False

        # Load SFX toggle spritesheet (sfx.png, 2 frames)
        sfx_sheet = pygame.image.load("Assets/Sprite/Music/sfx.png").convert_alpha()
        self.sfx_frames = [
            sfx_sheet.subsurface(pygame.Rect(0, 0, 150, 100)),   # ON
            sfx_sheet.subsurface(pygame.Rect(150, 0, 150, 100)) # OFF
        ]
        self.sfx_on = True  # start with SFX enabled

        # Back button
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

        # Load custom font
        font_path = os.path.join("assets", "font", "VCR_OSD_MONO_1.001.ttf")
        self.ui_font = pygame.font.Font(font_path, 28)

        self._create_layout()

    def _create_layout(self):
        screen_width, screen_height = self.screen.get_size()
        self.background_scaled = pygame.transform.smoothscale(self.background, (screen_width, screen_height))

        scale_factor = min(screen_width / self.base_width, screen_height / self.base_height)
        new_width = int(min(int(self.base_width * scale_factor), self.base_width) * 0.8)
        new_height = int(min(int(self.base_height * scale_factor), self.base_height) * 0.8)

        self.menu_box = pygame.transform.smoothscale(self.menu_box_original, (new_width, new_height))
        self.menu_box_rect = self.menu_box.get_rect(center=(screen_width // 2, (screen_height // 2) + self.vertical_offset))

        spacing = new_height // (len(self.main_buttons) + 1)
        center_x = self.menu_box_rect.centerx

        self.button_rects.clear()

        if self.current_buttons == self.main_buttons:
            start_y = self.menu_box_rect.top + spacing
            # Layout main buttons
            for i, button in enumerate(self.main_buttons):
                btn_width = int(new_width * 0.6)
                btn_height = int(new_height * 0.1)
                scaled_btn = pygame.transform.smoothscale(button["image"], (btn_width, btn_height))
                rect = scaled_btn.get_rect(center=(center_x, start_y + i * spacing))
                self.button_rects.append((scaled_btn, rect, button["action"]))
        else:
            # Options menu: add 20px padding at the top
            start_y = self.menu_box_rect.top + spacing + 50

            vol_width = int(new_width * 0.6)
            vol_height = int(new_height * 0.15)
            vol_image = pygame.transform.smoothscale(self.volume_frames[self.volume_level], (vol_width, vol_height))
            vol_rect = vol_image.get_rect(center=(center_x, start_y))
            self.button_rects.append((vol_image, vol_rect, "volume"))

            # Save scale factors for slider clickable area
            self.vol_scale_x = vol_width / self.frame_width
            self.vol_scale_y = vol_height / self.frame_height

            # SFX toggle button below volume
            scale_factor = 0.8
            sfx_image = self.sfx_frames[0 if self.sfx_on else 1]
            sfx_scaled = pygame.transform.smoothscale(
                sfx_image, (int(150 * scale_factor), int(100 * scale_factor))
            )
            sfx_rect = sfx_scaled.get_rect(center=(center_x, start_y + spacing * 2))
            self.button_rects.append((sfx_scaled, sfx_rect, "sfx"))

            # Back button below SFX
            back_width = int(new_width * 0.4)
            back_height = int(new_height * 0.1)
            back_scaled = pygame.transform.smoothscale(self.back_btn, (back_width, back_height))
            back_rect = back_scaled.get_rect(center=(center_x, start_y + spacing * 3))
            self.button_rects.append((back_scaled, back_rect, "back"))

            # Store rects for text placement
            self.volume_rect = vol_rect
            self.sfx_rect = sfx_rect


    def draw(self):
        self.screen.blit(self.background_scaled, (0, 0))
        self.screen.blit(self.menu_box, self.menu_box_rect)

        mouse_pos = pygame.mouse.get_pos()
        hovered_index = None

        for i, (image, rect, action) in enumerate(self.button_rects):
            if rect.collidepoint(mouse_pos) or self.selected_index == i:
                hovered_index = i
                if action not in ("volume", "sfx"):  # only non-volume/sfx buttons enlarge
                    scaled = pygame.transform.smoothscale(image, (int(rect.width * 1.1), int(rect.height * 1.1)))
                    scaled_rect = scaled.get_rect(center=rect.center)
                    self.screen.blit(scaled, scaled_rect)
                else:
                    self.screen.blit(image, rect)
            else:
                self.screen.blit(image, rect)

        # Labels above volume and sfx buttons
        if self.current_buttons != self.main_buttons:
            music_text = self.ui_font.render("MUSIC VOLUME", True, (255, 255, 255))
            sfx_text = self.ui_font.render("SOUND EFFECTS", True, (255, 255, 255))

            music_rect = music_text.get_rect(center=(self.volume_rect.centerx, self.volume_rect.top - 25))
            sfx_rect = sfx_text.get_rect(center=(self.sfx_rect.centerx, self.sfx_rect.top - 25))

            self.screen.blit(music_text, music_rect)
            self.screen.blit(sfx_text, sfx_rect)

        # Play hover sound only if SFX is enabled
        if hovered_index is not None and hovered_index != self.last_hovered_index and self.sfx_on:
            self.hover_sound.play()
        self.last_hovered_index = hovered_index

    def handle_input(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            for image, rect, action in self.button_rects:
                if rect.collidepoint(event.pos):
                    if action == "options":
                        self.current_buttons = "options"
                        self._create_layout()
                        return "options"
                    elif action == "back" and self.current_buttons == "options":
                        self.current_buttons = self.main_buttons
                        self._create_layout()
                        return "back"
                    elif action == "volume":
                        # Scale offsets to match scaled image
                        scaled_inner_x = int(self.inner_x_offset * self.vol_scale_x)
                        scaled_inner_y = int(self.inner_y_offset * self.vol_scale_y)
                        scaled_slider_w = int(self.slider_width * self.vol_scale_x)
                        scaled_slider_h = int(self.slider_height * self.vol_scale_y)

                        inner_rect = pygame.Rect(
                            rect.left + scaled_inner_x,
                            rect.top + scaled_inner_y,
                            scaled_slider_w,
                            scaled_slider_h
                        )
                        if inner_rect.collidepoint(event.pos):
                            self.dragging = True
                            self.update_volume(event.pos[0], inner_rect)
                            return "volume"
                    elif action == "sfx":
                        # Toggle SFX on/off
                        self.sfx_on = not self.sfx_on
                        self._create_layout()
                        return "sfx"
                    else:
                        return action

        elif event.type == pygame.MOUSEBUTTONUP:
            self.dragging = False

        elif event.type == pygame.MOUSEMOTION and self.dragging:
            for image, rect, action in self.button_rects:
                if action == "volume":
                    scaled_inner_x = int(self.inner_x_offset * self.vol_scale_x)
                    scaled_inner_y = int(self.inner_y_offset * self.vol_scale_y)
                    scaled_slider_w = int(self.slider_width * self.vol_scale_x)
                    scaled_slider_h = int(self.slider_height * self.vol_scale_y)

                    inner_rect = pygame.Rect(
                        rect.left + scaled_inner_x,
                        rect.top + scaled_inner_y,
                        scaled_slider_w,
                        scaled_slider_h
                    )
                    self.update_volume(event.pos[0], inner_rect)
                    return "volume"

        return None

    def update_volume(self, mouse_x, inner_rect):
        relative_x = mouse_x - inner_rect.left
        relative_x = max(0, min(relative_x, inner_rect.width))
        self.volume_level = round((relative_x / inner_rect.width) * (len(self.volume_frames) - 1))
        self.volume_level = max(0, min(self.volume_level, len(self.volume_frames) - 1))
        # Map frame index to actual audio volume (0.0–1.0)
        volume = self.volume_level / (len(self.volume_frames) - 1)
        pygame.mixer.music.set_volume(volume)
        self._create_layout()

    def update(self):
        self._create_layout()

    def render(self):
        self.draw()

