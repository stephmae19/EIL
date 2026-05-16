import pygame
import sys
import os

# --- 1. EXACT FILENAMES ---
WALK_FILE = "player_walk.jpg.jpg" 
IDLE_FILE = "player_idle.jpg.jpg"
BG_FILE = "received_836993658930381.webp"
ENEMY_FILE = "692179759_1338677191657438_512528723751180050_n.jpg"

# --- 2. TWEAK VARIABLES ---
FLOOR_HEIGHT_PERCENTAGE = 0.74 
FPS = 60
ENEMY_Y_OFFSET = -15 

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
        # Smooth camera glide
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
        self.speed = 12
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
        self.walk_frames = self.load_frames(WALK_FILE, 5, 5)
        self.idle_frames = self.load_frames(IDLE_FILE, 5, 5)

        self.current_frames = self.idle_frames
        self.frame_index = 0
        self.image = self.current_frames[self.frame_index]
        self.rect = self.image.get_rect(midbottom=(400, self.floor_y))
        
        self.walk_speed = 5    
        self.run_speed = 9     
        self.speed = self.walk_speed 
        
        self.facing_right = True
        self.is_moving = False
        self.is_running = False 
        
        self.last_update = pygame.time.get_ticks()
        self.frame_duration = 1000 // 12
        self.hit_timer = 0

    def load_frames(self, filename, rows, cols):
        if not os.path.exists(filename):
            safe = pygame.Surface((40, 40))
            safe.fill((50, 150, 255))
            return [safe]
        try:
            sheet = pygame.image.load(filename).convert_alpha()
            pixel_array = pygame.PixelArray(sheet)
            for x in range(sheet.get_width()):
                for y in range(sheet.get_height()):
                    color = sheet.unmap_rgb(pixel_array[x, y])
                    # Player uses simple tolerance since its colors are bright
                    if color.r <= 45 and color.g <= 45 and color.b <= 45:
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
        
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.rect.x -= self.speed
            self.facing_right = False
            self.is_moving = True
            
        elif keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.rect.x += self.speed
            self.facing_right = True
            self.is_moving = True

        if self.rect.left < 0: self.rect.left = 0
        if self.rect.right > map_width: self.rect.right = map_width

    def animate(self):
        now = pygame.time.get_ticks()
        
        if self.is_moving:
            if self.current_frames != self.walk_frames:
                self.current_frames = self.walk_frames
                self.frame_index = 0
            self.frame_duration = 1000 // 30 if self.is_running else 1000 // 16
        else:
            if self.current_frames != self.idle_frames:
                self.current_frames = self.idle_frames
                self.frame_index = 0
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

    def update(self, map_width):
        self.update_logic(map_width)
        self.animate()
        self.rect.midbottom = (self.rect.centerx, self.floor_y)


class Enemy(pygame.sprite.Sprite):
    def __init__(self, start_x, floor_y, target_width, target_height):
        super().__init__()
        
        self.enemy_w = int(target_width * 1.03)
        self.enemy_h = int(target_height * 1.03)
        
        self.floor_y = floor_y + ENEMY_Y_OFFSET
        self.all_frames = self.load_frames(ENEMY_FILE, 8, 6)
        
        if len(self.all_frames) >= 48:
            self.chase_frames = self.all_frames[0:6]
            self.attack_frames = self.all_frames[6:48]
        else:
            self.chase_frames = self.all_frames
            self.attack_frames = self.all_frames

        self.state = "chase"
        self.current_frames = self.chase_frames
        self.frame_index = 0
        self.image = self.current_frames[self.frame_index]
        
        self.rect = self.image.get_rect(midbottom=(start_x, self.floor_y))

        self.speed = 3 
        self.facing_right = True
        
        self.last_update = pygame.time.get_ticks()
        self.frame_duration = 1000 // 8 
        self.attack_cooldown = pygame.time.get_ticks() + 2000
        self.has_fired = False

    def load_frames(self, filename, rows, cols):
        if not os.path.exists(filename):
            surf = pygame.Surface((self.enemy_w, self.enemy_h))
            surf.fill((0, 0, 0))
            return [surf]
        try:
            sheet = pygame.image.load(filename).convert_alpha()
            pixel_array = pygame.PixelArray(sheet)
            
            # --- THE ULTIMATE DISTANCE ALGORITHM FIX ---
            # Grab the exact background color from the top left corner
            bg_color = sheet.unmap_rgb(pixel_array[0, 0])
            bg_r, bg_g, bg_b = bg_color.r, bg_color.g, bg_color.b
            
            for x in range(sheet.get_width()):
                for y in range(sheet.get_height()):
                    color = sheet.unmap_rgb(pixel_array[x, y])
                    r, g, b = color.r, color.g, color.b
                    
                    # 1. Keep bright glowing pixels (eyes and blast)
                    if r > 100 or g > 100 or b > 100:
                        continue 
                        
                    # 2. Calculate if the pixel is closer to the Background OR closer to Pure Black
                    dist_to_bg = abs(r - bg_r) + abs(g - bg_g) + abs(b - bg_b)
                    dist_to_black = r + g + b # Distance from (0,0,0)
                    
                    if dist_to_bg < dist_to_black:
                        # Closer to background -> Make 100% Transparent
                        pixel_array[x, y] = (0, 0, 0, 0)
                    else:
                        # Closer to pure black -> Make Solid Opaque Black (The Body)
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

        if self.state == "chase":
            self.frame_duration = 1000 // 8 
            if abs(dist_x) > 180: 
                if dist_x > 0:
                    self.rect.x += self.speed
                    self.facing_right = True
                else:
                    self.rect.x -= self.speed
                    self.facing_right = False
            else:
                if now > self.attack_cooldown:
                    self.state = "attack"
                    self.frame_index = 0
                    self.current_frames = self.attack_frames
                    self.has_fired = False
        
        if self.state == "attack":
            self.frame_duration = 1000 // 15 

        if now - self.last_update > self.frame_duration:
            self.last_update = now
            self.frame_index += 1

            if self.frame_index >= len(self.current_frames):
                if self.state == "attack":
                    self.state = "chase"
                    self.current_frames = self.chase_frames
                    self.attack_cooldown = now + 4000 
                self.frame_index = 0

            if self.state == "attack" and len(self.current_frames) > 10:
                if self.frame_index == len(self.current_frames) - 6 and not self.has_fired:
                    blast = Projectile(self.rect.centerx, self.rect.centery, self.facing_right)
                    projectile_group.add(blast)
                    self.has_fired = True

            raw_image = self.current_frames[self.frame_index]
            if not self.facing_right:
                self.image = pygame.transform.flip(raw_image, True, False)
            else:
                self.image = raw_image
                
        # Lock enemy to its unique offset floor line
        self.rect.midbottom = (self.rect.centerx, self.floor_y)


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

    # 2. Hit Detection
    for blast in projectiles:
        if player.rect.colliderect(blast.rect):
            player.take_damage() 
            blast.kill()

    # 3. Draw Background
    screen.fill((0, 0, 0)) 
    screen.blit(bg_image, (camera.camera.x, camera.camera.y))

    # 4. Draw Characters
    screen.blit(enemy.image, camera.apply(enemy))
    screen.blit(player.image, camera.apply(player))
    
    for blast in projectiles:
        screen.blit(blast.image, camera.apply(blast))

    # 5. Refresh Screen
    pygame.display.flip()
    clock.tick(FPS)

pygame.quit()
sys.exit()
