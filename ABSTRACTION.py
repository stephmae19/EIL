import pygame
import sys
import os

# --- 1. FILENAMES & GRID SETTINGS ---
# Set these to the exact names of your provided images
BACKDROP_FILE = "690856840_1447199653826161_7446595274037957518_n.jpg"
PLAYER_WALK_FILE = "player_walk.jpg.jpg" 
PLAYER_IDLE_FILE = "player_idle.jpg.jpg"
ENEMY_FILE = "690856840_1447199653826161_7446595274037957518_n.jpg" # Using the large multi-frame asset

# Grid dimensions for each sprite sheet (Rows x Columns)
PLAYER_GRID = (5, 5) # Assumption of a common grid based on image appearance
ENEMY_GRID = (8, 6)  # The large multi-asset sheet appears to be 8x6 frames

# --- 2. GAME VARIABLES ---
SCREEN_WIDTH = 1200
SCREEN_HEIGHT = 800
# Fixed FloorY line where feet land on the tile backdrop
FLOOR_Y = SCREEN_HEIGHT - 120 
JPG_BLACK_TOLERANCE = 45 
FPS = 60

# --- Advanced Image Processor ---

def load_enemy_silhouette(filename, target_w, target_h):
    """
    Load the large asset, filter it to create a PURE SOLID BLACK silhouette,
    ensure background is transparent (no box), and cut into frames.
    """
    if not os.path.exists(filename):
        print(f"MISSING ENEMY ASSET: {filename}. Fallback rectangle used.")
        safe = pygame.Surface((target_w, target_h))
        safe.fill((0, 0, 0)) # Failsafe is a black box
        return [safe]

    try:
        sheet = pygame.image.load(filename).convert_alpha()
        sheet_w, sheet_h = sheet.get_size()
        
        # Grab background color from top-left (assuming it's background)
        bg_color = sheet.get_at((0, 0)) 
        
        # Create a new surface to build the silhouettes on
        fixed_sheet = pygame.Surface((sheet_w, sheet_h), pygame.SRCALPHA)
        
        # Manually process pixel-by-pixel for ultimate robustness
        for x in range(sheet_w):
            for y in range(sheet_h):
                color = sheet.get_at((x, y))
                
                # Check for muddy JPEG background noise
                # Aggressive tolerance to completely kill the 'box'
                if abs(color.r - bg_color.r) < 30 and abs(color.g - bg_color.g) < 30 and abs(color.b - bg_color.b) < 30:
                    fixed_sheet.set_at((x, y), (0, 0, 0, 0)) # Invisible background
                # Keep bright parts (eyes, glitches)
                elif color.r > 200 or color.g > 200 or color.b > 200:
                    fixed_sheet.set_at((x, y), color) # Keep original detail
                # Everything else is the body. Paint it SOLID PURE OPAQUE BLACK.
                else:
                    fixed_sheet.set_at((x, y), (0, 0, 0, 255)) 
        
        # Slice the 8x6 grid
        fw = sheet_w // ENEMY_GRID[1]
        fh = sheet_h // ENEMY_GRID[0]
        frames = []
        
        # Scale to be menacingly larger than the player
        final_w, final_h = int(target_w * 1.1), int(target_h * 1.1)
        
        for r in range(ENEMY_GRID[0]):
            for c in range(ENEMY_GRID[1]):
                frame_rect = pygame.Rect(c * fw, r * fh, fw, fh)
                original_frame = fixed_sheet.subsurface(frame_rect)
                scaled = pygame.transform.scale(original_frame, (final_w, final_h))
                frames.append(scaled)
        return frames

    except Exception as e:
        print(f"CRITICAL ERROR LOADING ENEMY SHEET: {e}")
        # Failsafe return black box
        safe = pygame.Surface((target_w, target_h))
        safe.fill((0, 0, 0))
        return [safe]


def load_player_sheet(filename):
    """Slice the player sheet and remove the black JPG background."""
    if not os.path.exists(filename):
        print(f"MISSING PLAYER ASSET: {filename}. Fallback block used.")
        safe = pygame.Surface((64, 64))
        safe.fill((0, 0, 255)) # Failsafe is solid blue block
        return [safe]

    try:
        sheet = pygame.image.load(filename).convert_alpha()
        
        # Simple removal: if a pixel is nearly black, make it transparent
        for x in range(sheet.get_width()):
            for y in range(sheet.get_height()):
                color = sheet.get_at((x, y))
                if color.r <= JPG_BLACK_TOLERANCE and color.g <= JPG_BLACK_TOLERANCE and color.b <= JPG_BLACK_TOLERANCE:
                    sheet.set_at((x, y), (0, 0, 0, 0)) 
                    
        # Slice the 5x5 grid
        fw = sheet.get_width() // PLAYER_GRID[1]
        fh = sheet.get_height() // PLAYER_GRID[0]
        frames = []
        
        for r in range(PLAYER_GRID[0]):
            for c in range(PLAYER_GRID[1]):
                rect = pygame.Rect(c * fw, r * fh, fw, fh)
                original = sheet.subsurface(rect)
                # Scale for pixel art look in the resolution
                scaled = pygame.transform.scale(original, (int(fw * 0.45), int(fh * 0.45)))
                frames.append(scaled)
        return frames
    except Exception as e:
        print(f"CRITICAL ERROR LOADING PLAYER SHEET: {e}")
        safe = pygame.Surface((64, 64))
        safe.fill((0, 0, 255))
        return [safe]

# --- Game Classes ---

class Camera:
    def __init__(self, width, height):
        self.camera = pygame.Rect(0, 0, width, height)
        self.width = width
        self.height = height

    def apply(self, entity):
        # Applies camera offset to an entity (used for drawing)
        return entity.rect.move(self.camera.topleft)

    def update(self, target):
        # Centers the camera on the player X coordinate
        x = -target.rect.centerx + int(SCREEN_WIDTH / 2)
        # Smooth camera glide effect
        self.camera.x += (x - self.camera.x) * 0.1
        self.camera.y = 0 # No Y scroll
        
        # Keep camera inside bounds
        self.camera.x = min(0, self.camera.x)  # Left wall
        max_scroll = -(self.width - SCREEN_WIDTH)
        self.camera.x = max(max_scroll, self.camera.x)  # Right wall


class Projectile(pygame.sprite.Sprite):
    def __init__(self, x, y, facing_right):
        super().__init__()
        # Creating a glowing blue projectile
        self.image = pygame.Surface((35, 12), pygame.SRCALPHA)
        self.image.fill((100, 200, 255, 200)) # Blue blast
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
        
        # Load and slice sheets (uses filenames from uploads)
        print("Processing Survivor Sprites...")
        self.walk_frames = load_player_sheet(PLAYER_WALK_FILE)
        self.idle_frames = load_player_sheet(PLAYER_IDLE_FILE)

        # State and Animation
        self.state = "idle"
        self.current_frames = self.idle_frames
        self.frame_index = 0
        self.image = self.current_frames[self.frame_index]
        self.rect = self.image.get_rect(midbottom=(400, self.floor_y))
        
        # Movement speeds and direction
        self.walk_speed = 5    
        self.run_speed = 9     
        self.speed = self.walk_speed 
        self.facing_right = True
        self.is_moving = False
        
        # Animation Timers
        self.last_update = pygame.time.get_ticks()
        self.walk_anim_fps = 16 # FPS of walking animation
        self.idle_anim_fps = 8
        self.current_anim_fps = self.idle_anim_fps
        
        self.hit_timer = 0 # Visual indicator timer when hit

    def update(self, map_width):
        self.update_input(map_width)
        self.animate()

    def take_damage(self):
        # Triggers visual red tint effect for 1 second
        self.hit_timer = pygame.time.get_ticks() + 1000

    def update_input(self, map_width):
        keys = pygame.key.get_pressed()
        self.is_moving = False
        
        # Running check (L-Shift toggles run speed)
        if keys[pygame.K_LSHIFT] or keys[pygame.K_RSHIFT]:
            self.speed = self.run_speed
            self.current_anim_fps = 30 # Running anim FPS
        else:
            self.speed = self.walk_speed
            self.current_anim_fps = self.walk_anim_fps
        
        # Horiz movement (A/D or Arrows)
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.rect.x -= self.speed
            self.facing_right = False
            self.is_moving = True
            
        elif keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.rect.x += self.speed
            self.facing_right = True
            self.is_moving = True

        # Keep player on screen map bounds
        if self.rect.left < 0: self.rect.left = 0
        if self.rect.right > map_width: self.rect.right = map_width

    def animate(self):
        now = pygame.time.get_ticks()
        
        # Switch animation frames based on state
        if self.is_moving:
            if self.state != "walk":
                self.state = "walk"
                self.current_frames = self.walk_frames
                self.frame_index = 0
        else:
            if self.state != "idle":
                self.state = "idle"
                self.current_frames = self.idle_frames
                self.current_anim_fps = self.idle_anim_fps
                self.frame_index = 0

        # Run the animation loop
        if now - self.last_update > 1000 // self.current_anim_fps:
            self.last_update = now
            self.frame_index = (self.frame_index + 1) % len(self.current_frames)
            
        # Get frame and flip based on direction
        raw_frame = self.current_frames[self.frame_index]
        if not self.facing_right:
            self.image = pygame.transform.flip(raw_frame, True, False)
        else:
            self.image = raw_frame.copy() 

        # Red tint hit indicator (BLEND_RGB_ADD only makes bright parts redder)
        if now < self.hit_timer:
            self.image.fill((255, 0, 0), special_flags=pygame.BLEND_RGB_ADD)


class Enemy(pygame.sprite.Sprite):
    def __init__(self, start_x, floor_y, player_rect):
        super().__init__()
        self.floor_y = floor_y
        
        # Target size derived from Player's final scaled size
        target_w = player_rect.width
        target_h = player_rect.height
        
        # Special image processor: rips out the black box, forces body to pure black.
        print("Processing Entity sprites (Advanced Filter)...")
        self.all_frames = load_enemy_silhouette(ENEMY_FILE, target_w, target_h)
        
        # Asset has multiple cycles. Rows 1-4 are good running loops. 
        # (Slicing 24 frames of menacing walking cycle)
        self.chase_frames = self.all_frames[0:24]
        # Multi-blast attack is frames 30-48 (Rows 6-8)
        self.attack_frames = self.all_frames[30:48]

        # Menacing state machine (Chase -> Attack -> Cooldown)
        self.state = "chase"
        self.current_frames = self.chase_frames
        self.frame_index = 0
        self.image = self.current_frames[self.frame_index]
        self.rect = self.image.get_rect(midbottom=(start_x, self.floor_y))

        # Balanced pacing variables (Creeps slowly toward you)
        self.speed = 3 # Slow menacing walk speed
        self.facing_right = True
        
        # Animation and behavior timers
        self.last_update = pygame.time.get_ticks()
        self.anim_fps = 12 # Heavy animation rate for walk
        
        # Menacing Attack Rules:
        self.attack_range = 220 # Proximity threshold for attack
        self.attack_cooldown_duration = 4000 # 4 seconds between attacks
        self.cooldown_timer = pygame.time.get_ticks() + 2000 # Stop instant hit at launch
        self.has_fired_blast = False

    def update(self, player, projectile_group):
        now = pygame.time.get_ticks()
        dist_x = player.rect.centerx - self.rect.centerx
        
        # Menacing state machine
        if self.state == "chase":
            self.anim_fps = 12 # Heavy chase walk anim
            
            if abs(dist_x) > self.attack_range: 
                # Creep slowly toward player (slow, menacing walk)
                if dist_x > 0:
                    self.rect.x += self.speed
                    self.facing_right = True
                else:
                    self.rect.x -= self.speed
                    self.facing_right = False
            else:
                # Target within range. Are we ready to attack?
                if now > self.cooldown_timer:
                    # Switch to Attack sequence
                    self.state = "attack"
                    self.frame_index = 0
                    self.current_frames = self.attack_frames
                    self.anim_fps = 20 # Attack anim is slightly faster
                    self.has_fired_blast = False
                else:
                    # In range but waiting on cooldown (MENACING PAUSE)
                    self.state = "chase" # Just stand still
        
        elif self.state == "attack":
            # Fire Blast (Middle of animation sequence)
            if self.frame_index == 10 and not self.has_fired_blast:
                # Fires blast from central eyes area
                blast = Projectile(self.rect.centerx, self.rect.centery, self.facing_right)
                projectile_group.add(blast)
                self.has_fired_blast = True

        # Run the animation loop
        if now - self.last_update > 1000 // self.anim_fps:
            self.last_update = now
            self.frame_index += 1

            if self.frame_index >= len(self.current_frames):
                if self.state == "attack":
                    # --- MOVE SPAMMING FIX ---
                    # Attack sequence complete. Initiate long cooldown.
                    self.cooldown_timer = now + self.attack_cooldown_duration
                    self.state = "chase" # Return to Menacing Chase
                    self.current_frames = self.chase_frames
                self.frame_index = 0

            # Get frame and flip based on direction
            raw_frame = self.current_frames[self.frame_index]
            if not self.facing_right:
                self.image = pygame.transform.flip(raw_frame, True, False)
            else:
                self.image = raw_frame
                
        # Lock enemy strictly to its grounded floor line
        self.rect.midbottom = (self.rect.centerx, self.floor_y)


# --- Game Initialization & Loop ---

# Setup Pygame display
pygame.init()
pygame.display.set_caption("Survivor VS The Pure Black Glitch Shadow")

# Setup Screen (Attempts fullscreen, otherwise standard window)
try:
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.FULLSCREEN)
except pygame.error:
    print("Warning: Fullscreen not available. Windowed mode used.")
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

clock = pygame.time.Clock()

# Map size setup
MAP_WIDTH = SCREEN_WIDTH * 2 # Level is two screens wide
MAP_HEIGHT = SCREEN_HEIGHT

# Load assets in correct order so scale/dimensions flow correctly
print("\n--- LOADING ASSETS ---")

# Player loaded first so its size sets the benchmark
player = Player(FLOOR_Y)

# Enemy loaded second. MUST BE GROUNDED on fixed FLOOR_Y line.
# Note: Enemy processes the complex multi-asset image file.
enemy = Enemy(start_x=200, floor_y=FLOOR_Y, player_rect=player.rect) 

# Camera and Sprite Groups
camera = Camera(MAP_WIDTH, MAP_HEIGHT)
entities = pygame.sprite.Group(player, enemy)
projectiles = pygame.sprite.Group()

# Visual instruction text overlay (Uses built-in font for robustness)
try:
    font = pygame.font.SysFont("Courier New", 28, bold=True)
except pygame.error:
    font = pygame.font.Font(None, 32)
instructions_text = font.render("Arrows: Move | Shift: Run | ESC: Exit", True, (200, 200, 200))
instructions_rect = instructions_text.get_rect(bottomleft=(20, SCREEN_HEIGHT - 20))

# Damage timer to stop spam visual when colliding directly
damage_immune_until = pygame.time.get_ticks() + 3000 # Immunity at launch

# --- Main Game Loop ---
running = True
while running:
    # Set background color to PURE BLACK so silhouette blends are hidden
    screen.fill((0, 0, 0)) 

    # Handle quit events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            running = False

    # 1. Update Entities
    player.update(MAP_WIDTH)
    enemy.update(player, projectiles) 
    projectiles.update() # Update blue blasts
    camera.update(player)

    # 2. Hit Detection
    # Bullet hits Player
    hits_list = pygame.sprite.spritecollide(player, projectiles, True)
    for hit in hits_list:
        print("OW! Shadow hit me.")
        player.take_damage()
        
    # Physical contact with Beast (Menacing contact)
    if player.rect.colliderect(enemy.rect):
        now = pygame.time.get_ticks()
        # Contact dealing heavy immunity
        if now > damage_immune_until:
            print("CONTACT! The Shadow drains me...")
            player.take_damage()
            # Triggers significant cooldown before taking direct hit again
            damage_immune_until = now + 1500 

    # 3. Draw entities relative to Camera position
    # Draws are applied with BLEND_PREMULTIPLIED to alpha processing is smooth
    for entity in entities:
        screen.blit(entity.image, camera.apply(entity), special_flags=pygame.BLEND_PREMULTIPLIED)
    
    # Blit bullets
    for blast in projectiles:
        screen.blit(blast.image, camera.apply(blast), special_flags=pygame.BLEND_PREMULTIPLIED)

    # 4. Draw UI overlay (Text)
    screen.blit(instructions_text, instructions_rect)

    # 5. Refresh Screen
    pygame.display.flip()
    clock.tick(FPS)

# Clean Exit
pygame.quit()
sys.exit()
