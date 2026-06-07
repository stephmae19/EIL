import pygame
import sys
import os

# --- Configuration ---
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
GAME_FPS = 60 

WALK_FILE = "../Assets/Characters/player_walk.jpeg"
IDLE_FILE = "../Assets/Characters/player_idle.jpeg"

class Camera:
    def __init__(self, width, height):
        self.camera = pygame.Rect(0, 0, width, height)
        self.width = width
        self.height = height

    def apply(self, entity):
        """Returns the entity's rect shifted by the camera offset."""
        return entity.rect.move(self.camera.topleft)

    def update(self, target):
        """Centers the camera on the target (the player)."""
        x = -target.rect.centerx + int(SCREEN_WIDTH / 2)
        y = -target.rect.centery + int(SCREEN_HEIGHT / 2)
        
        # Optional: Stop the camera at the edges of your world
        # x = min(0, x) # Left side
        # y = min(0, y) # Top side
        
        self.camera = pygame.Rect(x, y, self.width, self.height)

class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.walk_frames = self.load_frames(WALK_FILE, 5, 5)
        self.idle_frames = self.load_frames(IDLE_FILE, 5, 5)

        self.current_frames = self.idle_frames
        self.frame_index = 0
        self.image = self.current_frames[self.frame_index]
        
        # Start at 0,0 or any world coordinate
        self.rect = self.image.get_rect(topleft=(100, 100))
        
        self.speed = 5
        self.facing_right = True
        self.is_moving = False
        self.last_update = pygame.time.get_ticks()

    def load_frames(self, filename, rows, cols):
        if not os.path.exists(filename):
            surf = pygame.Surface((64, 64))
            surf.fill((200, 0, 0))
            return [surf]
        sheet = pygame.image.load(filename).convert()
        sheet.set_colorkey((0, 0, 0))
        w, h = sheet.get_width() // cols, sheet.get_height() // rows
        frames = []
        for r in range(rows):
            for c in range(cols):
                frames.append(sheet.subsurface(pygame.Rect(c*w, r*h, w, h)))
        return frames

    def update(self):
        keys = pygame.key.get_pressed()
        self.is_moving = False
        
        if keys[pygame.K_LEFT]:
            self.rect.x -= self.speed
            self.facing_right = False
            self.is_moving = True
        elif keys[pygame.K_RIGHT]:
            self.rect.x += self.speed
            self.facing_right = True
            self.is_moving = True

        # Animation Logic
        now = pygame.time.get_ticks()
        if self.is_moving:
            self.current_frames = self.walk_frames
            duration = 1000 // 24
        else:
            self.current_frames = self.idle_frames
            duration = 1000 // 12

        if now - self.last_update > duration:
            self.last_update = now
            self.frame_index = (self.frame_index + 1) % len(self.current_frames)
            raw = self.current_frames[self.frame_index]
            self.image = pygame.transform.flip(raw, not self.facing_right, False)

# --- Initialization ---
pygame.init()
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
clock = pygame.time.Clock()

player = Player()
all_sprites = pygame.sprite.Group(player)

# Create the camera (Size of your total level, e.g., 2000x600)
camera = Camera(2000, 600)

# Create some dummy "world objects" so you can see the camera moving
background_objects = []
for i in range(0, 2000, 200):
    rect = pygame.Rect(i, 500, 50, 50)
    background_objects.append(rect)

while True:
    screen.fill((30, 30, 30))
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

    # Update
    all_sprites.update()
    camera.update(player)

    # Draw World Objects (Background)
    for obj in background_objects:
        # Subtract camera offset from object position
        pygame.draw.rect(screen, (100, 100, 100), obj.move(camera.camera.topleft))

    # Draw Player
    screen.blit(player.image, camera.apply(player))

    pygame.display.flip()
    clock.tick(GAME_FPS)
