# ch1_lvl1.py
import pygame
import sys
import os
from ui_layer import UILayer

# --- Filenames ---
WALK_FILE = "Assets/CHARACTERS/player_walk.png"
IDLE_FILE = "Assets/CHARACTERS/player_idle.png"
BG_FILE = "Assets/Maps/chapter1/level1/ch1_lvl1.png"

# --- Config ---
FLOOR_HEIGHT_PERCENTAGE = 0.74
JPG_BLACK_TOLERANCE = 25

# --- Base Resolution (design reference) ---
BASE_WIDTH, BASE_HEIGHT = 1920, 1080


def scale_x(value, screen_w):
    return int(value / BASE_WIDTH * screen_w)


def scale_y(value, screen_h):
    return int(value / BASE_HEIGHT * screen_h)


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
    def __init__(self, x, y, width=150, height=250, has_manuscript=False, prompt="Press 'E' to interact"):
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
        self.run_speed = 9
        self.speed = self.walk_speed

        self.facing_right = True
        self.is_moving = False
        self.is_running = False

        self.manuscripts_found = 0
        self.health = 100

        self.last_update = pygame.time.get_ticks()
        self.frame_duration = 1000 // 12

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

screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
SCREEN_WIDTH, SCREEN_HEIGHT = screen.get_size()
clock = pygame.time.Clock()

# Scaling factors
scale_factor_w = SCREEN_WIDTH / BASE_WIDTH
scale_factor_h = SCREEN_HEIGHT / BASE_HEIGHT

# Fonts scaled
ui_font_size = int(28 * scale_factor_h)
feedback_font_size = int(24 * scale_factor_h)

ui_font = pygame.font.SysFont("arial", ui_font_size, bold=True)
feedback_font = pygame.font.SysFont("arial", feedback_font_size, italic=True)

# Background
if not os.path.exists(BG_FILE):
    bg_image = pygame.Surface((SCREEN_WIDTH * 2, SCREEN_HEIGHT))
    bg_image.fill((50, 50, 80))
else:
    original_bg = pygame.image.load(BG_FILE).convert()
    scale_factor = SCREEN_HEIGHT / original_bg.get_height()
    new_bg_width = int(original_bg.get_width() * scale_factor)
    bg_image = pygame.transform.scale(original_bg, (new_bg_width, SCREEN_HEIGHT))

MAP_WIDTH, MAP_HEIGHT = bg_image.get_width(), bg_image.get_height()
floor_y = int(MAP_HEIGHT * FLOOR_HEIGHT_PERCENTAGE)

# Interactive objects scaled
interactive_objects = [
    InteractiveObject(x=scale_x(200, SCREEN_WIDTH), y=floor_y - scale_y(200, SCREEN_HEIGHT),
                      width=scale_x(200, SCREEN_WIDTH), height=scale_y(300, SCREEN_HEIGHT),
                      has_manuscript=False, prompt="I got locked out."),
    InteractiveObject(x=scale_x(900, SCREEN_WIDTH), y=floor_y - scale_y(50, SCREEN_HEIGHT),
                      width=scale_x(300, SCREEN_WIDTH), height=scale_y(150, SCREEN_HEIGHT),
                      has_manuscript=False, prompt="Some dusty table."),
    InteractiveObject(x=scale_x(1515, SCREEN_WIDTH), y=floor_y - scale_y(270, SCREEN_HEIGHT),
                      width=scale_x(320, SCREEN_WIDTH), height=scale_y(225, SCREEN_HEIGHT),
                      has_manuscript=False, prompt="Looks like it's missing something..."),
    InteractiveObject(x=scale_x(1800, SCREEN_WIDTH), y=floor_y - scale_y(200, SCREEN_HEIGHT),
                      width=scale_x(220, SCREEN_WIDTH), height=scale_y(280, SCREEN_HEIGHT),
                      has_manuscript=True, prompt="Glowing manuscript shelf"),
    InteractiveObject(x=scale_x(2300, SCREEN_WIDTH), y=floor_y - scale_y(200, SCREEN_HEIGHT),
                      width=scale_x(160, SCREEN_WIDTH), height=scale_y(240, SCREEN_HEIGHT),
                      has_manuscript=False, prompt="Just decoration"),
]

# Player scaled
player = Player(floor_y, x=scale_x(200, SCREEN_WIDTH), y=scale_y(610, SCREEN_HEIGHT),
                scale=SCREEN_WIDTH / BASE_WIDTH)
camera = Camera(MAP_WIDTH, MAP_HEIGHT, SCREEN_WIDTH, SCREEN_HEIGHT)

ui_layer = UILayer(screen)

feedback_msg = ""
feedback_timer = 0

# --- Main Loop ---
while True:
    now = pygame.time.get_ticks()
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            pygame.quit()
            sys.exit()
        if event.type == pygame.KEYDOWN and event.key == pygame.K_e:
            found = False
            for obj in interactive_objects:
                if player.rect.colliderect(obj.rect):
                    found = True
                    if obj.already_searched:
                        feedback_msg = "You already searched this object."
                        feedback_timer = now + 2000
                    elif obj.has_manuscript:
                        obj.already_searched = True
                        player.manuscripts_found += 1
                        feedback_msg = "You found a hidden manuscript!"
                        feedback_timer = now + 3000
                    else:
                        obj.already_searched = True
                        feedback_msg = obj.prompt
                        feedback_timer = now + 2000
                    break
            if not found:
                feedback_msg = "There is nothing to interact with here."
                feedback_timer = now + 1500

            # UI input handling
            ui_layer.handle_input(event)
            ui_layer.click_insanity_loss()

    # Update
    player.update(MAP_WIDTH)
    camera.update(player)

    # Draw
    screen.fill((0, 0, 0))
    screen.blit(bg_image, (camera.camera.x, camera.camera.y))

    for obj in interactive_objects:
        # Debug box scaled thickness
        line_thickness = max(1, int(2 * scale_factor_w))
        pygame.draw.rect(screen, (0, 255, 0), camera.apply_rect(obj.rect), line_thickness)

        if player.rect.colliderect(obj.rect):
            prompt_text = ui_font.render(obj.prompt, True, (255, 255, 255))
            prompt_rect = prompt_text.get_rect(midbottom=(obj.rect.centerx,
                                                         obj.rect.top - int(20 * scale_factor_h)))
            screen.blit(prompt_text, camera.apply_rect(prompt_rect))

    # Draw player
    screen.blit(player.image, camera.apply(player))

    # Manuscripts UI text (top-right corner)
    ui_text = ui_font.render(f"Manuscripts: {player.manuscripts_found} / 2", True, (255, 215, 0))
    screen.blit(ui_text, (SCREEN_WIDTH - int(280 * scale_factor_w), int(20 * scale_factor_h)))

    # Feedback message (bottom-center)
    if now < feedback_timer:
        msg_surface = feedback_font.render(feedback_msg, True, (150, 255, 150))
        msg_rect = msg_surface.get_rect(center=(SCREEN_WIDTH // 2,
                                                SCREEN_HEIGHT - int(50 * scale_factor_h)))
        screen.blit(msg_surface, msg_rect)

    # UI overlay last
    ui_layer.draw(player)

    pygame.display.flip()
    clock.tick(60)
