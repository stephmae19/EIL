# ch1_lvl2.py
import pygame
import sys
import os
from ui_layer import UILayer

# --- Filenames ---
WALK_FILE = "Assets/CHARACTERS/player_walk.png"
WALK2_FILE = "Assets/CHARACTERS/player_walk2.png"
IDLE_FILE = "Assets/CHARACTERS/player_idle.png"
BG_FILE = "Assets/MAPS/chapter1/ch1_lvl2.png"

SCALE_FILE = "Assets/MAPS/chapter1/scale.png"
# --- Orb Variations ---
ORB_GLOW_BLUE = "Assets/MAPS/chapter1/orb_glow_blue.png"
ORB_STATIC_BLUE = "Assets/MAPS/chapter1/orb_static_blue.png"

ORB_GLOW_GREEN = "Assets/MAPS/chapter1/orb_glow_green.png"
ORB_STATIC_GREEN = "Assets/MAPS/chapter1/orb_static_green.png"

ORB_GLOW_RED = "Assets/MAPS/chapter1/orb_glow_red.png"
ORB_STATIC_RED = "Assets/MAPS/chapter1/orb_static_red.png"

ORB_GLOW_VIOLET = "Assets/MAPS/chapter1/orb_glow_violet.png"
ORB_STATIC_VIOLET = "Assets/MAPS/chapter1/orb_static_violet.png"

# --- Book Variations ---
BOOK_BLUE = "Assets/MAPS/chapter1/book_blue.png"
BOOK_RED = "Assets/MAPS/chapter1/book_red.png"
BOOK_GREEN = "Assets/MAPS/chapter1/book_green.png"
BOOK_BROWN = "Assets/MAPS/chapter1/book_brown.png"

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
                 has_manuscript=False, has_scale=False,
                 inventory_item=None,
                 prompt="Press 'E' to interact", image_file=None):
        self.rect = pygame.Rect(x, y, width, height)
        self.has_manuscript = has_manuscript
        self.has_scale = has_scale
        self.inventory_item = inventory_item
        self.already_searched = False
        self.prompt = prompt

        self.image = None
        self.frames = None
        self.frame_index = 0
        self.last_update = pygame.time.get_ticks()
        self.frame_duration = 1000 // 12  # 12 FPS default

        if image_file and os.path.exists(image_file):
            if image_file and "orb_glow" in image_file:
                sheet = pygame.image.load(image_file).convert_alpha()
                rows, cols = 2, 2
                w, h = sheet.get_width() // cols, sheet.get_height() // rows
                self.frames = []
                for r in range(rows):
                    for c in range(cols):
                        frame = sheet.subsurface(pygame.Rect(c * w, r * h, w, h))
                        scale_factor = min(width / w, height / h)
                        new_w, new_h = int(w * scale_factor), int(h * scale_factor)
                        scaled = pygame.transform.scale(frame, (new_w, new_h))
                        self.frames.append(scaled)
                self.image = self.frames[self.frame_index]
                self.image_rect = self.image.get_rect(center=self.rect.center)
            else:
                raw = pygame.image.load(image_file).convert_alpha()
                raw_w, raw_h = raw.get_size()
                scale_factor = min(width / raw_w, height / raw_h)
                new_w, new_h = int(raw_w * scale_factor), int(raw_h * scale_factor)
                self.image = pygame.transform.scale(raw, (new_w, new_h))
                self.image_rect = self.image.get_rect(center=self.rect.center)
        else:
            self.image_rect = self.rect

    def update(self):
        if self.frames:
            now = pygame.time.get_ticks()
            if now - self.last_update >= self.frame_duration:
                self.last_update = now
                self.frame_index = (self.frame_index + 1) % len(self.frames)
                self.image = self.frames[self.frame_index]
                self.image_rect = self.image.get_rect(center=self.rect.center)

    def resize(self, new_width, new_height):
        self.rect.width = new_width
        self.rect.height = new_height

    def move(self, new_x, new_y):
        self.rect.x = new_x
        self.rect.y = new_y


class Player(pygame.sprite.Sprite):
    def __init__(self, floor_y, x=400, y=None, scale=0.45):
        super().__init__()
        self.scale = scale

        self.walk_frames = self.load_frames(WALK_FILE, 5, 5)
        self.idle_frames = self.load_frames(IDLE_FILE, 5, 5)

        self.current_frames = self.idle_frames
        self.frame_index = 0
        self.image = self.current_frames[self.frame_index]

        if y is None:
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

        sheet = sheet.copy()
        width, height = sheet.get_size()
        for x in range(width):
            for y in range(height):
                r, g, b, a = sheet.get_at((x, y))
                if r < JPG_BLACK_TOLERANCE and g < JPG_BLACK_TOLERANCE and b < JPG_BLACK_TOLERANCE:
                    sheet.set_at((x, y), (r, g, b, 0))

        w, h = sheet.get_width() // cols, sheet.get_height() // rows
        frames = []
        for r in range(rows):
            for c in range(cols):
                frame = sheet.subsurface(pygame.Rect(c * w, r * h, w, h))
                scaled_frame = pygame.transform.scale(frame, (int(w * self.scale), int(h * self.scale)))
                frames.append(scaled_frame)
        return frames

    def update_logic(self, scale_width):
        keys = pygame.key.get_pressed()
        self.is_moving = False
        self.is_running = False

        if keys[pygame.K_LSHIFT] or keys[pygame.K_RSHIFT]:
            self.is_running = True
            self.speed = self.run_speed
        else:
            self.speed = self.walk_speed

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
        if self.rect.right > scale_width:
            self.rect.right = scale_width

    def animate(self):
        now = pygame.time.get_ticks()
        target_frames = self.walk_frames if self.is_moving else self.idle_frames
        fps = 36 if self.is_running else (20 if self.is_moving else 12)
        self.frame_duration = 1000 // fps

        if self.current_frames != target_frames:
            self.current_frames = target_frames
            self.frame_index = 0
            self.last_update = now

        if now - self.last_update >= self.frame_duration:
            self.last_update = now
            self.frame_index = (self.frame_index + 1) % len(self.current_frames)
            raw_image = self.current_frames[self.frame_index]
            self.image = pygame.transform.flip(raw_image, True, False) if not self.facing_right else raw_image

    def update(self, scale_width):
        self.update_logic(scale_width)
        self.animate()


# --- Initialization ---
pygame.init()
pygame.font.init()

BASE_WIDTH, BASE_HEIGHT = 1920, 1080

info = pygame.display.Info()
native_width, native_height = info.current_w, info.current_h
os.environ['SDL_VIDEO_CENTERED'] = '1'

screen = pygame.display.set_mode((native_width, native_height - 50), pygame.RESIZABLE)
pygame.display.set_caption("Chapter 1 - Level 2")

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

SCALE_WIDTH, SCALE_HEIGHT = bg_image.get_width(), bg_image.get_height()
floor_y = int(SCALE_HEIGHT * FLOOR_HEIGHT_PERCENTAGE)

DESIGN_WIDTH = 1920
DESIGN_HEIGHT = 1080

scale_x = BASE_WIDTH / DESIGN_WIDTH
scale_y = BASE_HEIGHT / DESIGN_HEIGHT
scale_factor = BASE_HEIGHT / DESIGN_HEIGHT

# --- Adaptive Interactive Objects ---
interactive_objects = [
    InteractiveObject(
        x=int(180 * scale_factor),
        y=int(floor_y - int(140 * scale_factor)),
        width=int(5 * scale_factor),
        height=int(40 * scale_factor),
        has_manuscript=False,
        inventory_item="H",
        prompt="A glowing orb."
    ),
    InteractiveObject(
        x=int(350 * scale_factor),
        y=int(floor_y - int(200 * scale_factor)),
        width=int(5 * scale_factor),
        height=int(40 * scale_factor),
        has_manuscript=False,
        prompt="An alchemy book."
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
        x=int(2925 * scale_factor),
        y=int(floor_y - int(200 * scale_factor)),
        width=int(50 * scale_factor),
        height=int(50 * scale_factor),
        has_manuscript=False,
        inventory_item="ORB_GREEN",
        prompt="A glowing green orb.",
        image_file=ORB_GLOW_GREEN
    ),
    InteractiveObject(
        x=int(1450 * scale_factor),
        y=int(floor_y - int(240 * scale_factor)),
        width=int(30 * scale_factor),
        height=int(30 * scale_factor),
        has_manuscript=False,
        inventory_item="ORB_RED",
        prompt="A glowing red orb.",
        image_file=ORB_GLOW_RED
    ),
    InteractiveObject(
        x=int(2085 * scale_factor),
        y=int(floor_y - int(260 * scale_factor)),
        width=int(40 * scale_factor),
        height=int(40 * scale_factor),
        has_manuscript=False,
        inventory_item="ORB_VIOLET",
        prompt="A glowing violet orb.",
        image_file=ORB_GLOW_VIOLET
    ),
    InteractiveObject(
        x=int(2780 * scale_factor),
        y=int(floor_y - int(285 * scale_factor)),
        width=int(40 * scale_factor),
        height=int(40 * scale_factor),
        has_manuscript=False,
        inventory_item="BOOK_BLUE",
        prompt="A dusty blue book.",
        image_file=BOOK_BLUE
    ),
    InteractiveObject(
        x=int(3200 * scale_factor),
        y=int(floor_y - int(195 * scale_factor)),
        width=int(40 * scale_factor),
        height=int(40 * scale_factor),
        has_manuscript=False,
        inventory_item="BOOK_RED",
        prompt="A worn red book.",
        image_file=BOOK_RED
    ),
    InteractiveObject(
        x=int(3450 * scale_factor),
        y=int(floor_y - int(288 * scale_factor)),
        width=int(40 * scale_factor),
        height=int(40 * scale_factor),
        has_manuscript=False,
        inventory_item="BOOK_GREEN",
        prompt="A mossy green book.",
        image_file=BOOK_GREEN
    ),
    InteractiveObject(
        x=int(900 * scale_factor),
        y=int(floor_y - int(190 * scale_factor)),
        width=int(40 * scale_factor),
        height=int(40 * scale_factor),
        has_manuscript=False,
        inventory_item="BOOK_BROWN",
        prompt="An ancient brown book.",
        image_file=BOOK_BROWN
    ),
    InteractiveObject(
        x=int(2210 * scale_factor),
        y=int(floor_y - int(280 * scale_factor)),
        width=int(40 * scale_factor),
        height=int(40 * scale_factor),
        has_manuscript=False,
        prompt="The scales weigh not gold nor silver, but wisdom and light. Balance the spheres of power with the tomes of truth, and the hidden way shall open."
    ),
]

interactive_objects.append(
    InteractiveObject(
        x=int(SCALE_WIDTH * 0.68),
        y=int(floor_y - int(BASE_HEIGHT * 0.22)),
        width=int(91 * scale_factor),
        height=int(138 * scale_factor),
        has_scale=True,
        prompt="An antique scale...",
        image_file=SCALE_FILE
    )
)

player = Player(
    floor_y,
    x=int(BASE_WIDTH * 0.6),
    y=int(BASE_HEIGHT * 0.48),
    scale=(BASE_HEIGHT / 1080) * 1.1
)

camera = Camera(SCALE_WIDTH, SCALE_HEIGHT, BASE_WIDTH, BASE_HEIGHT)
ui_layer = UILayer(game_surface)


def run_level():
    clock = pygame.time.Clock()

    while True:
        now = pygame.time.get_ticks()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                return
            if event.type == pygame.KEYDOWN and event.key == pygame.K_e:
                found = False
                for obj in interactive_objects:
                    obj.update()
                    if player.rect.colliderect(obj.rect):
                        found = True

                        # --- Scale object ---
                        if obj.has_scale:
                            obj.already_searched = True
                            ui_layer.show_subtitle("You approach the antique scale...", 2000)

                            # 1. Safely calculate and save coordinates before entering scene
                            # Tweaking offsets shifts your destination relative to scale center
                            X_OFFSET = 0
                            Y_OFFSET = -83
                            temp_rect = player.image.get_rect(
                                midbottom=(obj.rect.centerx + X_OFFSET, floor_y + Y_OFFSET))
                            SAVED_PLAYER_X = temp_rect.x
                            SAVED_PLAYER_Y = temp_rect.y

                            # 2. Route to puzzle scene
                            import ch1_lvl2_puz
                            ch1_lvl2_puz.run_puzzle(game_surface, player)

                            # 3. ✅ CRITICAL FIX: Removed 'return' so progress isn't wiped.
                            # Force character coordinate synchronization immediately upon coming back.
                            player.rect.x = SAVED_PLAYER_X
                            player.rect.y = SAVED_PLAYER_Y

                            # Hide all items that were committed/placed in the puzzle
                            placed_on_scale = ch1_lvl2_puz.get_placed_item_ids() if hasattr(ch1_lvl2_puz,
                                                                                            'get_placed_item_ids') else []
                            for interactable in interactive_objects:
                                if interactable.inventory_item and interactable.inventory_item in placed_on_scale:
                                    interactable.already_searched = True
                                    interactable.image = None
                                    interactable.frames = None

                            continue  # Keep running the current map thread loop smoothly

                        # --- Manuscript object ---
                        elif obj.has_manuscript:
                            if player.puzzle_solved:
                                ui_layer.show_subtitle("You already searched this part.", 2000)
                            else:
                                if not obj.already_searched:
                                    obj.already_searched = True
                                    ui_layer.show_subtitle("You found a hidden manuscript!", 3000)
                                else:
                                    ui_layer.show_subtitle("You already searched this part.", 2000)

                                import ch1_lvl1_puz
                                ch1_lvl1_puz.run_puzzle(player, ui_layer)
                            break

                        # --- Inventory items ---
                        elif obj.inventory_item:
                            if not obj.already_searched:
                                if len(player.inventory) < 6:
                                    if obj.inventory_item.startswith("ORB"):
                                        orb_map = {
                                            "ORB_BLUE": ORB_STATIC_BLUE,
                                            "ORB_GREEN": ORB_STATIC_GREEN,
                                            "ORB_RED": ORB_STATIC_RED,
                                            "ORB_VIOLET": ORB_STATIC_VIOLET
                                        }
                                        orb_static_path = orb_map.get(obj.inventory_item)
                                        if orb_static_path:
                                            orb_icon = pygame.image.load(orb_static_path).convert_alpha()
                                            orb_icon = pygame.transform.scale(orb_icon, (40, 40))
                                            player.inventory.append({"id": obj.inventory_item, "icon": orb_icon})

                                        obj.already_searched = True
                                        obj.image = None
                                        obj.frames = None
                                        ui_layer.show_subtitle(f"You picked up a {obj.prompt.lower()}", 2000)

                                    elif obj.inventory_item.startswith("BOOK"):
                                        book_map = {
                                            "BOOK_BLUE": BOOK_BLUE,
                                            "BOOK_RED": BOOK_RED,
                                            "BOOK_GREEN": BOOK_GREEN,
                                            "BOOK_BROWN": BOOK_BROWN
                                        }
                                        book_path = book_map.get(obj.inventory_item)
                                        if book_path:
                                            book_icon = pygame.image.load(book_path).convert_alpha()
                                            book_icon = pygame.transform.scale(book_icon, (40, 40))
                                            player.inventory.append({"id": obj.inventory_item, "icon": book_icon})

                                        obj.already_searched = True
                                        obj.image = None
                                        obj.frames = None
                                        ui_layer.show_subtitle(f"You picked up {obj.prompt.lower()}", 2000)

                                    else:
                                        player.inventory.append({"id": obj.inventory_item, "icon": obj.inventory_item})
                                        obj.already_searched = True
                                        ui_layer.show_subtitle(f"You picked up {obj.inventory_item}!", 2000)
                                else:
                                    ui_layer.show_subtitle("My inventory is full.", 2000)
                            else:
                                ui_layer.show_subtitle("You already picked this up.", 2000)

                        else:
                            if obj.prompt.startswith("The scales weigh not gold"):
                                ui_layer.show_subtitle(obj.prompt, 4000)
                            else:
                                if not obj.already_searched:
                                    obj.already_searched = True
                                    ui_layer.show_subtitle(obj.prompt, 2000)
                                else:
                                    ui_layer.show_subtitle("You already searched this part.", 2000)

                        break

                if not found:
                    ui_layer.show_subtitle("There is nothing to interact with here.", 1500)

                ui_layer.handle_input(event)
                ui_layer.click_insanity_loss()

        player.update(SCALE_WIDTH)
        camera.update(player)
        for obj in interactive_objects:
            obj.update()

        game_surface.fill((0, 0, 0))
        game_surface.blit(bg_image, (camera.camera.x, camera.camera.y))

        for obj in interactive_objects:
            pygame.draw.rect(game_surface, (0, 255, 0), camera.apply_rect(obj.rect), 2)

            if obj.image:
                game_surface.blit(obj.image, camera.apply_rect(obj.image_rect))

            if player.rect.colliderect(obj.rect):
                prompt_text = ui_font.render(obj.prompt, True, (255, 255, 255))
                prompt_rect = prompt_text.get_rect(midbottom=(obj.rect.centerx, obj.rect.top - 20))
                game_surface.blit(prompt_text, camera.apply_rect(prompt_rect))

        game_surface.blit(player.image, camera.apply(player))

        ui_text = ui_font.render(f"Manuscripts: {player.manuscripts_found} / 1", True, (255, 215, 0))
        game_surface.blit(ui_text, (BASE_WIDTH - 280, 20))

        ui_layer.draw(player)

        window_width, window_height = screen.get_size()
        scale = min(window_width / BASE_WIDTH, window_height / BASE_HEIGHT)
        scaled_w, scaled_h = int(BASE_WIDTH * scale), int(BASE_HEIGHT * scale)

        scaled_surface = pygame.transform.smoothscale(game_surface, (scaled_w, scaled_h))

        x_offset = (window_width - scaled_w) // 2
        y_offset = (window_height - scaled_h) // 2

        screen.fill((0, 0, 0))
        screen.blit(scaled_surface, (x_offset, y_offset))

        pygame.display.flip()
        clock.tick(60)


if __name__ == "__main__":
    run_level()