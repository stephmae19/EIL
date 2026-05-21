# Model/Player.py
import pygame

class Player:
    def __init__(self, x=100, y=100, sprite_path=None, start_room=None):
        self.size = 40
        self.speed = 5
        self.vel_x = 0
        self.vel_y = 0
        self.gravity = 0.6
        self.jump_strength = 12
        self.on_ground = False

        self.rect = pygame.Rect(x, y, self.size, self.size)
        self.color = (0, 200, 0)
        self.sprite = None
        if sprite_path:
            try:
                self.sprite = pygame.image.load(sprite_path).convert_alpha()
                self.sprite = pygame.transform.scale(self.sprite, (self.size, self.size))
            except Exception as e:
                print(f"Failed to load sprite: {e}")

        self.health = 100
        self.inventory = []

    # --- Input Handling ---
    def handle_input(self, event):
        """Process keyboard input for left/right movement."""
        if event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_LEFT, pygame.K_a):
                self.move_left()
            elif event.key in (pygame.K_RIGHT, pygame.K_d):
                self.move_right()
            # elif event.key == pygame.K_SPACE and self.on_ground:
            #     # Jump only if on ground (commented out for now)
            #     self.vel_y = -self.jump_strength

        elif event.type == pygame.KEYUP:
            if event.key in (pygame.K_LEFT, pygame.K_RIGHT, pygame.K_a, pygame.K_d):
                self.stop_horizontal()

    # --- Movement controls ---
    def move_left(self):
        self.vel_x = -self.speed

    def move_right(self):
        self.vel_x = self.speed

    def stop_horizontal(self):
        self.vel_x = 0

    # --- Update Logic ---
    def update(self):
        # Apply gravity (still active, but jump disabled)
        self.vel_y += self.gravity

        # Update position
        self.rect.x += self.vel_x
        self.rect.y += self.vel_y

        # Clamp to screen bounds
        self.rect.x = max(0, min(self.rect.x, 800 - self.size))
        self.rect.y = min(self.rect.y, 600 - self.size)

    # --- Rendering ---
    def render(self, screen):
        if self.sprite:
            screen.blit(self.sprite, self.rect)
        else:
            pygame.draw.rect(screen, self.color, self.rect)

    # --- Inventory ---
    def add_item(self, item):
        self.inventory.append(item)

    def remove_item(self, item):
        if item in self.inventory:
            self.inventory.remove(item)

    # --- Combat / Health ---
    def take_damage(self, amount):
        self.health -= amount
        print(f"Player took {amount} damage. Health: {self.health}")

    @property
    def position(self):
        return (self.rect.x, self.rect.y)
