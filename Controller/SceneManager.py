# Controller/SceneManager.py
import pygame

class SceneManager:
    def __init__(self, surface, base_width=1920, base_height=1080):
        """
        SceneManager works with a fixed internal surface (BASE_WIDTH x BASE_HEIGHT).
        All scenes render to this surface. Input events are scaled back to match.
        """
        self.surface = surface
        self.current_scene = None
        self.base_width = base_width
        self.base_height = base_height
        self.window_size = (base_width, base_height)  # updated in main loop
        self.scale_info = {"scale": 1, "x_offset": 0, "y_offset": 0, "win_size": self.window_size}

    def set_scene(self, scene):
        self.current_scene = scene
        # propagate scale info immediately
        if hasattr(scene, "set_scale_info"):
            scene.set_scale_info(self.scale_info)

    def set_window_size(self, width, height):
        """Called from main.py when window is resized."""
        self.window_size = (width, height)

    def set_scale_info(self, scale_info):
        """Called from main.py each frame after scaling is calculated."""
        self.scale_info = scale_info
        if self.current_scene and hasattr(self.current_scene, "set_scale_info"):
            self.current_scene.set_scale_info(scale_info)

    def handle_input(self, event):
        """Scale mouse/touch events back to internal surface coordinates."""
        if not self.current_scene:
            return None

        if event.type in (pygame.MOUSEBUTTONDOWN, pygame.MOUSEBUTTONUP, pygame.MOUSEMOTION):
            win_w, win_h = self.window_size
            scale = min(win_w / self.base_width, win_h / self.base_height)
            scaled_w = int(self.base_width * scale)
            scaled_h = int(self.base_height * scale)
            x_offset = (win_w - scaled_w) // 2
            y_offset = (win_h - scaled_h) // 2

            mx, my = event.pos
            if (x_offset <= mx < x_offset + scaled_w) and (y_offset <= my < y_offset + scaled_h):
                # remap to internal surface coordinates
                adj_x = (mx - x_offset) / scale
                adj_y = (my - y_offset) / scale
                event.pos = (adj_x, adj_y)

                # ✅ update last_mouse_pos here
                self.current_scene.last_mouse_pos = event.pos
            else:
                return None  # ignore clicks outside game area

        return self.current_scene.handle_input(event)

    def update(self):
        if self.current_scene:
            self.current_scene.update()

    def render(self):
        if self.current_scene:
            self.surface.fill((0, 0, 0))
            self.current_scene.render()
