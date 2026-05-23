import pygame, os, shutil

MAPS_PATH = "../assets/maps"
PUBLISHED_PATH = "../published"

def delete_map(editor, filename):
    try:
        os.remove(os.path.join(MAPS_PATH, filename))
        print(f"Deleted map {filename}")
    except FileNotFoundError:
        print("Map file not found.")

def publish_map(editor):
    os.makedirs(PUBLISHED_PATH, exist_ok=True)
    filename = f"chapter{editor.chapter}_level{editor.level}.json"
    src = os.path.join(MAPS_PATH, filename)
    dst = os.path.join(PUBLISHED_PATH, filename)
    if os.path.exists(src):
        shutil.copy(src, dst)
        print(f"Published map: {filename}")
    else:
        print("Map not found to publish.")

def open_delete_window(editor):
    delete_screen = pygame.display.set_mode((400, 300))
    pygame.display.set_caption("Delete Map")
    maps = [f for f in os.listdir(MAPS_PATH) if f.endswith(".json")]
    font = pygame.font.SysFont(None, 24)

    running = True
    while running:
        delete_screen.fill((60, 60, 60))
        for i, m in enumerate(maps):
            rect = pygame.Rect(50, 50 + i*40, 300, 30)
            pygame.draw.rect(delete_screen, (200, 100, 100), rect)
            text = font.render(m, True, (255, 255, 255))
            delete_screen.blit(text, (60, 55 + i*40))
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                for i, m in enumerate(maps):
                    rect = pygame.Rect(50, 50 + i*40, 300, 30)
                    if rect.collidepoint(event.pos):
                        delete_map(editor, m)
                        running = False
        pygame.display.flip()

    editor.screen = pygame.display.set_mode((800, 600))
    pygame.display.set_caption("Tile Level Editor")
