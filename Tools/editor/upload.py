import os, pygame

UPLOAD_PATH = os.path.join("assets", "uploads")

def handle_upload_click(editor):
    if not os.path.exists(UPLOAD_PATH):
        os.makedirs(UPLOAD_PATH)

    files = [f for f in os.listdir(UPLOAD_PATH) if f.lower().endswith(".png")]
    if not files:
        print("No PNG files found in uploads folder.")
        return

    preview_screen = pygame.display.set_mode((600, 500))
    pygame.display.set_caption("Upload Preview")
    font = pygame.font.SysFont(None, 24)

    selected_file = None
    slice_mode = False
    running = True

    while running:
        preview_screen.fill((60, 60, 60))
        text = font.render("Click file to preview | SPACE toggle slice | ENTER confirm", True, (255, 255, 255))
        preview_screen.blit(text, (20, 20))

        # File list
        for i, f in enumerate(files):
            rect = pygame.Rect(20, 60 + i*30, 200, 25)
            color = (150, 150, 250) if f == selected_file else (100, 100, 200)
            pygame.draw.rect(preview_screen, color, rect)
            preview_screen.blit(font.render(f, True, (255, 255, 255)), (25, 65 + i*30))

        # Preview selected image
        if selected_file:
            filepath = os.path.join(UPLOAD_PATH, selected_file)
            try:
                img = pygame.image.load(filepath).convert_alpha()
                preview_img = pygame.transform.scale(img, (300, 300))
                preview_screen.blit(preview_img, (250, 100))

                if slice_mode:
                    w, h = preview_img.get_size()
                    cols, rows = w // 32, h // 32
                    # Draw grid overlay
                    for x in range(0, w, 32):
                        pygame.draw.line(preview_screen, (255, 255, 0), (250+x, 100), (250+x, 100+h))
                    for y in range(0, h, 32):
                        pygame.draw.line(preview_screen, (255, 255, 0), (250, 100+y), (250+w, 100+y))
            except Exception as e:
                preview_screen.blit(font.render(f"Error loading {selected_file}: {e}", True, (255, 0, 0)), (250, 80))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                for i, f in enumerate(files):
                    rect = pygame.Rect(20, 60 + i*30, 200, 25)
                    if rect.collidepoint(event.pos):
                        selected_file = f
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    slice_mode = not slice_mode
                    print("Slice mode:", slice_mode)
                elif event.key == pygame.K_RETURN and selected_file:
                    filepath = os.path.join(UPLOAD_PATH, selected_file)
                    img = pygame.image.load(filepath).convert_alpha()
                    w, h = img.get_size()

                    if slice_mode and (w > 32 or h > 32):
                        cols, rows = w // 32, h // 32
                        for y in range(rows):
                            for x in range(cols):
                                rect = pygame.Rect(x*32, y*32, 32, 32)
                                tile = img.subsurface(rect).copy()
                                tile_name = f"{selected_file}_{x}_{y}"
                                if tile_name not in editor.tile_names:
                                    editor.tiles[tile_name] = tile
                                    editor.tile_names.append(tile_name)
                        print(f"Sliced {selected_file} into {cols*rows} tiles")
                    else:
                        if selected_file not in editor.tile_names:
                            editor.tiles[selected_file] = pygame.transform.scale(img, (32, 32))
                            editor.tile_names.append(selected_file)
                            print(f"Uploaded single tile: {selected_file}")
                    running = False

        pygame.display.flip()

    # Return to main editor window
    editor.screen = pygame.display.set_mode((800, 600))
    pygame.display.set_caption("Tile Level Editor")
