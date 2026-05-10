import pygame

def open_layer_window(editor):
    layer_screen = pygame.display.set_mode((400, 300))
    pygame.display.set_caption("Layer Manager")
    font = pygame.font.SysFont(None, 24)

    dragging = None   # index of layer being dragged
    offset_y = 0
    running = True

    while running:
        layer_screen.fill((60, 60, 60))

        # Draw layers in current order
        for i, layer in enumerate(editor.grid.keys()):
            rect = pygame.Rect(50, 50 + i*40, 300, 30)
            color = (150, 150, 250) if dragging == i else (100, 100, 200)
            pygame.draw.rect(layer_screen, color, rect)
            text = font.render(layer, True, (255, 255, 255))
            layer_screen.blit(text, (60, 55 + i*40))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                # Start dragging
                for i, layer in enumerate(list(editor.grid.keys())):
                    rect = pygame.Rect(50, 50 + i*40, 300, 30)
                    if rect.collidepoint(event.pos):
                        dragging = i
                        offset_y = event.pos[1] - rect.y

            elif event.type == pygame.MOUSEBUTTONUP and event.button == 1 and dragging is not None:
                # Drop layer at new position
                drop_index = (event.pos[1] - 50) // 40
                layers = list(editor.grid.keys())
                layer_name = layers.pop(dragging)
                drop_index = max(0, min(drop_index, len(layers)))
                layers.insert(drop_index, layer_name)

                # Rebuild grid dict in new order
                editor.grid = {name: editor.grid[name] for name in layers}
                # Update global LAYERS list too
                editor.current_layer = layer_name
                running = False
                dragging = None

            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 3:
                # Right‑click to rename
                for i, layer in enumerate(list(editor.grid.keys())):
                    rect = pygame.Rect(50, 50 + i*40, 300, 30)
                    if rect.collidepoint(event.pos):
                        new_name = input(f"Rename {layer} to: ")
                        if new_name and new_name not in editor.grid:
                            editor.grid[new_name] = editor.grid.pop(layer)
                            layers = list(editor.grid.keys())
                            layers[i] = new_name
                            editor.grid = {name: editor.grid[name] for name in layers}
                            editor.current_layer = new_name
                        running = False

        pygame.display.flip()

    # Return to main editor window
    editor.screen = pygame.display.set_mode((800, 600))
    pygame.display.set_caption("Tile Level Editor")
