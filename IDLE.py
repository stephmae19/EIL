import pygame
import sys
import os

# --- Configuration ---
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60

# --- File Names ---
# Ensure these files are in the same folder as this script
WALK_FILENAME = 'player_walk.jpg'
IDLE_FILENAME = 'player_idle.png' 

# UPDATED: Set to 4x4 based on the pirate sprite sheet
ROWS, COLS = 4, 4

# Animation Speeds
WALK_ANIM_SPEED = 0.20
IDLE_ANIM_SPEED = 0.08

class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()

        # 1. Load both sets of frames
        self.walk_frames = self.load_sprite_sheet(WALK_FILENAME, ROWS, COLS)
        self.idle_frames = self.load_sprite_sheet(IDLE_FILENAME, ROWS, COLS)

        # 2. Initial Animation State
        self.current_frame_set = self.idle_frames
        self.animation_speed = IDLE_ANIM_SPEED
        self.current_frame_index = 0.0
        
        self.image = self.current_frame_set[0]
        self.rect = self.image.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))

        # 3. Movement Variables
        self.speed = 5
        self.facing_right = True
        self.is_moving = False
        self.direction = 0 

    def load_sprite_sheet(self, filename, rows, cols):
        """Slices the grid sheet into a list of surfaces."""
        if not os.path.exists(filename):
            print(f"ERROR: Missing file '{filename}'")
            pygame.quit()
            sys.exit()
            
        try:
            # Use convert() for JPG, convert_alpha() for PNG
            if filename.endswith('.jpg') or filename.endswith('.jpeg'):
                sheet = pygame.image.load(filename).convert()
                # Set colorkey to the color of the top-left pixel (usually the background)
                sheet.set_colorkey(sheet.get_at((0,0)))
            else:
                sheet = pygame.image.load(filename).convert_alpha()

            frame_width = sheet.get_width() // cols
            frame_height = sheet.get_height() // rows

            frames = []
            sheet_rect = sheet.get_rect()

            for r in range(rows):
                for c in range(cols):
                    # Calculate the rectangle for the current frame
                    rect = pygame.Rect(c * frame_width, r * frame_height,
                                       frame_width, frame_height)
                    
                    # SAFETY CHECK: Only cut if the rectangle is inside the image
                    if sheet_rect.contains(rect):
                        frames.append(sheet.subsurface(rect))
            
            if not frames:
                print(f"ERROR: No frames could be loaded from {filename}")
                pygame.quit()
                sys.exit()
                
            return frames
        except pygame.error as e:
            print(f"Error loading {filename}: {e}")
            pygame.quit()
            sys.exit()

    def handle_input(self):
        """Determines if the player is moving or idle."""
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
        """Updates position based on input."""
        if self.is_moving:
            self.rect.x += self.direction * self.speed
            # Boundaries
            self.rect.clamp_ip(pygame.Rect(0, 0, SCREEN_WIDTH, SCREEN_HEIGHT))

    def animate(self):
        """Switches between walking and idle animations."""
        if self.is_moving:
            target_set = self.walk_frames
            target_speed = WALK_ANIM_SPEED
        else:
            target_set = self.idle_frames
            target_speed = IDLE_ANIM_SPEED

        # Reset index if the state changes
        if self.current_frame_set != target_set:
            self.current_frame_set = target_set
            self.animation_speed = target_speed
            self.current_frame_index = 0.0

        # Cycle through frames
        self.current_frame_index += self.animation_speed
        if self.current_frame_index >= len(self.current_frame_set):
            self.current_frame_index = 0

        raw_image = self.current_frame_set[int(self.current_frame_index)]

        # Flip horizontally if facing left
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
pygame.display.set_caption("Pirate Project: Idle & Walk")
clock = pygame.time.Clock()

player = Player()
all_sprites = pygame.sprite.Group(player)
font = pygame.font.Font(None, 36)

running = True
while running:
    screen.fill((50, 120, 50)) # Green background

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    all_sprites.update()
    all_sprites.draw(screen)

    # UI Overlay
    status = "State: Walking" if player.is_moving else "State: Idle"
    text_surf = font.render(status, True, (255, 255, 255))
    screen.blit(text_surf, (10, 10))

    pygame.display.flip()
    clock.tick(FPS)

pygame.quit()
sys.exit()
