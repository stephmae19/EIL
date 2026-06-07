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
        self.scale_left = pygame.image.load(
            os.path.join("Assets", "MAPS", "chapter1", "scale_left.png")).convert_alpha()
        self.scale_right = pygame.image.load(
            os.path.join("Assets", "MAPS", "chapter1", "scale_right.png")).convert_alpha()

        self.scale_image = self.scale_bal
        self.scale_rect = self.scale_image.get_rect(center=(BASE_WIDTH // 2, BASE_HEIGHT // 2))

        # Slots
        self.orb_slots = [pygame.Rect(self.scale_rect.left + 100 + i * 80,
                                      self.scale_rect.centery - 50, 60, 60) for i in range(3)]
        self.book_slots = [pygame.Rect(self.scale_rect.right - 280 + i * 80,
                                       self.scale_rect.centery - 50, 60, 60) for i in range(3)]

        # Debug box horizontal offsets
        LEFT_BOX_OFFSET_X = 10
        RIGHT_BOX_OFFSET_X = -168

        self.debug_left_box = pygame.Rect(self.scale_rect.left + LEFT_BOX_OFFSET_X,
                                          self.scale_rect.centery - 100, 150, 140)
        self.debug_right_box = pygame.Rect(self.scale_rect.right + RIGHT_BOX_OFFSET_X,
                                           self.scale_rect.centery - 100, 150, 140)

        # Track placed items
        self.orbs_placed = []
        self.books_placed = []

        # Dragging states
        self.dragging_item = None
        self.dragged_item_index = None
        self.drag_offset_x = 0
        self.drag_offset_y = 0

        self.imposter_orb = "ORB_IMPOSTER"
        self.imposter_book = "BOOK_IMPOSTER"

        self.message = ""

    def get_virtual_mouse_pos(self, screen_pos):
        """Converts physical window mouse coordinates into virtual 1920x1080 space."""
        window_width, window_height = screen.get_size()
        scale = min(window_width / BASE_WIDTH, window_height / BASE_HEIGHT)
        scaled_w, scaled_h = int(BASE_WIDTH * scale), int(BASE_HEIGHT * scale)

        x_offset = (window_width - scaled_w) // 2
        y_offset = (window_height - scaled_h) // 2

        virtual_x = (screen_pos[0] - x_offset) / scale
        virtual_y = (screen_pos[1] - y_offset) / scale
        return int(virtual_x), int(virtual_y)

    def handle_event(self, event):
        # Pass native event down to UI layer features if needed
        self.ui_layer.handle_input(event)

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            virtual_pos = self.get_virtual_mouse_pos(event.pos)

            # Check inventory slots using virtual positions
            for i, slot in enumerate(self.ui_layer.inventory_slots):
                if slot.collidepoint(virtual_pos) and i < len(self.player.inventory):
                    self.dragging_item = self.player.inventory[i]
                    self.dragged_item_index = i
                    self.ui_layer.selected_slot = i

                    # Calculate offsets from item visual center
                    self.drag_offset_x = virtual_pos[0] - slot.centerx
                    self.drag_offset_y = virtual_pos[1] - slot.centery
                    break

        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            if self.dragging_item is not None:
                virtual_pos = self.get_virtual_mouse_pos(event.pos)
                placed = False
                item_str = str(self.dragging_item)

                # ✅ Rules validation: Orbs on left side
                if "ORB" in item_str:
                    for slot in self.orb_slots:
                        if slot.collidepoint(virtual_pos) and slot not in [s for _, s in self.orbs_placed]:
                            self.orbs_placed.append((self.dragging_item, slot))
                            placed = True
                            break
                    if not placed and self.debug_left_box.collidepoint(virtual_pos):
                        self.orbs_placed.append((self.dragging_item, self.debug_left_box))
                        placed = True

                # ✅ Rules validation: Books on right side
                elif "BOOK" in item_str:
                    for slot in self.book_slots:
                        if slot.collidepoint(virtual_pos) and slot not in [s for _, s in self.books_placed]:
                            self.books_placed.append((self.dragging_item, slot))
                            placed = True
                            break
                    if not placed and self.debug_right_box.collidepoint(virtual_pos):
                        self.books_placed.append((self.dragging_item, self.debug_right_box))
                        placed = True

                # Remove from inventory if successfully slotted
                if placed and self.dragged_item_index is not None:
                    self.player.inventory.pop(self.dragged_item_index)
                    self.ui_layer.selected_slot = None

                # Reset dragging configuration
                self.dragging_item = None
                self.dragged_item_index = None

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

        # Debug bounding blocks
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

        # Draw UI layer updates
        self.ui_layer.draw(self.player)

        # Show feedback message
        if self.message:
            self.ui_layer.show_subtitle(self.message, duration=3000)
        self.ui_layer.draw_subtitle()

        # Render dragged object locked to virtual mouse position
        if self.dragging_item is not None:
            raw_mouse = pygame.mouse.get_pos()
            v_mx, v_my = self.get_virtual_mouse_pos(raw_mouse)
            render_x = v_mx - self.drag_offset_x
            render_y = v_my - self.drag_offset_y

            if isinstance(self.dragging_item, pygame.Surface):
                rect = self.dragging_item.get_rect(center=(render_x, render_y))
                self.surface.blit(self.dragging_item, rect)
            else:
                text = self.ui_layer.inventory_font.render(str(self.dragging_item), True, (255, 255, 255))
                rect = text.get_rect(center=(render_x, render_y))
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