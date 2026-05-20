# Model/Player.py
import pygame

class Player:
    def __init__(self, x=100, y=100, sprite_path=None, start_room=None):
        # Position and movement
        self.x = x
        self.y = y
        self.speed = 5
        self.jump_strength = 12
        self.gravity = 0.6
        self.vel_y = 0

        # Visual representation
        self.size = 40
        self.color = (0, 200, 0)  # Default green rectangle
        self.sprite = None
        if sprite_path:
            try:
                self.sprite = pygame.image.load(sprite_path).convert_alpha()
                self.sprite = pygame.transform.scale(self.sprite, (self.size, self.size))
            except Exception as e:
                print(f"Failed to load sprite: {e}")

        # Rect for collisions
        self.rect = pygame.Rect(self.x, self.y, self.size, self.size)

        # Room reference
        self.current_room = start_room

        # Stats
        self.health = 100
        self.inventory = []

        # State flags
        self.on_ground = False

    # --- Input Handling ---
    def handle_input(self, event):
        """Process keyboard input for movement and jumping."""
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_LEFT:
                self.rect.x -= self.speed
            elif event.key == pygame.K_RIGHT:
                self.rect.x += self.speed
            elif event.key == pygame.K_SPACE and self.on_ground:
                # Jump only if on ground
                self.vel_y = -self.jump_strength

    # --- Update Logic ---
    def update(self):
        """Update player state each frame (gravity, movement)."""
        # Apply gravity
        self.vel_y += self.gravity
        self.rect.y += self.vel_y

        # Clamp position to screen bounds (example: 800x600 window)
        self.rect.x = max(0, min(self.rect.x, 800 - self.size))
        self.rect.y = min(self.rect.y, 600 - self.size)  # Prevent falling below screen

        # Sync x,y for convenience
        self.x, self.y = self.rect.x, self.rect.y

    # --- Rendering ---
    def render(self, screen):
        """Draw the player sprite or fallback rectangle."""
        if self.sprite:
            screen.blit(self.sprite, self.rect)
        else:
            pygame.draw.rect(screen, self.color, self.rect)

    # --- Inventory ---
    def add_item(self, item):
        """Add an item to inventory."""
        self.inventory.append(item)

    def remove_item(self, item):
        """Remove an item from inventory if present."""
        if item in self.inventory:
            self.inventory.remove(item)

    # --- Combat / Health ---
    def take_damage(self, amount):
        self.health -= amount
        print(f"Player took {amount} damage. Health: {self.health}")

    # --- Utility ---
    def stop_movement(self):
        """Stop vertical movement (used when colliding with ground)."""
        self.vel_y = 0

    @property
    def position(self):
        """Return the player's current (x, y) position as a tuple."""
        return (self.rect.x, self.rect.y)
