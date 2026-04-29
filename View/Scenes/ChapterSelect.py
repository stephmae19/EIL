# View/Scenes/ChapterSelect.py
import pygame
import os

class ChapterSelect:
    def __init__(self, screen):
        self.screen = screen

        # Load fonts
        font_path = os.path.join("assets", "font", "VCR_OSD_MONO_1.001.ttf")
        self.font = pygame.font.Font(font_path, 28)
        self.header_font = pygame.font.Font(font_path, 40)
        self.mini_header_font = pygame.font.Font(font_path, 24)

        # Load menu box background
        self.menu_box_original = pygame.image.load("assets/scenery/plain_box.jpeg").convert_alpha()

        # Load buttons
        self.back_btn_original = pygame.image.load("assets/menu options/back_btn.png").convert_alpha()
        self.continue_btn_original = pygame.image.load("assets/menu options/confirm_btn.png").convert_alpha()

        # Define chapters and levels
        self.chapters = {
            "CHAPTER 1: THE BEGINNING": ["Level 1", "Level 2", "Level 3"],
            "CHAPTER 2: THE WHISPERS": ["Level 1", "Level 2"],
            "CHAPTER 3: THE PUZZLES": ["Level 1", "Level 2", "Level 3", "Level 4"],
            "CHAPTER 4: THE REVELATION": ["Level 1", "Level 2"],
            "BACK TO MENU": []
        }

        # Layout state
        self.menu_box = None
        self.menu_box_rect = None
        self.chapter_header = []
        self.chapter_rows = []
        self.level_rects = []
        self.header_rect = None
        self.back_btn = None
        self.continue_btn = None
        self.back_btn_rect = None
        self.continue_btn_rect = None
        self.selected_chapter = None
        self.selected_index = None

        self._create_layout()

    def _create_layout(self):
        screen_width, screen_height = self.screen.get_size()

        # Scale menu box
        box_width = int(screen_width * 0.8)
        box_height = int(screen_height * 0.7)
        self.menu_box = pygame.transform.smoothscale(self.menu_box_original, (box_width, box_height))
        self.menu_box_rect = self.menu_box.get_rect(center=(screen_width // 2, screen_height // 2))

        # Margins
        margin_x, margin_y = 40, 40
        inner_left = self.menu_box_rect.left + margin_x
        inner_right = self.menu_box_rect.right - margin_x
        inner_top = self.menu_box_rect.top + margin_y
        inner_bottom = self.menu_box_rect.bottom - margin_y

        # Header
        header_surface = self.header_font.render("CHAPTERS & LEVELS", True, (255, 255, 255))
        self.header_rect = header_surface.get_rect(midtop=(self.menu_box_rect.centerx, inner_top))
        self.header_surface = header_surface

        # Chapter/Level layout
        left_x = inner_left
        right_x = self.menu_box_rect.centerx + 30
        start_y = self.header_rect.bottom + 20
        spacing = 50

        # Mini header for chapters side (2 columns: NAME wider, STATUS smaller)
        name_width = int((right_x - left_x) * 0.7)
        self.chapter_header = [
            ("CHAPTER NAME", self.mini_header_font.render("CHAPTER NAME", True, (200, 200, 200)).get_rect(topleft=(left_x, start_y))),
            ("STATUS", self.mini_header_font.render("STATUS", True, (200, 200, 200)).get_rect(topleft=(left_x + name_width, start_y)))
        ]

        # Chapter rows
        self.chapter_rows.clear()
        for i, chapter in enumerate(self.chapters.keys()):
            name_label = chapter
            status_label = "Unlocked" if self.selected_chapter == chapter else "Locked"

            row_y = start_y + 40 + i * spacing
            self.chapter_rows.append((
                name_label,
                self.font.render(name_label, True, (255, 255, 255)).get_rect(topleft=(left_x, row_y))
            ))
            self.chapter_rows.append((
                status_label,
                self.font.render(status_label, True, (255, 255, 255)).get_rect(topleft=(left_x + name_width, row_y))
            ))

        # Levels
        self.level_rects.clear()
        if self.selected_chapter and self.chapters[self.selected_chapter]:
            for i, level in enumerate(self.chapters[self.selected_chapter]):
                rect = self.font.render(level, True, (255, 255, 255)).get_rect(
                    topleft=(right_x, start_y + i * spacing)
                )
                if rect.bottom <= inner_bottom:
                    self.level_rects.append((level, rect))
        else:
            placeholder = "Select a chapter to view levels"
            placeholder_surface = self.font.render(placeholder, True, (180, 180, 180))
            rect = placeholder_surface.get_rect(midtop=(right_x + (inner_right - right_x) // 2, start_y))
            self.level_rects.append((placeholder, rect))
            self.placeholder_surface = placeholder_surface

        # Scale buttons larger
        btn_width = box_width // 5
        btn_height = int(btn_width * 0.4)
        self.back_btn = pygame.transform.smoothscale(self.back_btn_original, (btn_width, btn_height))
        self.continue_btn = pygame.transform.smoothscale(self.continue_btn_original, (btn_width, btn_height))

        # Position buttons below box (moved up by 20px)
        button_y = self.menu_box_rect.bottom + 20
        self.back_btn_rect = self.back_btn.get_rect(midtop=(self.menu_box_rect.centerx - btn_width // 2 - 40, button_y))
        self.continue_btn_rect = self.continue_btn.get_rect(midtop=(self.menu_box_rect.centerx + btn_width // 2 + 40, button_y))

    def draw(self):
        self.screen.fill((20, 20, 20))
        self.screen.blit(self.menu_box, self.menu_box_rect)
        self.screen.blit(self.header_surface, self.header_rect)

        mouse_pos = pygame.mouse.get_pos()

        # Mini header
        for label, rect in self.chapter_header:
            text_surface = self.mini_header_font.render(label, True, (200, 200, 200))
            self.screen.blit(text_surface, rect)

        # Chapter rows
        for label, rect in self.chapter_rows:
            text_surface = self.font.render(label, True, (255, 255, 255))
            self.screen.blit(text_surface, rect)

        # Levels
        for level, rect in self.level_rects:
            if "Select a chapter" in level:
                self.screen.blit(self.placeholder_surface, rect)
            else:
                text_surface = self.font.render(level, True, (200, 200, 200))
                self.screen.blit(text_surface, rect)

        # Buttons with hover effect
        if self.back_btn_rect.collidepoint(mouse_pos):
            back_hover = pygame.transform.smoothscale(self.back_btn_original, (self.back_btn_rect.width + 20, self.back_btn_rect.height + 10))
            back_rect = back_hover.get_rect(center=self.back_btn_rect.center)
            self.screen.blit(back_hover, back_rect)
        else:
            self.screen.blit(self.back_btn, self.back_btn_rect)

        if self.continue_btn_rect.collidepoint(mouse_pos):
            continue_hover = pygame.transform.smoothscale(self.continue_btn_original, (self.continue_btn_rect.width + 20, self.continue_btn_rect.height + 10))
            continue_rect = continue_hover.get_rect(center=self.continue_btn_rect.center)
            self.screen.blit(continue_hover, continue_rect)
        else:
            self.screen.blit(self.continue_btn, self.continue_btn_rect)

    def handle_input(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mouse_pos = event.pos
            # Check chapter rows
            for label, rect in self.chapter_rows:
                if rect.collidepoint(mouse_pos):
                    # Only allow selecting the CHAPTER NAME column
                    if label not in ["Locked", "Unlocked"]:
                        self.selected_chapter = label
                        self.selected_index = None
                        self._create_layout()
                        return label
            # Check level clicks
            for level, rect in self.level_rects:
                if rect.collidepoint(mouse_pos) and "Select a chapter" not in level:
                    return f"{self.selected_chapter} - {level}"
            # Check button clicks
            if self.back_btn_rect.collidepoint(mouse_pos):
                return "back"
            if self.continue_btn_rect.collidepoint(mouse_pos):
                return "continue"

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_DOWN:
                self.selected_index = 0 if self.selected_index is None else (self.selected_index + 1) % len(
                    self.chapter_rows)
            elif event.key == pygame.K_UP:
                self.selected_index = 0 if self.selected_index is None else (self.selected_index - 1) % len(
                    self.chapter_rows)
            elif event.key == pygame.K_RETURN and self.selected_index is not None:
                label, _ = self.chapter_rows[self.selected_index]
                # Only select if it's a CHAPTER NAME
                if label not in ["Locked", "Unlocked"]:
                    self.selected_chapter = label
                    self._create_layout()
                    return label

        return None

    def update(self):
        pass

    def render(self):
        self.draw()
