# View/Renderer.py
import pygame

class Renderer:
    def __init__(self, screen, virtual_width=1920, virtual_height=1080):
        """
        Renderer handles all drawing operations with automatic scaling.
        :param screen: The actual pygame display surface.
        :param virtual_width: Design resolution width.
        :param virtual_height: Design resolution height.
        """
        self.screen = screen
        self.virtual_width = virtual_width
        self.virtual_height = virtual_height
        self.virtual_surface = pygame.Surface((virtual_width, virtual_height))
        self.font_cache = {}

    def clear(self, color=(0, 0, 0)):
        """Fill the virtual surface with a background color."""
        self.virtual_surface.fill(color)

    def draw_sprite(self, sprite, position):
        """Draw a sprite at a given position on the virtual surface."""
        self.virtual_surface.blit(sprite, position)

    def draw_text(self, text, position, size=32, color=(255, 255, 255), center=False):
        """Draw text on the virtual surface, scaled later to window size."""
        font = self._get_font(size)
        surface = font.render(text, True, color)
        rect = surface.get_rect()
        if center:
            rect.center = position
        else:
            rect.topleft = position
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
