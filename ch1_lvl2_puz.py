# ch1_lvl2_puz.py
import pygame
import sys
import os
from ui_layer import UILayer
import ch1_lvl2  # ✅ Import your main level file

# --- Base Resolution (Design Target) ---
BASE_WIDTH, BASE_HEIGHT = 1920, 1080

# --- Initialization ---
pygame.init()
pygame.font.init()

# --- Display Setup ---
info = pygame.display.Info()
native_width, native_height = info.current_w, info.current_h
os.environ['SDL_VIDEO_CENTERED'] = '1'

# ✅ Resizable window consistent with ch1_lvl1.py and ch1_lvl2.py
screen = pygame.display.set_mode((native_width, native_height - 50), pygame.RESIZABLE)
pygame.display.set_caption("Chapter 1 - Level 2 Puzzle")

# Internal fixed surface (always BASE_WIDTH x BASE_HEIGHT)
game_surface = pygame.Surface((BASE_WIDTH, BASE_HEIGHT))


class PuzzleScene:
    def __init__(self, surface, player):
        self.surface = surface
        self.player = player
        self.ui_layer = UILayer(surface)

        # ✅ Always initialize health_rect so it's safe to use
        self.ui_layer.health_rect = pygame.Rect(0, 0, 0, 0)

        # Load balanced scale background
        scale_path = os.path.join("Assets", "MAPS", "chapter1", "scale_bal.png")
        if os.path.exists(scale_path):
            self.scale_image = pygame.image.load(scale_path).convert_alpha()
        else:
            self.scale_image = pygame.Surface((800, 400))
            self.scale_image.fill((120, 120, 120))

        self.scale_rect = self.scale_image.get_rect(center=(BASE_WIDTH // 2, BASE_HEIGHT // 2))

        # Slots for orbs (left) and books (right)
        self.orb_slots = [pygame.Rect(self.scale_rect.left + 100 + i * 80,
                                      self.scale_rect.centery - 50, 60, 60) for i in range(3)]
        self.book_slots = [pygame.Rect(self.scale_rect.right - 280 + i * 80,
                                       self.scale_rect.centery - 50, 60, 60) for i in range(3)]

        # Track placed items
        self.orbs_placed = []
        self.books_placed = []

        # Imposters (they can be placed but will never balance)
        self.imposter_orb = "ORB_IMPOSTER"
        self.imposter_book = "BOOK_IMPOSTER"

        # Subtitle feedback
        self.message = ""

    def handle_event(self, event):
        self.ui_layer.handle_input(event)

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.ui_layer.selected_slot is not None and self.ui_layer.selected_slot < len(self.player.inventory):
                item = self.player.inventory[self.ui_layer.selected_slot]

                if "ORB" in str(item):
                    for slot in self.orb_slots:
                        if slot.collidepoint(event.pos) and slot not in [s for _, s in self.orbs_placed]:
                            self.orbs_placed.append((item, slot))
                            break
                elif "BOOK" in str(item):
                    for slot in self.book_slots:
                        if slot.collidepoint(event.pos) and slot not in [s for _, s in self.books_placed]:
                            self.books_placed.append((item, slot))
                            break

    def check_balance(self):
        if len(self.orbs_placed) == 3 and len(self.books_placed) == 3:
            orb_names = [str(o[0]) for o in self.orbs_placed]
            book_names = [str(b[0]) for b in self.books_placed]

            if self.imposter_orb in orb_names or self.imposter_book in book_names:
                self.message = "The scale refuses to balance..."
                return False
            else:
                self.message = "The scale balances perfectly!"
                return True
        return False

    def draw(self):
        self.surface.fill((0, 0, 0))
        self.surface.blit(self.scale_image, self.scale_rect)

        # Draw placed orbs
        for item, slot in self.orbs_placed:
            if isinstance(item, pygame.Surface):
                rect = item.get_rect(center=slot.center)
                self.surface.blit(item, rect)
            else:
                text = self.ui_layer.inventory_font.render(str(item), True, (255, 255, 255))
                rect = text.get_rect(center=slot.center)
                self.surface.blit(text, rect)

        # Draw placed books
        for item, slot in self.books_placed:
            if isinstance(item, pygame.Surface):
                rect = item.get_rect(center=slot.center)
                self.surface.blit(item, rect)
            else:
                text = self.ui_layer.inventory_font.render(str(item), True, (255, 255, 255))
                rect = text.get_rect(center=slot.center)
                self.surface.blit(text, rect)

        # Draw UI layer
        self.ui_layer.draw(self.player)

        # Show feedback message
        if self.message:
            self.ui_layer.show_subtitle(self.message, duration=3000)
        self.ui_layer.draw_subtitle()

        # --- Scale & Blit to window with aspect ratio preserved ---
        window_width, window_height = screen.get_size()
        scale = min(window_width / BASE_WIDTH, window_height / BASE_HEIGHT)
        scaled_w, scaled_h = int(BASE_WIDTH * scale), int(BASE_HEIGHT * scale)

        scaled_surface = pygame.transform.smoothscale(self.surface, (scaled_w, scaled_h))
        x_offset = (window_width - scaled_w) // 2
        y_offset = (window_height - scaled_h) // 2

        screen.fill((0, 0, 0))
        screen.blit(scaled_surface, (x_offset, y_offset))
        pygame.display.flip()


def run_puzzle(surface, player):
    clock = pygame.time.Clock()
    puzzle = PuzzleScene(game_surface, player)

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                # ✅ Allow exit back to main level
                ch1_lvl2.run_level()
                return
            puzzle.handle_event(event)

        solved = puzzle.check_balance()
        puzzle.draw()

        if solved:
            pygame.time.delay(2000)
            ch1_lvl2.run_level()  # ✅ return to main level
            return

        clock.tick(60)
