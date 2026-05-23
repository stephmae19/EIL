import pygame
from .save_load import save_map, open_load_window
from .delete_publish import delete_map, publish_map, open_delete_window
from .upload import handle_upload_click
from .layer_manager import open_layer_window

WINDOW_WIDTH, WINDOW_HEIGHT = 800, 600
GRID_SIZE = 32
PALETTE_WIDTH = 200
CONTROL_PANEL_HEIGHT = 100
LAYERS = ["background", "walkable", "objects", "decor"]

COLUMNS = 5
PADDING = 5

class TileEditor:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption("Tile Level Editor")

        # Placeholder tiles
        self.tiles = {
            "red": self.make_tile((200, 50, 50)),
            "green": self.make_tile((50, 200, 50)),
            "blue": self.make_tile((50, 50, 200))
        }
        self.tile_names = list(self.tiles.keys())
        self.current_tile = None
        self.current_layer = LAYERS[0]

        # Dynamic grid dimensions
        self.grid_width = (WINDOW_WIDTH - PALETTE_WIDTH) // GRID_SIZE
        self.grid_height = (WINDOW_HEIGHT - CONTROL_PANEL_HEIGHT) // GRID_SIZE
        self.grid = {layer: {} for layer in LAYERS}

        # Scroll offsets
        self.scroll_offset = 0
        self.scroll_x = 0
        self.scroll_y = 0

        # Scrollbar dragging state
        self.dragging_hbar = False
        self.dragging_vbar = False
        self.hbar_rect = None
        self.vbar_rect = None
        self.drag_offset_x = 0
        self.drag_offset_y = 0

        self.clock = pygame.time.Clock()
        self.chapter = 1
        self.level = 1
        self.buttons = self.create_buttons()

        # Side selection flags
        self.column_side = "right"
        self.row_side = "bottom"

    def make_tile(self, color):
        surf = pygame.Surface((GRID_SIZE, GRID_SIZE))
        surf.fill(color)
        return surf

    def create_buttons(self):
        btns = {}
        font = pygame.font.SysFont(None, 24)
        labels = ["Save", "Load", "Delete", "Publish", "Upload",
                  "Layer", "+Width", "-Width", "+Height", "-Height",
                  "ColLeft", "ColRight", "RowTop", "RowBottom"]

        # Arrange buttons in 2 rows of 5
        for i, label in enumerate(labels):
            row = i // 5
            col = i % 5
            rect = pygame.Rect(
                20 + col * 95,
                WINDOW_HEIGHT - CONTROL_PANEL_HEIGHT + 20 + row * 50,
                90, 40
            )
            btns[label] = {"rect": rect, "label": label, "font": font}
        return btns

    def run(self):
        running = True
        while running:
            self.clock.tick(60)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

                elif event.type == pygame.KEYDOWN:
                    # Grid scrolling
                    if event.key == pygame.K_LEFT:
                        self.scroll_x = max(0, self.scroll_x - GRID_SIZE)
                    elif event.key == pygame.K_RIGHT:
                        max_scroll_x = max(0, self.grid_width * GRID_SIZE - (WINDOW_WIDTH - PALETTE_WIDTH))
                        self.scroll_x = min(max_scroll_x, self.scroll_x + GRID_SIZE)
                    elif event.key == pygame.K_UP:
                        self.scroll_y = max(0, self.scroll_y - GRID_SIZE)
                    elif event.key == pygame.K_DOWN:
                        max_scroll_y = max(0, self.grid_height * GRID_SIZE - (WINDOW_HEIGHT - CONTROL_PANEL_HEIGHT))
                        self.scroll_y = min(max_scroll_y, self.scroll_y + GRID_SIZE)

                    # 🔧 Grid Side Toggles (unique keys)
                    elif event.key == pygame.K_a:  # Column side left
                        self.column_side = "left"
                    elif event.key == pygame.K_z:  # Column side right
                        self.column_side = "right"
                    elif event.key == pygame.K_q:  # Row side top
                        self.row_side = "top"
                    elif event.key == pygame.K_w:  # Row side bottom
                        self.row_side = "bottom"

                    # 🎮 Editor Controls (unique keys)
                    elif event.key == pygame.K_s:  # Save
                        save_map(self)
                    elif event.key == pygame.K_l:  # Load
                        open_load_window(self)
                    elif event.key == pygame.K_x:  # Delete (changed from D to X)
                        open_delete_window(self)
                    elif event.key == pygame.K_p:  # Publish
                        publish_map(self)
                    elif event.key == pygame.K_u:  # Upload
                        handle_upload_click(self)
                    elif event.key == pygame.K_TAB:  # Switch layer
                        current_index = LAYERS.index(self.current_layer)
                        self.current_layer = LAYERS[(current_index + 1) % len(LAYERS)]
                    elif event.key == pygame.K_PAGEUP:  # Scroll palette up
                        self.scroll_offset = max(0, self.scroll_offset - GRID_SIZE)
                    elif event.key == pygame.K_PAGEDOWN:  # Scroll palette down
                        self.scroll_offset += GRID_SIZE

                    #Palette Function
                    elif event.key == pygame.K_PAGEUP:  # Scroll palette up
                        self.scroll_offset = max(0, self.scroll_offset - GRID_SIZE)
                    elif event.key == pygame.K_PAGEDOWN:  # Scroll palette down
                        rows = (len(self.tile_names) + COLUMNS - 1) // COLUMNS
                        total_height = rows * GRID_SIZE
                        visible_height = WINDOW_HEIGHT - CONTROL_PANEL_HEIGHT
                        max_offset = max(0, total_height - visible_height)
                        self.scroll_offset = min(max_offset, self.scroll_offset + GRID_SIZE)

                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:  # left click
                        if self.hbar_rect and self.hbar_rect.collidepoint(event.pos):
                            self.dragging_hbar = True
                            self.drag_offset_x = event.pos[0] - self.hbar_rect.x
                        elif self.vbar_rect and self.vbar_rect.collidepoint(event.pos):
                            self.dragging_vbar = True
                            self.drag_offset_y = event.pos[1] - self.vbar_rect.y
                        else:
                            self.handle_button_click(event.pos)
                            if event.pos[1] < WINDOW_HEIGHT - CONTROL_PANEL_HEIGHT:
                                if event.pos[0] > WINDOW_WIDTH - PALETTE_WIDTH:
                                    self.select_tile(event.pos)
                                else:
                                    self.place_tile(event.pos)

                    elif event.button == 3:  # right click
                        if event.pos[1] < WINDOW_HEIGHT - CONTROL_PANEL_HEIGHT:
                            if event.pos[0] > WINDOW_WIDTH - PALETTE_WIDTH:
                                self.delete_tile(event.pos)
                            else:
                                self.erase_tile(event.pos)

                elif event.type == pygame.MOUSEBUTTONUP:
                    if event.button == 1:
                        self.dragging_hbar = False
                        self.dragging_vbar = False

                elif event.type == pygame.MOUSEMOTION:
                    if self.dragging_hbar and self.hbar_rect:
                        new_x = event.pos[0] - self.drag_offset_x
                        max_x = (WINDOW_WIDTH - PALETTE_WIDTH) - self.hbar_rect.width
                        self.hbar_rect.x = max(0, min(new_x, max_x))
                        if max_x > 0:
                            self.scroll_x = int((self.hbar_rect.x / max_x) *
                                                (self.grid_width * GRID_SIZE - (WINDOW_WIDTH - PALETTE_WIDTH)))

                    if self.dragging_vbar and self.vbar_rect:
                        new_y = event.pos[1] - self.drag_offset_y
                        max_y = (WINDOW_HEIGHT - CONTROL_PANEL_HEIGHT) - self.vbar_rect.height
                        self.vbar_rect.y = max(0, min(new_y, max_y))
                        if max_y > 0:
                            self.scroll_y = int((self.vbar_rect.y / max_y) *
                                                (self.grid_height * GRID_SIZE - (WINDOW_HEIGHT - CONTROL_PANEL_HEIGHT)))

                    # Palette scrollbar dragging
                    if event.buttons[0]:  # left mouse held
                        if WINDOW_WIDTH - 15 <= event.pos[0] <= WINDOW_WIDTH - 5:  # scrollbar area
                            visible_height = WINDOW_HEIGHT - CONTROL_PANEL_HEIGHT
                            rows = (len(self.tile_names) + COLUMNS - 1) // COLUMNS
                            total_height = rows * GRID_SIZE
                            visible_height = WINDOW_HEIGHT - CONTROL_PANEL_HEIGHT
                            if total_height > visible_height:
                                bar_height = int(visible_height * (visible_height / total_height))
                                max_y = visible_height - bar_height
                                bar_y = int((self.scroll_offset / (total_height - visible_height)) * max_y)
                                pygame.draw.rect(self.screen, (180, 180, 180),
                                                 (WINDOW_WIDTH - 15, bar_y, 10, bar_height))

            self.draw()
        pygame.quit()

    def handle_button_click(self, pos):
        for label, btn in self.buttons.items():
            if btn["rect"].collidepoint(pos):
                if label == "Save":
                    save_map(self)
                elif label == "Load":
                    open_load_window(self)
                elif label == "Delete":
                    open_delete_window(self)
                elif label == "Publish":
                    publish_map(self)
                elif label == "Upload":
                    handle_upload_click(self)
                elif label == "Layer":
                    open_layer_window(self)
                elif label == "+Width":
                    self.grid_width += 1
                    if self.column_side == "left":
                        for layer in LAYERS:
                            self.grid[layer] = {(x+1, y): t for (x, y), t in self.grid[layer].items()}
                elif label == "-Width":
                    if self.grid_width > 5:
                        if self.column_side == "left":
                            for layer in LAYERS:
                                self.grid[layer] = {(x-1, y): t for (x, y), t in self.grid[layer].items() if x > 0}
                        else:
                            for layer in LAYERS:
                                self.grid[layer] = {(x, y): t for (x, y), t in self.grid[layer].items() if x < self.grid_width-1}
                        self.grid_width -= 1
                elif label == "+Height":
                    self.grid_height += 1
                    if self.row_side == "top":
                        for layer in LAYERS:
                            self.grid[layer] = {(x, y+1): t for (x, y), t in self.grid[layer].items()}
                elif label == "-Height":
                    if self.grid_height > 5:
                        if self.row_side == "top":
                            for layer in LAYERS:
                                self.grid[layer] = {(x, y-1): t for (x, y), t in self.grid[layer].items() if y > 0}
                        else:
                            for layer in LAYERS:
                                self.grid[layer] = {(x, y): t for (x, y), t in self.grid[layer].items() if y < self.grid_height-1}
                        self.grid_height -= 1
                elif label == "ColLeft":
                    self.column_side = "left"
                elif label == "ColRight":
                    self.column_side = "right"
                elif label == "RowTop":
                    self.row_side = "top"
                elif label == "RowBottom":
                    self.row_side = "bottom"

    def place_tile(self, pos):
        if not self.current_tile:
            return
        x = (pos[0] + self.scroll_x) // GRID_SIZE
        y = (pos[1] + self.scroll_y) // GRID_SIZE
        if x < self.grid_width and y < self.grid_height:
            self.grid[self.current_layer][(x, y)] = self.current_tile

    def erase_tile(self, pos):
        x = (pos[0] + self.scroll_x) // GRID_SIZE
        y = (pos[1] + self.scroll_y) // GRID_SIZE
        if (x, y) in self.grid[self.current_layer]:
            del self.grid[self.current_layer][(x, y)]

    def select_tile(self, pos):
        palette_x = pos[0] - (WINDOW_WIDTH - PALETTE_WIDTH + 10)
        palette_y = pos[1] + self.scroll_offset
        col = palette_x // (GRID_SIZE + PADDING)
        row = palette_y // GRID_SIZE
        index = row * COLUMNS + col
        if 0 <= index < len(self.tile_names):
            self.current_tile = self.tile_names[index]

    def delete_tile(self, pos):
        palette_x = pos[0] - (WINDOW_WIDTH - PALETTE_WIDTH + 10)
        palette_y = pos[1] + self.scroll_offset
        col = palette_x // (GRID_SIZE + PADDING)
        row = palette_y // GRID_SIZE
        index = row * COLUMNS + col
        if 0 <= index < len(self.tile_names):
            tile_name = self.tile_names[index]
            del self.tiles[tile_name]
            self.tile_names.remove(tile_name)

    def draw(self):
        self.screen.fill((50, 50, 50))

        # Grid lines
        for x in range(self.grid_width * GRID_SIZE):
            pygame.draw.line(self.screen, (80, 80, 80),
                             (x - self.scroll_x, 0),
                             (x - self.scroll_x, self.grid_height * GRID_SIZE - self.scroll_y))
        for y in range(self.grid_height * GRID_SIZE):
            pygame.draw.line(self.screen, (80, 80, 80),
                             (0, y - self.scroll_y),
                             (self.grid_width * GRID_SIZE - self.scroll_x, y - self.scroll_y))

        # Tiles placed
        for layer in LAYERS:
            for (x, y), tile_name in self.grid[layer].items():
                if tile_name in self.tiles and x < self.grid_width and y < self.grid_height:
                    self.screen.blit(self.tiles[tile_name],
                                     (x * GRID_SIZE - self.scroll_x, y * GRID_SIZE - self.scroll_y))

        # Palette background
        pygame.draw.rect(self.screen, (30, 30, 30),
                         (WINDOW_WIDTH - PALETTE_WIDTH, 0, PALETTE_WIDTH, WINDOW_HEIGHT - CONTROL_PANEL_HEIGHT))

        # Palette tiles
        for i, name in enumerate(self.tile_names):
            row = i // COLUMNS
            col = i % COLUMNS
            x = WINDOW_WIDTH - PALETTE_WIDTH + 10 + col * (GRID_SIZE + PADDING)
            y = row * GRID_SIZE - self.scroll_offset
            if 0 <= y < WINDOW_HEIGHT - CONTROL_PANEL_HEIGHT:
                self.screen.blit(self.tiles[name], (x, y))
                if name == self.current_tile:
                    pygame.draw.rect(self.screen, (255, 255, 0),
                                     (x, y, GRID_SIZE, GRID_SIZE), 2)

        # Palette scrollbar
        rows = (len(self.tile_names) + COLUMNS - 1) // COLUMNS
        total_height = rows * GRID_SIZE
        visible_height = WINDOW_HEIGHT - CONTROL_PANEL_HEIGHT
        if total_height > visible_height:
            bar_height = int(visible_height * (visible_height / total_height))
            bar_y = int((self.scroll_offset / max(1, total_height)) * visible_height)
            pygame.draw.rect(self.screen, (180, 180, 180),
                             (WINDOW_WIDTH - 15, bar_y, 10, bar_height))

        # Horizontal scrollbar for grid
        if self.grid_width * GRID_SIZE > (WINDOW_WIDTH - PALETTE_WIDTH):
            bar_width = int((WINDOW_WIDTH - PALETTE_WIDTH) *
                            ((WINDOW_WIDTH - PALETTE_WIDTH) / (self.grid_width * GRID_SIZE)))
            max_x = (WINDOW_WIDTH - PALETTE_WIDTH) - bar_width
            bar_x = int((self.scroll_x / max(1, self.grid_width * GRID_SIZE - (WINDOW_WIDTH - PALETTE_WIDTH))) * max_x)
            self.hbar_rect = pygame.Rect(bar_x, WINDOW_HEIGHT - CONTROL_PANEL_HEIGHT - 15, bar_width, 10)
            color = (200, 200, 250) if self.dragging_hbar else (180, 180, 180)
            pygame.draw.rect(self.screen, color, self.hbar_rect)
        else:
            self.hbar_rect = None

        # Vertical scrollbar for grid
        if self.grid_height * GRID_SIZE > (WINDOW_HEIGHT - CONTROL_PANEL_HEIGHT):
            bar_height = int((WINDOW_HEIGHT - CONTROL_PANEL_HEIGHT) *
                             ((WINDOW_HEIGHT - CONTROL_PANEL_HEIGHT) / (self.grid_height * GRID_SIZE)))
            max_y = (WINDOW_HEIGHT - CONTROL_PANEL_HEIGHT) - bar_height
            bar_y = int((self.scroll_y / max(1, self.grid_height * GRID_SIZE - (WINDOW_HEIGHT - CONTROL_PANEL_HEIGHT))) * max_y)
            self.vbar_rect = pygame.Rect(WINDOW_WIDTH - PALETTE_WIDTH - 15, bar_y, 10, bar_height)
            color = (200, 200, 250) if self.dragging_vbar else (180, 180, 180)
            pygame.draw.rect(self.screen, color, self.vbar_rect)
        else:
            self.vbar_rect = None

        # Control panel
        pygame.draw.rect(self.screen, (40, 40, 40),
                         (0, WINDOW_HEIGHT - CONTROL_PANEL_HEIGHT, WINDOW_WIDTH, CONTROL_PANEL_HEIGHT))
        for btn in self.buttons.values():
            pygame.draw.rect(self.screen, (100, 100, 200), btn["rect"])
            text = btn["font"].render(btn["label"], True, (255, 255, 255))
            text_rect = text.get_rect(center=btn["rect"].center)
            self.screen.blit(text, text_rect)

        # Grid size and mode indicator
        font = pygame.font.SysFont(None, 24)
        grid_text = font.render(f"Grid: {self.grid_width} x {self.grid_height}", True, (255, 255, 255))
        self.screen.blit(grid_text, (20, WINDOW_HEIGHT - CONTROL_PANEL_HEIGHT + 70))

        mode_text = font.render(f"Col: {self.column_side} | Row: {self.row_side}", True, (255, 255, 255))
        self.screen.blit(mode_text, (200, WINDOW_HEIGHT - CONTROL_PANEL_HEIGHT + 70))

        pygame.display.flip()
