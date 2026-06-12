# gameover.py
import pygame
import sys
import os


def show_game_over(screen):
    """Displays the Game Over screen with interactive UI buttons.

    Returns 'restart' if the retry button is clicked, or 'menu' to exit back to
    chapter selection.
    """
    window_w, window_h = screen.get_size()
    clock = pygame.time.Clock()

    # ---------------- 1. LOAD & SCALE GRAPHICS ----------------
    # Background
    bg_path = os.path.join("Assets", "Scenery", "gameover_bg.png")
    if os.path.exists(bg_path):
        bg_image = pygame.image.load(bg_path).convert_alpha()
    else:
        bg_image = pygame.Surface((window_w, window_h))
        bg_image.fill((15, 10, 10))
        font_title = pygame.font.SysFont("arial", 80, bold=True)
        text_title = font_title.render("GAME OVER", True, (200, 20, 20))
        bg_image.blit(
            text_title, text_title.get_rect(center=(window_w // 2, window_h // 3))
        )

    bg_image = pygame.transform.smoothscale(bg_image, (window_w, window_h))

    # Menu Panel / Button Placeholder Bar
    bar_path = os.path.join("Assets", "Scenery", "gameover_bar.png")
    if os.path.exists(bar_path):
        bar_image = pygame.image.load(bar_path).convert_alpha()
        # Scale bar cleanly to roughly 35% of screen width
        bar_w = int(window_w * 0.35)
        bar_h = int(bar_image.get_height() * (bar_w / bar_image.get_width()))
        bar_image = pygame.transform.smoothscale(bar_image, (bar_w, bar_h))
    else:
        bar_image = pygame.Surface((450, 120), pygame.SRCALPHA)
        bar_image.fill((30, 30, 40, 200))  # Semi-transparent fallback

    bar_rect = bar_image.get_rect(center=(window_w // 2, int(window_h * 0.65)))

    # Buttons Setup
    retry_path = os.path.join("Assets", "Scenery", "retry_btn.png")
    exit_path = os.path.join("Assets", "Scenery", "exit_btn.png")

    # Font for button fallbacks if images aren't present
    btn_font = pygame.font.SysFont("arial", 22, bold=True)

    # Load/Create Retry Button
    if os.path.exists(retry_path):
        retry_image = pygame.image.load(retry_path).convert_alpha()
        # Scale to fit nicely inside the container bar width
        btn_w = int(bar_rect.width * 0.38)
        btn_h = int(
            retry_image.get_height() * (btn_w / retry_image.get_width())
        )
        retry_image = pygame.transform.smoothscale(retry_image, (btn_w, btn_h))
    else:
        retry_image = pygame.Surface((150, 50))
        retry_image.fill((40, 140, 40))
        txt = btn_font.render("RETRY", True, (255, 255, 255))
        retry_image.blit(txt, txt.get_rect(center=(75, 25)))

    # Load/Create Exit Button
    if os.path.exists(exit_path):
        exit_image = pygame.image.load(exit_path).convert_alpha()
        btn_w = int(bar_rect.width * 0.38)
        btn_h = int(exit_image.get_height() * (btn_w / exit_image.get_width()))
        exit_image = pygame.transform.smoothscale(exit_image, (btn_w, btn_h))
    else:
        exit_image = pygame.Surface((150, 50))
        exit_image.fill((160, 40, 40))
        txt = btn_font.render("EXIT", True, (255, 255, 255))
        exit_image.blit(txt, txt.get_rect(center=(75, 25)))

    # Align buttons side-by-side inside the placeholder bar bounds
    retry_rect = retry_image.get_rect(
        center=(bar_rect.centerx - int(bar_rect.width * 0.24), bar_rect.centery)
    )
    exit_rect = exit_image.get_rect(
        center=(bar_rect.centerx + int(bar_rect.width * 0.24), bar_rect.centery)
    )

    # ---------------- 2. FADE-IN TRANSITION ----------------
    alpha_surface = pygame.Surface((window_w, window_h))
    alpha_surface.fill((0, 0, 0))

    for alpha in range(255, 0, -6):
        screen.blit(bg_image, (0, 0))
        screen.blit(bar_image, bar_rect)
        screen.blit(retry_image, retry_rect)
        screen.blit(exit_image, exit_rect)

        alpha_surface.set_alpha(alpha)
        screen.blit(alpha_surface, (0, 0))

        pygame.display.flip()
        clock.tick(60)

    # ---------------- 3. INTERACTION LOOP ----------------
    while True:
        mouse_pos = pygame.mouse.get_pos()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            # Keyboard Support
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return "menu"
                if event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
                    return "restart"

            # Mouse Button Support
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if retry_rect.collidepoint(mouse_pos):
                    return "restart"
                if exit_rect.collidepoint(mouse_pos):
                    return "menu"

        # Rendering
        screen.blit(bg_image, (0, 0))
        screen.blit(bar_image, bar_rect)
        screen.blit(retry_image, retry_rect)
        screen.blit(exit_image, exit_rect)

        pygame.display.flip()
        clock.tick(60)

def handle_game_over(screen, ui_layer, player, respawn_pos=None, base_width=None, floor_y=None):
    """
    Generic game-over handler usable by any level.

    - screen: main window surface
    - ui_layer: UILayer instance
    - player: Player instance
    - respawn_pos: (x, y) or None. If None and base_width/floor_y are provided,
      uses a default midbottom respawn like Level 1.
    - base_width, floor_y: used only to compute a default respawn if respawn_pos is None.

    Returns:
        "continue" if gameplay should resume (after restart),
        "menu" if caller should exit to menu / chapter select.
    """
    action = show_game_over(screen)

    if action == "restart":
        # Reset player
        player.health = 100

        # Respawn position
        if respawn_pos is not None:
            # Treat as midbottom by default, which matches side-scroller feel
            player.rect.midbottom = respawn_pos
        elif base_width is not None and floor_y is not None:
            # Fallback similar to ch1_lvl1
            player.rect.midbottom = (int(base_width * 0.10), floor_y)

        # Reset UI state
        ui_layer.hearts = ui_layer.max_hearts
        ui_layer.insanity_level = len(ui_layer.insanity_frames) - 1
        ui_layer.reset_timer()
        ui_layer.is_game_over = False

        return "continue"

    elif action == "menu":
        return "menu"

    # Safety fallback: treat anything else as “menu”
    return "menu"
