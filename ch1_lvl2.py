# ch1_lvl2.py
import pygame
import sys
import os
from ui_layer import UILayer
import ch1_lvl2_puz
from Model.Player import Player

# --- Filenames ---
WALK_FILE = "Assets/Characters/player_walk.png"
WALK2_FILE = "Assets/Characters/player_walk2.png"
IDLE_FILE = "Assets/Characters/player_idle.png"
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

camera = Camera(SCALE_WIDTH, SCALE_HEIGHT, BASE_WIDTH, BASE_HEIGHT)
ui_layer = UILayer(game_surface)

# Fix for AttributeError: Pre-initialize health_rect so early event handling doesn't crash
ui_layer.health_rect = pygame.Rect(20, 20, 200, 30)


def run_level(chosen_character=None):
    clock = pygame.time.Clock()

    # Create a fresh Player each time you start the level,
    # now using the shared Model.Player
    player = Player(
        floor_y=floor_y,
        x=int(BASE_WIDTH * 0.10),
        y=int(BASE_HEIGHT * 0.48),
        scale=(BASE_HEIGHT / 1080) * 1.1,
        chosen_character=chosen_character,
        map_width=SCALE_WIDTH,
    )

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
                    if player.rect.colliderect(obj.rect):
                        found = True

                        # --- SCALE INTERACTION BLOCK ---
                        if obj.has_scale:
                            if ch1_lvl2_puz.is_puzzle_solved():
                                ui_layer.show_subtitle("The puzzle has already been deciphered.", 2000)
                                obj.has_scale = False
                                break

                            ui_layer.show_subtitle("You approach the antique scale...", 2000)
                            SAVED_PLAYER_X, SAVED_PLAYER_Y = player.rect.x, player.rect.y

                            ch1_lvl2_puz.run_puzzle(game_surface, player, ui_layer)

                            if ch1_lvl2_puz.is_puzzle_solved():
                                if not player.puzzle_solved:
                                    player.manuscripts_found += 1
                                    player.puzzle_solved = True
                                    ui_layer.show_subtitle("The scale balances! You found a manuscript!", 3000)

                                obj.has_scale = False
                                obj.prompt = "The scale is already balanced."

                            player.rect.x = SAVED_PLAYER_X
                            player.rect.y = SAVED_PLAYER_Y
                            break

                            placed_on_scale = ch1_lvl2_puz.get_placed_item_ids()
                            for interactable in interactive_objects:
                                if interactable.inventory_item and interactable.inventory_item in placed_on_scale:
                                    interactable.already_searched = True
                                    interactable.image = None
                                    interactable.frames = None
                            break

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

        # shared Player behavior from Model/Player
        player.update(SCALE_WIDTH)
        camera.update(player)
        for obj in interactive_objects:
            obj.update()

        game_surface.fill((0, 0, 0))
        game_surface.blit(bg_image, (camera.camera.x, camera.camera.y))

        for obj in interactive_objects:
            if obj.image:
                game_surface.blit(obj.image, camera.apply_rect(obj.image_rect))

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
