import pygame
import sys
import os

# --- Configuration ---
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600

WORLD_WIDTH = 1400
WORLD_HEIGHT = 787  

GAME_FPS = 60 

WALK_FILE = "player_walk.jpg.jpg"
IDLE_FILE = "player_idle.jpg.jpg"
BG_FILE = "Assets/Maps/chapter1/level2/ch1_lvl2.png"

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
        # Universal safe init
        pygame.sprite.Sprite.__init__(self)
        
        self.base_walk_frames = self.load_frames(WALK_FILE, 5, 5)
        self.base_idle_frames = self.load_frames(IDLE_FILE, 5, 5)

        self.layer = "foreground"
        self.fg_height = 80  
        self.bg_height = 55  
        
        self.current_frames = self.base_idle_frames
        self.frame_index = 0
        
        self.image = self.scale_frame(self.current_frames[self.frame_index], self.fg_height)
        self.rect = self.image.get_rect(topleft=(200, 500))
        
        self.speed = 5
        self.velocity_y = 0
        self.gravity = 0.8
        self.jump_strength = -12
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
        
        w = sheet.get_width() // cols
        h = sheet.get_height() // rows
        frames = []
        for r in range(rows):
            for c in range(cols):
                frames.append(sheet.subsurface(pygame.Rect(c*w, r*h, w, h)))
        return frames

    def scale_frame(self, raw_frame, target_height):
        # Force float division for safety across Python versions
        ratio = float(raw_frame.get_width()) / float(raw_frame.get_height())
        target_width = int(target_height * ratio)
        return pygame.transform.scale(raw_frame, (target_width, target_height))

    def handle_input(self, transition_zones):
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

        if keys[pygame.K_SPACE] and self.on_ground:
            self.velocity_y = self.jump_strength
            self.on_ground = False

        for zone in transition_zones:
            if self.rect.colliderect(zone):
                if keys[pygame.K_UP] and self.layer == "foreground":
                    self.layer = "background"
                    self.rect.y -= 70  
                    self.speed = 3     
                    
                elif keys[pygame.K_DOWN] and self.layer == "background":
                    self.layer = "foreground"
                    self.rect.y += 70
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
        
        if self.is_moving:
            base_set = self.base_walk_frames
            duration = 1000 // 24
        else:
            base_set = self.base_idle_frames
            duration = 1000 // 12

        if now - self.last_update > duration:
            self.last_update = now
            self.frame_index = (self.frame_index + 1) % len(base_set)
            
            raw_frame = base_set[self.frame_index]
            
            if self.layer == "foreground":
                target_h = self.fg_height
            else:
                target_h = self.bg_height
                
            scaled_frame = self.scale_frame(raw_frame, target_h)
            self.image = pygame.transform.flip(scaled_frame, not self.facing_right, False)
            
            old_bottom = self.rect.bottom
            self.rect = self.image.get_rect()
            self.rect.bottom = old_bottom 

    def update(self, platforms, transition_zones):
        self.handle_input(transition_zones)
        self.apply_physics(platforms)
        self.animate()


class Game:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Scrolling Library with Depth")
        self.clock = pygame.time.Clock()
        self.running = True

        try:
            self.bg_image = pygame.image.load(BG_FILE).convert()
            self.bg_image = pygame.transform.scale(self.bg_image, (WORLD_WIDTH, WORLD_HEIGHT))
        except Exception:
            print("Error: Could not find " + BG_FILE)
            self.bg_image = pygame.Surface((WORLD_WIDTH, WORLD_HEIGHT))
            self.bg_image.fill((30, 30, 40))

        self.player = Player()
        self.camera = Camera(WORLD_WIDTH, WORLD_HEIGHT)

        self.foreground_platforms = [
            pygame.Rect(0, 720, WORLD_WIDTH, 60) 
        ]
        
        self.background_platforms = [
            pygame.Rect(0, 650, WORLD_WIDTH, 50) 
        ]

        self.transition_zones = [
            pygame.Rect(350, 600, 100, 150),  
            pygame.Rect(800, 600, 100, 150),  
            pygame.Rect(1100, 600, 100, 150)  
        ]

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False

    def update(self):
        if self.player.layer == "foreground":
            active_platforms = self.foreground_platforms
        else:
            active_platforms = self.background_platforms
            
        self.player.update(active_platforms, self.transition_zones)
        self.camera.update(self.player)

    def draw(self):
        self.screen.blit(self.bg_image, self.camera.apply(self.bg_image.get_rect()))

        for zone in self.transition_zones:
            pygame.draw.rect(self.screen, (0, 255, 0), self.camera.apply(zone), 2)

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
