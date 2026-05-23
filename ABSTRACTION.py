import pygame
import sys
import os

# --- 1. EXACT FILENAMES FROM YOUR UPLOADS ---
WALK_FILE = "player_walk.jpg.jpg" 
IDLE_FILE = "player_idle.jpg.jpg"
# Using the multi-frame, 8x6 multi-blast sheet for full animation
ENEMY_FILE = "690856840_1447199653826161_7446595274037957518_n.jpg"

# --- 2. GRID SLICING VARIABLES (Rows x Columns) ---
PLAYER_GRID = (5, 5) # Both idle and walk are 5x5 grids
ENEMY_GRID = (8, 6) # Multi-frame Glitch Beast is an 8x6 grid

# --- 3. GAME TWEAK VARIABLES ---
SCREEN_WIDTH = 1200
SCREEN_HEIGHT = 800
FLOOR_Y = SCREEN_HEIGHT - 120 # Where feet land
JPG_BLACK_TOLERANCE = 45 # For cleaning JPG background noise
FPS = 60

# --- Helper Functions for Image Processing ---

def load_and_filter_enemy_frames(filename, grid_rows, grid_cols, target_width, target_height):
    """
    Creates full silhouettes of the glitch beast.
    Background is made 100% transparent (no black box).
    Monster body is painted SOLID PURE BLACK.
    """
    if not os.path.exists(filename):
        print(f"MISSING FILE: {filename}. Fallback rectangle used.")
        safe = pygame.Surface((target_width, target_height))
        safe.fill((0, 0, 0)) # Failsafe is solid black box
        return [safe]

    try:
        # Load the large sheet with alpha support
        sheet = pygame.image.load(filename).convert_alpha()
        sheet_w, sheet_h = sheet.get_size()
        
        # --- THE SILHOUETTE FILTER ---
        # Grab background color from top left corner for dynamic tolerance
        bg_color = sheet.get_at((0, 0)) 
        
        # Create a new surface to build the silhouettes on
        fixed_sheet = pygame.Surface((sheet_w, sheet_h), pygame.SRCALPHA)
        
        for x in range(sheet_w):
            for y in range(sheet_h):
                color = sheet.get_at((x, y))
                
                # Is it the muddy JPEG background?
                if abs(color.r - bg_color.r) < 30 and abs(color.g - bg_color.g) < 30 and abs(color.b - bg_color.b) < 30:
                    fixed_sheet.set_at((x, y), (0, 0, 0, 0)) # Invisible
                # Is it the extremely bright glowing parts? (eyes/glitch)
                elif color.r > 200 or color.g > 200 or color.b > 200:
                    # Keep the exact colors of the glows/eyes
                    fixed_sheet.set_at((x, y), color) 
                # Everything else is the monster's body. Paint it SOLID PURE BLACK.
                else:
                    fixed_sheet.set_at((x, y), (0, 0, 0, 255)) 
        
        # Now cut the fixed sheet into frames
        fw = sheet_w // grid_cols
        fh = sheet_h // grid_rows
        frames = []
        
        for r in range(grid_rows):
            for c in range(grid_cols):
                frame_rect = pygame.Rect(c * fw, r * fh, fw, fh)
                original_frame = fixed_sheet.subsurface(frame_rect)
                
                # Scale the monster to be slightly larger than the player
                scaled = pygame.transform.scale(original_frame, (int(target_width * 1.1), int(target_height * 1.1)))
                frames.append(scaled)
                
        return frames
    except Exception as e:
        print(f"ERROR LOAD_ENEMY: {e}")
        # Failsafe... return a single solid black block.
        safe = pygame.Surface((target_width, target_height))
        safe.fill((0, 0, 0))
        return [safe]


def load_and_slice_player(filename, grid_rows, grid_cols):
    """Slices the player and makes the black JPG background transparent."""
    if not os.path.exists(filename):
        print(f"MISSING FILE: {filename}. Fallback used.")
        safe = pygame.Surface((64, 64))
        safe.fill((0, 0, 255))
        return [safe]

    try:
        sheet = pygame.image.load(filename).convert_alpha()
        # Clean JPG noise: anything nearly black is transparent
        for x in range(sheet.get_width()):
            for y in range(sheet.get_height()):
                color = sheet.get_at((x, y))
                if color.r <= JPG_BLACK_TOLERANCE and color.g <= JPG_BLACK_TOLERANCE and color.b <= JPG_BLACK_TOLERANCE:
                    sheet.set_at((x, y), (0, 0, 0, 0)) 

        # Slice the 5x5 grid
        fw = sheet.get_width() // grid_cols
        fh = sheet.get_height() // grid_rows
        frames = []
        
        for r in range(grid_rows):
            for c in range(grid_cols):
                rect = pygame.Rect(c * fw, r * fh, fw, fh)
                original = sheet.subsurface(rect)
                # Scale down for pixel art look
                scaled = pygame.transform.scale(original, (int(fw * 0.45), int(fh * 0.45)))
                frames.append(scaled)
        return frames
    except Exception as e:
        print(f"ERROR LOAD_PLAYER: {e}")
        # Failsafe
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
        return entity.rect.move(self.camera.topleft)

    def update(self, target):
        # Center camera on player X, stay grounded on Y
        x = -target.rect.centerx + int(SCREEN_WIDTH / 2)
        # Smooth camera glide
        self.camera.x += (x - self.camera.x) * 0.1
        self.camera.y = 0 
        
        # Lock camera to bounds
        self.camera.x = min(0, self.camera.x)  # Left wall
        self.camera.x = max(-(self.width - SCREEN_WIDTH), self.camera.x)  # Right wall


class Player(pygame.sprite.Sprite):
    def __init__(self, floor_y):
        super().__init__()
        self.floor_y = floor_y
        
        # Load and slice the provided images
        print("Processing Player Sheets...")
        self.walk_frames = load_and_slice_player(WALK_FILE, PLAYER_GRID[0], PLAYER_GRID[1])
        self.idle_frames = load_and_slice_player(IDLE_FILE, PLAYER_GRID[0], PLAYER_GRID[1])

        # State and Animation
        self.state = "idle"
        self.current_frames = self.idle_frames
        self.frame_index = 0
        self.image = self.current_frames[self.frame_index]
        self.rect = self.image.get_rect(midbottom=(400, self.floor_y))
        
        # Speeds and Direction
        self.walk_speed = 5    
        self.run_speed = 9     
        self.speed = self.walk_speed 
        self.facing_right = True
        self.is_moving = False
        
        # Animation Timers
        self.last_update = pygame.time.get_ticks()
        self.walk_anim_fps = 16 
        self.idle_anim_fps = 8
        self.current_anim_fps = self.idle_anim_fps
        
        self.hit_timer = 0 # Indicators when hit

    def update(self, map_width):
        self.update_input(map_width)
        self.animate()

    def take_damage(self):
        # Triggers a red visual tint for 1 second
        self.hit_timer = pygame.time.get_ticks() + 1000

    def update_input(self, map_width):
        keys = pygame.key.get_pressed()
        self.is_moving = False
        
        # Running check
        if keys[pygame.K_LSHIFT] or keys[pygame.K_RSHIFT]:
            self.speed = self.run_speed
            self.current_anim_fps = 30 # Fast animation for running
        else:
            self.speed = self.walk_speed
            self.current_anim_fps = self.walk_anim_fps
        
        # Horiz Movement
        if keys[pygame.K_LEFT]:
            self.rect.x -= self.speed
            self.facing_right = False
            self.is_moving = True
            
        elif keys[pygame.K_RIGHT]:
            self.rect.x += self.speed
            self.facing_right = True
            self.is_moving = True

        # Keep within map bounds
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
            
        # Get raw frame and flip based on direction
        raw_image = self.current_frames[self.frame_index]
        
        if not self.facing_right:
            self.image = pygame.transform.flip(raw_image, True, False)
        else:
            self.image = raw_image.copy() 

        # Red tint hit indicator (BLEND_RGB_ADD makes bright parts red)
        if now < self.hit_timer:
            self.image.fill((255, 0, 0), special_flags=pygame.BLEND_RGB_ADD)


class Enemy(pygame.sprite.Sprite):
    def __init__(self, start_x, floor_y, player_rect):
        super().__init__()
        self.floor_y = floor_y
        
        # Target size based on player scale
        target_w = player_rect.width
        target_h = player_rect.height
        
        # Processing the multi-frame sheet to full solid black silhouettes
        print("Processing Entity Sheet...")
        self.all_frames = load_and_filter_enemy_frames(ENEMY_FILE, ENEMY_GRID[0], ENEMY_GRID[1], target_w, target_h)
        
        # original multi-blast sheet has multiple walk cycles and attack cycles.
        # Running Frames: Rows 1-4 (Looping these 24 frames)
        self.chase_frames = self.all_frames[0:24]
        # Multi-blast attack frames: Rows 6-8 (looping 18 frames)
        self.attack_frames = self.all_frames[30:48]

        # Menacing state machine
        self.state = "chase" # Chase -> PreAttack -> Attack -> Cooldown
        self.current_frames = self.chase_frames
        self.frame_index = 0
        self.image = self.current_frames[self.frame_index]
        self.rect = self.image.get_rect(midbottom=(start_x, self.floor_y))

        # Menacing pacing (No move spamming)
        self.speed = 3 # Slow, menacing walk towards player
        self.facing_right = True
        
        # Animation and behavior timers
        self.last_update = pygame.time.get_ticks()
        self.anim_fps = 12 # Slow, heavy animation rate for walk
        
        # Menacing Attack Rules:
        self.attack_range = 200 # Must be close enough to attack
        # A long cooldown to stop move spamming (4 seconds between attacks)
        self.attack_cooldown_duration = 4000 
        self.cooldown_timer = 0
        self.attack_sound_delay = pygame.time.get_ticks() + 5000 # Stop spamming at launch

    def update(self, player):
        now = pygame.time.get_ticks()
        dist_x = player.rect.centerx - self.rect.centerx
        
        # Menacing behavior state machine
        if self.state == "chase":
            self.anim_fps = 12 # Heavy chase walk
            # MENACING: Creeps towards the player slowly
            if abs(dist_x) > self.attack_range: 
                # Move towards character
                if dist_x > 0:
                    self.rect.x += self.speed
                    self.facing_right = True
                else:
                    self.rect.x -= self.speed
                    self.facing_right = False
            else:
                # Close enough, are we ready to attack?
                if now > self.cooldown_timer:
                    # PREPARE ATTACK (Pause, switch to first frame)
                    self.state = "attack"
                    self.frame_index = 0
                    self.current_frames = self.attack_frames
                    self.anim_fps = 24 # Attack animation is faster
                else:
                    # Within range but waiting for cooldown
                    # (Stopsmove spamming!)
                    self.state = "chase" # Just stay still
        
        elif self.state == "attack":
            # Just let animation run. Don't move.
            pass

        # Run the animation loop
        if now - self.last_update > 1000 // self.anim_fps:
            self.last_update = now
            self.frame_index += 1

            # Get raw frame and flip based on direction
            if self.frame_index >= len(self.current_frames):
                if self.state == "attack":
                    # --- NO ATTACK SPAMMING FIX ---
                    # End of Attack Sequence. Set the Cooldown Timer.
                    # This locks the beast from attacking for 4 seconds.
                    self.cooldown_timer = now + self.attack_cooldown_duration
                    self.state = "chase" # Return to chasing
                    self.current_frames = self.chase_frames
                self.frame_index = 0

            raw_image = self.current_frames[self.frame_index]
            if not self.facing_right:
                self.image = pygame.transform.flip(raw_image, True, False)
            else:
                self.image = raw_image
                
        # Lock enemy strictly to its grounded floor line
        self.rect.midbottom = (self.rect.centerx, self.floor_y)


# --- GAME INITIALIZATION & LOOP ---

# 1. Setup Pygame
pygame.init()
pygame.display.set_caption("Menacing Pure Black Shadow Chases You")

# 2. Setup Screen (Try fullscreen, otherwise standard window)
try:
    screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
    SCREEN_WIDTH, SCREEN_HEIGHT = screen.get_size()
except pygame.error:
    print("Warning: Fullscreen failed, standard window used.")
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

clock = pygame.time.Clock()

# Use font from early interaction if available (else fallback)
try:
    font = pygame.font.Font("Early-Interaction.ttf", 32)
except pygame.error:
    font = pygame.font.SysFont("Courier New", 28)

# 3. Create Map Bounds
MAP_WIDTH = SCREEN_WIDTH * 3 # The level is 3 screens wide
MAP_HEIGHT = SCREEN_HEIGHT

# 4. Create Entities and GROUND them on the fixed FloorY line
player = Player(FLOOR_Y)
# Beast starts far off-screen
enemy = Enemy(start_x=100, floor_y=FLOOR_Y, player_rect=player.rect) 

camera = Camera(MAP_WIDTH, MAP_HEIGHT)
entities = pygame.sprite.Group(player, enemy)

# Visual instruction text
instructions_text = font.render("ARROWS: Move | SHIFT: Run | ESC: Exit", True, (200, 200, 200))
instructions_rect = instructions_text.get_rect(bottomleft=(20, SCREEN_HEIGHT - 20))

# Hit sound failsafe stops visual spam
can_take_damage = pygame.time.get_ticks() + 5000 # Stop damage at launch

# --- Main Game Loop ---
running = True
while running:
    # Set background color to PURE BLACK to hide silhouette artifacts
    screen.fill((0, 0, 0)) 

    # Handle Events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            running = False

    # 1. Update Entities
    player.update(MAP_WIDTH)
    enemy.update(player)
    camera.update(player)

    # 2. Basic Hit Detection
    if player.rect.colliderect(enemy.rect):
        now = pygame.time.get_ticks()
        if now > can_take_damage:
            print("OUCH! Beast hit me.")
            player.take_damage()
            can_take_damage = now + 1500 # Don't spam the hit effect

    # 3. Draw entities relative to Camera
    for entity in entities:
        # Drawing with BLEND_PREMULTIPLIED so alpha processing is respected
        screen.blit(entity.image, camera.apply(entity), special_flags=pygame.BLEND_PREMULTIPLIED)

    # 4. Draw UI Overlay
    screen.blit(instructions_text, instructions_rect)

    # 5. Refresh Screen
    pygame.display.flip()
    clock.tick(FPS)

# Clean Exit
pygame.quit()
sys.exit()
