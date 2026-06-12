# Model/Player.py
import pygame
import os

ROWS = 5
COLS = 5
JPG_BLACK_TOLERANCE = 25

# Default sprite paths (you can override when creating the player)
WALK_FILE = "Assets/Characters/player_walk.png"
WALK_FILE2 = "Assets/Characters/player_walk2.png"
IDLE_FILE = "Assets/Characters/player_idle.png"
IDLE_FILE2 = "Assets/Characters/player_idle2.png"


class Player(pygame.sprite.Sprite):
    def __init__(
        self,
        floor_y=None,
        x=100,
        y=None,
        scale=0.45,
        chosen_character=None,
        walk_file=WALK_FILE,
        walk_file2=WALK_FILE2,
        idle_file=IDLE_FILE,
        idle_file2=IDLE_FILE2,
        map_width=800,
    ):
        super().__init__()

        self.scale = scale
        self.map_width = map_width

        # --- Select files based on character ---
        # Adjust this condition to match how you name characters:
        # e.g. "charlie"/"blake" or "girl"/"boy"
        if chosen_character == "charlie" or chosen_character == "girl":
            sprite_walk = walk_file2
            sprite_idle = idle_file2
        else:
            sprite_walk = walk_file
            sprite_idle = idle_file

        # --- Load frames with transparency and scaling ---
        self.walk_frames = self._load_frames(sprite_walk, ROWS, COLS)
        self.idle_frames = self._load_frames(sprite_idle, ROWS, COLS)

        self.current_frames = self.idle_frames
        self.frame_index = 0
        self.image = self.current_frames[self.frame_index]

        # Position
        if y is None and floor_y is not None:
            # Place at floor level
            self.rect = self.image.get_rect(midbottom=(x, floor_y))
        else:
            self.rect = self.image.get_rect(topleft=(x, y if y is not None else 100))

        # Movement & animation
        self.walk_speed = 4
        self.run_speed = 9
        self.speed = self.walk_speed

        self.facing_right = True
        self.is_moving = False
        self.is_running = False

        self.last_update = pygame.time.get_ticks()
        self.frame_duration = 1000 // 12  # default 12 fps

        # Stats
        self.health = 100
        self.inventory = []
        self.manuscripts_found = 0
        self.puzzle_solved = False

    # ---------- SPRITE SHEET HELPERS ----------
    def _load_frames(self, filename, rows, cols):
        if not os.path.exists(filename):
            surf = pygame.Surface((32, 32))
            surf.fill((255, 0, 0))
            return [surf]

        sheet = pygame.image.load(filename).convert_alpha()

        # Apply transparency to almost-black pixels
        sheet = sheet.copy()
        width, height = sheet.get_size()
        for x in range(width):
            for y in range(height):
                r, g, b, a = sheet.get_at((x, y))
                if r < JPG_BLACK_TOLERANCE and g < JPG_BLACK_TOLERANCE and b < JPG_BLACK_TOLERANCE:
                    sheet.set_at((x, y), (r, g, b, 0))

        # Slice into frames
        w = sheet.get_width() // cols
        h = sheet.get_height() // rows
        frames = []
        for r in range(rows):
            for c in range(cols):
                frame = sheet.subsurface(pygame.Rect(c * w, r * h, w, h))
                scaled_frame = pygame.transform.scale(
                    frame,
                    (int(w * self.scale), int(h * self.scale)),
                )
                frames.append(scaled_frame)
        return frames

    # ---------- INPUT HANDLING ----------
    def handle_input(self, event):
        """Optional per-event handler, if you want explicit keydown/keyup logic."""
        if event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_LEFT, pygame.K_a):
                self.facing_right = False
                self.is_moving = True
            elif event.key in (pygame.K_RIGHT, pygame.K_d):
                self.facing_right = True
                self.is_moving = True
            elif event.key in (pygame.K_LSHIFT, pygame.K_RSHIFT):
                self.is_running = True

        elif event.type == pygame.KEYUP:
            if event.key in (pygame.K_LEFT, pygame.K_RIGHT, pygame.K_a, pygame.K_d):
                self.is_moving = False
            elif event.key in (pygame.K_LSHIFT, pygame.K_RSHIFT):
                self.is_running = False

    # ---------- FRAME-BASED LOGIC (POLLED EACH TICK) ----------
    def update_logic(self):
        keys = pygame.key.get_pressed()
        self.is_moving = False

        if keys[pygame.K_LSHIFT] or keys[pygame.K_RSHIFT]:
            self.is_running = True
            self.speed = self.run_speed
        else:
            self.is_running = False
            self.speed = self.walk_speed

        # Movement: A/D and Arrow keys
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.rect.x -= self.speed
            self.facing_right = False
            self.is_moving = True
        elif keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.rect.x += self.speed
            self.facing_right = True
            self.is_moving = True

        # Clamp horizontally
        if self.rect.left < 0:
            self.rect.left = 0
        if self.rect.right > self.map_width:
            self.rect.right = self.map_width

    def animate(self):
        now = pygame.time.get_ticks()
        target_frames = self.walk_frames if self.is_moving else self.idle_frames

        # Adjust fps based on state
        self.frame_duration = 1000 // (
            36 if self.is_running else (20 if self.is_moving else 12)
        )

        if self.current_frames != target_frames:
            self.current_frames = target_frames
            self.frame_index = 0
            self.last_update = now

        if now - self.last_update > self.frame_duration:
            self.last_update = now
            self.frame_index = (self.frame_index + 1) % len(self.current_frames)
            raw_image = self.current_frames[self.frame_index]
            self.image = (
                pygame.transform.flip(raw_image, True, False)
                if not self.facing_right
                else raw_image
            )

    def update(self):
        """Call once per frame from the level: does both logic + animation."""
        self.update_logic()
        self.animate()

    def render(self, screen):
        screen.blit(self.image, self.rect)

    # ---------- SIMPLE INVENTORY / STATS HELPERS ----------
    def add_item(self, item):
        self.inventory.append(item)

    def remove_item(self, item):
        if item in self.inventory:
            self.inventory.remove(item)

    def take_damage(self, amount):
        self.health -= amount
        print(f"Player took {amount} damage. Health: {self.health}")

    @property
    def position(self):
        return (self.rect.x, self.rect.y)
