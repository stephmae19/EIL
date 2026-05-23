# Model/Player.py
import pygame
import sys

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
ROWS = 5
COLS = 5

class Player(pygame.sprite.Sprite):
    def __init__(self, x=100, y=100, sprite_path="Assets/Characters/player_walk.jpeg", start_room=None):
        super().__init__()

        try:
            self.sprite_sheet = pygame.image.load(sprite_path).convert()
        except pygame.error as e:
            print(f"Error: Could not load sprite sheet {sprite_path}. {e}")
            pygame.quit()
            sys.exit()

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
        self.rect = self.image.get_rect(topleft=(x, y))

        # Movement state
        self.speed = 5
        self.animation_speed = 0.2
        self.facing_right = True
        self.is_moving = False
        self.direction = 0

        # Stats
        self.health = 100
        self.inventory = []

    # --- Method Overloading Examples ---
    def move(self, speed=None, direction=None):
        """Move with optional speed and direction overrides."""
        if speed is not None:
            self.speed = speed
        if direction is not None:
            self.direction = direction
            self.is_moving = True

        if self.is_moving:
            self.rect.x += self.direction * self.speed
            if self.rect.left < 0:
                self.rect.left = 0
            if self.rect.right > SCREEN_WIDTH:
                self.rect.right = SCREEN_WIDTH

    def interact(self, item=None):
        """Interact with environment or optional item."""
        if item:
            print(f"Player interacts with {item}.")
            if item in self.inventory:
                print(f"{item} is already in inventory.")
            else:
                self.add_item(item)
                print(f"{item} added to inventory.")
        else:
            print("Player interacts with the environment.")

    def examine(self, target=None):
        """Examine surroundings or a specific target."""
        if target:
            print(f"Player examines {target}.")
        else:
            print("Player looks around the room.")

    # --- Input Handling ---
    def handle_input(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_LEFT, pygame.K_a):
                self.direction = -1
                self.facing_right = False
                self.is_moving = True
            elif event.key in (pygame.K_RIGHT, pygame.K_d):
                self.direction = 1
                self.facing_right = True
                self.is_moving = True

        elif event.type == pygame.KEYUP:
            if event.key in (pygame.K_LEFT, pygame.K_RIGHT, pygame.K_a, pygame.K_d):
                self.stop_movement()

    def stop_movement(self):
        self.is_moving = False
        self.direction = 0

    def animate(self):
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

        self.rect = self.image.get_rect(center=old_center)

    def update(self):
        self.move()
        self.animate()

    def render(self, screen):
        screen.blit(self.image, self.rect)

    # --- Inventory ---
    def add_item(self, item):
        self.inventory.append(item)

    def remove_item(self, item):
        if item in self.inventory:
            self.inventory.remove(item)

    def take_damage(self, amount):
        self.health -= amount
        print(f"Player took {amount} damage. Health: {self.health}")

    @property
    def position(self):
        return (self.rect.x, self.rect.y)
