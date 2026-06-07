# ch1_lvl3_puz.py
import pygame
import sys
import os

# --- Layout Configuration ---
BASE_WIDTH, BASE_HEIGHT = 1920, 1080
MANU_TEXT_FILE = "Assets/Objects-Items/manu_text.png"
CUSTOM_FONT_PATH = "Assets/Font/VCR_OSD_MONO_1.001.ttf"
BACK_BUTTON_Y = 230  # Adjust this value to change the vertical position of the back button

pygame.init()
pygame.font.init()

# Setup display configurations locally
info = pygame.display.Info()
native_width, native_height = info.current_w, info.current_h
screen = pygame.display.set_mode((native_width, native_height - 50), pygame.RESIZABLE)
game_surface = pygame.Surface((BASE_WIDTH, BASE_HEIGHT))


def run_puzzle(player, ui_layer):
    clock = pygame.time.Clock()

    # Load custom text layout fonts
    if os.path.exists(CUSTOM_FONT_PATH):
        puzzle_font = pygame.font.Font(CUSTOM_FONT_PATH, 55)
        label_font = pygame.font.Font(CUSTOM_FONT_PATH, 40)
    else:
        puzzle_font = pygame.font.SysFont("mono", 55, bold=True)
        label_font = pygame.font.SysFont("arial", 40, bold=True)

    # Persistent State Initialization on Player Object
    if not hasattr(player, 'book1_solved'):
        player.book1_solved = False
    if not hasattr(player, 'book2_solved'):
        player.book2_solved = False
    if not hasattr(player, 'row1_input_saved'):
        player.row1_input_saved = []
    if not hasattr(player, 'row2_input_saved'):
        player.row2_input_saved = []

    # Restore saved inputs
    row1_input = list(player.row1_input_saved)
    row2_input = list(player.row2_input_saved)
    active_row = 0  # 0 for Row 1, 1 for Row 2

    # Target solutions
    ans_row1 = "TRAITORS"
    ans_row2 = "DEMONIC"

    # Box layout math metrics
    box_size = 75
    spacing = 20

    # Calculate center boundaries for columns/rows
    row1_total_w = (len(ans_row1) * box_size) + ((len(ans_row1) - 1) * spacing)
    row2_total_w = (len(ans_row2) * box_size) + ((len(ans_row2) - 1) * spacing)

    start_x1 = (BASE_WIDTH - row1_total_w) // 2 + 100
    start_x2 = (BASE_WIDTH - row2_total_w) // 2 + 100

    row1_y = 420
    row2_y = 620

    solved = player.book1_solved and player.book2_solved
    solved_timer = 0

    # Load manuscript background template layout
    bg_texture = None
    if os.path.exists(MANU_TEXT_FILE):
        bg_texture = pygame.image.load(MANU_TEXT_FILE).convert_alpha()
        bg_texture = pygame.transform.scale(bg_texture, (BASE_WIDTH, BASE_HEIGHT))

    while True:
        # Scale handling variables
        window_width, window_height = screen.get_size()
        scale = min(window_width / BASE_WIDTH, window_height / BASE_HEIGHT)
        offset_x = (window_width - int(BASE_WIDTH * scale)) // 2
        offset_y = (window_height - int(BASE_HEIGHT * scale)) // 2

        raw_mouse = pygame.mouse.get_pos()
        adj_mouse_x = (raw_mouse[0] - offset_x) / scale
        adj_mouse_y = (raw_mouse[1] - offset_y) / scale

        # Event handling layer
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    # Save progress before escaping
                    player.row1_input_saved = list(row1_input)
                    player.row2_input_saved = list(row2_input)
                    return

                # Toggle selection between fields via Arrow Keys or TAB
                if event.key in [pygame.K_TAB, pygame.K_DOWN, pygame.K_UP]:
                    active_row = 1 if active_row == 0 else 0

                elif event.key == pygame.K_BACKSPACE:
                    if active_row == 0 and len(row1_input) > 0 and not player.book1_solved:
                        row1_input.pop()
                    elif active_row == 1 and len(row2_input) > 0 and not player.book2_solved:
                        row2_input.pop()

                # Text input processor with automatic forced capitalization conversion
                elif event.unicode and event.unicode.isalpha():
                    char_upper = event.unicode.upper()
                    if active_row == 0 and len(row1_input) < len(ans_row1) and not player.book1_solved:
                        row1_input.append(char_upper)
                    elif active_row == 1 and len(row2_input) < len(ans_row2) and not player.book2_solved:
                        row2_input.append(char_upper)

            # Click selection for typing grids
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                # Row 1 alignment bounds check
                if row1_y <= adj_mouse_y <= row1_y + box_size:
                    active_row = 0
                # Row 2 alignment bounds check
                elif row2_y <= adj_mouse_y <= row2_y + box_size:
                    active_row = 1

                # Back button boundaries check
                if 40 <= adj_mouse_x <= 180 and BACK_BUTTON_Y <= adj_mouse_y <= BACK_BUTTON_Y + 55:
                    # Save progress before returning
                    player.row1_input_saved = list(row1_input)
                    player.row2_input_saved = list(row2_input)
                    return

        # Verification check
        current_r1 = "".join(row1_input)
        current_r2 = "".join(row2_input)

        # Handle Book 1 Solving State independently
        if len(row1_input) == len(ans_row1) and not player.book1_solved:
            if current_r1 == ans_row1:
                player.book1_solved = True
                player.manuscripts_found += 1
            else:
                # ✅ Clear slots and drain insanity cleanly without interrupting the loop
                if hasattr(ui_layer, 'click_insanity_loss'):
                    ui_layer.click_insanity_loss()
                elif hasattr(ui_layer, 'insanity_level'):
                    ui_layer.insanity_level = max(0, ui_layer.insanity_level - 5)
                row1_input.clear()

        # Handle Book 2 Solving State independently
        if len(row2_input) == len(ans_row2) and not player.book2_solved:
            if current_r2 == ans_row2:
                player.book2_solved = True
                player.manuscripts_found += 1
            else:
                # ✅ Clear slots and drain insanity cleanly without interrupting the loop
                if hasattr(ui_layer, 'click_insanity_loss'):
                    ui_layer.click_insanity_loss()
                elif hasattr(ui_layer, 'insanity_level'):
                    ui_layer.insanity_level = max(0, ui_layer.insanity_level - 5)
                row2_input.clear()

        # Check for universal puzzle solution
        if player.book1_solved and player.book2_solved:
            if not solved:
                solved = True
                player.puzzle_solved = True
                solved_timer = pygame.time.get_ticks()

        # Sync live changes to persistent state memory
        player.row1_input_saved = list(row1_input)
        player.row2_input_saved = list(row2_input)

        # Visual Rendering Scene Layer
        game_surface.fill((30, 25, 25))
        if bg_texture:
            game_surface.blit(bg_texture, (0, 0))
        else:
            # Simple dark tint container backup overlay
            pygame.draw.rect(game_surface, (50, 45, 40), (200, 150, BASE_WIDTH - 400, BASE_HEIGHT - 300))

        # Render explicit UI escape back button node
        pygame.draw.rect(game_surface, (120, 30, 30), (40, BACK_BUTTON_Y, 140, 55), border_radius=5)
        back_txt = label_font.render("BACK", True, (255, 255, 255))
        game_surface.blit(back_txt, (55, BACK_BUTTON_Y + 8))

        # Render Input Labels
        lbl_color1 = (240, 200, 80) if active_row == 0 else (160, 140, 100)
        lbl_color2 = (240, 200, 80) if active_row == 1 else (160, 140, 100)

        label_r1 = label_font.render("BOOK 1:", True, lbl_color1)
        label_r2 = label_font.render("BOOK 2:", True, lbl_color2)
        game_surface.blit(label_r1, (start_x1 - 180, row1_y + 15))
        game_surface.blit(label_r2, (start_x2 - 180, row2_y + 15))

        # Render Row 1 Input Fields (TRAITORS)
        for i in range(len(ans_row1)):
            bx = start_x1 + i * (box_size + spacing)
            box_rect = pygame.Rect(bx, row1_y, box_size, box_size)
            border_w = 4 if (active_row == 0 and len(row1_input) == i) else 2
            border_color = (0, 255, 0) if player.book1_solved else ((255, 215, 0) if active_row == 0 else (100, 100, 100))

            pygame.draw.rect(game_surface, (20, 20, 20), box_rect)
            pygame.draw.rect(game_surface, border_color, box_rect, border_w)

            if i < len(row1_input):
                text_color = (0, 255, 0) if player.book1_solved else (238, 130, 238)
                char_surf = puzzle_font.render(row1_input[i], True, text_color)
                game_surface.blit(char_surf, char_surf.get_rect(center=box_rect.center))

        # Render Row 2 Input Fields (DEMONIC)
        for i in range(len(ans_row2)):
            bx = start_x2 + i * (box_size + spacing)
            box_rect = pygame.Rect(bx, row2_y, box_size, box_size)
            border_w = 4 if (active_row == 1 and len(row2_input) == i) else 2
            border_color = (0, 255, 0) if player.book2_solved else ((255, 215, 0) if active_row == 1 else (100, 100, 100))

            pygame.draw.rect(game_surface, (20, 20, 20), box_rect)
            pygame.draw.rect(game_surface, border_color, box_rect, border_w)

            if i < len(row2_input):
                text_color = (0, 255, 0) if player.book2_solved else (255, 50, 50)
                char_surf = puzzle_font.render(row2_input[i], True, text_color)
                game_surface.blit(char_surf, char_surf.get_rect(center=box_rect.center))

        # Display Success Feedback Metrics
        if solved:
            success_txt = label_font.render("MANUSCRIPTS DECIPHERED COMPLETED!", True, (0, 255, 0))
            game_surface.blit(success_txt, (BASE_WIDTH // 2 - success_txt.get_width() // 2, 780))
            if pygame.time.get_ticks() - solved_timer > 1500:
                return

        # Overlay UILayer behaviors
        old_surface = ui_layer.surface
        ui_layer.surface = game_surface
        ui_layer.draw(player)
        ui_layer.surface = old_surface

        # Adaptive Blit Transformations
        scaled_surf = pygame.transform.smoothscale(game_surface, (int(BASE_WIDTH * scale), int(BASE_HEIGHT * scale)))
        screen.fill((0, 0, 0))
        screen.blit(scaled_surf, (offset_x, offset_y))

        pygame.display.flip()
        clock.tick(60)