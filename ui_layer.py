import pygame
import os
import time
import sys

class UILayer:
    def __init__(self, screen):
        self.screen = screen
        self.font = pygame.font.SysFont("arial", 24, bold=True)

        # --- Health hearts setup ---
        self.max_hearts = 5
        self.hearts = self.max_hearts   # ✅ player starts with 5 hearts

        # Load health bar frames (health_01.png = empty, health_06.png = full)
        self.health_frames = []
        for i in range(1, 7):  # 1 → 6
            path = os.path.join("Assets", "Sprite", "Gameplay", f"health_{i:02}.png")
            if os.path.exists(path):
                frame = pygame.image.load(path).convert_alpha()
                self.health_frames.append(frame)
            else:
                # fallback: simple red rect
                surf = pygame.Surface((200, 40))
                surf.fill((200, 0, 0))
                self.health_frames.append(surf)

        # --- Timer bar setup ---
        asset_path = os.path.join("Assets", "health-sanity bar-timer", "timer_bar.png")
        if os.path.exists(asset_path):
            self.timer_bar = pygame.image.load(asset_path).convert_alpha()
            self.timer_rect = self.timer_bar.get_rect(midtop=(self.screen.get_width() // 2, 10))
        else:
            self.timer_bar = pygame.Surface((300, 50))
            self.timer_bar.fill((100, 100, 100))
            self.timer_rect = self.timer_bar.get_rect(midtop=(self.screen.get_width() // 2, 10))

        font_path = os.path.join("Assets", "FONT", "VCR_OSD_MONO_1.001.ttf")
        if os.path.exists(font_path):
            self.timer_font = pygame.font.Font(font_path, 36)
        else:
            self.timer_font = pygame.font.SysFont("arial", 36)

        # Timer settings
        self.countdown_seconds = 300
        self.start_time = time.time()

        # --- Insanity bar setup ---
        insanity_path = os.path.join("Assets", "Sprite", "gameplay", "insanity.png")
        self.insanity_frames = []
        self.insanity_level = 55   # ✅ start full (frame 55)
        self.dragging = False

        if os.path.exists(insanity_path):
            insanity_sheet = pygame.image.load(insanity_path).convert_alpha()
            frame_width, frame_height = 397, 90
            cols = 1985 // frame_width   # 5
            rows = 1080 // frame_height  # 12
            frame_count = 56

            for row in range(rows):
                for col in range(cols):
                    rect = pygame.Rect(col * frame_width, row * frame_height, frame_width, frame_height)
                    frame = insanity_sheet.subsurface(rect)
                    self.insanity_frames.append(frame)

            self.insanity_frames = self.insanity_frames[:frame_count]

            # ✅ Keep original size
            self.bar_width = 600
            self.bar_height = 150
            self.scale_x = self.bar_width / frame_width
            self.scale_y = self.bar_height / frame_height

            # ✅ Position: below health bar
            self.insanity_x = 20
            self.insanity_y = 80

        # --- Insanity drain settings ---
        self.last_drain = time.time()
        self.drain_rate = 1.0   # seconds per drain tick
        self.drain_amount = 1   # frames lost per tick
        self.click_penalty = 5  # frames lost per E key press

    def reset_timer(self, new_seconds=None):
        self.start_time = time.time()
        if new_seconds is not None:
            self.countdown_seconds = new_seconds

    # ---------------- HEALTH BAR ----------------
    def draw_health_bar(self):
        # Clamp hearts between 0–5
        self.hearts = max(0, min(self.hearts, self.max_hearts))
        # Pick correct frame (health_01 = empty, health_06 = full)
        frame_index = self.hearts + 1
        frame_index = min(frame_index, len(self.health_frames)) - 1
        current_frame = self.health_frames[frame_index]

        rect = current_frame.get_rect(topleft=(20, 20))
        self.screen.blit(current_frame, rect)

        # Label above health bar
        text = self.font.render(f"Health: {self.hearts}/{self.max_hearts}", True, (255, 0, 0))
        text_rect = text.get_rect(midtop=(rect.centerx, rect.top - 20))
        self.screen.blit(text, text_rect)

        return rect

    # ---------------- INSANITY BAR ----------------
    def drain_insanity(self):
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

    def draw_insanity_bar(self):
        if not self.insanity_frames:
            return None

        self.insanity_level = max(0, min(self.insanity_level, len(self.insanity_frames) - 1))
        current_frame = pygame.transform.smoothscale(
            self.insanity_frames[self.insanity_level],
            (self.bar_width, self.bar_height)
        )
        rect = current_frame.get_rect(topleft=(self.insanity_x, self.insanity_y))
        self.screen.blit(current_frame, rect)

        text = self.font.render(f"Insanity: {self.insanity_level}", True, (255, 255, 255))
        text_rect = text.get_rect(midtop=(rect.centerx, rect.top - 20))
        self.screen.blit(text, text_rect)

        return rect

    # ---------------- DRAW ALL ----------------
    def draw(self, player):
        # Health bar first
        self.draw_health_bar()

        # Inventory button
        inv_text = self.font.render("Inventory [I]", True, (255, 255, 255))
        self.screen.blit(inv_text, (20, 50))

        # Manuscripts count
        manuscripts_text = self.font.render(f"Manuscripts: {player.manuscripts_found}", True, (255, 215, 0))
        self.screen.blit(manuscripts_text, (20, 110))

        # Timer bar
        elapsed = time.time() - self.start_time
        remaining = max(0, self.countdown_seconds - int(elapsed))
        minutes, seconds = divmod(remaining, 60)
        time_str = f"{minutes:02}:{seconds:02}"

        self.screen.blit(self.timer_bar, self.timer_rect)
        timer_text = self.timer_font.render(time_str, True, (255, 255, 255))
        text_rect = timer_text.get_rect(center=self.timer_rect.center)
        text_rect.x += 17
        self.screen.blit(timer_text, text_rect)

        if remaining <= 0:
            print("Time's up! Game Over!")
            pygame.quit()
            sys.exit()

        # Insanity bar below health bar
        self.drain_insanity()
        self.draw_insanity_bar()

    # ---------------- HANDLE INPUT ----------------
    def handle_input(self, event):
        """Process mouse input for insanity bar slider."""
        bar_rect = self.draw_insanity_bar()
        if not bar_rect:
            return

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            # Example slider rect (adjust offsets if needed)
            inner_rect = pygame.Rect(
                bar_rect.left + int(50 * self.scale_x),
                bar_rect.top + int(20 * self.scale_y),
                int(100 * self.scale_x),
                int(30 * self.scale_y)
            )
            if inner_rect.collidepoint(event.pos):
                self.dragging = True
                self.update_insanity(event.pos[0], inner_rect)

        elif event.type == pygame.MOUSEBUTTONUP:
            self.dragging = False

        elif event.type == pygame.MOUSEMOTION and self.dragging:
            inner_rect = pygame.Rect(
                bar_rect.left + int(50 * self.scale_x),
                bar_rect.top + int(20 * self.scale_y),
                int(100 * self.scale_x),
                int(30 * self.scale_y)
            )
            self.update_insanity(event.pos[0], inner_rect)

    def update_insanity(self, mouse_x, inner_rect):
        """Update insanity level based on slider position."""
        relative_x = mouse_x - inner_rect.left
        percent = relative_x / inner_rect.width
        percent = max(0.0, min(1.0, percent))
        self.insanity_level = int(percent * (len(self.insanity_frames) - 1))
