import pygame
import sys
import os

# --- 1. YOUR FILENAMES ---
WALK_FILE = "player_walk.jpg.jpg" 
IDLE_FILE = "player_idle.jpg.jpg"
BG_FILE = "received_836993658930381.webp"
# Your newly uploaded enemy image
ENEMY_FILE = "690856840_1447199653826161_7446595274037957518_n.jpg"

# --- 2. EASY TWEAK VARIABLES ---
FLOOR_HEIGHT_PERCENTAGE = 0.74 
JPG_BLACK_TOLERANCE = 40 # Increased slightly to catch more compression artifacts

class Camera:
    def __init__(self, width, height, screen_w, screen_h):
        self.camera = pygame.Rect(0, 0, width, height)
        self.width = width
        self.height = height
        self.screen_w = screen_w
        self.screen_h = screen_h

    def apply(self, entity):
        return entity.rect.move(self.camera.topleft)
        
    def apply_rect(self, rect):
        return rect.move(self.camera.topleft)

    def update(self, target):
        desired_x = -target.rect.centerx + int(self.screen_w / 2)
        # Smooth gliding camera so you can clearly see both characters running
        self.camera.x += (desired_x - self.camera.x) * 0.1
        self.camera.y = 0 
        
        self.camera.x = min(0, self.camera.x)  
        self.camera.x = max(-(self.width - self.screen_w), self.camera.x)  

class Projectile(pygame.sprite.Sprite):
    def __init__(self, x, y, facing_right):
        super().__init__()
        self.image = pygame.Surface((35, 12), pygame.SRCALPHA)
        self.image.fill((100, 200, 255, 200)) # Glowing blue blast
        self.rect = self.image.get_rect(center=(x, y))
        self.speed = 14
        self.facing_right = facing_right

    def update(self):
        if self.facing_right:
            self.rect.x += self.speed
        else:
            self.rect.x -= self.speed

class Player(pygame.sprite.Sprite):
    def __init__(self, floor_y):
        super().__init__()
        self.walk_frames = self.load_frames(WALK_FILE, 5, 5, is_player=True)
        self.idle_frames = self.load_frames(IDLE_FILE, 5, 5, is_player=True)

        self.current_frames = self.idle_frames
        self.frame_index = 0
        self.image = self.current_frames[self.frame_index]
        self.rect = self.image.get_rect(midbottom=(400, floor_y))
        
        self.walk_speed = 4    
        self.run_speed = 9     
        self.speed = self.walk_speed 
        
        self.facing_right = True
        self.is_moving = False
        self.is_running = False 
        
        self.last_update = pygame.time.get_ticks()
        self.frame_duration = 1000 // 12
        self.hit_timer = 0

    def load_frames(self, filename, rows, cols, is_player=True):
        if not os.path.exists(filename):
            safe = pygame.Surface((40, 40))
            safe.fill((50, 150, 255) if is_player else (255, 50, 50))
            return [safe]
        try:
            sheet = pygame.image.load(filename).convert_alpha()
            pixel_array = pygame.PixelArray(sheet)
            for x in range(sheet.get_width()):
                for y in range(sheet.get_height()):
                    color = sheet.unmap_rgb(pixel_array[x, y])
                    if color.r <= JPG_BLACK_TOLERANCE and color.g <= JPG_BLACK_TOLERANCE and color.b <= JPG_BLACK_TOLERANCE:
                        pixel_array[x, y] = (0, 0, 0, 0) 
            del pixel_array 
            
            w = sheet.get_width() // cols
            h = sheet.get_height() // rows
            frames = []
            
            for r in range(rows):
                for c in range(cols):
                    original = sheet.subsurface(pygame.Rect(c * w, r * h, w, h))
                    scaled_w = int(w * 0.45)
                    scaled_h = int(h * 0.45)
                    scaled = pygame.transform.scale(original, (scaled_w, scaled_h))
                    frames.append(scaled)
            return frames
        except Exception:
            safe = pygame.Surface((40, 40))
            safe.fill((255, 0, 255))
            return [safe]

    def take_damage(self):
        # Glow red for EXACTLY 1 second (1000 ms)
        self.hit_timer = pygame.time.get_ticks() + 1000

    def update_logic(self, map_width):
        keys = pygame.key.get_pressed()
        self.is_moving = False
        self.is_running = False
        
        if keys[pygame.K_LSHIFT] or keys[pygame.K_RSHIFT]:
            self.is_running = True
            self.speed = self.run_speed
        else:
            self.is_running = False
            self.speed = self.walk_speed
        
        if keys[pygame.K_LEFT]:
            self.rect.x -= self.speed
            self.facing_right = False
            self.is_moving = True
        elif keys[pygame.K_RIGHT]:
            self.rect.x += self.speed
            self.facing_right = True
            self.is_moving = True

        if self.rect.left < 0: self.rect.left = 0
        if self.rect.right > map_width: self.rect.right = map_width

    def animate(self):
        now = pygame.time.get_ticks()
        
        if self.is_moving:
            self.current_frames = self.walk_frames
            self.frame_duration = 1000 // 36 if self.is_running else 1000 // 20
        else:
            self.current_frames = self.idle_frames
            self.frame_duration = 1000 // 12

        if now - self.last_update > self.frame_duration:
            self.last_update = now
            self.frame_index = (self.frame_index + 1) % len(self.current_frames)
            
        raw_image = self.current_frames[self.frame_index]
        
        if not self.facing_right:
            self.image = pygame.transform.flip(raw_image, True, False)
        else:
            self.image = raw_image.copy() 

        if now < self.hit_timer:
            self.image.fill((255, 0, 0), special_flags=pygame.BLEND_RGB_ADD)


class Enemy(pygame.sprite.Sprite):
    def __init__(self, start_x, floor_y, target_width, target_height):
        super().__init__()
        
        self.enemy_w = int(target_width * 1.03)
        self.enemy_h = int(target_height * 1.03)
        
        # New sprite sheet is 3 rows, 4 columns
        self.run_frames = self.load_frames(ENEMY_FILE, 3, 4)
        
        self.frame_index = 0
        self.image = self.run_frames[self.frame_index]
        
        # GROUNDED: Places the enemy's feet on the exact same tile line as the player
        self.rect = self.image.get_rect(midbottom=(start_x, floor_y))

        self.speed = 6 # Chase speed
        self.facing_right = True
        
        self.last_update = pygame.time.get_ticks()
        self.frame_duration = 1000 // 18 
        
        self.attack_cooldown = pygame.time.get_ticks() + 3000 # Wait 3s before first shot

    def load_frames(self, filename, rows, cols):
        if not os.path.exists(filename):
            surf = pygame.Surface((self.enemy_w, self.enemy_h))
            surf.fill((0, 0, 0))
            return [surf]
        try:
            sheet = pygame.image.load(filename).convert_alpha()
            pixel_array = pygame.PixelArray(sheet)
            for x in range(sheet.get_width()):
                for y in range(sheet.get_height()):
                    color = sheet.unmap_rgb(pixel_array[x, y])
                    # If it is dark background...
                    if color.r <= JPG_BLACK_TOLERANCE and color.g <= JPG_BLACK_TOLERANCE and color.b <= JPG_BLACK_TOLERANCE:
                        pixel_array[x, y] = (0, 0, 0, 0) # Make transparent
                    else:
                        # PURE BLACK SILHOUETTE: Force all entity pixels to be solid black
                        pixel_array[x, y] = (0, 0, 0, 255) 
            del pixel_array 
            
            w = sheet.get_width() // cols
            h = sheet.get_height() // rows
            frames = []
            for r in range(rows):
                for c in range(cols):
                    original = sheet.subsurface(pygame.Rect(c * w, r * h, w, h))
                    scaled = pygame.transform.scale(original, (self.enemy_w, self.enemy_h))
                    frames.append(scaled)
            return frames
        except Exception:
            surf = pygame.Surface((self.enemy_w, self.enemy_h))
            surf.fill((0, 0, 0))
            return [surf]

    def update(self, player, projectile_group):
        now = pygame.time.get_ticks()
        dist_x = player.rect.centerx - self.rect.centerx

        # --- GROUNDED CHASE LOGIC ---
        # The enemy actively runs left and right to catch you
        if abs(dist_x) > 10: # Small buffer so it doesn't vibrate when touching player
            if dist_x > 0:
                self.rect.x += self.speed
                self.facing_right = True
            else:
                self.rect.x -= self.speed
                self.facing_right = False
        
        # --- BLAST ATTACK LOGIC ---
        if now > self.attack_cooldown:
            # Fire a blast
            blast = Projectile(self.rect.centerx, self.rect.centery, self.facing_right)
            projectile_group.add(blast)
            # 5-Second Cooldown before it can shoot again
            self.attack_cooldown = now + 5000 
        
        # --- ANIMATION LOGIC ---
        if now - self.last_update > self.frame_duration:
            self.last_update = now
            self.frame_index = (self.frame_index + 1) % len(self.run_frames)

            raw_image = self.run_frames[self.frame_index]
            if not self.facing_right:
                self.image = pygame.transform.flip(raw_image, True, False)
            else:
                self.image = raw_image


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

# Spawn enemy grounded to the same floor_y as the player
enemy = Enemy(start_x=100, floor_y=floor_y, target_width=player.rect.width, target_height=player.rect.height) 

camera = Camera(MAP_WIDTH, MAP_HEIGHT, SCREEN_WIDTH, SCREEN_HEIGHT)
projectiles = pygame.sprite.Group()

# --- Main Game Loop ---
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            running = False

    # 1. Update Entities
    player.update(MAP_WIDTH)
    enemy.update(player, projectiles) 
    projectiles.update() 
    camera.update(player)

    # 2. Hit Detection (Projectiles vs Player)
    for blast in projectiles:
        if player.rect.colliderect(blast.rect):
            player.take_damage() # This triggers the exactly 1-second red glow
            blast.kill()

    # 3. Draw Background
    screen.fill((0, 0, 0)) 
    screen.blit(bg_image, (camera.camera.x, camera.camera.y))

    # 4. Draw Characters
    # Draw enemy first so player appears "in front" if they cross paths
    screen.blit(enemy.image, camera.apply(enemy))
    screen.blit(player.image, camera.apply(player))
    
    for blast in projectiles:
        screen.blit(blast.image, camera.apply(blast))

    # 5. Refresh Screen
    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()
