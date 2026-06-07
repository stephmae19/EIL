import pygame
import sys
import os

# --- 1. EXACT FILENAMES ---
WALK_FILE = "Assets/Characters/player_walk.png"
IDLE_FILE = "Assets/Characters/player_idle.png"
BG_FILE = "Assets/Maps/chapter1_level1.png"
ENEMY_FILE = "Assets/Characters/entity.jpeg"

# --- 2. TWEAK VARIABLES ---
FLOOR_HEIGHT_PERCENTAGE = 0.74 
FPS = 60

# Nudge the enemy up/down so their feet perfectly match the player's tiles
ENEMY_Y_OFFSET = -15 

# Color definitions for interaction prompt and text box
SHELF_TEXT_COLOR = (255, 255, 255) # White
SHELF_BOX_COLOR = (40, 40, 40, 200) # Semi-transparent dark grey
PROMPT_COLOR = (255, 255, 100) # Yellow for the "E to Read" prompt

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
        
        # Keep camera inside bounds
        self.camera.x = min(0, self.camera.x)  
        max_scroll = max(0, self.width - self.screen_w)
        self.camera.x = max(-max_scroll, self.camera.x)  

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
            print(f"MISSING FILE: {filename}")
            safe = pygame.Surface((40, 40))
            safe.fill((0, 255, 0)) 
            return [safe]
        try:
            sheet = pygame.image.load(filename).convert_alpha()
            
            sheet.lock()
            for x in range(sheet.get_width()):
                for y in range(sheet.get_height()):
                    r, g, b, a = sheet.get_at((x, y))
                    if r <= 50 and g <= 50 and b <= 50:
                        sheet.set_at((x, y), (0, 0, 0, 0)) # Transparent background
            sheet.unlock()
            
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
        except Exception as e:
            print(f"ERROR LOADING PLAYER: {e}")
            safe = pygame.Surface((40, 40))
            safe.fill((0, 255, 0)) 
            return [safe]

    def take_damage(self):
        self.hit_timer = pygame.time.get_ticks() + 1000

    def update_logic(self, map_width, global_game_state): # Pass game state to clear text
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
            global_game_state['active_message'] = None # Clear text box on move
            
        elif keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.rect.x += self.speed
            self.facing_right = True
            self.is_moving = True
            global_game_state['active_message'] = None # Clear text box on move

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

    def update(self, map_width, global_game_state):
        self.update_logic(map_width, global_game_state)
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
            print(f"MISSING FILE: {filename}")
            surf = pygame.Surface((self.enemy_w, self.enemy_h))
            surf.fill((0, 255, 0)) 
            return [surf]
        try:
            sheet = pygame.image.load(filename).convert_alpha()
            
            sheet.lock()
            for x in range(sheet.get_width()):
                for y in range(sheet.get_height()):
                    r, g, b, a = sheet.get_at((x, y))
                    
                    if r > 80 or g > 80 or b > 80:
                        continue 
                        
                    elif r <= 15 and g <= 15 and b <= 15:
                        sheet.set_at((x, y), (0, 0, 0, 255)) 
                        
                    else:
                        sheet.set_at((x, y), (0, 0, 0, 0)) # Transparent

            sheet.unlock()
            
            w = sheet.get_width() // cols
            h = sheet.get_height() // rows
            frames = []
            for r in range(rows):
                for c in range(cols):
                    original = sheet.subsurface(pygame.Rect(c * w, r * h, w, h))
                    scaled = pygame.transform.scale(original, (self.enemy_w, self.enemy_h))
                    frames.append(scaled)
            return frames
            
        except Exception as e:
            print(f"ERROR LOADING ENEMY: {e}")
            surf = pygame.Surface((self.enemy_w, self.enemy_h))
            surf.fill((0, 255, 0)) 
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
                
        self.rect.midbottom = (self.rect.centerx, self.floor_y)

# --- 3. NEW OBJECT CLASS: BOOKSHELF ---
class Bookshelf(pygame.sprite.Sprite):
    def __init__(self, x, floor_y, width=64, height=128, message="You found a book!"):
        super().__init__()
        # Instead of an image file, we use a simple brown rectangle for this code
        # You can replace this with pygame.image.load("bookshelf.png").convert_alpha()
        self.image = pygame.Surface((width, height))
        self.image.fill((101, 67, 33)) # Brown
        # To make the interaction clear, let's add a slight lighter edge
        pygame.draw.rect(self.image, (139, 94, 60), (0, 0, width, height), 2)
        
        self.rect = self.image.get_rect(midbottom=(x, floor_y))
        
        # Unique message for this bookshelf
        self.message = message
        
        # Define an interaction zone wider than the physical hitbox
        self.interaction_rect = self.rect.inflate(80, 0) # Extend 40 pixels left and right

# --- Initialization & Setup ---
pygame.init()

# Initial state dictionary for cross-object interaction
game_state = {'active_message': None}

screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
SCREEN_WIDTH = screen.get_width()
SCREEN_HEIGHT = screen.get_height()
clock = pygame.time.Clock()

# UI Font setup
main_font = pygame.font.SysFont("Courier New", 28, bold=True)
prompt_font = pygame.font.SysFont("Courier New", 22, bold=True, italic=True)

if not os.path.exists(BG_FILE):
    bg_image = pygame.Surface((SCREEN_WIDTH * 2, SCREEN_HEIGHT))
    bg_image.fill((50, 50, 80))
else:
    original_bg = pygame.image.load(BG_FILE).convert()
    scale_factor = SCREEN_HEIGHT / original_bg.get_height()
    new_bg_width = int(original_bg.get_width() * scale_factor)
    safe_bg_width = max(new_bg_width, SCREEN_WIDTH)
    bg_image = pygame.transform.scale(original_bg, (safe_bg_width, SCREEN_HEIGHT))

MAP_WIDTH = bg_image.get_width()
MAP_HEIGHT = bg_image.get_height()
floor_y = int(MAP_HEIGHT * FLOOR_HEIGHT_PERCENTAGE)

# --- Define Book Shelf Positions and Messages ---
# Adjust these positions (X coordinates) based on MAP_WIDTH
# Since I can't see your bookshelves, I'm scattering them across the world
shelves_list = [
    Bookshelf(700, floor_y, message="The Art of Stealth - Read by a shadow..."),
    Bookshelf(1800, floor_y, message="Glitch Diary: Day 1 - Everything feels pixelated."),
    Bookshelf(2500, floor_y, message="Library Lore: The beast only moves when you aren't reading.")
]

# Create sprite group for shelves
bookshelves = pygame.sprite.Group()
for shelf in shelves_list:
    bookshelves.add(shelf)

player = Player(floor_y)
enemy = Enemy(start_x=100, floor_y=floor_y, target_width=player.rect.width, target_height=player.rect.height) 
camera = Camera(MAP_WIDTH, MAP_HEIGHT, SCREEN_WIDTH, SCREEN_HEIGHT)
projectiles = pygame.sprite.Group()

# --- Main Game Loop ---
running = True
while running:
    nearby_shelf = None # Store if player is close enough to a shelf to draw prompt

    # Clear screen tint
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                running = False
            
            # INTERACTION INPUT: If 'E' is pressed
            if event.key == pygame.K_e:
                # Loop through shelves and find the close one
                close_shelf_found = False
                for shelf in bookshelves:
                    if abs(player.rect.centerx - shelf.rect.centerx) < 70: # Standard side distance check
                        game_state['active_message'] = shelf.message
                        close_shelf_found = True
                        break # Only interact with one
                
                # Close the message if 'E' is pressed again
                if not close_shelf_found:
                     game_state['active_message'] = None


    # Proximity checking (before updates to prepare prompt)
    # This checks if player is close to ANY shelf and stores the reference
    for shelf in bookshelves:
        if abs(player.rect.centerx - shelf.rect.centerx) < 70: # Standard side distance check
            nearby_shelf = shelf
            break # Store reference to first one found

    # 1. Update Entities
    player.update(MAP_WIDTH, game_state) # Pass game state to clear text
    enemy.update(player, projectiles) 
    projectiles.update() 
    camera.update(player)

    # 2. Hit Detection
    for blast in projectiles:
        if player.rect.colliderect(blast.rect):
            player.take_damage() 
            blast.kill()
            game_state['active_message'] = None # Hit closes text boxes

    # 3. Draw Background
    screen.fill((0, 0, 0)) 
    screen.blit(bg_image, (camera.camera.x, camera.camera.y))

    # 4. Draw Characters & Objects relative to camera
    for shelf in bookshelves:
        screen.blit(shelf.image, camera.apply(shelf))

    screen.blit(enemy.image, camera.apply(enemy))
    screen.blit(player.image, camera.apply(player))
    
    for blast in projectiles:
        screen.blit(blast.image, camera.apply(blast))

    # 5. UI Draw: Prompts and Text Boxes
    
    # If the player is near a shelf and not actively reading
    if nearby_shelf and game_state['active_message'] is None:
        # Create the prompt text
        prompt_text = prompt_font.render("[E to Read]", True, PROMPT_COLOR)
        prompt_rect = prompt_text.get_rect()
        
        # Position the prompt text based on the shelf's position relative to the camera
        # Note: We position it slightly above the physical rect of the shelf object
        shelf_screen_pos = camera.apply_rect(nearby_shelf.rect)
        prompt_rect.midbottom = (shelf_screen_pos.centerx, shelf_screen_pos.top - 10)
        
        # Draw text
        screen.blit(prompt_text, prompt_rect)

    # If the player is actively reading a message
    if game_state['active_message'] is not None:
        # 1. Render the text first to find dimensions
        message_surface = main_font.render(game_state['active_message'], True, SHELF_TEXT_COLOR)
        text_rect = message_surface.get_rect()
        
        # 2. Position the text box: Center-Top of the screen, with padding
        # Define the padding around the text
        padding = 20
        # Define the main box rect
        box_width = text_rect.width + (padding * 2)
        box_height = text_rect.height + (padding * 2)
        box_x = (SCREEN_WIDTH // 2) - (box_width // 2)
        box_y = 50 # Sligthly below the top edge
        
        text_box_rect = pygame.Rect(box_x, box_y, box_width, box_height)
        
        # 3. Create semi-transparent box surface and draw it
        box_surface = pygame.Surface((box_width, box_height), pygame.SRCALPHA)
        pygame.draw.rect(box_surface, SHELF_BOX_COLOR, (0, 0, box_width, box_height), 0, 8) # Rounded corners
        screen.blit(box_surface, (box_x, box_y))
        
        # 4. Position the rendered text inside the padding of the box
        text_rect.topleft = (box_x + padding, box_y + padding)
        
        # 5. Draw the text surface
        screen.blit(message_surface, text_rect)

    # 6. Refresh Screen
    pygame.display.flip()
    clock.tick(FPS)

pygame.quit()
sys.exit()
