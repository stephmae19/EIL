import pygame, os, json

MAPS_PATH = "../assets/maps"

def save_map(editor):
    data = {
        "chapter": editor.chapter,
        "level": editor.level,
        "grid_width": editor.grid_width,
        "grid_height": editor.grid_height,
        "layers": {
            layer: {f"{x},{y}": tile for (x, y), tile in tiles.items()}
            for layer, tiles in editor.grid.items()
        }
    }
    os.makedirs(MAPS_PATH, exist_ok=True)
    filename = f"chapter{editor.chapter}_level{editor.level}.json"
    with open(os.path.join(MAPS_PATH, filename), "w") as f:
        json.dump(data, f, indent=4)
    print(f"Map saved: {filename}")

def open_load_window(editor):
    load_screen = pygame.display.set_mode((400, 300))
    pygame.display.set_caption("Load Map")
    maps = [f for f in os.listdir(MAPS_PATH) if f.endswith(".json")]
    font = pygame.font.SysFont(None, 24)

    running = True
    while running:
        load_screen.fill((60, 60, 60))
        for i, m in enumerate(maps):
            rect = pygame.Rect(50, 50 + i*40, 300, 30)
            pygame.draw.rect(load_screen, (100, 100, 200), rect)
            text = font.render(m, True, (255, 255, 255))
            load_screen.blit(text, (60, 55 + i*40))
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                for i, m in enumerate(maps):
                    rect = pygame.Rect(50, 50 + i*40, 300, 30)
                    if rect.collidepoint(event.pos):
                        with open(os.path.join(MAPS_PATH, m), "r") as f:
                            data = json.load(f)
                        editor.chapter = data.get("chapter", 1)
                        editor.level = data.get("level", 1)
                        editor.grid_width = data.get("grid_width", editor.grid_width)
                        editor.grid_height = data.get("grid_height", editor.grid_height)
                        editor.grid = {layer: {} for layer in editor.grid.keys()}
                        for layer, tiles in data["layers"].items():
                            for pos, tile in tiles.items():
                                x, y = map(int, pos.split(","))
                                editor.grid[layer][(x, y)] = tile
                        running = False
        pygame.display.flip()

    # return to main editor window
    editor.screen = pygame.display.set_mode((800, 600))
    pygame.display.set_caption("Tile Level Editor")
