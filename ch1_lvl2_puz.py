# ch1_lvl2_puz.py
import pygame
import sys
import os
from ui_layer import UILayer

# ❌ REMOVED: import ch1_lvl2 to break circular execution loops

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

# --- Persistent Puzzle State Instance ---
_puzzle_instance = None
_puzzle_completed = False  # ✅ Add this persistent flag


class PuzzleScene:
    def __init__(self, surface, player, ui_layer):
        self.surface = surface
        self.player = player
        self.ui_layer = ui_layer

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

        # =============================================================
        # ⚙️ POSITION CONFIGURATIONS FOR ACTIVE AREAS
        # =============================================================
        # 1. Balanced State Offsets (scale_bal.png)
        self.BAL_LEFT_X = 10
        self.BAL_RIGHT_X = -168
        self.BAL_Y = -10

        # 2. Left Tilted State Offsets (scale_left.png)
        self.LEFT_TILT_LEFT_X = 10      # Left side horizontal shift
        self.LEFT_TILT_LEFT_Y = 40      # 💡 MANUALLY ADJUST THIS: Shifts the Left box up/down when tilted left
        self.LEFT_TILT_RIGHT_X = -168   # Right side horizontal shift
        self.LEFT_TILT_RIGHT_Y = -10    # 💡 MANUALLY ADJUST THIS: Shifts the Right box up/down when tilted left

        # 3. Right Tilted State Offsets (scale_right.png)
        self.RIGHT_TILT_LEFT_X = 10     # Left side horizontal shift
        self.RIGHT_TILT_LEFT_Y = -10    # 💡 MANUALLY ADJUST THIS: Shifts the Left box up/down when tilted right
        self.RIGHT_TILT_RIGHT_X = -168  # Right side horizontal shift
        self.RIGHT_TILT_RIGHT_Y = 40    # 💡 MANUALLY ADJUST THIS: Shifts the Right box up/down when tilted right
        # =============================================================

        # Initialize base hitboxes
        self.recalculate_hitboxes(self.BAL_LEFT_X, self.BAL_RIGHT_X, self.BAL_Y, self.BAL_Y)

        # Track placed items
        self.orbs_placed = []
        self.books_placed = []

        # Dragging states
        self.dragging_item = None
        self.dragged_item_index = None
        self.drag_source = None  # Track state origins: "INVENTORY", "ORBS", or "BOOKS"
        self.drag_offset_x = 0
        self.drag_offset_y = 0

        # ✅ UPDATED: Setting the correct imposter IDs tracking back to level interactive inventory items
        self.imposter_orb = "ORB_VIOLET"
        self.imposter_book = "BOOK_BROWN"

        self.message = ""
        self.last_checked_message = ""  # Track state to prevent resetting the 3-second timer constantly

    def recalculate_hitboxes(self, left_x, right_x, left_y, right_y):
        """Helper to re-anchor active area bounds and item slots smoothly on demand."""
        self.debug_left_box = pygame.Rect(self.scale_rect.left + left_x,
                                          self.scale_rect.centery + left_y, 150, 50)
        self.debug_right_box = pygame.Rect(self.scale_rect.right + right_x,
                                           self.scale_rect.centery + right_y, 150, 50)

        # Automatically re-calculate internal slots relative to the modified hitboxes
        self.orb_slots = [
            pygame.Rect(self.debug_left_box.left + 10 + i * 45, self.debug_left_box.centery - 20, 40, 40)
            for i in range(3)
        ]

        self.book_slots = [
            pygame.Rect(self.debug_right_box.left + 10 + i * 45, self.debug_right_box.centery - 20, 40, 40)
            for i in range(3)
        ]

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

            # 1. Try to pick up an item directly from the inventory bar
            for i, slot in enumerate(self.ui_layer.inventory_slots):
                if slot.collidepoint(virtual_pos) and i < len(self.player.inventory):
                    self.dragging_item = self.player.inventory[i]
                    self.dragged_item_index = i
                    self.drag_source = "INVENTORY"
                    self.ui_layer.selected_slot = i

                    self.drag_offset_x = virtual_pos[0] - slot.centerx
                    self.drag_offset_y = virtual_pos[1] - slot.centery
                    return None

            # 2. Allow picking up items already dropped onto the LEFT orb plate
            for i, (item, _) in enumerate(self.orbs_placed):
                if i < len(self.orb_slots) and self.orb_slots[i].collidepoint(virtual_pos):
                    self.dragging_item = item
                    self.dragged_item_index = i
                    self.drag_source = "ORBS"
                    self.drag_offset_x = virtual_pos[0] - self.orb_slots[i].centerx
                    self.drag_offset_y = virtual_pos[1] - self.orb_slots[i].centery
                    self.orbs_placed.pop(i)
                    return None

            # 3. Allow picking up items already dropped onto the RIGHT book plate
            for i, (item, _) in enumerate(self.books_placed):
                if i < len(self.book_slots) and self.book_slots[i].collidepoint(virtual_pos):
                    self.dragging_item = item
                    self.dragged_item_index = i
                    self.drag_source = "BOOKS"
                    self.drag_offset_x = virtual_pos[0] - self.book_slots[i].centerx
                    self.drag_offset_y = virtual_pos[1] - self.book_slots[i].centery
                    self.books_placed.pop(i)
                    return None

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
                        if len(self.orbs_placed) < 3:
                            self.orbs_placed.append((self.dragging_item, None))
                            placed = True
                        else:
                            self.message = "The orb plate is completely full!"
                    else:
                        self.message = "Only round orbs fit on the left plate!"

                # 2. Check if dropped over the RIGHT area (Scale's Book Side)
                elif self.debug_right_box.collidepoint(virtual_pos) or any(
                        slot.collidepoint(virtual_pos) for slot in self.book_slots):
                    if "BOOK" in item_id:
                        if len(self.books_placed) < 3:
                            self.books_placed.append((self.dragging_item, None))
                            placed = True
                        else:
                            self.message = "The book plate is completely full!"
                    else:
                        self.message = "Only books belong on the right plate!"

                # Resolution of states to completely block items duplicating
                if placed:
                    # Successfully transferred from inventory to plate layout slot
                    if self.drag_source == "INVENTORY" and self.dragged_item_index is not None:
                        self.player.inventory.pop(self.dragged_item_index)
                    self.message = ""
                else:
                    # Item was dropped in open space: return safely back inside user inventory bar
                    if self.drag_source == "INVENTORY":
                        pass
                    else:
                        self.player.inventory.append(self.dragging_item)
                        self.message = "Returned item back into your inventory bar."

                # ✅ Trigger the 3-second UI subtitle timer on dropping/returning an item
                if self.message:
                    self.ui_layer.show_subtitle(self.message, duration=3000)

                # Reset drag properties cleanly
                self.dragging_item = None
                self.dragged_item_index = None
                self.drag_source = None
                self.ui_layer.selected_slot = None
        return None

    def check_balance(self):
        new_msg = ""
        is_balanced = False

        if len(self.orbs_placed) == 3 and len(self.books_placed) == 3:
            orb_names = [o[0]["id"] if isinstance(o[0], dict) else str(o[0]) for o in self.orbs_placed]
            book_names = [b[0]["id"] if isinstance(b[0], dict) else str(b[0]) for b in self.books_placed]

            if self.imposter_orb in orb_names or self.imposter_book in book_names:
                new_msg = "The scale refuses to balance..."
                if self.imposter_orb in orb_names:
                    self.scale_image = self.scale_left
                    self.recalculate_hitboxes(self.LEFT_TILT_LEFT_X, self.LEFT_TILT_RIGHT_X, self.LEFT_TILT_LEFT_Y, self.LEFT_TILT_RIGHT_Y)
                else:
                    self.scale_image = self.scale_right
                    self.recalculate_hitboxes(self.RIGHT_TILT_LEFT_X, self.RIGHT_TILT_RIGHT_X, self.RIGHT_TILT_LEFT_Y, self.RIGHT_TILT_RIGHT_Y)
            else:
                new_msg = "The scale balances perfectly!"
                self.scale_image = self.scale_bal
                self.recalculate_hitboxes(self.BAL_LEFT_X, self.BAL_RIGHT_X, self.BAL_Y, self.BAL_Y)
                is_balanced = True
        else:
            if len(self.orbs_placed) > len(self.books_placed):
                self.scale_image = self.scale_left
                self.recalculate_hitboxes(self.LEFT_TILT_LEFT_X, self.LEFT_TILT_RIGHT_X, self.LEFT_TILT_LEFT_Y, self.LEFT_TILT_RIGHT_Y)
            elif len(self.books_placed) > len(self.orbs_placed):
                self.scale_image = self.scale_right
                self.recalculate_hitboxes(self.RIGHT_TILT_LEFT_X, self.RIGHT_TILT_RIGHT_X, self.RIGHT_TILT_LEFT_Y, self.RIGHT_TILT_RIGHT_Y)
            else:
                self.scale_image = self.scale_bal
                self.recalculate_hitboxes(self.BAL_LEFT_X, self.BAL_RIGHT_X, self.BAL_Y, self.BAL_Y)

        # ✅ Only trigger subtitle update if the balancing state message actually changed
        if new_msg != self.last_checked_message:
            self.last_checked_message = new_msg
            self.message = new_msg
            if self.message:
                self.ui_layer.show_subtitle(self.message, duration=3000)

        return is_balanced

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

        # Draw placed orbs into their adaptive slots
        for i, (item, _) in enumerate(self.orbs_placed):
            if i < len(self.orb_slots):
                self.draw_placed_item(item, self.orb_slots[i])

        # Draw placed books into their adaptive slots
        for i, (item, _) in enumerate(self.books_placed):
            if i < len(self.book_slots):
                self.draw_placed_item(item, self.book_slots[i])

        # Draw UI layer updates
        self.ui_layer.draw(self.player)

        # ✅ Render subtitle using its internal timer ticks safely
        self.ui_layer.draw_subtitle()

        # Clear external tracking variable if UILayer internally finishes displaying it
        if not getattr(self.ui_layer, 'subtitle_text', None):
            self.message = ""

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


def run_puzzle(game_surface, player, ui_layer):
    clock = pygame.time.Clock()
    global _puzzle_instance, _puzzle_completed # Access the flags

    if _puzzle_instance is None:
        _puzzle_instance = PuzzleScene(game_surface, player, ui_layer)
    else:
        _puzzle_instance.player = player
        _puzzle_instance.ui_layer = ui_layer

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            # Escape key handles tracking exactly like a Back Button event
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                # ✅ FIX: Just return to drop out of this scene loop cleanly!
                return

            # Process structural click interaction feedback loops
            action = _puzzle_instance.handle_event(event)
            if action == "BACK":
                # ✅ FIX: Just return to drop out of this scene loop cleanly!
                return

        solved = _puzzle_instance.check_balance()
        _puzzle_instance.draw()

        if solved:
            _puzzle_completed = True  # ✅ Mark as solved
            pygame.time.delay(1000)
            _puzzle_instance = None  # Reset instance
            return  # Exit to main loop

        clock.tick(60)


def get_placed_item_ids():
    """Returns a combined list of item IDs currently situated on the plates."""
    global _puzzle_instance
    if _puzzle_instance is None:
        return []
    ids = []
    for item, _ in _puzzle_instance.orbs_placed:
        ids.append(item["id"] if isinstance(item, dict) else str(item))
    for item, _ in _puzzle_instance.books_placed:
        ids.append(item["id"] if isinstance(item, dict) else str(item))
    return ids

# --- Ensure this logic is in ch1_lvl2_puz.py ---
def is_puzzle_solved():
    """Returns the persistent completion status."""
    global _puzzle_completed
    return _puzzle_completed