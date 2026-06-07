# ch1_lvl3.py
import pygame
import sys
import os
from ui_layer import UILayer

# --- Filenames ---
WALK_FILE = "Assets/CHARACTERS/player_walk.png"
WALK2_FILE = "Assets/CHARACTERS/player_walk2.png"
IDLE_FILE = "Assets/CHARACTERS/player_idle.png"
BG_FILE = "Assets/MAPS/chapter1/ch1_lvl3.png"
MANUSCRIPT_FILE = "Assets/OBJECTS-ITEMS/manuscript.png"
ORB_GLOW_BLUE = "Assets/MAPS/chapter1/orb_glow_blue.png"

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
                 prompt="Press 'E' to interact", image_file=None, is_glowing=False,
                 is_repeatable=False): # Add this parameter
        self.rect = pygame.Rect(x, y, width, height)
        self.has_manuscript = has_manuscript
        self.inventory_item = inventory_item
        self.already_searched = False
        self.prompt = prompt
        self.is_glowing = is_glowing
        self.is_repeatable = is_repeatable # Store it

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
pygame.display.set_caption("Chapter 1 - Level 3")

# Internal fixed surface (always BASE_WIDTH x BASE_HEIGHT)
game_surface = pygame.Surface((BASE_WIDTH, BASE_HEIGHT))

clock = pygame.time.Clock()

# --- Fonts ---
ui_font = pygame.font.SysFont("arial", 28, bold=True)
feedback_font = pygame.font.SysFont("arial", 24, italic=True)

# ✅ Load your specific custom font
CUSTOM_FONT_PATH = "Assets/FONT/VCR_OSD_MONO_1.001.ttf"
h_font = pygame.font.Font(CUSTOM_FONT_PATH, 50) # Set size to 50 for visibility

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
        width=int(50 * scale_factor), # Adjusted width for visibility
        height=int(80 * scale_factor),
        has_manuscript=False,
        inventory_item="H",
        prompt="I found a letter H.",
        is_glowing=True # Enable glow
    ),
    InteractiveObject(
        x=int(680 * scale_factor),
        y=int(floor_y - int(270 * scale_factor)),
        width=int(80 * scale_factor),
        height=int(80 * scale_factor),
        has_manuscript=False,
        inventory_item="ORB_BLUE",
        prompt="A glowing blue orb.",
        image_file=ORB_GLOW_BLUE
    ),
    InteractiveObject(
        x=int(2300 * scale_factor),
        y=int(floor_y - int(280 * scale_factor)),
        width=int(40 * scale_factor),
        height=int(40 * scale_factor),
        has_manuscript=False,
        prompt="Driven by fear of the angry mob, this is what the library's once-loyal visitors have turned into.",
        is_repeatable=True  # <--- Set to True
    ),
    InteractiveObject(
        x=int(1800 * scale_factor),
        y=int(floor_y - int(280 * scale_factor)),
        width=int(40 * scale_factor),
        height=int(40 * scale_factor),
        has_manuscript=False,
        prompt="Driven by guesses and fear, this is the dark, supernatural nature of what the townspeople now believe is happening within the library's walls.",
        is_repeatable=True  # <--- Set to True
    ),
]

interactive_objects.append(
    InteractiveObject(
        x=int(MAP_WIDTH * 0.77),  # right side
        y=int(floor_y - int(BASE_HEIGHT * 0.25)),  # center vertically above floor
        width=int(80 * scale_factor),
        height=int(80 * scale_factor),
        has_manuscript=True,
        prompt="A mysterious manuscript lies here...",
        image_file=MANUSCRIPT_FILE
    )
)

import random

# --- Create TRAITORS set ---
for char in "TRAITORS":
    interactive_objects.append(
        InteractiveObject(
            x=random.randint(200, MAP_WIDTH - 200),
            y=int(floor_y - 100),
            width=50, height=50,
            prompt=f"A small carving in the wall: {char}",
            is_repeatable=True
        )
    )

# --- Create DEMONIC set ---
for char in "DEMONIC":
    interactive_objects.append(
        InteractiveObject(
            x=random.randint(200, MAP_WIDTH - 200),
            y=int(floor_y - 200),
            width=50, height=50,
            prompt=f"A faint whisper seems to emanate from this spot: {char}",
            is_repeatable=True
        )
    )

# --- Adaptive Player Initialization ---
player = Player(
    floor_y,
    x=int(BASE_WIDTH * 0.10),
    y=int(BASE_HEIGHT * 0.48),
    scale=(BASE_HEIGHT / 1080) * 1.1   # adaptive + manual multiplier
)

camera = Camera(MAP_WIDTH, MAP_HEIGHT, BASE_WIDTH, BASE_HEIGHT)

# ✅ UI Layer
ui_layer = UILayer(game_surface)

# --- Main Loop wrapped in a function ---
def run_level():
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
                                ui_layer.show_subtitle("You already searched this part.", 2000)
                            else:
                                if not obj.already_searched:
                                    obj.already_searched = True
                                    ui_layer.show_subtitle("You found a hidden manuscript!", 3000)
                                else:
                                    ui_layer.show_subtitle("You examine the manuscript again...", 2000)

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
                                    ui_layer.show_subtitle(f"You picked up {obj.inventory_item}!")
                                else:
                                    # ✅ Inventory full, but item not yet picked up
                                    ui_layer.show_subtitle("My inventory is full.", 2000)
                            else:
                                # ✅ Item was already picked up before
                                ui_layer.show_subtitle("You already picked this up.", 2000)

                        # --- Other prompts ---
                        else:
                            if obj.is_repeatable:
                                # Always show the prompt, never set already_searched
                                ui_layer.show_subtitle(obj.prompt, 3000)
                            else:
                                # Original behavior for normal items
                                if not obj.already_searched:
                                    obj.already_searched = True
                                    ui_layer.show_subtitle(obj.prompt, 2000)
                                else:
                                    ui_layer.show_subtitle("You already searched this part.", 2000)
                        break
                if not found:
                    ui_layer.show_subtitle("There is nothing to interact with here.", 1500)

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

            # --- Original object rendering ---
            if obj.image:
                game_surface.blit(obj.image, camera.apply_rect(obj.rect))

            # Show prompt when player collides
            if player.rect.colliderect(obj.rect):
                prompt_text = ui_font.render(obj.prompt, True, (255, 255, 255))
                prompt_rect = prompt_text.get_rect(midbottom=(obj.rect.centerx, obj.rect.top - 20))
                game_surface.blit(prompt_text, camera.apply_rect(prompt_rect))

            if obj.is_glowing and not obj.already_searched:
                # --- Pulse Effect ---
                import math
                pulse = 1.0 + (0.2 * math.sin(pygame.time.get_ticks() / 200))

                # 1. Apply pulse to size here
                base_w = int(obj.rect.width * 1.5)
                base_h = int(obj.rect.height * 1.5)
                glow_size = (int(base_w * pulse), int(base_h * pulse)) # Apply pulse!
                glow_surf = pygame.Surface(glow_size, pygame.SRCALPHA)

                # 2. Adjust the SPREAD and DENSITY
                for i in range(10, 0, -1):
                    alpha = 50
                    # Inflate dynamically based on the pulse-affected size
                    glow_surf.fill((0, 0, 0, 0)) # Clear previous frame if necessary
                    pygame.draw.ellipse(glow_surf, (255, 255, 0, alpha),
                                        glow_surf.get_rect().inflate(-i * 5, -i * 5))

                glow_rect = glow_surf.get_rect(center=obj.rect.center)
                game_surface.blit(glow_surf, camera.apply_rect(glow_rect))

                # ✅ Render the text "H"
                if obj.inventory_item == "H":
                    h_text = h_font.render("H", True, (255, 255, 255))
                    text_rect = h_text.get_rect(center=obj.rect.center)
                    game_surface.blit(h_text, camera.apply_rect(text_rect))

            pygame.draw.rect(game_surface, (0, 255, 0), camera.apply_rect(obj.rect), 2)

        # Draw player
        game_surface.blit(player.image, camera.apply(player))

        # Manuscripts UI text
        ui_text = ui_font.render(f"Manuscripts: {player.manuscripts_found} / 2", True, (255, 215, 0))
        game_surface.blit(ui_text, (BASE_WIDTH - 280, 20))

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