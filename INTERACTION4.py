import pygame
import sys
import os

# --- GAME SETTINGS ---
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60

# Colors
TEXT_COLOR = (255, 255, 255)
UI_BOX_COLOR = (40, 40, 40, 220)
PROMPT_COLOR = (255, 255, 100)

# --- CLASSES ---
class Camera:
    def __init__(self, width, height):
        self.camera = pygame.Rect(0, 0, width, height)
        self.width = width
        self.height = height

    def apply(self, entity):
        return entity.rect.move(self.camera.topleft)

    def update(self, target):
        x = -target.rect.centerx + int(SCREEN_WIDTH / 2)
        # Limit scrolling to map bounds
        x = min(0, x) 
        x = max(-(self.width - SCREEN_WIDTH), x)
        self.camera = pygame.Rect(x, 0, self.width, self.height)

class InteractableZone(pygame.sprite.Sprite):
    def __init__(self, x, y, width, height, message):
        super().__init__()
        self.image = pygame.Surface((width, height), pygame.SRCALPHA)
        # Draws a semi-transparent green box so you can see where the zones are.
        # CHANGE TO (0, 0, 0, 0) later to make them completely invisible!
        self.image.fill((0, 255, 0, 100)) 
        self.rect = self.image.get_rect(topleft=(x, y))
        self.message = message

    def update(self, player, screen, camera, game_state, font):
        # Check if player is standing in front of the bookshelf
        if self.rect.left < player.rect.centerx < self.rect.right:
            
            # Draw "E to Read"
            prompt_surf = font.render("E to Read", True, PROMPT_COLOR)
            prompt_x = player.rect.centerx + camera.camera.x
            prompt_y = player.rect.top + camera.camera.y - 30
            prompt_rect = prompt_surf.get_rect(midbottom=(prompt_x, prompt_y))
            screen.blit(prompt_surf, prompt_rect)

            # Check for interaction
            keys = pygame.key.get_pressed()
            if keys[pygame.K_e]:
                game_state['active_message'] = self.message

class Player(pygame.sprite.Sprite):
    def __init__(self, floor_y):
        super().__init__()
        self.image = pygame.Surface((40, 80))
        self.image.fill((50, 150, 250)) # Blue rectangle player
        self.rect = self.image.get_rect(midbottom=(400, floor_y))
        self.speed = 5 
        self.floor_y = floor_y

    def update(self, map_width, game_state):
        keys = pygame.key.get_pressed()
        
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.rect.x -= self.speed
            game_state['active_message'] = None # Hide text when moving
            
        elif keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.rect.x += self.speed
            game_state['active_message'] = None # Hide text when moving

        # Keep player on screen bounds
        if self.rect.left < 0: self.rect.left = 0
        if self.rect.right > map_width: self.rect.right = map_width
        self.rect.midbottom = (self.rect.centerx, self.floor_y)

def draw_ui(screen, game_state, font):
    if game_state.get('active_message'):
        msg_surf = font.render(game_state['active_message'], True, TEXT_COLOR)
        
        box_width = msg_surf.get_width() + 40
        box_height = msg_surf.get_height() + 20
        box_surf = pygame.Surface((box_width, box_height), pygame.SRCALPHA)
        box_surf.fill(UI_BOX_COLOR)

        box_rect = box_surf.get_rect(center=(SCREEN_WIDTH // 2, 100))
        screen.blit(box_surf, box_rect)

        msg_rect = msg_surf.get_rect(center=box_rect.center)
        screen.blit(msg_surf, msg_rect)

# --- MAIN EXECUTION ---
def main():
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Bookshelf Interaction Demo")
    clock = pygame.time.Clock()
    font = pygame.font.SysFont("Arial", 24, bold=True)

    # 1. SAFELY LOAD BACKGROUND
    bg_filename = "chapter1_level1.jpg"
    if os.path.exists(bg_filename):
        bg_image = pygame.image.load(bg_filename).convert()
        # Scale it to fit the screen height properly
        scale_ratio = SCREEN_HEIGHT / bg_image.get_height()
        map_width = int(bg_image.get_width() * scale_ratio)
        bg_image = pygame.transform.scale(bg_image, (map_width, SCREEN_HEIGHT))
    else:
        print(f"WARNING: Could not find '{bg_filename}'. Using a grey fallback background.")
        map_width = 1600
        bg_image = pygame.Surface((map_width, SCREEN_HEIGHT))
        bg_image.fill((50, 50, 50))

    floor_y = int(SCREEN_HEIGHT * 0.74) # Set player feet level

    player = Player(floor_y)
    camera = Camera(map_width, SCREEN_HEIGHT)
    game_state = {'active_message': None}

    # 2. CREATE INTERACTION ZONES
    # I have estimated these based on your image. 
    # Tweak the x, y, width, and height to make them fit perfectly!
    zones = pygame.sprite.Group()
    
    # Far Left Wooden Shelf
    zones.add(InteractableZone(x=20, y=250, width=150, height=190, message="A dusty wooden shelf. The books are unreadable."))
    
    # Middle-Left Wooden Shelf
    zones.add(InteractableZone(x=225, y=250, width=150, height=190, message="There is a strange symbol on these bindings..."))
    
    # Massive Gothic Background Shelf
    zones.add(InteractableZone(x=400, y=80, width=380, height=360, message="Hundreds of ancient, heavy tomes sit upon these stone shelves."))

    # Middle-Right Wooden Shelf
    zones.add(InteractableZone(x=515, y=250, width=150, height=190, message="These books are all written in a language you do not know."))

    # Right Side Desk/Books
    zones.add(InteractableZone(x=820, y=320, width=100, height=120, message="Someone was reading these recently. The ink is still fresh."))

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # --- UPDATE ---
        player.update(map_width, game_state)
        camera.update(player)

        # --- DRAW ---
        screen.blit(bg_image, (camera.camera.x, 0))

        for zone in zones:
            screen.blit(zone.image, camera.apply(zone))

        screen.blit(player.image, camera.apply(player))

        # Check for interactions (drawn above player)
        for zone in zones:
            zone.update(player, screen, camera, game_state, font)

        draw_ui(screen, game_state, font)

        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
