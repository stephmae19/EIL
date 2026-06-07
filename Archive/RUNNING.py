import pygame
import sys
import os

# --- 1. YOUR FILENAMES ---
WALK_FILE = "../Assets/Characters/player_walk.jpeg"
IDLE_FILE = "../Assets/Characters/player_idle.jpeg"
BG_FILE = "../Assets/Maps/chapter1_level1.png"

# --- 2. EASY TWEAK VARIABLES ---
FLOOR_HEIGHT_PERCENTAGE = 0.74 
JPG_BLACK_TOLERANCE = 25 


class Camera:
    def __init__(self, width, height, screen_w, screen_h):
        self.camera = pygame.Rect(0, 0, width, height)
        self.width = width
        self.height = height
        self.screen_w = screen_w
        self.screen_h = screen_h

    def apply(self, entity):
        return entity.rect.move(self.camera.topleft)

    def update(self, target):
        x = -target.rect.centerx + int(self.screen_w / 2)
        y = 0 
        x = min(0, x)  
        x = max(-(self.width - self.screen_w), x)  
        self.camera = pygame.Rect(x, y, self.width, self.height)

class Player(pygame.sprite.Sprite):
    def __init__(self, floor_y):
        super().__init__()
        self.walk_frames = self.load_frames(WALK_FILE, 5, 5)
        self.idle_frames = self.load_frames(IDLE_FILE, 5, 5)

        self.current_frames = self.idle_frames
        self.frame_index = 0
        self.image = self.current_frames[self.frame_index]
        self.rect = self.image.get_rect(midbottom=(400, floor_y))
        
        # --- NEW SPEED VARIABLES ---
        self.walk_speed = 4    # Slower normal walking pace
        self.run_speed = 9     # Faster running pace
        self.speed = self.walk_speed 
        
        self.facing_right = True
        self.is_moving = False
        self.is_running = False # New state to track running
        
        self.last_update = pygame.time.get_ticks()
        self.frame_duration = 1000 // 12

    def load_frames(self, filename, rows, cols):
        if not os.path.exists(filename):
            print(f"!!! MISSING: {filename} !!!")
            surf = pygame.Surface((32, 32))
            surf.fill((255, 0, 0))
            return [surf]
        
        sheet = pygame.image.load(filename).convert_alpha()
        
        pixel_array = pygame.PixelArray(sheet)
        for x in range(sheet.get_width()):
            for y in range(sheet.get_height()):
                color = sheet.unmap_rgb(pixel_array[x][y])
                if color.r < JPG_BLACK_TOLERANCE and color.g < JPG_BLACK_TOLERANCE and color.b < JPG_BLACK_TOLERANCE:
                    pixel_array[x][y] = (0, 0, 0, 0) 
        del pixel_array 
        
        w, h = sheet.get_width() // cols, sheet.get_height() // rows
        frames = []
        for r in range(rows):
            for c in range(cols):
                original_frame = sheet.subsurface(pygame.Rect(c*w, r*h, w, h))
                scaled_w = int(w * 0.45)
                scaled_h = int(h * 0.45)
                scaled_frame = pygame.transform.scale(original_frame, (scaled_w, scaled_h))
                frames.append(scaled_frame)
        return frames

    def update_logic(self, map_width):
        keys = pygame.key.get_pressed()
        self.is_moving = False
        self.is_running = False
        
        # --- SHIFT KEY LOGIC ---
        # Check if either Left Shift or Right Shift is held down
        if keys[pygame.K_LSHIFT] or keys[pygame.K_RSHIFT]:
            self.is_running = True
            self.speed = self.run_speed
        else:
            self.is_running = False
            self.speed = self.walk_speed
        
        # --- MOVEMENT LOGIC ---
        if keys[pygame.K_LEFT]:
            self.rect.x -= self.speed
            self.facing_right = False
            self.is_moving = True
        elif keys[pygame.K_RIGHT]:
            self.rect.x += self.speed
            self.facing_right = True
            self.is_moving = True
        elif keys[pygame.K_ESCAPE]:
            pygame.quit()
            sys.exit()

        if self.rect.left < 0:
            self.rect.left = 0
        if self.rect.right > map_width:
            self.rect.right = map_width

    def animate(self):
        now = pygame.time.get_ticks()
        
        if self.is_moving:
            target_frames = self.walk_frames
            # --- RUNNING ANIMATION SPEED ---
            if self.is_running:
                # Play walking frames much faster to look like running (36 FPS)
                self.frame_duration = 1000 // 36 
            else:
                # Normal walking speed (20 FPS)
                self.frame_duration = 1000 // 20  
        else:
            target_frames = self.idle_frames
            self.frame_duration = 1000 // 12  # Idle breathing

        if self.current_frames != target_frames:
            self.current_frames = target_frames
            self.frame_index = 0
            self.last_update = now

        if now - self.last_update > self.frame_duration:
            self.last_update = now
            self.frame_index = (self.frame_index + 1) % len(self.current_frames)
            
            raw_image = self.current_frames[self.frame_index]
            if not self.facing_right:
                self.image = pygame.transform.flip(raw_image, True, False)
            else:
                self.image = raw_image

    def update(self, map_width):
        self.update_logic(map_width)
        self.animate()

# --- Initialization & Setup ---
pygame.init()

screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
SCREEN_WIDTH = screen.get_width()
SCREEN_HEIGHT = screen.get_height()
clock = pygame.time.Clock()

if not os.path.exists(BG_FILE):
    bg_image = pygame.Surface((SCREEN_WIDTH * 2, SCREEN_HEIGHT))
    bg_image.fill((50, 50, 80))
else:
    original_bg = pygame.image.load(BG_FILE).convert()
    scale_factor = SCREEN_HEIGHT / original_bg.get_height()
    new_bg_width = int(original_bg.get_width() * scale_factor)
    bg_image = pygame.transform.scale(original_bg, (new_bg_width, SCREEN_HEIGHT))

MAP_WIDTH = bg_image.get_width()
MAP_HEIGHT = bg_image.get_height()

floor_y = int(MAP_HEIGHT * FLOOR_HEIGHT_PERCENTAGE)

player = Player(floor_y)
all_sprites = pygame.sprite.Group(player)
camera = Camera(MAP_WIDTH, MAP_HEIGHT, SCREEN_WIDTH, SCREEN_HEIGHT)

# --- Main Game Loop ---
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

    player.update(MAP_WIDTH)
    camera.update(player)

    screen.fill((0, 0, 0)) 
    screen.blit(bg_image, (camera.camera.x, camera.camera.y))
    screen.blit(player.image, camera.apply(player))

    pygame.display.flip()
    clock.tick(60)
