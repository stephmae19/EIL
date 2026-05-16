import pygame
import sys
import os
import math

# --- 1. YOUR FILENAMES ---
WALK_FILE = "player_walk.jpg.jpg" 
IDLE_FILE = "player_idle.jpg.jpg"
BG_FILE = "received_836993658930381.webp"
ENEMY_FILE = "692179759_1338677191657438_512528723751180050_n.jpg"

# --- 2. EASY TWEAK VARIABLES ---
FLOOR_HEIGHT_PERCENTAGE = 0.74 
JPG_BLACK_TOLERANCE = 35 

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
        x = -target.rect.centerx + int(self.screen_w / 2)
        y = 0 
        x = min(0, x)  
        x = max(-(self.width - self.screen_w), x)  
        self.camera = pygame.Rect(x, y, self.width, self.height)


class BookshelfZone:
    def __init__(self, x, bottom_y, flavor_text):
        self.rect = pygame.Rect(x, bottom_y - 250, 150, 250)
        self.already_searched = False
        self.flavor_text = flavor_text


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
        # Bulletproof Fallback: If image fails, create safe squares
        if not os.path.exists(filename):
            print(f"--- WARNING: Could not find {filename} ---")
            safe_surface = pygame.Surface((40, 40))
            safe_surface.fill((50, 150, 255) if is_player else (255, 50, 50))
            return [safe_surface]
        
        try:
            sheet = pygame.image.load(filename).convert_alpha()
            
            # The Safe JPG Cleaner
            pixel_array = pygame.PixelArray(sheet)
            for x in range(sheet.get_width()):
                for y in range(sheet.get_height()):
                    color = sheet.unmap_rgb(pixel_array[x, y])
                    if color.r <= JPG_BLACK_TOLERANCE and color.g <= JPG_BLACK_TOLERANCE and color.b <= JPG_BLACK_TOLERANCE:
                        # (0,0,0,0) is standard RGBA for transparent, much safer than hex codes
                        pixel_array[x, y] = (0, 0, 0, 0) 
            del pixel_array 
            
            w = sheet.get_width() // cols
            h = sheet.get_height() // rows
            frames = []
            
            for r in range(rows):
                for c in range(cols):
                    original_frame = sheet.subsurface(pygame.Rect(c * w, r * h, w, h))
                    scaled_w = int(w * 0.45)
                    scaled_h = int(h * 0.45)
                    scaled_frame = pygame.transform.scale(original_frame, (scaled_w, scaled_h))
                    frames.append(scaled_frame)
            return frames
            
        except Exception as e:
            print(f"--- ERROR LOADING {filename}: {e} ---")
            safe_surface = pygame.Surface((40, 40))
            safe_surface.fill((255, 0, 255))
            return [safe_surface]

    def take_damage(self):
        self.hit_timer = pygame.time.get_ticks() + 250

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

        if self.rect.left < 0: 
            self.rect.left = 0
        if self.rect.right > map_width: 
            self.rect.right = map_width

    def animate(self):
        now = pygame.time.get_ticks()
        
        if self.is_moving:
            self.current_frames = self.walk_frames
            if self.is_running:
                self.frame_duration = 1000 // 36
            else:
                self.frame_duration = 1000 // 20
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
            self.image.fill((200, 0, 0), special_flags=pygame.BLEND_RGB_ADD)


class Enemy(pygame.sprite.Sprite):
    def __init__(self, start_x, start_y, target_width, target_height):
        super().__init__()
        
        self.enemy_w = int(target_width * 1.03)
        self.enemy_h = int(target_height * 1.03)
        
        self.all_frames = self.load_frames(ENEMY_FILE, 8, 6)
        
        # Safe slicing in case image failed to load and returned 1 safe frame
        if len(self.all_frames) >= 48:
            self.chase_frames = self.all_frames[0:6]
            self.attack_frames = self.all_frames[6:] 
        else:
            self.chase_frames = self.all_frames
            self.attack_frames = self.all_frames

        self.state = "chase"
        self.current_frames = self.chase_frames
        self.frame_index = 0
        self.image = self.current_frames[self.frame_index]
        self.rect = self.image.get_rect(center=(start_x, start_y))

        self.base_y = start_y
        self.speed = 3
        self.facing_right = True
        
        self.last_update = pygame.time.get_ticks()
        self.frame_duration = 1000 // 15 
        self.attack_cooldown = 0 

    def load_frames(self, filename, rows, cols):
        if not os.path.exists(filename):
            print(f"--- WARNING: Could not find {filename} ---")
            surf = pygame.Surface((self.enemy_w, self.enemy_h))
            surf.fill((200, 50, 50))
            return [surf]
        
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
                    original_frame = sheet.subsurface(pygame.Rect(c * w, r * h, w, h))
                    scaled_frame = pygame.transform.scale(original_frame, (self.enemy_w, self.enemy_h))
                    frames.append(scaled_frame)
            return frames
        except Exception as e:
            print(f"--- ERROR LOADING {filename}: {e} ---")
            surf = pygame.Surface((self.enemy_w, self.enemy_h))
            surf.fill((255, 0, 0))
            return [surf]

    def update(self, player):
        now = pygame.time.get_ticks()
        dist_x = player.rect.centerx - self.rect.centerx

        # Bobbing floating logic
        self.rect.centery = self.base_y + int(math.sin(now / 200.0) * 15)

        if self.state == "chase":
            if abs(dist_x) > 140: 
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
        
        if now - self.last_update > self.frame_duration:
            self.last_update = now
            self.frame_index += 1

            if self.frame_index >= len(self.current_frames):
                if self.state == "attack":
                    self.state = "chase"
                    self.current_frames = self.chase_frames
                    self.attack_cooldown = now + 5000 # 5 Seconds Cooldown
                self.frame_index = 0

            # Only trigger damage if we have enough attack frames loaded
            if self.state == "attack" and len(self.current_frames) > 8:
                if self.frame_index == len(self.current_frames) - 8:
                    if abs(player.rect.centerx - self.rect.centerx) < 180: 
                        player.take_damage()

            raw_image = self.current_frames[self.frame_index]
            if not self.facing_right:
                self.image = pygame.transform.flip(raw_image, True, False)
            else:
                self.image = raw_image


# --- Initialization & Setup ---
pygame.init()
pygame.font.init() 

screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
SCREEN_WIDTH = screen.get_width()
SCREEN_HEIGHT = screen.get_height()
clock = pygame.time.Clock()

ui_font = pygame.font.SysFont("arial", 28, bold=True)
feedback_font = pygame.font.SysFont("arial", 28, italic=True)

# Safe Background Loading
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

bookshelves = [
    BookshelfZone(x=300, bottom_y=floor_y, flavor_text="You found a dusty book on ancient magic."),
    BookshelfZone(x=800, bottom_y=floor_y, flavor_text="Just cobwebs and blank pages..."),
    BookshelfZone(x=1300, bottom_y=floor_y, flavor_text="You found a diary belonging to a lost scholar.")
]

player = Player(floor_y)

# Enemy starts slightly above the floor
enemy = Enemy(start_x=200, start_y=floor_y - 80, 
              target_width=player.rect.width, 
              target_height=player.rect.height) 

camera = Camera(MAP_WIDTH, MAP_HEIGHT, SCREEN_WIDTH, SCREEN_HEIGHT)

feedback_msg = ""
feedback_timer = 0

# --- Main Game Loop ---
running = True
while running:
    now = pygame.time.get_ticks()
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
            
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            running = False

        if event.type == pygame.KEYDOWN and event.key == pygame.K_e:
            found_something = False
            for shelf in bookshelves:
                if player.rect.colliderect(shelf.rect):
                    found_something = True
                    if shelf.already_searched:
                        feedback_msg = "You already searched this shelf."
                    else:
                        shelf.already_searched = True
                        feedback_msg = shelf.flavor_text 
                    feedback_timer = now + 3000 
                    break 

            if not found_something:
                feedback_msg = "There is nothing to interact with here."
                feedback_timer = now + 1500

    # 1. Update Game State
    player.update(MAP_WIDTH)
    enemy.update(player) 
    camera.update(player)

    # 2. Draw Background
    screen.fill((0, 0, 0)) 
    screen.blit(bg_image, (camera.camera.x, camera.camera.y))

    # 3. Draw Characters
    screen.blit(enemy.image, camera.apply(enemy))
    screen.blit(player.image, camera.apply(player))

    # 4. Draw Interaction Prompts
    for shelf in bookshelves:
        if player.rect.colliderect(shelf.rect):
            prompt_text = ui_font.render("Press 'E' to Search", True, (255, 255, 200))
            prompt_rect = prompt_text.get_rect(midbottom=(shelf.rect.centerx, shelf.rect.top - 20))
            screen.blit(prompt_text, camera.apply_rect(prompt_rect))

    # 5. Draw UI Feedback
    if now < feedback_timer:
        msg_surface = feedback_font.render(feedback_msg, True, (150, 255, 150))
        msg_rect = msg_surface.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 80))
        screen.blit(msg_surface, msg_rect)

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()
