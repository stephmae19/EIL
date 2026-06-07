# ui_layer.py
import pygame
import os
import time
import sys


class UILayer:
    def __init__(self, surface):
        self.surface = surface
        self.font = pygame.font.SysFont("arial", 24, bold=True)
        self.dragging_item = None  # Add this line

        # --- SINGLE SOURCE OF TRUTH (STATE) ---
        self.max_hearts = 5
        self.hearts = self.max_hearts
        self.insanity_level = 55
        self.countdown_seconds = 300
        self.start_time = time.time()

        # Pre-initialize rects to prevent AttributeError
        self.health_rect = pygame.Rect(20, 20, 350, 40)
        self.inventory_rect = pygame.Rect(0, 0, 0, 0)  # Placeholder

        # ADD THIS LINE TO INITIALIZE THE ATTRIBUTE
        self.health_rect = pygame.Rect(20, 20, 350, 40)

        # Default scale info (updated later by SceneManager or run_level)
        self.scale_info = {"scale": 1, "x_offset": 0, "y_offset": 0, "win_size": (1920, 1080)}

        # --- UI CONFIG ---
        self.ui_config = {
            "health": {"width": 350, "x": 20, "y": 20},
            "insanity": {"width": 350, "x": 20, "y": 80},
            "timer": {"width": 300, "x": 1750, "y": 10}
        }

        # --- Health hearts setup ---
        self.max_hearts = 5
        self.hearts = self.max_hearts
        self.health_frames = []
        for i in range(1, 7):
            path = os.path.join("Assets", "Sprite", "Gameplay", f"health_{i:02}.png")
            if os.path.exists(path):
                frame = pygame.image.load(path).convert_alpha()
                self.health_frames.append(frame)
            else:
                surf = pygame.Surface((200, 40))
                surf.fill((200, 0, 0))
                self.health_frames.append(surf)

        # --- Timer bar setup ---
        asset_path = os.path.join("Assets", "health-sanity bar-timer", "timer_bar.png")
        if os.path.exists(asset_path):
            self.timer_bar = pygame.image.load(asset_path).convert_alpha()
        else:
            self.timer_bar = pygame.Surface((300, 50))
            self.timer_bar.fill((100, 100, 100))

        tw = self.ui_config["timer"]["width"]
        th = int(self.timer_bar.get_height() * (tw / self.timer_bar.get_width()))
        self.timer_bar = pygame.transform.smoothscale(self.timer_bar, (tw, th))
        self.timer_rect = self.timer_bar.get_rect(midtop=(self.ui_config["timer"]["x"], self.ui_config["timer"]["y"]))

        # --- Timer font setup ---
        font_path = os.path.join("Assets", "Font", "VCR_OSD_MONO_1.001.ttf")
        if os.path.exists(font_path):
            self.timer_font = pygame.font.Font(font_path, 36)
        else:
            self.timer_font = pygame.font.SysFont("arial", 36)

        # --- Inventory font setup (same font, smaller size) ---
        if os.path.exists(font_path):
            self.inventory_font = pygame.font.Font(font_path, 32)
        else:
            self.inventory_font = pygame.font.SysFont("arial", 32)

        # --- Timer setup ---
        self.countdown_seconds = 300
        self.start_time = time.time()  # ✅ this fixes the AttributeError

        # --- Insanity bar setup ---
        insanity_path = os.path.join("Assets", "Sprite", "gameplay", "insanity.png")

        # --- Subtitle font setup ---
        subtitle_font_path = os.path.join("Assets", "Font", "VCR_OSD_MONO_1.001.ttf")
        if os.path.exists(subtitle_font_path):
            self.subtitle_font = pygame.font.Font(subtitle_font_path, 28)
        else:
            self.subtitle_font = pygame.font.SysFont("arial", 28)

        self.subtitle_msg = ""
        self.subtitle_timer = 0

        # ✅ Always initialize the list first
        self.insanity_frames = []
        self.insanity_level = 55
        self.dragging = False
        self.is_dragging = False

        if os.path.exists(insanity_path):
            insanity_sheet = pygame.image.load(insanity_path).convert_alpha()
            frame_width, frame_height = 397, 90
            cols = 1985 // frame_width
            rows = 1080 // frame_height
            frame_count = 56

            for row in range(rows):
                for col in range(cols):
                    rect = pygame.Rect(col * frame_width, row * frame_height, frame_width, frame_height)
                    frame = insanity_sheet.subsurface(rect)
                    self.insanity_frames.append(frame)

            self.insanity_frames = self.insanity_frames[:frame_count]

            iw = self.ui_config["insanity"]["width"]
            ih = int(frame_height * (iw / frame_width))
            self.bar_width, self.bar_height = iw, ih
            self.insanity_x = self.ui_config["insanity"]["x"]
            self.insanity_y = self.ui_config["insanity"]["y"]

        self.last_drain = time.time()
        self.drain_rate = 1.0
        self.drain_amount = 1
        self.click_penalty = 5

        # --- Inventory bar setup ---
        inventory_path = os.path.join("Assets", "Sprite", "Gameplay", "inventory.png")
        if os.path.exists(inventory_path):
            self.inventory_bar = pygame.image.load(inventory_path).convert_alpha()
        else:
            self.inventory_bar = pygame.Surface((600, 100))
            self.inventory_bar.fill((50, 50, 50))

        # Scale inventory bar to fit width of window (or custom width)
        inv_width = int(self.scale_info["win_size"][0] * 0.35)   # 60% of screen width
        inv_height = int(self.inventory_bar.get_height() * (inv_width / self.inventory_bar.get_width()))
        self.inventory_bar = pygame.transform.smoothscale(self.inventory_bar, (inv_width, inv_height))

        # Position at bottom center of screen
        self.inventory_rect = self.inventory_bar.get_rect(
            midbottom=(self.scale_info["win_size"][0] // 2, self.scale_info["win_size"][1] - 0)
        )

        # --- Inventory slot configuration ---
        self.slot_config = {
            "x": self.inventory_rect.left + 42,   # starting X position
            "y": self.inventory_rect.top + 138,    # starting Y position
            "width": 75,                         # slot width
            "height": 75,                        # slot height
            "margin": 27                          # spacing between slots
        }

        # ✅ Auto-generate 6 slots based on config
        self.inventory_slots = []
        for i in range(6):
            slot_x = self.slot_config["x"] + i * (self.slot_config["width"] + self.slot_config["margin"])
            slot_y = self.slot_config["y"]
            slot_rect = pygame.Rect(slot_x, slot_y, self.slot_config["width"], self.slot_config["height"])
            self.inventory_slots.append(slot_rect)

        # Track selected slot
        self.selected_slot = None

    def handle_inventory_drag(self, event, player, adj_mouse_pos):
        # 1. Start Dragging
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            for i, slot in enumerate(self.inventory_slots):
                # Ensure we use the scaled mouse coordinates
                if slot.collidepoint(adj_mouse_pos) and i < len(player.inventory):
                    self.dragging_item = player.inventory.pop(i)
                    self.is_dragging = True
                    break

        # 2. Release Drag (Consolidated)
        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            if getattr(self, 'is_dragging', False):
                dropped_in_slot = False
                for slot in self.inventory_slots:
                    if slot.collidepoint(adj_mouse_pos):
                        # Re-insert into inventory
                        player.inventory.append(self.dragging_item)
                        dropped_in_slot = True
                        break

                # Return it to the inventory if dropped anywhere else in the world
                if not dropped_in_slot:
                    player.inventory.append(self.dragging_item)

                self.dragging_item = None
                self.is_dragging = False

    def draw_dragged_item(self, mouse_pos):
        if self.dragging_item and isinstance(self.dragging_item, dict):
            icon = self.dragging_item.get("icon")
            if icon:
                # Scale the orb to 80x80 as requested
                drag_img = pygame.transform.scale(icon, (80, 80))
                # Center the 80x80 image on the cursor (offset by 40)
                self.surface.blit(drag_img, (mouse_pos[0] - 40, mouse_pos[1] - 40))

    def set_scale_info(self, scale_info):
        """Update scale info from SceneManager so UI adapts to window size."""
        self.scale_info = scale_info

    def reset_timer(self, new_seconds=None):
        self.start_time = time.time()
        if new_seconds is not None:
            self.countdown_seconds = new_seconds

    # ---------------- HEALTH BAR ----------------
    def draw_health_bar(self):
        self.hearts = max(0, min(self.hearts, self.max_hearts))
        frame_index = min(self.hearts + 1, len(self.health_frames)) - 1
        current_frame = self.health_frames[frame_index]

        hw = self.ui_config["health"]["width"]
        hh = int(current_frame.get_height() * (hw / current_frame.get_width()))
        current_frame = pygame.transform.smoothscale(current_frame, (hw, hh))

        rect = current_frame.get_rect(topleft=(self.ui_config["health"]["x"], self.ui_config["health"]["y"]))
        self.surface.blit(current_frame, rect)

        # ✅ Store rect so we can position insanity bar with padding
        self.health_rect = rect
        return rect

    # ---------------- INSANITY BAR ----------------
    def drain_insanity(self):
        # If we are currently dragging an item, do not drain insanity
        if self.dragging_item is not None:
            return

        now = time.time()
        if now - self.last_drain >= self.drain_rate:
            self.insanity_level -= self.drain_amount
            self.last_drain = now
            self.check_insanity()

    def click_insanity_loss(self):
        self.insanity_level -= self.click_penalty
        self.check_insanity()

    def check_insanity(self):
        if self.insanity_level <= 0:
            self.hearts -= 1
            if self.hearts > 0:
                self.insanity_level = len(self.insanity_frames) - 1
            else:
                print("Game Over!")
                pygame.quit()
                sys.exit()

    def draw_insanity_bar(self, padding=10):
        if not self.insanity_frames:
            return None

        self.insanity_level = max(0, min(self.insanity_level, len(self.insanity_frames) - 1))
        current_frame = pygame.transform.smoothscale(
            self.insanity_frames[self.insanity_level],
            (self.bar_width, self.bar_height)
        )

        # ✅ Position insanity bar below health bar with padding
        x = self.ui_config["insanity"]["x"]
        y = self.health_rect.bottom + padding
        rect = current_frame.get_rect(topleft=(x, y))
        self.surface.blit(current_frame, rect)
        return rect

    # ---------------- INVENTORY BAR ----------------
    def draw_inventory_bar(self, player):
        # Draw the inventory bar background
        self.surface.blit(self.inventory_bar, self.inventory_rect)

        # Draw each slot outline + item
        for i, slot in enumerate(self.inventory_slots):
            if self.selected_slot == i:
                highlight = pygame.Surface((slot.width, slot.height), pygame.SRCALPHA)
                highlight.fill((255, 255, 0, 80))  # semi-transparent yellow
                self.surface.blit(highlight, slot)
                pygame.draw.rect(self.surface, (255, 255, 0), slot, 3)

            # ✅ Unpack the new dictionary structure safely
            if i < len(player.inventory):
                item_data = player.inventory[i]

                # Extract icon and item ID values
                item_icon = item_data["icon"] if isinstance(item_data, dict) else item_data
                item_id = item_data["id"] if isinstance(item_data, dict) else str(item_data)

                if isinstance(item_icon, pygame.Surface):
                    # ✅ Draw image surfaces directly
                    item_rect = item_icon.get_rect(center=slot.center)
                    self.surface.blit(item_icon, item_rect)
                else:
                    # ✅ Fallback: render text for non-image items
                    letter_text = self.inventory_font.render(str(item_id), True, (255, 255, 255))
                    letter_rect = letter_text.get_rect(center=slot.center)
                    self.surface.blit(letter_text, letter_rect)

        return self.inventory_rect

    # ---------------- SUBTITLES ----------------
    def show_subtitle(self, message, duration=2000):
        """Set a subtitle message with a timer (ms)."""
        self.subtitle_msg = message
        self.subtitle_timer = pygame.time.get_ticks() + duration

    def wrap_text(self, text, font, max_width):
        """Split text into wrapped lines that fit within max_width."""
        words = text.split(' ')
        lines = []
        current_line = ""

        for word in words:
            test_line = current_line + word + " "
            if font.size(test_line)[0] <= max_width:
                current_line = test_line
            else:
                lines.append(current_line.strip())
                current_line = word + " "
        if current_line:
            lines.append(current_line.strip())

        return lines

    def draw_subtitle(self):
        """Render wrapped subtitle text above inventory bar, max width 500px."""
        now = pygame.time.get_ticks()
        if now < self.subtitle_timer and self.subtitle_msg:
            # Wrap text into multiple lines
            lines = self.wrap_text(self.subtitle_msg, self.subtitle_font, 1300)

            # Draw each line stacked above inventory bar
            y_offset = self.inventory_rect.top - 10
            for line in reversed(lines):  # last line closest to bar
                msg_surface = self.subtitle_font.render(line, True, (255, 255, 255))
                msg_rect = msg_surface.get_rect(midbottom=(self.inventory_rect.centerx, y_offset))
                self.surface.blit(msg_surface, msg_rect)
                y_offset -= msg_surface.get_height() + 5

    # ---------------- DRAW ALL ----------------
    def draw(self, player):
        self.draw_health_bar()

        manuscripts_text = self.font.render(f"Manuscripts: {player.manuscripts_found}", True, (255, 215, 0))
        self.surface.blit(manuscripts_text, (20, 110))

        elapsed = time.time() - self.start_time
        remaining = max(0, self.countdown_seconds - int(elapsed))
        minutes, seconds = divmod(remaining, 60)
        time_str = f"{minutes:02}:{seconds:02}"

        self.surface.blit(self.timer_bar, self.timer_rect)
        timer_text = self.timer_font.render(time_str, True, (255, 255, 255))
        text_rect = timer_text.get_rect(center=self.timer_rect.center)
        text_rect.x += 17
        self.surface.blit(timer_text, text_rect)

        if remaining <= 0:
            print("Time's up! Game Over!")
            pygame.quit()
            sys.exit()

        self.drain_insanity()
        self.draw_insanity_bar()

        # ✅ Draw inventory bar
        self.draw_inventory_bar(player)

        # ✅ Draw subtitles last so they overlay cleanly
        self.draw_subtitle()
    # ---------------- HANDLE INPUT ----------------
    def handle_input(self, event):
        # --- Insanity bar input ---
        bar_rect = self.draw_insanity_bar()
        if bar_rect:
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                inner_rect = pygame.Rect(
                    bar_rect.left + int(50 * (self.bar_width / 397)),
                    bar_rect.top + int(20 * (self.bar_height / 90)),
                    int(100 * (self.bar_width / 397)),
                    int(30 * (self.bar_height / 90))
                )
                if inner_rect.collidepoint(event.pos):
                    self.dragging = True
                    self.update_insanity(event.pos[0], inner_rect)
            elif event.type == pygame.MOUSEBUTTONUP:
                self.is_dragging = False
            elif event.type == pygame.MOUSEMOTION and self.dragging:
                inner_rect = pygame.Rect(
                    bar_rect.left + int(50 * (self.bar_width / 397)),
                    bar_rect.top + int(20 * (self.bar_height / 90)),
                    int(100 * (self.bar_width / 397)),
                    int(30 * (self.bar_height / 90))
                )
                self.update_insanity(event.pos[0], inner_rect)

        # --- Inventory slot input ---
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            for i, slot in enumerate(self.inventory_slots):
                if slot.collidepoint(event.pos):
                    self.selected_slot = i
                    break

    def update_insanity(self, mouse_x, inner_rect):
        relative_x = mouse_x - inner_rect.left
        percent = relative_x / inner_rect.width
        percent = max(0.0, min(1.0, percent))
        self.insanity_level = int(percent * (len(self.insanity_frames) - 1))
