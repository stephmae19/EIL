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

# ✅ Persistent Puzzle State Instance reference variable
_puzzle_instance = None


class PuzzleScene:
    def __init__(self, surface, player):
        self.surface = surface
        self.player = player
        self.ui_layer = UILayer(surface)
        self.ui_layer.health_rect = pygame.Rect(0, 0, 0, 0)

        # ✅ Font for the Back Button text rendering layer
        self.button_font = pygame.font.SysFont("arial", 32, bold=True)

        # --- Scale images ---
        self.scale_bal = pygame.image.load(os.path.join("Assets", "MAPS", "chapter1", "scale_bal.png")).convert_alpha()
        self.scale_left = pygame.image.load(
            os.path.join("Assets", "MAPS", "chapter1", "scale_left.png")).convert_alpha()
        self.scale_right = pygame.image.load(
            os.path.join("Assets", "MAPS", "chapter1", "scale_right.png")).convert_alpha()

        self.scale_image = self.scale_bal
        self.scale_rect = self.scale_image.get_rect(center=(BASE_WIDTH // 2, BASE_HEIGHT // 2))

        # ✅ Back Button Hitbox Area Rectangle definition (Match Level 1 style)
        self.back_button = pygame.Rect(50, 50, 120, 50)

        # Debug box horizontal offsets
        LEFT_BOX_OFFSET_X = 10
        RIGHT_BOX_OFFSET_X = -168

        self.debug_left_box = pygame.Rect(self.scale_rect.left + LEFT_BOX_OFFSET_X,
                                          self.scale_rect.centery - 100, 150, 140)
        self.debug_right_box = pygame.Rect(self.scale_rect.right + RIGHT_BOX_OFFSET_X,
                                           self.scale_rect.centery - 100, 150, 140)

        # Automatically calculate slots inside the visual box bounds to prevent overflow
        self.orb_slots = [
            pygame.Rect(self.debug_left_box.left + 10 + i * 45, self.debug_left_box.centery - 20, 40, 40)
            for i in range(3)
        ]

        self.book_slots = [
            pygame.Rect(self.debug_right_box.left + 10 + i * 45, self.debug_right_box.centery - 20, 40, 40)
            for i in range(3)
        ]

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
        self.ui_layer.handle_input(event)

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            virtual_pos = self.get_virtual_mouse_pos(event.pos)

            # ✅ Check if the player clicked on the custom Back Button bounding frame
            if self.back_button.collidepoint(virtual_pos):
                return "BACK"

            # Pick up an item dictionary structure from the inventory bar
            for i, slot in enumerate(self.ui_layer.inventory_slots):
                if slot.collidepoint(virtual_pos) and i < len(self.player.inventory):
                    self.dragging_item = self.player.inventory[i]
                    self.dragged_item_index = i
                    self.ui_layer.selected_slot = i

                    self.drag_offset_x = virtual_pos[0] - slot.centerx
                    self.drag_offset_y = virtual_pos[1] - slot.centery
                    break

        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            if self.dragging_item is not None:
                virtual_pos = self.get_virtual_mouse_pos(event.pos)
                placed = False

                # Read the ID string from the dict object directly
                item_id = self.dragging_item["id"] if isinstance(self.dragging_item, dict) else str(self.dragging_item)

                # 1. Check if dropped over the LEFT area (Scale's Orb Side)
                if self.debug_left_box.collidepoint(virtual_pos) or any(
                        slot.collidepoint(virtual_pos) for slot in self.orb_slots):
                    if "ORB" in item_id:
                        already_taken_slots = [slot for _, slot in self.orbs_placed]
                        for slot in self.orb_slots:
                            if slot not in already_taken_slots:
                                self.orbs_placed.append((self.dragging_item, slot))
                                placed = True
                                break
                    else:
                        self.message = "Only round orbs fit on the left plate!"

                # 2. Check if dropped over the RIGHT area (Scale's Book Side)
                elif self.debug_right_box.collidepoint(virtual_pos) or any(
                        slot.collidepoint(virtual_pos) for slot in self.book_slots):
                    if "BOOK" in item_id:
                        already_taken_slots = [slot for _, slot in self.books_placed]
                        for slot in self.book_slots:
                            if slot not in already_taken_slots:
                                self.books_placed.append((self.dragging_item, slot))
                                placed = True
                                break
                    else:
                        self.message = "Only books belong on the right plate!"

                # Remove from inventory if placed into a target layout slot successfully
                if placed and self.dragged_item_index is not None:
                    self.player.inventory.pop(self.dragged_item_index)
                    self.ui_layer.selected_slot = None
                    self.message = ""

                # Reset drag properties cleanly
                self.dragging_item = None
                self.dragged_item_index = None
        return None

    def check_balance(self):
        if len(self.orbs_placed) == 3 and len(self.books_placed) == 3:
            orb_names = [o[0]["id"] if isinstance(o[0], dict) else str(o[0]) for o in self.orbs_placed]
            book_names = [b[0]["id"] if isinstance(b[0], dict) else str(b[0]) for b in self.books_placed]

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

    def draw_placed_item(self, item, slot):
        """Helper function to render dictionary items onto target puzzle slots."""
        item_icon = item["icon"] if isinstance(item, dict) else item
        item_id = item["id"] if isinstance(item, dict) else str(item)

        if isinstance(item_icon, pygame.Surface):
            if item_icon.get_width() > slot.width or item_icon.get_height() > slot.height:
                item_icon = pygame.transform.smoothscale(item_icon, (slot.width, slot.height))
            rect = item_icon.get_rect(center=slot.center)
            self.surface.blit(item_icon, rect)
        else:
            text = self.ui_layer.inventory_font.render(str(item_id)[:4], True, (255, 255, 255))
            rect = text.get_rect(center=slot.center)
            self.surface.blit(text, rect)

    def draw(self):
        self.surface.fill((0, 0, 0))
        self.surface.blit(self.scale_image, self.scale_rect)

        # Debug bounding boxes
        pygame.draw.rect(self.surface, (255, 0, 0), self.debug_left_box, 2)
        pygame.draw.rect(self.surface, (0, 0, 255), self.debug_right_box, 2)

        # ✅ Draw Back Button elements onto layout layer
        pygame.draw.rect(self.surface, (200, 50, 50), self.back_button)
        back_txt = self.button_font.render("BACK", True, (255, 255, 255))
        self.surface.blit(back_txt, self.back_button.move(20, 10))

        # Draw placed orbs
        for item, slot in self.orbs_placed:
            self.draw_placed_item(item, slot)

        # Draw placed books
        for item, slot in self.books_placed:
            self.draw_placed_item(item, slot)

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

            item_icon = self.dragging_item["icon"] if isinstance(self.dragging_item, dict) else self.dragging_item
            item_id = self.dragging_item["id"] if isinstance(self.dragging_item, dict) else str(self.dragging_item)

            if isinstance(item_icon, pygame.Surface):
                rect = item_icon.get_rect(center=(render_x, render_y))
                self.surface.blit(item_icon, rect)
            else:
                text = self.ui_layer.inventory_font.render(str(item_id), True, (255, 255, 255))
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

    # Pull from global container state so items placed remain saved across level scene transitions
    global _puzzle_instance
    if _puzzle_instance is None:
        _puzzle_instance = PuzzleScene(game_surface, player)
    else:
        # ✅ CRITICAL FIX: Refresh the player reference inside the persistent instance
        # so freshly picked items from ch1_lvl2.py display correctly in the UI bar.
        _puzzle_instance.player = player

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            # Escape key handles tracking exactly like a Back Button event
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                ch1_lvl2.run_level()
                return

            # Process structural click interaction feedback loops
            action = _puzzle_instance.handle_event(event)
            if action == "BACK":
                ch1_lvl2.run_level()
                return

        solved = _puzzle_instance.check_balance()
        _puzzle_instance.draw()

        if solved:
            pygame.time.delay(2000)
            # Reset persistent layout context upon a successful puzzle solution run
            _puzzle_instance = None
            ch1_lvl2.run_level()
            return

        clock.tick(60)