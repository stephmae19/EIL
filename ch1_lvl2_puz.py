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

screen = pygame.display.set_mode((native_width, native_height - 50), pygame.RESIZABLE)
pygame.display.set_caption("Chapter 1 - Level 2 Puzzle")

game_surface = pygame.Surface((BASE_WIDTH, BASE_HEIGHT))


class PuzzleScene:
    def __init__(self, surface, player):
        self.surface = surface
        self.player = player
        self.ui_layer = UILayer(surface)
        self.ui_layer.health_rect = pygame.Rect(0, 0, 0, 0)

        # --- Scale images ---
        self.scale_bal = pygame.image.load(os.path.join("Assets", "MAPS", "chapter1", "scale_bal.png")).convert_alpha()
        self.scale_left = pygame.image.load(os.path.join("Assets", "MAPS", "chapter1", "scale_left.png")).convert_alpha()
        self.scale_right = pygame.image.load(os.path.join("Assets", "MAPS", "chapter1", "scale_right.png")).convert_alpha()

        self.scale_image = self.scale_bal
        self.scale_rect = self.scale_image.get_rect(center=(BASE_WIDTH // 2, BASE_HEIGHT // 2))

        # Slots
        self.orb_slots = [pygame.Rect(self.scale_rect.left + 100 + i * 80,
                                      self.scale_rect.centery - 50, 60, 60) for i in range(3)]
        self.book_slots = [pygame.Rect(self.scale_rect.right - 280 + i * 80,
                                       self.scale_rect.centery - 50, 60, 60) for i in range(3)]

        # Debug box horizontal offsets
        LEFT_BOX_OFFSET_X = 10  # adjust this value to move left box horizontally
        RIGHT_BOX_OFFSET_X = -168  # adjust this value to move right box horizontally

        self.debug_left_box = pygame.Rect(self.scale_rect.left + LEFT_BOX_OFFSET_X,
                                          self.scale_rect.centery - 100, 150, 140)
        self.debug_right_box = pygame.Rect(self.scale_rect.right + RIGHT_BOX_OFFSET_X,
                                           self.scale_rect.centery - 100, 150, 140)

        # Track placed items
        self.orbs_placed = []
        self.books_placed = []

        self.dragging_item = None
        self.drag_offset = (0, 0)

        self.imposter_orb = "ORB_IMPOSTER"
        self.imposter_book = "BOOK_IMPOSTER"

        self.message = ""

    def handle_event(self, event):
        self.ui_layer.handle_input(event)

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            # Start dragging from inventory
            if self.ui_layer.selected_slot is not None and self.ui_layer.selected_slot < len(self.player.inventory):
                item = self.player.inventory[self.ui_layer.selected_slot]
                self.dragging_item = item
                self.drag_offset = (event.pos[0], event.pos[1])

        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            if self.dragging_item:
                # Drop into orb slots
                if "ORB" in str(self.dragging_item):
                    for slot in self.orb_slots:
                        if slot.collidepoint(event.pos) and slot not in [s for _, s in self.orbs_placed]:
                            self.orbs_placed.append((self.dragging_item, slot))
                            break
                    # ✅ Debug left box
                    if self.debug_left_box.collidepoint(event.pos):
                        self.orbs_placed.append((self.dragging_item, self.debug_left_box))
                # Drop into book slots
                elif "BOOK" in str(self.dragging_item):
                    for slot in self.book_slots:
                        if slot.collidepoint(event.pos) and slot not in [s for _, s in self.books_placed]:
                            self.books_placed.append((self.dragging_item, slot))
                            break
                    # ✅ Debug right box
                    if self.debug_right_box.collidepoint(event.pos):
                        self.books_placed.append((self.dragging_item, self.debug_right_box))
                self.dragging_item = None

    def check_balance(self):
        if len(self.orbs_placed) == 3 and len(self.books_placed) == 3:
            orb_names = [str(o[0]) for o in self.orbs_placed]
            book_names = [str(b[0]) for b in self.books_placed]

            if self.imposter_orb in orb_names or self.imposter_book in book_names:
                self.message = "The scale refuses to balance..."
                self.scale_image = self.scale_left if self.imposter_orb in orb_names else self.scale_right
                return False
            else:
                self.message = "The scale balances perfectly!"
                self.scale_image = self.scale_bal
                return True
        else:
            # Tilt depending on imbalance
            if len(self.orbs_placed) > len(self.books_placed):
                self.scale_image = self.scale_left
            elif len(self.books_placed) > len(self.orbs_placed):
                self.scale_image = self.scale_right
            else:
                self.scale_image = self.scale_bal
        return False

    def draw(self):
        self.surface.fill((0, 0, 0))
        self.surface.blit(self.scale_image, self.scale_rect)

        # Debug boxes
        pygame.draw.rect(self.surface, (255, 0, 0), self.debug_left_box, 2)
        pygame.draw.rect(self.surface, (0, 0, 255), self.debug_right_box, 2)

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

        # Draw dragged item while moving
        if self.dragging_item:
            mouse_x, mouse_y = pygame.mouse.get_pos()
            if isinstance(self.dragging_item, pygame.Surface):
                rect = self.dragging_item.get_rect(center=(mouse_x, mouse_y))
                self.surface.blit(self.dragging_item, rect)
            else:
                text = self.ui_layer.inventory_font.render(str(self.dragging_item), True, (255, 255, 255))
                rect = text.get_rect(center=(mouse_x, mouse_y))
                self.surface.blit(text, rect)

        # --- Scale & Blit to window ---
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
                ch1_lvl2.run_level()
                return
            puzzle.handle_event(event)

        solved = puzzle.check_balance()
        puzzle.draw()

        if solved:
            pygame.time.delay(2000)
            ch1_lvl2.run_level()
            return

        clock.tick(60)
