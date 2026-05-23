import pygame
import sys
import os

# --- GAME SETTINGS ---
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60

# --- EXACT FILENAMES ---
# Make sure these 4 files are in the exact same folder as this Python script!
BG_FILE = "chapter1_level1.jpg"
WALK_FILE = "player_walk.jpg.jpg" 
IDLE_FILE = "player_idle.jpg.jpg"
ENEMY_FILE = "692179759_1338677191657438_512528723751180050_n.jpg"

# Colors
TEXT_COLOR = (255, 255, 255)
UI_BOX_COLOR = (20, 20, 25, 230)
PROMPT_COLOR = (255, 255, 100)

# --- HELPER FUNCTION: LOAD SPRITES ---
def load_sprite_sheet(filename, rows, cols, scale_factor, bg_threshold=40):
    """Loads a sprite sheet, removes the dark JPEG background, and splits it into frames."""
    if not os.path.exists(filename):
        print(f"WARNING: Missing {filename}. Using a colored box instead.")
        safe = pygame.Surface((50, 80))
        safe.fill((255, 0, 255)) 
        return [safe]

    try:
        sheet = pygame.image.load(filename).convert_alpha()
        
        # Remove dark background (JPEG artifact cleanup)
        sheet.lock()
        for x in range(sheet.get_width()):
            for y in range(sheet.get_height()):
                color = sheet.get_at((x, y))
                if color.r < bg_threshold and color.g < bg_threshold and color.b < bg_threshold:
                    sheet.set_at((x, y), (0, 0, 0, 0)) # Make transparent
        sheet.unlock()
        
        w = sheet.get_width() // cols
        h = sheet.get_height() // rows
        frames = []
        for r in range(rows):
            for c in range(cols):
                original_frame = sheet.subsurface(pygame.Rect(c * w, r * h, w, h))
                scaled = pygame.transform.scale(original_frame, (int(w * scale_factor), int(h * scale_factor)))
                frames.append(scaled)
        return frames
    except Exception as e:
        print(f"ERROR loading {filename}: {e}")
        safe = pygame.Surface((50, 80))
        safe.fill((255, 0, 255))
        return [safe]

# --- CLASSES ---
class Camera:
    def __init__(self, width, height):
        self.camera = pygame.Rect(0, 0, width, height)
        self.width = width
        self.height = height

    def apply(self, entity):
        return entity.rect.move(self.camera.topleft)

    def update(self, target):
        x = -target.rect.centerx + int(SCREEN_WIDTH / 2)
        x = min(0, x) # Don't scroll past left edge
        x = max(-(self.width - SCREEN_WIDTH), x) # Don't scroll past right edge
        self.camera = pygame.Rect(x, 0, self.width, self.height)

class InteractableZone(pygame.sprite.Sprite):
    def __init__(self, x, y, width, height, message):
        super().__init__()
        self.image = pygame.Surface((width, height), pygame.SRCALPHA)
        # Change the '100' below to '0' to make the green zones invisible in your final game!
        self.image.fill((0, 255, 0, 100)) 
        self.rect = self.image.get_rect(topleft=(x, y))
        self.message = message

    def update(self, player, screen, camera, game_state, font):
        # Check if player is touching this zone
        if self.rect.colliderect(player.rect):
            # Draw "E to Read"
            prompt_surf = font.render("E to Read", True, PROMPT_COLOR)
            prompt_x = player.rect.centerx + camera.camera.x
            prompt_y = player.rect.top + camera.camera.y - 30
            prompt_rect = prompt_surf.get_rect(midbottom=(prompt_x, prompt_y))
            screen.blit(prompt_surf, prompt_rect)

            keys = pygame.key.get_pressed()
            if keys[pygame.K_e]:
                game_state['active_message'] = self.message

class Projectile(pygame.sprite.Sprite):
    def __init__(self, x, y, facing_right):
        super().__init__()
        self.image = pygame.Surface((20, 8), pygame.SRCALPHA)
        self.image.fill((100, 200, 255)) 
        self.rect = self.image.get_rect(center=(x, y))
        self.speed = 10
        self.facing_right = facing_right

    def update(self):
        if self.facing_right:
            self.rect.x += self.speed
        else:
            self.rect.x -= self.speed

class Player(pygame.sprite.Sprite):
    def __init__(self, floor_y):
        super().__init__()
        self.floor_y = floor_y
        
        # Load 5x5 sprite sheets
        self.walk_frames = load_sprite_sheet(WALK_FILE, 5, 5, 1.5)
        self.idle_frames = load_sprite_sheet(IDLE_FILE, 5, 5, 1.5)
        
        self.current_frames = self.idle_frames
        self.frame_index = 0
        self.image = self.current_frames[self.frame_index]
        self.rect = self.image.get_rect(midbottom=(400, floor_y))
        
        self.speed = 5 
        self.facing_right = True
        self.is_moving = False
        
        self.last_update = pygame.time.get_ticks()
        self.frame_duration = 1000 // 12

    def update(self, map_width, game_state):
        keys = pygame.key.get_pressed()
        self.is_moving = False
        
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.rect.x -= self.speed
            self.facing_right = False
            self.is_moving = True
            game_state['active_message'] = None 
            
        elif keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.rect.x += self.speed
            self.facing_right = True
            self.is_moving = True
            game_state['active_message'] = None 

        # Screen boundaries
        if self.rect.left < 0: self.rect.left = 0
        if self.rect.right > map_width: self.rect.right = map_width

        # Animation logic
        now = pygame.time.get_ticks()
        self.current_frames = self.walk_frames if self.is_moving else self.idle_frames
        
        if now - self.last_update > self.frame_duration:
            self.last_update = now
            self.frame_index = (self.frame_index + 1) % len(self.current_frames)
            
        raw_image = self.current_frames[self.frame_index]
        if not self.facing_right:
            self.image = pygame.transform.flip(raw_image, True, False)
        else:
            self.image = raw_image

        self.rect = self.image.get_rect(midbottom=(self.rect.centerx, self.floor_y))

class Enemy(pygame.sprite.Sprite):
    def __init__(self, start_x, floor_y):
        super().__init__()
        self.floor_y = floor_y - 15 # Nudge up slightly
        
        # Load 8x6 sprite sheet
        self.all_frames = load_sprite_sheet(ENEMY_FILE, 8, 6, 1.5, bg_threshold=50)
        
        if len(self.all_frames) >= 48:
            self.chase_frames = self.all_frames[0:24]
            self.attack_frames = self.all_frames[30:48]
        else:
            self.chase_frames = self.all_frames
            self.attack_frames = self.all_frames

        self.state = "chase"
        self.current_frames = self.chase_frames
        self.frame_index = 0
        self.image = self.current_frames[self.frame_index]
        self.rect = self.image.get_rect(midbottom=(start_x, self.floor_y))

        self.speed = 2 
        self.facing_right = True
        self.last_update = pygame.time.get_ticks()
        self.frame_duration = 1000 // 8 
        self.attack_cooldown_timer = pygame.time.get_ticks() + 2000 
        self.has_fired_blast = False

    def update(self, player, projectile_group):
        now = pygame.time.get_ticks()
        dist_x = player.rect.centerx - self.rect.centerx

        if self.state == "chase":
            self.frame_duration = 1000 // 8 
            if abs(dist_x) > 180: 
                if dist_x > 0:
                    self.rect.x += self.speed
                    self.facing_right = True
                else:
                    self.rect.x -= self.speed
                    self.facing_right = False
