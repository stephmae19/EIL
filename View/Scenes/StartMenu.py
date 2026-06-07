# View/Scenes/StartMenu.py
import pygame
import os
from View.Scenes.Credits import run_credits
from View.UI import VolumeSlider  # ✅ Imported our newly migrated widget

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

        # Volume spritesheet layout initialization
        spritesheet = pygame.image.load("Assets/Sprite/Music/music_volume.png").convert_alpha()
        frame_width, frame_height = 340, 91
        volume_frames = [
            spritesheet.subsurface(pygame.Rect(col * frame_width, row * frame_height, frame_width, frame_height))
            for row in range(3) for col in range(3)
        ]

        # ✅ Instantiate the migrated UI object instead of hardcoding variables local to the scene
        self.slider_ui = VolumeSlider(volume_frames)

        # SFX toggle spritesheet (2 frames)
        sfx_sheet = pygame.image.load("Assets/Sprite/Music/sfx.png").convert_alpha()
        self.sfx_frames = [
            sfx_sheet.subsurface(pygame.Rect(0, 0, 150, 100)),   # ON
            sfx_sheet.subsurface(pygame.Rect(150, 0, 150, 100)) # OFF
        ]
        self.sfx_on = True

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

        # Custom font
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
            for i, button in enumerate(self.main_buttons):
                btn_width = int(new_width * 0.6)
                btn_height = int(new_height * 0.1)
                scaled_btn = pygame.transform.smoothscale(button["image"], (btn_width, btn_height))
                rect = scaled_btn.get_rect(center=(center_x, start_y + i * spacing))
                self.button_rects.append((scaled_btn, rect, button["action"]))
        else:
            start_y = self.menu_box_rect.top + spacing + 50

            vol_width = int(new_width * 0.6)
            vol_height = int(new_height * 0.15)
            # ✅ Reference UI helper volume level
            vol_image = pygame.transform.smoothscale(self.slider_ui.frames[self.slider_ui.volume_level], (vol_width, vol_height))
            vol_rect = vol_image.get_rect(center=(center_x, start_y))
            self.button_rects.append((vol_image, vol_rect, "volume"))

            self.vol_scale_x = vol_width / self.slider_ui.frame_width
            self.vol_scale_y = vol_height / self.slider_ui.frame_height

            sfx_image = self.sfx_frames[0 if self.sfx_on else 1]
            sfx_scaled = pygame.transform.smoothscale(sfx_image, (int(150 * 0.8), int(100 * 0.8)))
            sfx_rect = sfx_scaled.get_rect(center=(center_x, start_y + spacing * 2))
            self.button_rects.append((sfx_scaled, sfx_rect, "sfx"))

            back_scaled = pygame.transform.smoothscale(self.back_btn, (int(new_width * 0.4), int(new_height * 0.1)))
            back_rect = back_scaled.get_rect(center=(center_x, start_y + spacing * 3))
            self.button_rects.append((back_scaled, back_rect, "back"))

            self.volume_rect = vol_rect
            self.sfx_rect = sfx_rect

    def draw(self):
        mouse_pos = getattr(self, "last_mouse_pos", None)
        if mouse_pos is None:
            return

        self.screen.blit(self.background_scaled, (0, 0))
        self.screen.blit(self.menu_box, self.menu_box_rect)

        hovered_index = None
        for i, (image, rect, action) in enumerate(self.button_rects):
            if rect.collidepoint(mouse_pos) or self.selected_index == i:
                hovered_index = i
                if action not in ("volume", "sfx"):
                    scaled = pygame.transform.smoothscale(image, (int(rect.width * 1.1), int(rect.height * 1.1)))
                    scaled_rect = scaled.get_rect(center=rect.center)
                    self.screen.blit(scaled, scaled_rect)
                else:
                    self.screen.blit(image, rect)
            else:
                self.screen.blit(image, rect)

        if hovered_index is not None and hovered_index != self.last_hovered_index and self.sfx_on:
            self.hover_sound.play()
        self.last_hovered_index = hovered_index

        if self.current_buttons != self.main_buttons:
            music_text = self.ui_font.render("MUSIC VOLUME", True, (255, 255, 255))
            sfx_text = self.ui_font.render("SOUND EFFECTS", True, (255, 255, 255))
            self.screen.blit(music_text, music_text.get_rect(center=(self.volume_rect.centerx, self.volume_rect.top - 25)))
            self.screen.blit(sfx_text, sfx_text.get_rect(center=(self.sfx_rect.centerx, self.sfx_rect.top - 25)))

    def handle_input(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            for _, rect, action in self.button_rects:
                if rect.collidepoint(event.pos):
                    if action == "options":
                        self.current_buttons = "options"
                        self._create_layout()
                        return "options"
                    elif action == "back" and self.current_buttons == "options":
                        self.current_buttons = self.main_buttons
                        self._create_layout()
                        return "back"
                    elif action == "credits":
                        run_credits()
                        return "credits"
                    elif action == "volume":
                        # ✅ Check interactive boundary layout safely using the UI component tracking properties
                        inner_rect = pygame.Rect(
                            rect.left + int(self.slider_ui.inner_x_offset * self.vol_scale_x),
                            rect.top + int(self.slider_ui.inner_y_offset * self.vol_scale_y),
                            int(self.slider_ui.slider_width * self.vol_scale_x),
                            int(self.slider_ui.slider_height * self.vol_scale_y)
                        )
                        if inner_rect.collidepoint(event.pos):
                            self.slider_ui.dragging = True
                            self.slider_ui.update_volume(event.pos[0], rect, self.vol_scale_x, self.vol_scale_y)
                            self._create_layout()
                            return "volume"
                    elif action == "sfx":
                        self.sfx_on = not self.sfx_on
                        self._create_layout()
                        return "sfx"
                    else:
                        return action

        elif event.type == pygame.MOUSEBUTTONUP:
            self.slider_ui.dragging = False

        elif event.type == pygame.MOUSEMOTION and self.slider_ui.dragging:
            for _, rect, action in self.button_rects:
                if action == "volume":
                    # ✅ Route audio update calls tracking through migrated component
                    self.slider_ui.update_volume(event.pos[0], rect, self.vol_scale_x, self.vol_scale_y)
                    self._create_layout()
                    return "volume"

        return None

    def update(self):
        self._create_layout()

    def render(self):
        self.draw()