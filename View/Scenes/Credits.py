# credits.py
import pygame
import sys
import os

# --- Credits Data ---
CREDITS = [
    ("Antonio", "Team Leader / Project Owner"),
    ("Bulos", "Artist / Animator"),
    ("Jurado", "Developer"),
    ("Movillon", "Developer"),
    ("Reyes", "Developer"),
    ("Ventura", "Artist / Animator"),
]

pygame.init()
pygame.font.init()

# --- Config ---
BASE_WIDTH, BASE_HEIGHT = 1280, 720
FADE_IN_ZONE = 250       # pixels from bottom where fade-in starts
TITLE_Y = 60             # y-position of the "Credits" header
TITLE_PADDING = 400      # reserved space above the title
FADE_OUT_LIMIT = TITLE_Y + TITLE_PADDING  # fade-out cutoff


screen = pygame.display.set_mode((BASE_WIDTH, BASE_HEIGHT), pygame.RESIZABLE)
pygame.display.set_caption("Credits")

# --- Custom Font Path ---
font_path = os.path.join(os.path.dirname(__file__), "..", "..", "Assets", "Font", "VCR_OSD_MONO_1.001.ttf")

# Fonts
title_font = pygame.font.Font(font_path, 48)
credit_font = pygame.font.Font(font_path, 36)

clock = pygame.time.Clock()

def run_credits():
    # Pre-render all credit surfaces
    credit_surfaces = []
    for name, role in CREDITS:
        text = f"{name} - {role}"
        surf = credit_font.render(text, True, (255, 255, 255))
        credit_surfaces.append(surf)

    # Starting Y position (below screen)
    start_y = BASE_HEIGHT + 100
    spacing = 100
    scroll_speed = 1.5

    # Build positions
    positions = []
    for i, surf in enumerate(credit_surfaces):
        rect = surf.get_rect(center=(BASE_WIDTH // 2, start_y + i * spacing))
        positions.append(rect)

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN and event.key in (pygame.K_ESCAPE, pygame.K_RETURN):
                return

        screen.fill((0, 0, 0))

        # Title stays fixed at top
        title_surface = title_font.render("Credits", True, (255, 215, 0))
        title_rect = title_surface.get_rect(center=(screen.get_width() // 2, TITLE_Y))
        screen.blit(title_surface, title_rect)

        # Scroll credits upward
        for i, surf in enumerate(credit_surfaces):
            rect = positions[i]
            rect.y -= scroll_speed

            # Fade in/out based on position
            alpha = 255
            # Fade in when entering from bottom
            if rect.top > BASE_HEIGHT - FADE_IN_ZONE:
                distance = BASE_HEIGHT - rect.top
                alpha = max(0, min(255, (distance / FADE_IN_ZONE) * 255))

            elif rect.top < FADE_OUT_LIMIT:
                distance = rect.top
                alpha = max(0, min(255, (distance / FADE_OUT_LIMIT) * 255))

            fade_surface = surf.copy()
            fade_surface.set_alpha(alpha)

            # Center horizontally
            fade_rect = fade_surface.get_rect(center=(screen.get_width() // 2, rect.centery))
            screen.blit(fade_surface, fade_rect)

        pygame.display.flip()
        clock.tick(60)

# ✅ Allow standalone execution
if __name__ == "__main__":
    run_credits()
