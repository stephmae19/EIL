import pygame
import sys

# --- Configuration ---
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60
ROWS = 5
COLS = 5

class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        
        try:
            # .convert() is good, but .convert_alpha() is better if you switch to PNG later
            self.sprite_sheet = pygame.image.load('player(1).jpg').convert()
        except pygame.error as e:
            print(f"Error: Could not find 'player(1).jpg' in the folder. {e}")
            pygame.quit()
            sys.exit()

        # JPGs often have "dirty" blacks. If it doesn't look transparent, 
        # ensure the background of your JPG is exactly (0,0,0) black.
        self.sprite_sheet.set_colorkey((0, 0, 0))
        
        sheet_rect = self.sprite_sheet.get_rect()
        self.frame_width = sheet_rect.width // COLS
        self.frame_height = sheet_rect.height // ROWS
        
        self.walk_frames = []
        for r in range(ROWS):
            for c in range(COLS):
                rect = pygame.Rect(c * self.frame_width, r * self.frame_height, 
                                   self.frame_width, self.frame_height)
                frame = self.sprite_sheet.subsurface(rect)
                self.walk_frames.append(frame)

        self.current_frame = 0.0
        self.image = self.walk_frames[0]
        # Store position in a Rect
        self.rect = self.image.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
        
        self.speed = 5
        self.animation_speed = 0.2  
        self.facing_right = True
        self.is_moving = False
        self.direction = 0

    def handle_input(self):
        keys = pygame.key.get_pressed()
        self.is_moving = False
        self.direction = 0
        
        # Added A/D keys as well, just in case your friend prefers WASD!
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.direction = -1
            self.facing_right = False
            self.is_moving = True
        elif keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.direction = 1
            self.facing_right = True
            self.is_moving = True

    def move(self):
        if self.is_moving:
            self.rect.x += self.direction * self.speed
            # Debugging: Uncomment the line below to see if coordinates are changing in the console
            # print(f"Player X: {self.rect.x}") 
            
            if self.rect.left < 0:
                self.rect.left = 0
            if self.rect.right > SCREEN_WIDTH:
                self.rect.right = SCREEN_WIDTH

    def animate(self):
        # Save the current position before changing the image
        old_center = self.rect.center
        
        if self.is_moving:
            self.current_frame += self.animation_speed
            if self.current_frame >= len(self.walk_frames):
                self.current_frame = 0
            new_image = self.walk_frames[int(self.current_frame)]
        else:
            new_image = self.walk_frames[0]

        if not self.facing_right:
            self.image = pygame.transform.flip(new_image, True, False)
        else:
            self.image = new_image
            
        # Re-apply the rect so the character doesn't "jump" if frames are different sizes
        self.rect = self.image.get_rect(center=old_center)

    def update(self):
        self.handle_input()
        self.move()
        self.animate()

# --- Main Game Loop ---
pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Pirate Game Development") # A bit more descriptive!
clock = pygame.time.Clock()

player_instance = Player()
all_sprites = pygame.sprite.Group(player_instance)

running = True
while running:
    # Set a background color (Darker green looks a bit more professional)
    screen.fill((30, 100, 30)) 
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    all_sprites.update()
    all_sprites.draw(screen)

    pygame.display.flip()
    clock.tick(FPS)

pygame.quit()
