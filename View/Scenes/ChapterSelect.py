# View/Scenes/ChapterSelect.py
import pygame

class ChapterSelect:
    def __init__(self, screen):
        self.screen = screen
        self.font = pygame.font.Font(None, 48)

        # Define chapters
        self.chapters = [
            {"label": "CHAPTER 1: THE BEGINNING", "id": 1},
            {"label": "CHAPTER 2: THE WHISPERS", "id": 2},
            {"label": "CHAPTER 3: THE PUZZLES", "id": 3},
            {"label": "CHAPTER 4: THE REVELATION", "id": 4},
            {"label": "BACK TO MENU", "id": "menu"},
        ]

        # Button layout
        self.chapter_rects = []
        self._create_layout()

        # Track keyboard selection
        self.selected_index = None

    def _create_layout(self):
        """Create chapter rectangles centered on screen."""
        screen_width, screen_height = self.screen.get_size()
        spacing = 70
        start_y = screen_height // 4

        for i, chapter in enumerate(self.chapters):
            rect = self.font.render(chapter["label"], True, (255, 255, 255)).get_rect(
                center=(screen_width // 2, start_y + i * spacing)
            )
            self.chapter_rects.append((chapter["label"], rect, chapter["id"]))

    def draw(self):
        """Render chapter buttons with hover and keyboard highlight."""
        self.screen.fill((20, 20, 20))  # Dark background
        mouse_pos = pygame.mouse.get_pos()

        for i, (label, rect, chap_id) in enumerate(self.chapter_rects):
            if rect.collidepoint(mouse_pos):
                text_surface = self.font.render(label, True, (255, 215, 0))  # Gold hover
            elif self.selected_index == i:
                text_surface = self.font.render(label, True, (173, 216, 230))  # Light blue keyboard highlight
            else:
                text_surface = self.font.render(label, True, (255, 255, 255))
            self.screen.blit(text_surface, rect)

    def handle_input(self, event):
        """Check if a chapter is clicked or selected with keyboard."""
        # Mouse click
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mouse_pos = event.pos
            for i, (label, rect, chap_id) in enumerate(self.chapter_rects):
                if rect.collidepoint(mouse_pos):
                    self.selected_index = None
                    return chap_id

        # Keyboard navigation
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_DOWN:
                if self.selected_index is None:
                    self.selected_index = 0
                else:
                    self.selected_index = (self.selected_index + 1) % len(self.chapter_rects)
            elif event.key == pygame.K_UP:
                if self.selected_index is None:
                    self.selected_index = 0
                else:
                    self.selected_index = (self.selected_index - 1) % len(self.chapter_rects)
            elif event.key == pygame.K_RETURN and self.selected_index is not None:
                _, _, chap_id = self.chapter_rects[self.selected_index]
                return chap_id

        return None

    def update(self):
        pass

    def render(self):
        self.draw()
