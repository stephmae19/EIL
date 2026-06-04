import pygame
import sys
import os

# --- Configuration ---
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
GAME_FPS = 60 

WALK_FILE = "player_walk.jpg.jpg"
IDLE_FILE = "player_idle.jpg.jpg"

class Camera:
    def __init__(self, width, height):
        self.camera = pygame.Rect(0, 0, width, height)
        self.width = width
        self.height = height

    def apply(self, entity_rect):
        return entity_rect.move(self.camera.topleft)

    def update(self, target):
        x = -target.rect.centerx + int(SCREEN_WIDTH / 2)
        y = -target.rect.centery + int(SCREEN_HEIGHT / 2)
        x = min(0, max(x, -(self.width - SCREEN_WIDTH)))
        y = min(0, max(y, -(self.height - SCREEN_HEIGHT)))
        self.camera = pygame.Rect(x, y, self.width, self.height)


class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        # Cache pristine base frames at full resolution
        self.base_walk_frames = self.load_frames(WALK_FILE, 5, 5)
        self.base_idle_frames = self.load_frames(IDLE_FILE, 5, 5)

        # Depth Layer management
        self.layer = "foreground"  # Options: "foreground", "background"
        self.scale_factor = 1.0     # 1.0 for foreground, scaled down for background

        self.current_frames = self.base_idle_frames
        self.frame_index = 0
        self.image = self.current_frames[self.frame_index]
        self.rect = self.image.get_rect(topleft=(100, 380))
        
        # Physics / Movement
        self.speed = 5
        self.velocity_y = 0
        self.gravity = 0.8
        self.jump_strength = -14
        self.on_ground = False
        
        self.facing_right = True
        self.is_moving = False
        self.last_update = pygame.time.get_ticks()

    def load_frames(self, filename, rows, cols):
        if not os.path.exists(filename):
            surf = pygame.Surface((64, 128))
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

    def handle_input(self, transition_zones):
        keys = pygame.key.get_pressed()
        self.is_moving = False
        
        # Horizontal Movement
        if keys[pygame.K_LEFT]:
            self.rect.x -= self.speed
            self.facing_right = False
            self.is_moving = True
        elif keys[pygame.K_RIGHT]:
            self.rect.x += self.speed
            self.facing_right = True
            self.is_moving = True

        # Jump
        if keys[pygame.K_SPACE] and self.on_ground:
            self.velocity_y = self.jump_strength
            self.on_ground = False

        # --- Layer Transition Detection ("Proper Tile" logic) ---
        for zone in transition_zones:
            if self.rect.colliderect(zone):
                # Move to background if standing on a zone in foreground and pressing UP
                if keys[pygame.K_UP] and self.layer == "foreground":
                    self.layer = "background"
                    self.scale_factor = 0.60  # Scale down to be smaller than back bookshelves
                    # Offset position slightly upward to align visually with back floor path
                    self.rect.y -= 40 
                    self.speed = 3 # Slightly slower movement speed adds depth realism
                    
                # Move to foreground if standing on a zone in background and pressing DOWN
                elif keys[pygame.K_DOWN] and self.layer == "background":
                    self.layer = "foreground"
                    self.scale_factor = 1.0
                    self.rect.y += 40
                    self.speed = 5

    def apply_physics(self, platforms):
        self.velocity_y += self.gravity
        self.rect.y += self.velocity_y

        self.on_ground = False
        for platform in platforms:
            if self.rect.colliderect(platform):
                if self.velocity_y > 0:
                    self.rect.bottom = platform.top
                    self.velocity_y = 0
                    self.on_ground = True

    def animate(self):
        now = pygame.time.get_ticks()
        # Select base source animation map
        base_set = self.base_walk_frames if self.is_moving else self.base_idle_frames
        duration = (1000 // 24) if self.is_moving else (1000 // 12)

        if now - self.last_update > duration:
            self.last_update = now
            self.frame_index = (self.frame_index + 1) % len(base_set)
            
            # 1. Grab raw source frame
            raw_frame = base_set[self.frame_index]
            
            # 2. Dynamic Scaling based on layer constraint
            new_width = int(raw_frame.get_width() * self.scale_factor)
            new_height = int(raw_frame.get_height() * self.scale_factor)
            scaled_frame = pygame.transform.scale(raw_frame, (new_width, new_height))
            
            # 3. Handle flipping orientation
            self.image = pygame.transform.flip(scaled_frame, not self.facing_right, False)
            
            # 4. Readjust collision box to match newly scaled image size dimensions
            old_center = self.rect.center
            self.rect = self.image.get_rect()
            self.rect.center = old_center

    def update(self, platforms, transition_zones):
        self.handle_input(transition_zones)
        self.apply_physics(platforms)
        self.animate()


class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Layer Shifting Library System")
        self.clock = pygame.time.Clock()
        self.running = True

        self.player = Player()

        self.world_width = 1600
        self.world_height = 600
        self.camera = Camera(self.world_width, self.world_height)

        # --- Environment Layout ---
        
        # 1. Collidable Platforms segregated by layer depth
        self.foreground_platforms = [
            pygame.Rect(0, 500, 1600, 100) # Foreground Floor Line
        ]
        self.background_platforms = [
            pygame.Rect(0, 460, 1600, 100) # Recessed Background floor line
        ]

        # 2. Proper Tiles / Interactive Transfer Zones (e.g. at the open archway space or alcoves)
        self.transition_zones = [
            pygame.Rect(450, 450, 80, 60), # Transition point 1 (e.g., between shelves)
            pygame.Rect(1100, 450, 80, 60) # Transition point 2 (e.g., near the arch/clock)
        ]

        # 3. Environmental Objects for Visual Depth layering
        self.background_bookshelves = [
            pygame.Rect(100, 200, 250, 260),
            pygame.Rect(700, 180, 300, 280)
        ]
        self.foreground_bookshelves = [
            pygame.Rect(50, 260, 200, 240),   # Left foreground bookshelf
            pygame.Rect(350, 260, 200, 240),  # Center foreground bookshelf
            pygame.Rect(1200, 260, 200, 240)  # Right foreground bookshelf
        ]

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False

    def update(self):
        # Select active path configurations depending on player depth layer location
        active_platforms = (self.foreground_platforms if self.player.layer == "foreground" 
                            else self.background_platforms)
        
        self.player.update(active_platforms, self.transition_zones)
        self.camera.update(self.player)

    def draw(self):
        self.screen.fill((18, 16, 22)) # Atmospheric Dark Tint
        
        # LAYER 1: Deep Static Background Wall Geometry
        for shelf in self.background_bookshelves:
            pygame.draw.rect(self.screen, (32, 30, 40), self.camera.apply(shelf)) # Deep Background Shelves

        # LAYER 2: Draw Transition Zones Visual Indicators ("Proper tiles")
        for zone in self.transition_zones:
            # Subtle indicator overlay context on the floor
            pygame.draw.rect(self.screen, (50, 120, 80), self.camera.apply(zone), 2)

        # LAYER 3: Draw Player if they are standing in the BACKGROUND depth
        if self.player.layer == "background":
            self.screen.blit(self.player.image, self.camera.apply(self.player.rect))

        # LAYER 4: Draw Foreground Solid Elements (Overlaps background player)
        for shelf in self.foreground_bookshelves:
            pygame.draw.rect(self.screen, (55, 42, 35), self.camera.apply(shelf)) # Solid Main Shelves
            pygame.draw.rect(self.screen, (85, 65, 55), self.camera.apply(shelf), 3) # Shelf trims

        for floor in self.foreground_platforms:
            pygame.draw.rect(self.screen, (75, 55, 45), self.camera.apply(floor)) # Floorboards

        # LAYER 5: Draw Player if they are standing in the FOREGROUND depth
        if self.player.layer == "foreground":
            self.screen.blit(self.player.image, self.camera.apply(self.player.rect))

        pygame.display.flip()

    def run(self):
        while self.running:
            self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(GAME_FPS)
        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    game = Game()
    game.run()
