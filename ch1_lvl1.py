# ch1_lvl1.py
import pygame
import sys
import os
import gameover  # Add this import
from ui_layer import UILayer

# --- Filenames ---
WALK_FILE = "Assets/Characters/player_walk.png"
WALK_FILE2 = "Assets/Characters/player_walk2.png"
IDLE_FILE = "Assets/Characters/player_idle.png"
IDLE_FILE2 = "Assets/Characters/player_idle2.png"
BG_FILE = "Assets/MAPS/chapter1/ch1_lvl1.png"
MANUSCRIPT_FILE = "Assets/Objects-Items/manuscript.png"

# --- Config ---
FLOOR_HEIGHT_PERCENTAGE = 0.74
JPG_BLACK_TOLERANCE = 25


class Camera:
    def __init__(self, width, height, screen_w, screen_h):
        self.camera = pygame.Rect(0, 0, width, height)
        self.width = width
        self.height = height
        self.screen_w = screen_w
        self.screen_h = screen_h
        self.health = 100  # starting health value

    def apply(self, entity):
        return entity.rect.move(self.camera.topleft)

    def apply_rect(self, rect):
        return rect.move(self.camera.topleft)

    def update(self, target):
        x = -target.rect.centerx + int(self.screen_w / 2)
        y = 0
        x = min(0, x)
        x = max(-(self.width - self.screen_w), x)
        self.camera = pygame.Rect(x, y, self.width, self.height)


class InteractiveObject:
    def __init__(self, x, y, width=150, height=250,
                 has_manuscript=False, inventory_item=None,
                 prompt="Press 'E' to interact", image_file=None):
        self.rect = pygame.Rect(x, y, width, height)
        self.has_manuscript = has_manuscript
        self.inventory_item = inventory_item
        self.already_searched = False
        self.prompt = prompt

        # ✅ Load image if provided
        self.image = None
        if image_file and os.path.exists(image_file):
            raw = pygame.image.load(image_file).convert_alpha()
            self.image = pygame.transform.scale(raw, (width, height))

    def resize(self, new_width, new_height):
        """Resize the interactive object rectangle."""
        self.rect.width = new_width
        self.rect.height = new_height

    def move(self, new_x, new_y):
        """Move the interactive object to a new position."""
        self.rect.x = new_x
        self.rect.y = new_y


class Player(pygame.sprite.Sprite):
    def __init__(self, floor_y, x=400, y=None, scale=0.45, chosen_character=None):
        super().__init__()
        self.scale = scale

        # Select files based on character
        if chosen_character == "charlie":  # Charlie
            walk_file = WALK_FILE2
            idle_file = IDLE_FILE2
        else:
            walk_file = WALK_FILE
            idle_file = IDLE_FILE

        # Load frames with transparency and scaling
        self.walk_frames = self.load_frames(walk_file, 5, 5)
        self.idle_frames = self.load_frames(idle_file, 5, 5)

        self.current_frames = self.idle_frames
        self.frame_index = 0
        self.image = self.current_frames[self.frame_index]

        # ✅ adjustable position
        if y is None:
            # Default: place at floor level
            self.rect = self.image.get_rect(midbottom=(x, floor_y))
        else:
            self.rect = self.image.get_rect(topleft=(x, y))

        self.walk_speed = 4
        self.run_speed = 9
        self.speed = self.walk_speed

        self.facing_right = True
        self.is_moving = False
        self.is_running = False

        self.manuscripts_found = 0
        self.puzzle_solved = False

        self.health = 100

        self.last_update = pygame.time.get_ticks()
        self.frame_duration = 1000 // 12

        self.inventory = []

    def load_frames(self, filename, rows, cols):
        if not os.path.exists(filename):
            surf = pygame.Surface((32, 32))
            surf.fill((255, 0, 0))
            return [surf]

        sheet = pygame.image.load(filename).convert_alpha()

        # Apply transparency to almost-black pixels
        sheet = sheet.copy()
        width, height = sheet.get_size()
        for x in range(width):
            for y in range(height):
                r, g, b, a = sheet.get_at((x, y))
                if r < JPG_BLACK_TOLERANCE and g < JPG_BLACK_TOLERANCE and b < JPG_BLACK_TOLERANCE:
                    sheet.set_at((x, y), (r, g, b, 0))

        # Slice into frames
        w, h = sheet.get_width() // cols, sheet.get_height() // rows
        frames = []
        for r in range(rows):
            for c in range(cols):
                frame = sheet.subsurface(pygame.Rect(c * w, r * h, w, h))
                # ✅ use scale factor
                scaled_frame = pygame.transform.scale(frame, (int(w * self.scale), int(h * self.scale)))
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
            self.speed = self.walk_speed

        # Movement: A/D and Arrow keys
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.rect.x -= self.speed
            self.facing_right = False
            self.is_moving = True
        elif keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.rect.x += self.speed
            self.facing_right = True
            self.is_moving = True

        if self.rect.left < 0:
            self.rect.left = 0
        if self.rect.right > map_width:
            self.rect.right = map_width

    def animate(self):
        now = pygame.time.get_ticks()
        target_frames = self.walk_frames if self.is_moving else self.idle_frames
        self.frame_duration = 1000 // (36 if self.is_running else (20 if self.is_moving else 12))

        if self.current_frames != target_frames:
            self.current_frames = target_frames
            self.frame_index = 0
            self.last_update = now

        if now - self.last_update > self.frame_duration:
            self.last_update = now
            self.frame_index = (self.frame_index + 1) % len(self.current_frames)
            raw_image = self.current_frames[self.frame_index]
            self.image = pygame.transform.flip(raw_image, True, False) if not self.facing_right else raw_image

    def update(self, map_width):
        self.update_logic(map_width)
        self.animate()


# --- Main Loop wrapped in a function ---
def run_level(chosen_character=None):
    pygame.init()
    pygame.font.init()

    # --- Base Resolution (Design Target) ---
    BASE_WIDTH, BASE_HEIGHT = 1920, 1080

    # ✨ FIX: Reuse main.py's window surface instead of executing set_mode globally upon module import
    screen = pygame.display.get_surface()
    if screen is None:
        info = pygame.display.Info()
        native_width, native_height = info.current_w, info.current_h
        os.environ['SDL_VIDEO_CENTERED'] = '1'
        screen = pygame.display.set_mode((native_width, native_height - 50), pygame.RESIZABLE)

    pygame.display.set_caption("Chapter 1 - Level 1")

    # Internal fixed surface (always BASE_WIDTH x BASE_HEIGHT)
    game_surface = pygame.Surface((BASE_WIDTH, BASE_HEIGHT))
    clock = pygame.time.Clock()

    ui_font = pygame.font.SysFont("arial", 28, bold=True)
    feedback_font = pygame.font.SysFont("arial", 24, italic=True)

    # Background Setup
    if not os.path.exists(BG_FILE):
        bg_image = pygame.Surface((BASE_WIDTH * 2, BASE_HEIGHT))
        bg_image.fill((50, 50, 80))
    else:
        original_bg = pygame.image.load(BG_FILE).convert()
        scale_factor = BASE_HEIGHT / original_bg.get_height()
        new_bg_width = int(original_bg.get_width() * scale_factor)
        bg_image = pygame.transform.scale(original_bg, (new_bg_width, BASE_HEIGHT))

    MAP_WIDTH, MAP_HEIGHT = bg_image.get_width(), bg_image.get_height()
    floor_y = int(MAP_HEIGHT * FLOOR_HEIGHT_PERCENTAGE)

    # --- Scaling factor ---
    scale_factor = BASE_HEIGHT / 1080

    # ✨ FIX: Moved interactive object creation inside run_level() so state resets fresh on every entry
    interactive_objects = [
        InteractiveObject(
            x=int(180 * scale_factor),
            y=int(floor_y - int(140 * scale_factor)),
            width=int(5 * scale_factor),
            height=int(40 * scale_factor),
            has_manuscript=False,
            inventory_item="H",
            prompt="I found a letter H."
        ),
        InteractiveObject(
            x=int(490 * scale_factor),
            y=int(floor_y - int(200 * scale_factor)),
            width=int(5 * scale_factor),
            height=int(40 * scale_factor),
            has_manuscript=False,
            inventory_item="L",
            prompt="I found a letter L."
        ),
        InteractiveObject(
            x=int(560 * scale_factor),
            y=int(floor_y - int(200 * scale_factor)),
            width=int(5 * scale_factor),
            height=int(40 * scale_factor),
            has_manuscript=False,
            inventory_item="E",
            prompt="I found a letter E."
        ),
        InteractiveObject(
            x=int(1000 * scale_factor),
            y=int(floor_y - int(200 * scale_factor)),
            width=int(5 * scale_factor),
            height=int(40 * scale_factor),
            has_manuscript=False,
            inventory_item="K",
            prompt="I found a letter K."
        ),
        InteractiveObject(
            x=int(1100 * scale_factor),
            y=int(floor_y - int(200 * scale_factor)),
            width=int(5 * scale_factor),
            height=int(40 * scale_factor),
            has_manuscript=False,
            inventory_item="M",
            prompt="I found a letter M."
        ),
        InteractiveObject(
            x=int(900 * scale_factor),
            y=int(floor_y - int(120 * scale_factor)),
            width=int(5 * scale_factor),
            height=int(40 * scale_factor),
            has_manuscript=False,
            inventory_item="C",
            prompt="I found a letter C."
        ),
        InteractiveObject(
            x=int(1400 * scale_factor),
            y=int(floor_y - int(100 * scale_factor)),
            width=int(5 * scale_factor),
            height=int(40 * scale_factor),
            has_manuscript=False,
            inventory_item="O",
            prompt="Oh, there's something on the floor. I found a letter O."
        ),
    ]

    interactive_objects.append(
        InteractiveObject(
            x=int(MAP_WIDTH * 0.78),
            y=int(floor_y - int(BASE_HEIGHT * 0.25)),
            width=int(80 * scale_factor),
            height=int(80 * scale_factor),
            has_manuscript=True,
            prompt="A mysterious manuscript lies here...",
            image_file=MANUSCRIPT_FILE
        )
    )

    # ✨ FIX: Instantiate player once with the correct character choice
    player = Player(
        floor_y,
        x=int(BASE_WIDTH * 0.10),
        y=int(BASE_HEIGHT * 0.48),
        scale=(BASE_HEIGHT / 1080) * 1.1,
        chosen_character=chosen_character
    )

    camera = Camera(MAP_WIDTH, MAP_HEIGHT, BASE_WIDTH, BASE_HEIGHT)
    ui_layer = UILayer(game_surface)

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                return "escape"

            if event.type == pygame.KEYDOWN and event.key == pygame.K_e:
                found = False
                for obj in interactive_objects:
                    if player.rect.colliderect(obj.rect):
                        found = True

                        if obj.has_manuscript:
                            if player.puzzle_solved:
                                obj.prompt = "The manuscript has already been deciphered."
                                ui_layer.show_subtitle(obj.prompt, 2000)
                            else:
                                if not obj.already_searched:
                                    obj.already_searched = True
                                else:
                                    ui_layer.show_subtitle("You examine the manuscript again...", 2000)

                                import ch1_lvl1_puz
                                ch1_lvl1_puz.run_puzzle(player, ui_layer, screen)

                                if player.puzzle_solved and not obj.already_searched:
                                    ui_layer.show_subtitle("You found a hidden manuscript!", 3000)
                                    obj.already_searched = True
                                    obj.prompt = "The manuscript has already been deciphered."
                            break

                        elif obj.inventory_item:
                            if not obj.already_searched:
                                if len(player.inventory) < 6:
                                    player.inventory.append(obj.inventory_item)
                                    obj.already_searched = True
                                    ui_layer.show_subtitle(f"You picked up {obj.inventory_item}!")
                                else:
                                    ui_layer.show_subtitle("My inventory is full.", 2000)
                            else:
                                ui_layer.show_subtitle("You already picked this up.", 2000)

                        else:
                            if not obj.already_searched:
                                obj.already_searched = True
                                ui_layer.show_subtitle(obj.prompt, 2000)
                            else:
                                ui_layer.show_subtitle("You already searched this part.", 2000)
                        break

                if not found:
                    ui_layer.show_subtitle("There is nothing to interact with here.", 1500)

                ui_layer.handle_input(event)
                ui_layer.click_insanity_loss()

        # Update Game Logic
        player.update(MAP_WIDTH)
        camera.update(player)

        # Render Game Surface
        game_surface.fill((0, 0, 0))
        game_surface.blit(bg_image, (camera.camera.x, camera.camera.y))

        for obj in interactive_objects:
            if obj.image:
                game_surface.blit(obj.image, camera.apply_rect(obj.rect))

        game_surface.blit(player.image, camera.apply(player))

        ui_text = ui_font.render(f"Manuscripts: {player.manuscripts_found} / 1", True, (255, 215, 0))
        game_surface.blit(ui_text, (BASE_WIDTH - 280, 20))

        ui_layer.draw(player)

        # Scale & Preserving Aspect Ratio Blit
        window_width, window_height = screen.get_size()
        scale = min(window_width / BASE_WIDTH, window_height / BASE_HEIGHT)
        scaled_w, scaled_h = int(BASE_WIDTH * scale), int(BASE_HEIGHT * scale)

        scaled_surface = pygame.transform.smoothscale(game_surface, (scaled_w, scaled_h))

        x_offset = (window_width - scaled_w) // 2
        y_offset = (window_height - scaled_h) // 2

        screen.fill((0, 0, 0))
        screen.blit(scaled_surface, (x_offset, y_offset))
        pygame.display.flip()
        clock.tick(60)

        # ✅ Check for Game Over state
        if ui_layer.is_game_over:
            action = gameover.show_game_over(screen)

            if action == "restart":
                player.health = 100
                player.rect.midbottom = (int(BASE_WIDTH * 0.10), floor_y)
                ui_layer.hearts = ui_layer.max_hearts
                ui_layer.insanity_level = len(ui_layer.insanity_frames) - 1
                ui_layer.reset_timer()
                ui_layer.is_game_over = False
                continue

            elif action == "menu":
                return "menu"


# ✅ Allow standalone execution (safely hooks back into main loop if requested)
if __name__ == "__main__":
    result = run_level()
    if result == "menu":
        try:
            import main

            main.main()
        except ImportError:
            pass