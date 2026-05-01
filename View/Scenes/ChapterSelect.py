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
        self.menu_box_original = pygame.image.load("assets/scenery/chapter_select_window.png").convert_alpha()

        # Load buttons
        self.back_btn_original = pygame.image.load("assets/menu options/back_btn.png").convert_alpha()
        self.start_btn_original = pygame.image.load("assets/menu options/simple_start_btn.png").convert_alpha()

        # Load book icon
        self.book_icon_original = pygame.image.load("assets/objects-items/book.png").convert_alpha()
        self.book_icon = None

        # Define chapters and levels
        self.chapters = {
            "CHAPTER 1: THE BEGINNING": ["Level 1", "Level 2", "Level 3"],
            "CHAPTER 2: THE WHISPERS": ["Level 1", "Level 2"],
            "CHAPTER 3: THE PUZZLES": ["Level 1", "Level 2", "Level 3", "Level 4"],
            "CHAPTER 4: THE REVELATION": ["Level 1", "Level 2"],
        }

        # Layout state
        self.menu_box = None
        self.menu_box_rect = None
        self.chapter_rows = []
        self.level_rects = []
        self.header_rect = None
        self.chapter_name_header = None
        self.status_header = None
        self.levels_header = None
        self.back_btn = None
        self.start_btn = None
        self.back_btn_rect = None
        self.start_btn_rect = None
        self.selected_chapter = None

        # Hover sound
        self.hover_sound = pygame.mixer.Sound("sounds/button_hover.mp3")
        self.last_hovered = None

        self._create_layout()

    def _wrap_text(self, text, font, max_width):
        words = text.split(" ")
        lines, current_line = [], ""
        for word in words:
            test_line = current_line + (" " if current_line else "") + word
            if font.size(test_line)[0] <= max_width:
                current_line = test_line
            else:
                lines.append(current_line)
                current_line = word
        if current_line:
            lines.append(current_line)
        return lines

    def _create_layout(self):
        screen_width, screen_height = self.screen.get_size()

        # Scale menu box
        box_width = int(screen_width * 0.8)
        box_height = int(screen_height * 0.7)
        self.menu_box = pygame.transform.smoothscale(self.menu_box_original, (box_width, box_height))
        self.menu_box_rect = self.menu_box.get_rect(center=(screen_width // 2, screen_height // 2))

        # Resize book icon
        icon_size = 64
        self.book_icon = pygame.transform.smoothscale(self.book_icon_original, (icon_size, icon_size))

        # Margins
        margin_x, margin_y = 40, 40
        inner_left = self.menu_box_rect.left + margin_x
        inner_right = self.menu_box_rect.right - margin_x
        inner_top = self.menu_box_rect.top + margin_y
        inner_bottom = self.menu_box_rect.bottom - margin_y

        # Divide into left (chapters) and right (levels)
        mid_x = self.menu_box_rect.centerx
        left_x = inner_left
        right_x = mid_x + 30
        start_y = inner_top + 100
        spacing = 70

        # Main header
        header_surface = self.header_font.render("CHAPTERS & LEVELS", True, (255, 255, 255))
        self.header_rect = header_surface.get_rect(midtop=(self.menu_box_rect.centerx, inner_top))
        self.header_surface = header_surface

        # Sub-headers
        self.chapter_name_header = self.mini_header_font.render("CHAPTER NAME", True, (200, 200, 200))
        self.status_header = self.mini_header_font.render("STATUS", True, (200, 200, 200))
        self.levels_header = self.mini_header_font.render("LEVELS", True, (200, 200, 200))

        self.chapter_name_header_rect = self.chapter_name_header.get_rect(topleft=(left_x, inner_top + 60))
        self.status_header_rect = self.status_header.get_rect(topleft=(left_x + 340, inner_top + 60))
        self.levels_header_rect = self.levels_header.get_rect(topleft=(right_x, inner_top + 60))

        # Chapter rows
        self.chapter_rows.clear()
        for i, chapter in enumerate(self.chapters.keys()):
            row_y = start_y + i * spacing
            book_rect = self.book_icon.get_rect(topleft=(left_x, row_y))

            wrapped_lines = self._wrap_text(chapter, self.font, 250)
            text_surfaces = []
            for j, line in enumerate(wrapped_lines):
                surf = self.font.render(line, True, (255, 255, 255))
                rect = surf.get_rect(topleft=(book_rect.right + 10, row_y + j * 30))
                text_surfaces.append((surf, rect))

            status_surface = self.font.render("Unlocked" if self.selected_chapter == chapter else "Locked", True, (255, 255, 255))
            status_rect = status_surface.get_rect(topleft=(left_x + 340, row_y))

            self.chapter_rows.append((book_rect, text_surfaces, status_surface, status_rect, chapter))

        # Levels
        self.level_rects.clear()
        if self.selected_chapter:
            for i, level in enumerate(self.chapters[self.selected_chapter]):
                rect = self.font.render(level, True, (255, 255, 255)).get_rect(topleft=(right_x, start_y + i * spacing))
                if rect.bottom <= inner_bottom:
                    self.level_rects.append((level, rect))
        else:
            placeholder = "Select a chapter to view levels"
            placeholder_surface = self.font.render(placeholder, True, (180, 180, 180))
            rect = placeholder_surface.get_rect(topleft=(right_x, start_y))
            self.level_rects.append((placeholder, rect))
            self.placeholder_surface = placeholder_surface

        # Buttons
        btn_width = box_width // 5
        btn_height = int(btn_width * 0.4)
        self.back_btn = pygame.transform.smoothscale(self.back_btn_original, (btn_width, btn_height))
        self.start_btn = pygame.transform.smoothscale(self.start_btn_original, (btn_width, btn_height))

        button_y = self.menu_box_rect.bottom + 20
        self.back_btn_rect = self.back_btn.get_rect(midtop=(self.menu_box_rect.centerx - btn_width // 2 - 40, button_y))
        self.start_btn_rect = self.start_btn.get_rect(midtop=(self.menu_box_rect.centerx + btn_width // 2 + 40, button_y))

    def draw(self):
        self.screen.fill((20, 20, 20))
        self.screen.blit(self.menu_box, self.menu_box_rect)
        self.screen.blit(self.header_surface, self.header_rect)

        # Draw sub-headers
        self.screen.blit(self.chapter_name_header, self.chapter_name_header_rect)
        self.screen.blit(self.status_header, self.status_header_rect)
        self.screen.blit(self.levels_header, self.levels_header_rect)

        mouse_pos = pygame.mouse.get_pos()
        hovered = None

        # Draw chapters
        for book_rect, text_surfaces, status_surface, status_rect, chapter in self.chapter_rows:
            self.screen.blit(self.book_icon, book_rect)
            for surf, rect in text_surfaces:
                self.screen.blit(surf, rect)
                if rect.collidepoint(mouse_pos):
                    hovered = chapter
            self.screen.blit(status_surface, status_rect)

        # Draw levels
        for level, rect in self.level_rects:
            if "Select a chapter" in level:
                self.screen.blit(self.placeholder_surface, rect)
            else:
                text_surface = self.font.render(level, True, (200, 200, 200))
                self.screen.blit(text_surface, rect)
                if rect.collidepoint(mouse_pos):
                    hovered = level

        # Buttons (same hover logic)
        if self.back_btn_rect.collidepoint(mouse_pos):
            back_hover = pygame.transform.smoothscale(
                self.back_btn_original,
                (self.back_btn_rect.width + 20, self.back_btn_rect.height + 10)
            )
            back_rect = back_hover.get_rect(center=self.back_btn_rect.center)
            self.screen.blit(back_hover, back_rect)
            hovered = "back"
        else:
            self.screen.blit(self.back_btn, self.back_btn_rect)

        if self.start_btn_rect.collidepoint(mouse_pos):
            start_hover = pygame.transform.smoothscale(
                self.start_btn_original,
                (self.start_btn_rect.width + 20, self.start_btn_rect.height + 10)
            )
            start_rect = start_hover.get_rect(center=self.start_btn_rect.center)
            self.screen.blit(start_hover, start_rect)
            hovered = "start"
        else:
            self.screen.blit(self.start_btn, self.start_btn_rect)

        # Play hover sound only when entering a new element
        if hovered is not None and hovered != self.last_hovered:
            self.hover_sound.play()
        self.last_hovered = hovered

    def handle_input(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mouse_pos = event.pos
            # Check chapter clicks
            for _, text_surfaces, status_surface, status_rect, chapter in self.chapter_rows:
                for _, rect in text_surfaces:
                    if rect.collidepoint(mouse_pos):
                        self.selected_chapter = chapter
                        self._create_layout()
                        return chapter
            # Check level clicks
            for level, rect in self.level_rects:
                if rect.collidepoint(mouse_pos) and "Select a chapter" not in level:
                    return f"{self.selected_chapter} - {level}"
            # Buttons
            if self.back_btn_rect.collidepoint(mouse_pos):
                return "back"
            if self.start_btn_rect.collidepoint(mouse_pos):
                return "start"
        return None

    def update(self):
        self._create_layout()

    def render(self):
        self.draw()
