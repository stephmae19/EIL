import pygame
import sys
import os

# --- 1. YOUR FILENAMES ---
WALK_FILE = "player_walk.jpg.jpg" 
IDLE_FILE = "player_idle.jpg.jpg"
BG_FILE = "received_836993658930381.webp"
MANUSCRIPT_FILE = "OIP.jpg" # Updated to your exact filename

# --- 2. EASY TWEAK VARIABLES ---
FLOOR_HEIGHT_PERCENTAGE = 0.74 
JPG_BLACK_TOLERANCE = 25 


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
        """Helper to apply camera offset to a standard pygame.Rect"""
        return rect.move(self.camera.topleft)

    def update(self, target):
        x = -target.rect.centerx + int(self.screen_w / 2)
        y = 0 
        x = min(0, x)  
        x = max(-(self.width - self.screen_w), x)  
        self.camera = pygame.Rect(x, y, self.width, self.height)


# --- NEW: INVISIBLE BOOKSHELF ZONES ---
class BookshelfZone:
    def __init__(self, x, bottom_y, has_manuscript):
        # We make the interaction zone 150px wide and 250px tall
        self.rect = pygame.Rect(x, bottom_y - 250, 150, 250)
        self.has_manuscript = has_manuscript
        self.already_searched = False

class Player(pygame.sprite.Sprite):
    def __init__(self, floor_y):
        super().__init__()
        self.walk_frames = self.load_frames(WALK_FILE, 5, 5)
        self.idle_frames = self.load_frames(IDLE_FILE, 5, 5)

        self.current_frames = self.idle_frames
        self.frame_index = 0
        self.image = self.current_frames[self.frame_index]
        self.rect = self.image.get_rect(midbottom=(400, floor_y))
        
        self.walk_speed = 4    
        self.run_speed = 9     
        self.speed = self.walk_speed 
        
        self.facing_right = True
        self.is_moving = False
        self.is_running = False 
        
        # INVENTORY SYSTEM
        self.manuscripts_found = 0 
        
        self.last_update = pygame.time.get_ticks()
        self.frame_duration = 1000 // 12

    def load_frames(self, filename, rows, cols):
        if not os.path.exists(filename):
            surf = pygame.Surface((32, 32))
            surf.fill((255, 0, 0))
            return [surf]
        
        sheet = pygame.image.load(filename).convert_alpha()
        pixel_array = pygame.PixelArray(sheet)
        for x in range(sheet.get_width()):
            for y in range(sheet.get_height()):
                color = sheet.unmap_rgb(pixel_array[x][y])
                if color.r < JPG_BLACK_TOLERANCE and color.g < JPG_BLACK_TOLERANCE and color.b < JPG_BLACK_TOLERANCE:
                    pixel_array[x][y] = (0, 0, 0, 0) 
        del pixel_array 
        
        w, h = sheet.get_width() // cols, sheet.get_height() // rows
        frames = []
        for r in range(rows):
            for c in range(cols):
                original_frame = sheet.subsurface(pygame.Rect(c*w, r*h, w, h))
                scaled_w = int(w * 0.45)
                scaled_h = int(h * 0.45)
                scaled_frame = pygame.transform.scale(original_frame, (scaled_w, scaled_h))
                frames.append(scaled_frame)
        return frames

    def update_logic(self, map_width):
        keys = pygame.key.get_pressed()
        self.is_moving = False
        self.is_running = False
        
        if keys[pygame.K_LSHIFT] or keys[pygame.K_RSHIFT]:
            self.is_running = True
            self.speed = self.run_speed
        else:
            self.is_running = False
            self.speed = self.walk_speed
        
        if keys[pygame.K_LEFT]:
            self.rect.x -= self.speed
            self.facing_right = False
            self.is_moving = True
        elif keys[pygame.K_RIGHT]:
            self.rect.x += self.speed
            self.facing_right = True
            self.is_moving = True

        if self.rect.left < 0:
            self.rect.left = 0
        if self.rect.right > map_width:
            self.rect.right = map_width

    def animate(self):
        now = pygame.time.get_ticks()
        
        if self.is_moving:
            target_frames = self.walk_frames
            if self.is_running:
                self.frame_duration = 1000 // 36 
            else:
                self.frame_duration = 1000 // 20  
        else:
            target_frames = self.idle_frames
            self.frame_duration = 1000 // 12 

        if self.current_frames != target_frames:
            self.current_frames = target_frames
            self.frame_index = 0
            self.last_update = now

        if now - self.last_update > self.frame_duration:
            self.last_update = now
            self.frame_index = (self.frame_index + 1) % len(self.current_frames)
            
            raw_image = self.current_frames[self.frame_index]
            if not self.facing_right:
                self.image = pygame.transform.flip(raw_image, True, False)
            else:
                self.image = raw_image

    def update(self, map_width):
        self.update_logic(map_width)
        self.animate()

# --- Initialization & Setup ---
pygame.init()
pygame.font.init()

screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
SCREEN_WIDTH = screen.get_width()
SCREEN_HEIGHT = screen.get_height()
clock = pygame.time.Clock()

ui_font = pygame.font.SysFont("arial", 28, bold=True)
feedback_font = pygame.font.SysFont("arial", 24, italic=True)

if not os.path.exists(BG_FILE):
    bg_image = pygame.Surface((SCREEN_WIDTH * 2, SCREEN_HEIGHT))
    bg_image.fill((50, 50, 80))
else:
    original_bg = pygame.image.load(BG_FILE).convert()
    scale_factor = SCREEN_HEIGHT / original_bg.get_height()
    new_bg_width = int(original_bg.get_width() * scale_factor)
    bg_image = pygame.transform.scale(original_bg, (new_bg_width, SCREEN_HEIGHT))

MAP_WIDTH = bg_image.get_width()
MAP_HEIGHT = bg_image.get_height()
floor_y = int(MAP_HEIGHT * FLOOR_HEIGHT_PERCENTAGE)

# --- LOAD MANUSCRIPT ICON FOR UI ---
if os.path.exists(MANUSCRIPT_FILE):
    manuscript_icon = pygame.image.load(MANUSCRIPT_FILE).convert()
    manuscript_icon.set_colorkey((0,0,0)) # Remove black background if it has one
    manuscript_icon = pygame.transform.scale(manuscript_icon, (40, 40))
else:
    manuscript_icon = pygame.Surface((40, 40))
    manuscript_icon.fill((255, 215, 0))

# --- CREATE BOOKSHELF ZONES ---
# Tweak these X-coordinates to perfectly align with the shelves in your background!
bookshelves = [
    BookshelfZone(x=300, bottom_y=floor_y, has_manuscript=False),
    BookshelfZone(x=800, bottom_y=floor_y, has_manuscript=True),  # Contains Manuscript
    BookshelfZone(x=1300, bottom_y=floor_y, has_manuscript=False),
    BookshelfZone(x=1800, bottom_y=floor_y, has_manuscript=True), # Contains Manuscript
    BookshelfZone(x=2300, bottom_y=floor_y, has_manuscript=False)
]

player = Player(floor_y)
camera = Camera(MAP_WIDTH, MAP_HEIGHT, SCREEN_WIDTH, SCREEN_HEIGHT)

# Feedback message system
feedback_msg = ""
feedback_timer = 0

# --- Main Game Loop ---
while True:
    now = pygame.time.get_ticks()
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
            
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            pygame.quit()
            sys.exit()

        # --- INTERACT LOGIC ---
        if event.type == pygame.KEYDOWN and event.key == pygame.K_e:
            found_something_nearby = False
            
            for shelf in bookshelves:
                # If player is touching this invisible shelf zone
                if player.rect.colliderect(shelf.rect):
                    found_something_nearby = True
                    
                    if shelf.already_searched:
                        feedback_msg = "You already searched this shelf."
                        feedback_timer = now + 2000 # Show for 2 seconds
                    elif shelf.has_manuscript:
                        shelf.already_searched = True
                        player.manuscripts_found += 1
                        feedback_msg = "You found a hidden manuscript!"
                        feedback_timer = now + 3000 
                    else:
                        shelf.already_searched = True
                        feedback_msg = "Just old, dusty books..."
                        feedback_timer = now + 2000
                        
                    break # Stop checking other shelves once we interacted with one

            if not found_something_nearby:
                feedback_msg = "There is nothing to interact with here."
                feedback_timer = now + 1500

    # 1. Update Game State
    player.update(MAP_WIDTH)
    camera.update(player)

    # 2. Draw Background
    screen.fill((0, 0, 0)) 
    screen.blit(bg_image, (camera.camera.x, camera.camera.y))

    # 3. Draw Interaction Prompts
    for shelf in bookshelves:
        if player.rect.colliderect(shelf.rect):
            # Show the E prompt above the shelf if we are touching it
            prompt_text = ui_font.render("Press 'E' to Search", True, (255, 255, 255))
            prompt_rect = prompt_text.get_rect(midbottom=(shelf.rect.centerx, shelf.rect.top - 20))
            screen.blit(prompt_text, camera.apply_rect(prompt_rect))

    # 4. Draw Player
    screen.blit(player.image, camera.apply(player))

    # 5. Draw UI (Inventory)
    ui_text = ui_font.render(f"Manuscripts: {player.manuscripts_found} / 2", True, (255, 215, 0)) 
    screen.blit(ui_text, (SCREEN_WIDTH - 280, 20))
    screen.blit(manuscript_icon, (SCREEN_WIDTH - 330, 15))

    # 6. Draw Feedback Message (e.g. "You found a manuscript!")
    if now < feedback_timer:
        msg_surface = feedback_font.render(feedback_msg, True, (150, 255, 150))
        # Draw it near the bottom of the screen
        msg_rect = msg_surface.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 50))
        screen.blit(msg_surface, msg_rect)

    # 7. Flip Display
    pygame.display.flip()
    clock.tick(60)
