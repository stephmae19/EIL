# View/Scenes/ChapterSelect.py
import pygame
import os

class ChapterSelect:
    def __init__(self, screen):
        self.screen = screen

        # Load custom font (VCR OSD Mono)
        font_path = os.path.join("assets", "font", "VCR_OSD_MONO_1.001.ttf")
        self.font = pygame.font.Font(font_path, 32)
        self.header_font = pygame.font.Font(font_path, 40)

        # Load menu box background
        self.menu_box_original = pygame.image.load("assets/scenery/plain_box.jpeg").convert_alpha()

        # Load buttons
        self.back_btn_original = pygame.image.load("assets/menu options/back_btn.png").convert_alpha()
        self.start_btn_original = pygame.image.load("assets/menu options/simple_start_btn.png").convert_alpha()

        # Scale buttons to default size
        self.back_btn = pygame.transform.smoothscale(self.back_btn_original, (150, 60))
        self.start_btn = pygame.transform.smoothscale(self.start_btn_original, (150, 60))

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
        self.chapter_rects = []
        self.level_rects = []
        self.header_rect = None
        self.back_btn_rect = None
        self.start_btn_rect = None
        self.selected_chapter = None
        self.selected_index = None

        self._create_layout()

    def _create_layout(self):
        """Create menu box, header, chapters, levels, and buttons with bounds checking."""
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

        self.chapter_rects.clear()
        for i, chapter in enumerate(self.chapters.keys()):
            rect = self.font.render(chapter, True, (255, 255, 255)).get_rect(
                topleft=(left_x, start_y + i * spacing)
            )
            if rect.bottom <= inner_bottom:
                self.chapter_rects.append((chapter, rect))

        self.level_rects.clear()
        if self.selected_chapter and self.chapters[self.selected_chapter]:
            for i, level in enumerate(self.chapters[self.selected_chapter]):
                rect = self.font.render(level, True, (255, 255, 255)).get_rect(
                    topleft=(right_x, start_y + i * spacing)
                )
                if rect.bottom <= inner_bottom:
                    if rect.right > inner_right:
                        rect.right = inner_right
                    self.level_rects.append((level, rect))
        else:
            placeholder = "Select a chapter to view levels"
            placeholder_surface = self.font.render(placeholder, True, (180, 180, 180))
            rect = placeholder_surface.get_rect(midtop=(right_x + (inner_right - right_x) // 2, start_y))
            if rect.right > inner_right: rect.right = inner_right
            if rect.left < right_x: rect.left = right_x
            if rect.bottom > inner_bottom: rect.bottom = inner_bottom
            self.level_rects.append((placeholder, rect))
            self.placeholder_surface = placeholder_surface

        # Position buttons below box
        button_y = self.menu_box_rect.bottom + 40
        self.back_btn_rect = self.back_btn.get_rect(midtop=(self.menu_box_rect.centerx - 100, button_y))
        self.start_btn_rect = self.start_btn.get_rect(midtop=(self.menu_box_rect.centerx + 100, button_y))

    def draw(self):
        """Render menu box, header, chapters, levels, and buttons with hover effects."""
        self.screen.fill((20, 20, 20))
        self.screen.blit(self.menu_box, self.menu_box_rect)
        self.screen.blit(self.header_surface, self.header_rect)

        mouse_pos = pygame.mouse.get_pos()

        # Chapters
        for i, (label, rect) in enumerate(self.chapter_rects):
            if rect.collidepoint(mouse_pos):
                text_surface = self.font.render(label, True, (255, 215, 0))
            elif self.selected_index == i:
                text_surface = self.font.render(label, True, (173, 216, 230))
            else:
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
            back_hover = pygame.transform.smoothscale(self.back_btn_original, (165, 66))
            back_rect = back_hover.get_rect(center=self.back_btn_rect.center)
            self.screen.blit(back_hover, back_rect)
        else:
            self.screen.blit(self.back_btn, self.back_btn_rect)

        if self.start_btn_rect.collidepoint(mouse_pos):
            start_hover = pygame.transform.smoothscale(self.start_btn_original, (165, 66))
            start_rect = start_hover.get_rect(center=self.start_btn_rect.center)
            self.screen.blit(start_hover, start_rect)
        else:
            self.screen.blit(self.start_btn, self.start_btn_rect)

    def handle_input(self, event):
        """Handle mouse clicks and keyboard navigation."""
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mouse_pos = event.pos
            for i, (label, rect) in enumerate(self.chapter_rects):
                if rect.collidepoint(mouse_pos):
                    self.selected_chapter = label
                    self.selected_index = None
                    self._create_layout()
                    return label
            for level, rect in self.level_rects:
                if rect.collidepoint(mouse_pos) and "Select a chapter" not in level:
                    return f"{self.selected_chapter} - {level}"
            if self.back_btn_rect.collidepoint(mouse_pos):
                return "back"
            if self.start_btn_rect.collidepoint(mouse_pos):
                return "start"

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_DOWN:
                self.selected_index = 0 if self.selected_index is None else (self.selected_index + 1) % len(self.chapter_rects)
            elif event.key == pygame.K_UP:
                self.selected_index = 0 if self.selected_index is None else (self.selected_index - 1) % len(self.chapter_rects)
            elif event.key == pygame.K_RETURN and self.selected_index is not None:
                label, _ = self.chapter_rects[self.selected_index]
                self.selected_chapter = label
                self._create_layout()
                return label

        return None

    def update(self):
        pass

    def render(self):
        self.draw()
