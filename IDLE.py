import pygame
import sys
import os

# --- Configuration ---
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60

# --- File Names (Set these verbatim) ---
# Assuming you saved the walking sheet as 'player_walk.jpg'
WALK_FILENAME = 'player_walk.jpg' 
# Save your new breathing sheet as 'player_idle.jpg'
IDLE_FILENAME = 'player_idle.jpg' 

# Grid details for the WALKING sheet (5x5)
WALK_ROWS = 5
WALK_COLS = 5

# Grid details for the IDLE sheet (5x5)
IDLE_ROWS = 5
IDLE_COLS = 5

# Speed settings
WALK_ANIM_SPEED = 0.20  # Fast (walking)
IDLE_ANIM_SPEED = 0.08  # Slow (breathing)

class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        
        # 1. LOAD AND SLICE THE WALKING SHEET (5x5)
        self.walk_frames = self.load_sprite_sheet(WALK_FILENAME, WALK_ROWS, WALK_COLS)
        
        # 2. LOAD AND SLICE THE IDLE SHEET (5x5)
        # Add error checking for this new file
        if not os.path.exists(IDLE_FILENAME):
            print(f"ERROR: Could not find '{IDLE_FILENAME}'.")
            print("Please save the breathing sheet image to this folder.")
            pygame.quit()
            sys.exit()
        self.idle_frames = self.load_sprite_sheet(IDLE_FILENAME, IDLE_ROWS, IDLE_COLS)

        # 3. INITIAL STATE
        # Set the starting list of frames and animation speed
        self.current_frame_set = self.idle_frames
        self.animation_speed = IDLE_ANIM_SPEED

        self.current_frame_index = 0.0
        self.image = self.current_frame_set[0]
        self.rect = self.image.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
        
        self.speed = 5
        self.facing_right = True
        self.is_moving = False
        self.direction = 0  # 1 (Right), -1 (Left), 0 (Idle)

    def load_sprite_sheet(self, filename, rows, cols):
        """Helper function to slice any grid sheet."""
        try:
            sheet = pygame.image.load(filename).convert()
            sheet.set_colorkey((0, 0, 0)) # Set black transparent
            
            sheet_rect = sheet.get_rect()
            frame_width = sheet_rect.width // cols
            frame_height = sheet_rect.height // rows
            
            frames = []
            for r in range(rows):
                for c in range(cols):
                    rect = pygame.Rect(c * frame_width, r * frame_height, 
                                       frame_width, frame_height)
                    frame = sheet.subsurface(rect)
                    frames.append(frame)
            return frames
        except pygame.error as e:
            print(f"Unable to load image '{filename}'! Error: {e}")
            pygame.quit()
            sys.exit()

    def handle_input(self):
        """Checks keys and sets movement/animation state."""
        keys = pygame.key.get_pressed()
        self.is_moving = False
        self.direction = 0
        
        if keys[pygame.K_LEFT]:
            self.direction = -1
            self.facing_right = False
            self.is_moving = True
        elif keys[pygame.K_RIGHT]:
            self.direction = 1
            self.facing_right = True
            self.is_moving = True

    def move(self):
        """Handles screen boundaries and updates position."""
        if self.is_moving:
            self.rect.x += self.direction * self.speed
            
            # Simple Boundary Collision
            if self.rect.left < 0:
                self.rect.left = 0
            if self.rect.right > SCREEN_WIDTH:
                self.rect.right = SCREEN_WIDTH

    def animate(self):
        """Cycles through frames based on movement state."""
        
        # 1. Decide which set of frames to use and reset index if needed
        # (This is important: resetting the index ensures that when you *stop* moving,
        # you start the breathing cycle from the 'start' frame, not mid-breath.)
        
        new_frame_set = self.idle_frames
        new_anim_speed = IDLE_ANIM_SPEED

        if self.is_moving:
            new_frame_set = self.walk_frames
            new_anim_speed = WALK_ANIM_SPEED
        
        # If the frame set has changed (e.g., just started walking), reset index
        if new_frame_set != self.current_frame_set:
            self.current_frame_set = new_frame_set
            self.animation_speed = new_anim_speed
            self.current_frame_index = 0.0

        # 2. Cycle through the current set of frames
        self.current_frame_index += self.animation_speed
        if self.current_frame_index >= len(self.current_frame_set):
            self.current_frame_index = 0
        
        # Grab the raw frame
        raw_image = self.current_frame_set[int(self.current_frame_index)]

        # 3. Apply facing/flip (Since both sheets face right/front, we only need to flip when moving left)
        # (Note: Since the idle pose is mostly front-on, we flip it based on the *last* known facing direction)
        if not self.facing_right:
            self.image = pygame.transform.flip(raw_image, True, False)
        else:
            self.image = raw_image

    def update(self):
        self.handle_input()
        self.move()
        self.animate()

# --- Main Game Loop ---
pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Player Movement and Idle Animation")
clock = pygame.time.Clock()

player_instance = Player()
all_sprites = pygame.sprite.Group(player_instance)

# Text setup for debugging
font = pygame.font.Font(None, 36)

running = True
while running:
    # A green background to verify colorkey/transparency
    screen.fill((50, 120, 50)) 
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    all_sprites.update()
    all_sprites.draw(screen)

    # Optional Debug info
    state_text = "State: Walking" if player_instance.is_moving else "State: Idle"
    text_surf = font.render(state_text, True, (255, 255, 255))
    screen.blit(text_surf, (10, 10))

    pygame.display.flip()
    clock.tick(FPS)

pygame.quit()
