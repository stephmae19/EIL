# View/Renderer.py
import pygame

class Renderer:
    def __init__(self, screen, tile_width=32, tile_height=32, view_tiles_w=35, view_tiles_h=20):
        """
        Renderer handles all drawing operations with automatic scaling and camera support.
        :param screen: The actual pygame display surface.
        :param tile_width: Width of a single tile in pixels.
        :param tile_height: Height of a single tile in pixels.
        :param view_tiles_w: Number of tiles visible horizontally.
        :param view_tiles_h: Number of tiles visible vertically.
        """
        self.screen = screen
        self.tile_width = tile_width
        self.tile_height = tile_height
        self.virtual_width = view_tiles_w * tile_width   # 35 tiles wide
        self.virtual_height = view_tiles_h * tile_height # 20 tiles tall
        self.virtual_surface = pygame.Surface((self.virtual_width, self.virtual_height))
        self.font_cache = {}

        # Camera offset for scrolling maps
        self.camera_x = 0
        self.camera_y = 0

    def clear(self, color=(0, 0, 0)):
        """Fill the virtual surface with a background color."""
        self.virtual_surface.fill(color)

    def set_camera(self, target_rect, map_width, map_height):
        """
        Center the camera on a target (usually the player).
        Keeps the camera within map bounds.
        """
        self.camera_x = target_rect.centerx - self.virtual_width // 2
        self.camera_y = target_rect.centery - self.virtual_height // 2

        # Clamp camera to map bounds
        self.camera_x = max(0, min(self.camera_x, map_width - self.virtual_width))
        self.camera_y = max(0, min(self.camera_y, map_height - self.virtual_height))

    def draw_map(self, tmx_data):
        """Draw TMX map layers in correct order: ground → wall → objects."""
        for layer in tmx_data.visible_layers:
            if hasattr(layer, "tiles"):
                for x, y, tile in layer.tiles():
                    if tile:
                        pos = (
                            x * tmx_data.tilewidth - self.camera_x,
                            y * tmx_data.tileheight - self.camera_y
                        )
                        self.virtual_surface.blit(tile, pos)

    def draw_sprite(self, sprite, rect):
        """Draw a sprite at a given rect on the virtual surface."""
        self.virtual_surface.blit(sprite, (rect.x - self.camera_x, rect.y - self.camera_y))

    def draw_rect(self, color, rect):
        """Draw a rectangle (fallback for player or objects without sprites)."""
        shifted_rect = pygame.Rect(
            rect.x - self.camera_x, rect.y - self.camera_y, rect.width, rect.height
        )
        pygame.draw.rect(self.virtual_surface, color, shifted_rect)

    def draw_text(self, text, position, size=32, color=(255, 255, 255), center=False):
        """Draw text on the virtual surface, scaled later to window size."""
        font = self._get_font(size)
        surface = font.render(text, True, color)
        rect = surface.get_rect()
        if center:
            rect.center = (position[0] - self.camera_x, position[1] - self.camera_y)
        else:
            rect.topleft = (position[0] - self.camera_x, position[1] - self.camera_y)
        self.virtual_surface.blit(surface, rect)

    def _get_font(self, size):
        """Cache fonts to avoid recreating them every frame."""
        if size not in self.font_cache:
            self.font_cache[size] = pygame.font.SysFont("arial", size)
        return self.font_cache[size]

    def draw_ui_element(self, element_surface, position):
        """Draw a UI element (like a button or HUD component)."""
        self.virtual_surface.blit(element_surface, position)

    def render_scene(self, scene):
        """Render a scene by calling its render method with this renderer."""
        scene.render(self)

    def update_display(self):
        """Scale the virtual surface to the actual window size and flip display."""
        window_width, window_height = self.screen.get_size()
        scaled_surface = pygame.transform.smoothscale(
            self.virtual_surface, (window_width, window_height)
        )
        self.screen.blit(scaled_surface, (0, 0))
        pygame.display.flip()
