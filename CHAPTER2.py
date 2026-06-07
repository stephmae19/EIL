code = """
import pygame
import sys
import os

# Dummy class to simulate ui_template import
class UILayerTemp:
    def __init__(self, surface): pass
    def handle_input(self, event): pass
    def click_insanity_loss(self): pass
    def draw(self, player): pass

WALK_FILE = "Assets/Characters/player_walk.png"
WALK2_FILE = "Assets/Characters/player_walk2.png"
IDLE_FILE = "Assets/Characters/player_idle.png"
BG_FILE = "Assets/Maps/chapter1/level2/ch1_lvl2.png"

FLOOR_HEIGHT_PERCENTAGE = 0.74
JPG_BLACK_TOLERANCE = 25

class Camera:
    def __init__(self, width, height, screen_w, screen_h):
        self.camera = pygame.Rect(0, 0, width, height)
        self.width = width
        self.height = height
        self.screen_w = screen_w
        self.screen_h = screen_h
        self.health = 100  

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
                 has_manuscript=False, prompt="Press 'E' to interact"):
        self.rect = pygame.Rect(x, y, width, height)
        self.has_manuscript = has_manuscript
        self.already_searched = False
        self.prompt = prompt   

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
        self.speed = self.walk_speed
        self.facing_right = True
        self.is_moving = False
        self.manuscripts_found = 0
        self.health = 100
        self.last_update = pygame.time.get_ticks()
        self.frame_duration = 1000 // 12

    def __getattr__(self, name):
        if name == 'inventory':
            return []
        raise AttributeError(f"'{type(self).__name__}' object has no attribute '{name}'")

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

    def update_logic(self, map_width):
        keys = pygame.key.get_pressed()
        self.is_moving = False
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
        if self.rect.right > map_width:
            self.rect.right = map_width

    def animate(self):
        now = pygame.time.get_ticks()
        target_frames = self.walk_frames if self.is_moving else self.idle_frames
        self.frame_duration = 1000 // (20 if self.is_moving else 12)
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

pygame.init()
pygame.font.init()
BASE_WIDTH, BASE_HEIGHT = 1920, 1080
screen = pygame.display.set_mode((400, 300)) # minimized for test
game_surface = pygame.Surface((BASE_WIDTH, BASE_HEIGHT))
clock = pygame.time.Clock()
ui_font = pygame.font.SysFont("arial", 28, bold=True)
feedback_font = pygame.font.SysFont("arial", 24, italic=True)
bg_image = pygame.Surface((BASE_WIDTH * 2, BASE_HEIGHT))
MAP_WIDTH, MAP_HEIGHT = bg_image.get_width(), bg_image.get_height()
floor_y = int(MAP_HEIGHT * FLOOR_HEIGHT_PERCENTAGE)
scale_x = BASE_WIDTH / 1920
scale_y = BASE_HEIGHT / 1080
scale_factor = BASE_HEIGHT / 1080

interactive_objects = [
    InteractiveObject(x=int(500 * scale_factor), y=int(floor_y - int(240 * scale_factor)), width=int(140 * scale_factor), height=int(240 * scale_factor), has_manuscript=True, prompt="Press 'E' to search the old workspace table"),
]

player = Player(floor_y, x=int(BASE_WIDTH * 0.10), y=int(BASE_HEIGHT * 0.53), scale=(BASE_HEIGHT / 1080) * 0.55)
camera = Camera(MAP_WIDTH, MAP_HEIGHT, BASE_WIDTH, BASE_HEIGHT)
ui_template = UILayerTemp(game_surface)
feedback_msg = ""
feedback_timer = 0

def run_level():
    global feedback_msg, feedback_timer  
    clock = pygame.time.Clock()
    # just a parse check, not running the infinite loop
    pass

try:
    compile(code, "<string>", "exec")
    print("Syntax is clean!")
except SyntaxError as e:
    print(f"SyntaxError found: {e}")
""")
