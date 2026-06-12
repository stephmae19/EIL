import pygame
import sys
import os


def show_game_over(screen):
    """
    Displays the Game Over screen and waits for player input.
    Returns 'restart' if the user wants to play again, or 'menu' to exit.
    """
    # Load the background image
    # Note: Using the standard path structure aligned with your other assets
    bg_path = os.path.join("Assets", "Scenery", "gameover_bg.png")

    if os.path.exists(bg_path):
        bg_image = pygame.image.load(bg_path).convert_alpha()
    else:
        # Visual fallback for the artist: simple black screen with red text
        bg_image = pygame.Surface(screen.get_size())
        bg_image.fill((10, 10, 15))
        font = pygame.font.SysFont("arial", 72, bold=True)
        text = font.render("GAME OVER", True, (200, 0, 0))
        bg_image.blit(text, text.get_rect(center=bg_image.get_rect().center))

    # Scale to seamlessly fit the current window size
    window_w, window_h = screen.get_size()
    bg_image = pygame.transform.smoothscale(bg_image, (window_w, window_h))

    clock = pygame.time.Clock()

    # Simple fade-in effect for a polished transition
    alpha_surface = pygame.Surface((window_w, window_h))
    alpha_surface.fill((0, 0, 0))

    for alpha in range(255, 0, -5):
        screen.blit(bg_image, (0, 0))
        alpha_surface.set_alpha(alpha)
        screen.blit(alpha_surface, (0, 0))
        pygame.display.flip()
        clock.tick(60)

    # Input loop
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return "menu"  # Return control to ChapterSelect
                if event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
                    return "restart"  # Signal the loop to restart

        screen.blit(bg_image, (0, 0))
        pygame.display.flip()
        clock.tick(60)