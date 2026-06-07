# ch1_lvl3.py
import pygame
import sys
import os
from ui_layer import UILayer
import math

# --- Filenames ---
WALK_FILE = "Assets/CHARACTERS/player_walk.png"
WALK2_FILE = "Assets/CHARACTERS/player_walk2.png"
IDLE_FILE = "Assets/CHARACTERS/player_idle.png"
BG_FILE = "Assets/MAPS/chapter1/ch1_lvl3.png"
MANUSCRIPT_FILE = "Assets/OBJECTS-ITEMS/manuscript.png"

# --- Orbs ---
ORB_GLOW_VIOLET = "Assets/MAPS/chapter1/orb_glow_violet.png"
ORB_GLOW_RED = "Assets/MAPS/chapter1/orb_glow_red.png"

ORB_STATIC_VIOLET = "Assets/MAPS/chapter1/orb_static_violet.png"
ORB_STATIC_RED = "Assets/MAPS/chapter1/orb_static_red.png"

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
                 prompt="Press 'E' to interact", prompt_duration=None, image_file=None, static_image=None,
                 is_glowing=False, is_repeatable=False, rows=1, cols=1):
        self.rect = pygame.Rect(x, y, width, height)
        self.has_manuscript = has_manuscript
        self.inventory_item = inventory_item
        self.already_searched = False
        self.prompt = prompt
        self.prompt_duration = prompt_duration  # ✅ New attribute to control text screen time
        self.is_glowing = is_glowing
        self.is_repeatable = is_repeatable
        self.is_revealed = False

        self.static_image = None
        if static_image and os.path.exists(static_image):
            self.static_image = pygame.transform.scale(pygame.image.load(static_image).convert_alpha(), (width, height))

        self.frames = []
        self.frame_index = 0
        self.last_update = pygame.time.get_ticks()

        if image_file and os.path.exists(image_file):
            sheet = pygame.image.load(image_file).convert_alpha()
            w, h = sheet.get_width() // cols, sheet.get_height() // rows
            for r in range(rows):
                for c in range(cols):
                    frame = sheet.subsurface(pygame.Rect(c * w, r * h, w, h))
                    self.frames.append(pygame.transform.scale(frame, (width, height)))
        self.image = self.frames[0] if self.frames else None

    def update_animation(self):
        if self.frames and not self.already_searched:
            if pygame.time.get_ticks() - self.last_update > 150:
                self.frame_index = (self.frame_index + 1) % len(self.frames)
                self.image = self.frames[self.frame_index]
                self.last_update = pygame.time.get_ticks()
        elif self.already_searched and self.static_image:
            self.image = self.static_image

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
h_font = pygame.font.Font(CUSTOM_FONT_PATH, 50)  # Set size to 50 for visibility

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
        x=int(680 * scale_factor), y=int(floor_y - 270 * scale_factor),
        width=int(80 * scale_factor), height=int(80 * scale_factor),
        inventory_item="ORB_VIOLET", prompt="A glowing violet orb.",
        image_file=ORB_GLOW_VIOLET, static_image=ORB_STATIC_VIOLET,
        rows=2, cols=2
    ),
    InteractiveObject(
        x=int(2000 * scale_factor), y=int(floor_y - 270 * scale_factor),
        width=int(80 * scale_factor), height=int(80 * scale_factor),
        inventory_item="ORB_RED", prompt="A glowing red orb.",
        image_file=ORB_GLOW_RED, static_image=ORB_STATIC_RED,
        rows=2, cols=2
    ),
    InteractiveObject(
        x=int(1300 * scale_factor),
        y=int(floor_y - int(280 * scale_factor)),
        width=int(40 * scale_factor),
        height=int(40 * scale_factor),
        has_manuscript=False,
        prompt="The spheres whisper to the walls, and the tomes guard their riddles. Inscribe the true sequence upon the drifting parchment, for only balanced letters reveal the hidden way.",
        prompt_duration=8000,  # ✅ Kept on screen for 8 seconds
        is_repeatable=True
    ),
    InteractiveObject(
        x=int(2300 * scale_factor),
        y=int(floor_y - int(280 * scale_factor)),
        width=int(40 * scale_factor),
        height=int(40 * scale_factor),
        has_manuscript=False,
        prompt="Driven by fear of the angry mob, this is what the library's once-loyal visitors have turned into.",
        is_repeatable=True
    ),
    InteractiveObject(
        x=int(1800 * scale_factor),
        y=int(floor_y - int(280 * scale_factor)),
        width=int(40 * scale_factor),
        height=int(40 * scale_factor),
        has_manuscript=False,
        prompt="Driven by guesses and fear, this is the dark, supernatural nature of what the townspeople now believe is happening within the library's walls.",
        is_repeatable=True
    ),
]

interactive_objects.append(
    InteractiveObject(
        x=int(MAP_WIDTH * 0.79),  # right side
        y=int(floor_y - int(BASE_HEIGHT * 0.25)),  # center vertically above floor
        width=int(80 * scale_factor),
        height=int(80 * scale_factor),
        has_manuscript=True,
        prompt="A mysterious manuscript lies here...",
        image_file=MANUSCRIPT_FILE
    )
)

import random

# --- Configuration ---
# Letters will spawn between 100px from top and 320px above the floor
min_y = 100
max_y = floor_y - 320
object_width = 60
object_height = 60
min_distance = 100


def is_position_valid(new_rect, existing_objects):
    for obj in existing_objects:
        # Check if the new rect is too close to an existing object
        # We use a buffer to ensure they don't overlap
        if new_rect.colliderect(obj.rect.inflate(min_distance, min_distance)):
            return False
    return True


# --- Create sets ---
# Explicitly define which letter belongs to which word/color
traitors_letters = list("TRAITORS")
demonic_letters = list("DEMONIC")

# Combine them while tagging them with their word source
all_char_data = []
for char in traitors_letters:
    all_char_data.append((char, "TRAITORS"))
for char in demonic_letters:
    all_char_data.append((char, "DEMONIC"))

for char, set_name in all_char_data:
    placed = False
    attempts = 0
    while not placed and attempts < 100:
        # ✅ Adjusted boundaries to keep positions away from the left 350px and right 350px of the map
        spawn_x = random.randint(350, MAP_WIDTH - 350)
        spawn_y = random.randint(min_y, max_y)
        new_rect = pygame.Rect(spawn_x, spawn_y, object_width, object_height)

        if is_position_valid(new_rect, interactive_objects):
            obj = InteractiveObject(
                x=spawn_x, y=spawn_y,
                width=object_width, height=object_height,
                prompt=f"A faint carving or whisper: {char}",
                is_glowing=True,
                is_repeatable=True
            )
            obj.inventory_item = char
            obj.set_type = set_name  # Now explicitly set to "TRAITORS" or "DEMONIC"

            interactive_objects.append(obj)
            placed = True
        attempts += 1

# --- Adaptive Player Initialization ---
player = Player(
    floor_y,
    x=int(BASE_WIDTH * 0.10),
    y=int(BASE_HEIGHT * 0.48),
    scale=(BASE_HEIGHT / 1080) * 1.1  # adaptive + manual multiplier
)

camera = Camera(MAP_WIDTH, MAP_HEIGHT, BASE_WIDTH, BASE_HEIGHT)

# ✅ UI Layer
ui_layer = UILayer(game_surface)


# --- Main Loop wrapped in a function ---
def run_level():
    clock = pygame.time.Clock()

    while True:
        # 1. Capture Input State
        raw_mouse_pos = pygame.mouse.get_pos()
        now = pygame.time.get_ticks()

        # ✅ Calculate normalized mouse pos relative to the game_surface immediately
        window_width, window_height = screen.get_size()
        scale = min(window_width / BASE_WIDTH, window_height / BASE_HEIGHT)
        offset_x = (window_width - int(BASE_WIDTH * scale)) // 2
        offset_y = (window_height - int(BASE_HEIGHT * scale)) // 2

        adj_mouse_x = (raw_mouse_pos[0] - offset_x) / scale
        adj_mouse_y = (raw_mouse_pos[1] - offset_y) / scale
        adj_mouse_pos = (adj_mouse_x, adj_mouse_y)

        # 2. Event Loop
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            # ✅ Pass the adjusted mouse position to the drag handler
            ui_layer.handle_inventory_drag(event, player, adj_mouse_pos)

            # Escape to exit
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                return

            # Interact with objects
            if event.type == pygame.KEYDOWN and event.key == pygame.K_e:
                found = False
                for obj in interactive_objects:
                    if player.rect.colliderect(obj.rect):
                        found = True
                        # --- Manuscript logic ---
                        if obj.has_manuscript:
                            if player.puzzle_solved:
                                ui_layer.show_subtitle("You already searched this part.", 2000)
                            else:
                                if not obj.already_searched:
                                    obj.already_searched = True
                                    ui_layer.show_subtitle("You found a hidden manuscript!", 3000)
                                else:
                                    ui_layer.show_subtitle("You examine the manuscript again...", 2000)
                                # ✅ Connected to level 3 puzzle module
                                import ch1_lvl3_puz
                                ch1_lvl3_puz.run_puzzle(player, ui_layer)
                            break
                        # --- Inventory logic ---
                        elif obj.inventory_item:
                            if not obj.already_searched:
                                if len(player.inventory) < 6:
                                    item_data = {"id": obj.inventory_item,
                                                 "icon": obj.static_image if obj.inventory_item.startswith(
                                                     "ORB") else None}
                                    player.inventory.append(item_data)
                                    obj.already_searched = True
                                    ui_layer.show_subtitle(f"You picked up {obj.inventory_item}!")
                                else:
                                    ui_layer.show_subtitle("My inventory is full.", 2000)
                            else:
                                ui_layer.show_subtitle("You already picked this up.", 2000)
                        else:
                            # ✅ Use custom duration if it exists, otherwise fall back to 3s/2s
                            display_time = obj.prompt_duration if obj.prompt_duration else (
                                3000 if obj.is_repeatable else 2000)

                            if obj.is_repeatable:
                                ui_layer.show_subtitle(obj.prompt, display_time)
                            elif not obj.already_searched:
                                obj.already_searched = True
                                ui_layer.show_subtitle(obj.prompt, display_time)
                        break

                if not found:
                    ui_layer.show_subtitle("There is nothing to interact with here.", 1500)

                # ✅ ADDED: Accelerate the insanity drain on 'E' press, matching ch1_lvl2.py
                ui_layer.click_insanity_loss()

            # UI input handling
            ui_layer.handle_input(event)

        # 3. Update
        player.update(MAP_WIDTH)
        camera.update(player)

        # ✅ Check for Drag Collisions (Orb Reveal Logic)
        if ui_layer.is_dragging and ui_layer.dragging_item:
            dragged_id = ui_layer.dragging_item.get("id")
            # Create an 80x80 hitbox around the mouse cursor to match your dragged orb
            mouse_rect = pygame.Rect(adj_mouse_x - 40, adj_mouse_y - 40, 80, 80)

            for obj in interactive_objects:
                # Check if it's a letter object (has set_type) and is not yet revealed
                if hasattr(obj, 'set_type') and not getattr(obj, 'is_revealed', False):
                    # Apply camera offset to the object's rect so it matches mouse screen space
                    screen_rect = camera.apply_rect(obj.rect)

                    if screen_rect.colliderect(mouse_rect):
                        # Reveal logic based on Orb ID and Set Type
                        if dragged_id == "ORB_VIOLET" and obj.set_type == "TRAITORS":
                            obj.is_revealed = True
                        elif dragged_id == "ORB_RED" and obj.set_type == "DEMONIC":
                            obj.is_revealed = True

        # 4. Render
        game_surface.fill((0, 0, 0))
        game_surface.blit(bg_image, (camera.camera.x, camera.camera.y))

        for obj in interactive_objects:
            obj.update_animation()

            # ✅ FIX: Always render the manuscript image even if already_searched is True
            if not obj.already_searched or obj.has_manuscript:
                if obj.image:
                    game_surface.blit(obj.image, camera.apply_rect(obj.rect))

                # Check if this object is a letter that hasn't been revealed yet
                is_hidden_letter = hasattr(obj, 'set_type') and not getattr(obj, 'is_revealed', False)

                # Pulse Effect (Circular and expanding)
                if obj.is_glowing and not is_hidden_letter:
                    pulse = (math.sin(pygame.time.get_ticks() * 0.005) + 1) / 2
                    glow_radius = int(max(obj.rect.width, obj.rect.height) * (0.8 + pulse * 0.4))
                    glow_surf_size = (glow_radius * 2, glow_radius * 2)
                    glow_surf = pygame.Surface(glow_surf_size, pygame.SRCALPHA)

                    # Draw soft, semi-transparent circle
                    for i in range(5):
                        alpha = int(40 * (1 - (i / 5)))
                        pygame.draw.circle(
                            glow_surf,
                            (255, 255, 200, alpha),
                            (glow_radius, glow_radius),
                            glow_radius - (i * 5)
                        )

                    glow_rect = glow_surf.get_rect(center=obj.rect.center)
                    game_surface.blit(glow_surf, camera.apply_rect(glow_rect))

                # Glow/Letter logic
                if obj.is_glowing and obj.inventory_item and len(str(obj.inventory_item)) == 1:
                    if getattr(obj, 'is_revealed', False):
                        text_color = (238, 130, 238) if getattr(obj, 'set_type', '') == "TRAITORS" else (255, 0, 0)
                        char_text = h_font.render(str(obj.inventory_item), True, text_color)
                        text_rect = char_text.get_rect(center=obj.rect.center)
                        game_surface.blit(char_text, camera.apply_rect(text_rect))

        # Draw player
        game_surface.blit(player.image, camera.apply(player))

        # Draw UI
        ui_layer.draw(player)

        # Draw the dragged item
        ui_layer.draw_dragged_item(adj_mouse_pos)

        # Manuscripts UI text
        ui_text = ui_font.render(f"Manuscripts: {player.manuscripts_found} / 2", True, (255, 215, 0))
        game_surface.blit(ui_text, (BASE_WIDTH - 280, 20))

        # Display Scaling
        window_width, window_height = screen.get_size()
        scale = min(window_width / BASE_WIDTH, window_height / BASE_HEIGHT)
        scaled_w, scaled_h = int(BASE_WIDTH * scale), int(BASE_HEIGHT * scale)
        scaled_surface = pygame.transform.smoothscale(game_surface, (scaled_w, scaled_h))

        screen.fill((0, 0, 0))
        screen.blit(scaled_surface, ((window_width - scaled_w) // 2, (window_height - scaled_h) // 2))

        pygame.display.flip()
        clock.tick(60)


if __name__ == "__main__":
    run_level()