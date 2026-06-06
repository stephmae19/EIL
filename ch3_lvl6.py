# ch3_lvl6.py
import pygame
import sys
import os
from ui_layer import UILayer

# --- Filenames ---
WALK_FILE = "Assets/CHARACTERS/player_walk.png"
WALK2_FILE = "Assets/CHARACTERS/player_walk2.png"
IDLE_FILE = "Assets/CHARACTERS/player_idle.png"
BG_FILE = "Assets/MAPS/chapter3/ch3_lvl6.jpg"
MANUSCRIPT_FILE = "Assets/OBJECTS-ITEMS/manuscript.png"

# --- Config ---
FLOOR_HEIGHT_PERCENTAGE = 0.74
JPG_BLACK_TOLERANCE = 25


class Camera:
    def __init__(self, width, height, screen_w, screen_h):
        self.camera = pygame.Rect(0, 0, width, height)
        self.width = width
        self.height = height
        self.screen_w = screen_w
        self.screen_h = screen_h
        self.health = 100  # starting health value

    def apply(self, entity):
        return entity.rect.move(self.camera.topleft)

    def apply_rect(self, rect):
        return rect.move(self.camera.topleft)

    def update(self, target):
        x = -target.rect.centerx + int(self.screen_w / 2)
        y = 0
        x = min(0, x)
        x = max(-(self.width - self.screen_w), x)
        self.camera = pygame.Rect(x, y, self.width, self.height)


class InteractiveObject:
    def __init__(self, x, y, width=150, height=250,
                 has_manuscript=False, inventory_item=None,
                 prompt="Press 'E' to interact", image_file=None):
        self.rect = pygame.Rect(x, y, width, height)
        self.has_manuscript = has_manuscript
        self.inventory_item = inventory_item
        self.already_searched = False
        self.prompt = prompt

        # ✅ Load image if provided
        self.image = None
        if image_file and os.path.exists(image_file):
            raw = pygame.image.load(image_file).convert_alpha()
            self.image = pygame.transform.scale(raw, (width, height))

    def resize(self, new_width, new_height):
        """Resize the interactive object rectangle."""
        self.rect.width = new_width
        self.rect.height = new_height

    def move(self, new_x, new_y):
        """Move the interactive object to a new position."""
        self.rect.x = new_x
        self.rect.y = new_y


class Player(pygame.sprite.Sprite):
    def __init__(self, floor_y, x=400, y=None, scale=0.45):
        super().__init__()
        self.scale = scale  # ✅ adjustable scale factor

        # Load frames with transparency and scaling
        self.walk_frames = self.load_frames(WALK_FILE, 5, 5)
        self.idle_frames = self.load_frames(IDLE_FILE, 5, 5)

        self.current_frames = self.idle_frames
        self.frame_index = 0
        self.image = self.current_frames[self.frame_index]

        # ✅ adjustable position
        if y is None:
            # Default: place at floor level
            self.rect = self.image.get_rect(midbottom=(x, floor_y))
        else:
            self.rect = self.image.get_rect(topleft=(x, y))

        self.walk_speed = 4
        self.run_speed = 9
        self.speed = self.walk_speed

        self.facing_right = True
        self.is_moving = False
        self.is_running = False

        self.manuscripts_found = 0
        self.puzzle_solved = False

        self.health = 100

        self.last_update = pygame.time.get_ticks()
        self.frame_duration = 1000 // 12

        self.inventory = []

    def load_frames(self, filename, rows, cols):
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
        w, h = sheet.get_width() // cols, sheet.get_height() // rows
        frames = []
        for r in range(rows):
            for c in range(cols):
                frame = sheet.subsurface(pygame.Rect(c * w, r * h, w, h))
                # ✅ use scale factor
                scaled_frame = pygame.transform.scale(frame, (int(w * self.scale), int(h * self.scale)))
                frames.append(scaled_frame)
        return frames

    def update_logic(self, map_width):
        keys = pygame.key.get_pressed()
        self.is_moving = False
        self.is_running = False

        if keys[pygame.K_LSHIFT] or keys[pygame.K_RSHIFT]:
            self.is_running = True
            self.speed = self.run_speed
        else:
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

        if self.rect.left < 0:
            self.rect.left = 0
        if self.rect.right > map_width:
            self.rect.right = map_width

    def animate(self):
        now = pygame.time.get_ticks()
        target_frames = self.walk_frames if self.is_moving else self.idle_frames
        self.frame_duration = 1000 // (36 if self.is_running else (20 if self.is_moving else 12))

        if self.current_frames != target_frames:
            self.current_frames = target_frames
            self.frame_index = 0
            self.last_update = now

        if now - self.last_update > self.frame_duration:
            self.last_update = now
            self.frame_index = (self.frame_index + 1) % len(self.current_frames)
            raw_image = self.current_frames[self.frame_index]
            self.image = pygame.transform.flip(raw_image, True, False) if not self.facing_right else raw_image

    def update(self, map_width):
        self.update_logic(map_width)
        self.animate()


# --- Initialization ---
pygame.init()
pygame.font.init()

# --- Base Resolution (Design Target) ---
BASE_WIDTH, BASE_HEIGHT = 1920, 1080

# --- Display Setup ---
info = pygame.display.Info()
native_width, native_height = info.current_w, info.current_h
os.environ['SDL_VIDEO_CENTERED'] = '1'

# Start with resizable window
screen = pygame.display.set_mode((native_width, native_height - 50), pygame.RESIZABLE)
pygame.display.set_caption("Chapter 1 - Level 1")

# Internal fixed surface (always BASE_WIDTH x BASE_HEIGHT)
game_surface = pygame.Surface((BASE_WIDTH, BASE_HEIGHT))

clock = pygame.time.Clock()

ui_font = pygame.font.SysFont("arial", 28, bold=True)
feedback_font = pygame.font.SysFont("arial", 24, italic=True)

# Background
if not os.path.exists(BG_FILE):
    bg_image = pygame.Surface((BASE_WIDTH * 2, BASE_HEIGHT))
    bg_image.fill((50, 50, 80))
else:
    original_bg = pygame.image.load(BG_FILE).convert()
    scale_factor = BASE_HEIGHT / original_bg.get_height()
    new_bg_width = int(original_bg.get_width() * scale_factor)
    bg_image = pygame.transform.scale(original_bg, (new_bg_width, BASE_HEIGHT))

MAP_WIDTH, MAP_HEIGHT = bg_image.get_width(), bg_image.get_height()
floor_y = int(MAP_HEIGHT * FLOOR_HEIGHT_PERCENTAGE)

# --- Scaling ratios based on design resolution ---
DESIGN_WIDTH = 1920
DESIGN_HEIGHT = 1080

# Use BASE_WIDTH/BASE_HEIGHT instead of SCREEN_WIDTH/SCREEN_HEIGHT
scale_x = BASE_WIDTH / DESIGN_WIDTH
scale_y = BASE_HEIGHT / DESIGN_HEIGHT

# Player-style scaling factor
scale_factor = BASE_HEIGHT / DESIGN_HEIGHT

# --- Adaptive Interactive Objects (player-style scaling) ---
interactive_objects = [
    InteractiveObject(
        x=int(180 * scale_factor),
        y=int(floor_y - int(140 * scale_factor)),
        width=int(5 * scale_factor),
        height=int(40 * scale_factor),
        has_manuscript=False,
        inventory_item="H",
        prompt="I found a letter H."
    ),
    InteractiveObject(
        x=int(490 * scale_factor),
        y=int(floor_y - int(200 * scale_factor)),
        width=int(5 * scale_factor),
        height=int(40 * scale_factor),
        has_manuscript=False,
        inventory_item="L",
        prompt="I found a letter L."
    ),
    InteractiveObject(
        x=int(560 * scale_factor),
        y=int(floor_y - int(200 * scale_factor)),
        width=int(5 * scale_factor),
        height=int(40 * scale_factor),
        has_manuscript=False,
        inventory_item="E",
        prompt="I found a letter E."
    ),
    InteractiveObject(
        x=int(1000 * scale_factor),
        y=int(floor_y - int(200 * scale_factor)),
        width=int(5 * scale_factor),
        height=int(40 * scale_factor),
        has_manuscript=False,
        inventory_item="K",
        prompt="I found a letter K."
    ),
    InteractiveObject(
        x=int(1100 * scale_factor),
        y=int(floor_y - int(200 * scale_factor)),
        width=int(5 * scale_factor),
        height=int(40 * scale_factor),
        has_manuscript=False,
        inventory_item="M",
        prompt="I found a letter M."
    ),
    InteractiveObject(
        x=int(1250 * scale_factor),
        y=int(floor_y - int(120 * scale_factor)),
        width=int(5 * scale_factor),
        height=int(40 * scale_factor),
        has_manuscript=False,
        inventory_item="C",
        prompt="I found a letter C."
    ),
    InteractiveObject(
        x=int(1500 * scale_factor),
        y=int(floor_y - int(100 * scale_factor)),
        width=int(5 * scale_factor),
        height=int(40 * scale_factor),
        has_manuscript=False,
        inventory_item="O",
        prompt="Oh, there's something on the floor. I found a letter O."
    ),
]

interactive_objects.append(
    InteractiveObject(
        x=int(MAP_WIDTH * 0.845),  # right side
        y=int(floor_y - int(BASE_HEIGHT * 0.20)),  # center vertically above floor
        width=int(80 * scale_factor),
        height=int(80 * scale_factor),
        has_manuscript=True,
        prompt="A mysterious manuscript lies here...",
        image_file=MANUSCRIPT_FILE
    )
)

# --- Adaptive Player Initialization ---
player = Player(
    floor_y,
    x=int(BASE_WIDTH * 0.10),
    y=int(BASE_HEIGHT * 0.53),
    scale=(BASE_HEIGHT / 1080) * 1.2   # adaptive + manual multiplier
)

camera = Camera(MAP_WIDTH, MAP_HEIGHT, BASE_WIDTH, BASE_HEIGHT)

# ✅ UI Layer
ui_layer = UILayer(game_surface)

feedback_msg = ""
feedback_timer = 0

feedback_msg = ""
feedback_timer = 0

# --- Main Loop wrapped in a function ---
def run_level():
    global feedback_msg, feedback_timer  # keep these accessible
    clock = pygame.time.Clock()

    while True:
        now = pygame.time.get_ticks()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                # ✅ Instead of quitting the whole program, return control to ChapterSelect
                return
            if event.type == pygame.KEYDOWN and event.key == pygame.K_e:
                found = False
                for obj in interactive_objects:
                    if player.rect.colliderect(obj.rect):
                        found = True

                        # --- Manuscript object ---
                        if obj.has_manuscript:
                            if player.puzzle_solved:
                                # ✅ Puzzle already solved, don’t allow re-entry
                                feedback_msg = "You already searched this part."
                                feedback_timer = now + 2000
                            else:
                                if not obj.already_searched:
                                    obj.already_searched = True
                                    feedback_msg = "You found a hidden manuscript!"
                                    feedback_timer = now + 3000
                                else:
                                    feedback_msg = "You examine the manuscript again..."
                                    feedback_timer = now + 2000

                                # Route to puzzle only if not solved yet
                                import ch1_lvl1_puz
                                ch1_lvl1_puz.run_puzzle(player, ui_layer)
                            break

                        # --- Inventory items ---
                        elif obj.inventory_item:
                            if not obj.already_searched:
                                if len(player.inventory) < 6:
                                    # ✅ Successfully pick up item
                                    player.inventory.append(obj.inventory_item)
                                    obj.already_searched = True
                                    feedback_msg = f"You picked up {obj.inventory_item}!"
                                else:
                                    # ✅ Inventory full, but item not yet picked up
                                    feedback_msg = "My inventory is full."
                                feedback_timer = now + 2000
                            else:
                                # ✅ Item was already picked up before
                                feedback_msg = "You already picked this up."
                                feedback_timer = now + 2000

                        # --- Other prompts ---
                        else:
                            if not obj.already_searched:
                                obj.already_searched = True
                                feedback_msg = obj.prompt
                                feedback_timer = now + 2000
                            else:
                                feedback_msg = "You already searched this part."
                                feedback_timer = now + 2000
                        break
                if not found:
                    feedback_msg = "There is nothing to interact with here."
                    feedback_timer = now + 1500

                # ✅ UI input handling
                ui_layer.handle_input(event)
                ui_layer.click_insanity_loss()

        # Update
        player.update(MAP_WIDTH)
        camera.update(player)

        # --- Render everything to internal surface ---
        game_surface.fill((0, 0, 0))
        game_surface.blit(bg_image, (camera.camera.x, camera.camera.y))

        # DEBUG + object rendering
        for obj in interactive_objects:
            pygame.draw.rect(game_surface, (0, 255, 0), camera.apply_rect(obj.rect), 2)

            # ✅ Render object image if available
            if obj.image:
                game_surface.blit(obj.image, camera.apply_rect(obj.rect))

            # Show prompt when player collides
            if player.rect.colliderect(obj.rect):
                prompt_text = ui_font.render(obj.prompt, True, (255, 255, 255))
                prompt_rect = prompt_text.get_rect(midbottom=(obj.rect.centerx, obj.rect.top - 20))
                game_surface.blit(prompt_text, camera.apply_rect(prompt_rect))

        # Draw player
        game_surface.blit(player.image, camera.apply(player))

        # Manuscripts UI text
        ui_text = ui_font.render(f"Manuscripts: {player.manuscripts_found} / 2", True, (255, 215, 0))
        game_surface.blit(ui_text, (BASE_WIDTH - 280, 20))

        # Feedback message
        if now < feedback_timer:
            msg_surface = feedback_font.render(feedback_msg, True, (150, 255, 150))

            # --- Adaptive horizontal offset ---
            # Positive values push right, negative push left
            SUBTITLE_OFFSET_X = 0  # adjust this value to move horizontally
            SUBTITLE_OFFSET_Y = 280  # vertical offset from bottom

            msg_rect = msg_surface.get_rect(
                center=(
                    BASE_WIDTH // 2 + int(SUBTITLE_OFFSET_X * scale_x),
                    BASE_HEIGHT - int(SUBTITLE_OFFSET_Y * scale_y)
                )
            )
            game_surface.blit(msg_surface, msg_rect)

        # ✅ Draw UI overlay last
        ui_layer.draw(player)

        # --- Scale & Blit to window with aspect ratio preserved ---
        window_width, window_height = screen.get_size()
        scale = min(window_width / BASE_WIDTH, window_height / BASE_HEIGHT)
        scaled_w, scaled_h = int(BASE_WIDTH * scale), int(BASE_HEIGHT * scale)

        scaled_surface = pygame.transform.smoothscale(game_surface, (scaled_w, scaled_h))

        x_offset = (window_width - scaled_w) // 2
        y_offset = (window_height - scaled_h) // 2

        screen.fill((0, 0, 0))  # black padding
        screen.blit(scaled_surface, (x_offset, y_offset))

        pygame.display.flip()
        clock.tick(60)

# ✅ Allow standalone execution
if __name__ == "__main__":
    run_level()