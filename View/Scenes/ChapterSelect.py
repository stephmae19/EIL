# View/Scenes/ChapterSelect.py
import pygame

class ChapterSelect:
    def __init__(self, screen):
        self.screen = screen
        self.font = pygame.font.Font(None, 48)

        # Load menu box background
        self.menu_box_original = pygame.image.load("assets/scenery/plain_box.jpeg").convert_alpha()

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
        self.selected_chapter = None
        self.selected_index = None

        self._create_layout()

    def _create_layout(self):
        """Create menu box and divide into chapter/level areas."""
        screen_width, screen_height = self.screen.get_size()

        # Scale menu box to fit nicely
        box_width = int(screen_width * 0.8)
        box_height = int(screen_height * 0.7)
        self.menu_box = pygame.transform.smoothscale(self.menu_box_original, (box_width, box_height))
        self.menu_box_rect = self.menu_box.get_rect(center=(screen_width // 2, screen_height // 2))

        # Divide box into left (chapters) and right (levels)
        left_x = self.menu_box_rect.left + 100
        right_x = self.menu_box_rect.centerx + 100
        start_y = self.menu_box_rect.top + 80
        spacing = 70

        # Chapter labels
        self.chapter_rects.clear()
        for i, chapter in enumerate(self.chapters.keys()):
            rect = self.font.render(chapter, True, (255, 255, 255)).get_rect(
                topleft=(left_x, start_y + i * spacing)
            )
            self.chapter_rects.append((chapter, rect))

        # Level labels (placeholder if none selected)
        self.level_rects.clear()
        if self.selected_chapter and self.chapters[self.selected_chapter]:
            for i, level in enumerate(self.chapters[self.selected_chapter]):
                rect = self.font.render(level, True, (255, 255, 255)).get_rect(
                    topleft=(right_x, start_y + i * spacing)
                )
                self.level_rects.append((level, rect))
        else:
            # Placeholder text
            placeholder = "Select a chapter to view levels"
            rect = self.font.render(placeholder, True, (180, 180, 180)).get_rect(
                topleft=(right_x, start_y)
            )
            self.level_rects.append((placeholder, rect))

    def draw(self):
        """Render menu box, chapters, and levels."""
        self.screen.fill((20, 20, 20))  # Dark background
        self.screen.blit(self.menu_box, self.menu_box_rect)

        mouse_pos = pygame.mouse.get_pos()

        # Draw chapters
        for i, (label, rect) in enumerate(self.chapter_rects):
            if rect.collidepoint(mouse_pos):
                text_surface = self.font.render(label, True, (255, 215, 0))  # Gold hover
            elif self.selected_index == i:
                text_surface = self.font.render(label, True, (173, 216, 230))  # Light blue highlight
            else:
                text_surface = self.font.render(label, True, (255, 255, 255))
            self.screen.blit(text_surface, rect)

        # Draw levels (or placeholder)
        for level, rect in self.level_rects:
            text_surface = self.font.render(level, True, (200, 200, 200))
            self.screen.blit(text_surface, rect)

    def handle_input(self, event):
        """Handle mouse clicks and keyboard navigation."""
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mouse_pos = event.pos
            # Check chapter clicks
            for i, (label, rect) in enumerate(self.chapter_rects):
                if rect.collidepoint(mouse_pos):
                    self.selected_chapter = label
                    self.selected_index = None
                    self._create_layout()
                    return label
            # Check level clicks
            for level, rect in self.level_rects:
                if rect.collidepoint(mouse_pos) and "Select a chapter" not in level:
                    return f"{self.selected_chapter} - {level}"

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
