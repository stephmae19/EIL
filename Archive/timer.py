import pygame
import sys
import os
import time

pygame.init()

# Screen setup
screen = pygame.display.set_mode((800, 600))
pygame.display.set_caption("Countdown Timer")

# Load timer bar image (no scaling/stretching)
asset_path = os.path.join(os.path.dirname(__file__), "../Assets/Health-Sanity Bar-Timer/timer_bar.png")
timer_bar = pygame.image.load(asset_path).convert_alpha()
bar_rect = timer_bar.get_rect(center=(screen.get_width() // 2, screen.get_height() // 2))

# Load custom font
font_path = os.path.join("../Assets", "Font", "VCR_OSD_MONO_1.001.ttf")
ui_font = pygame.font.Font(font_path, 36)

# Timer settings
countdown_seconds = 30
start_time = time.time()

clock = pygame.time.Clock()
running = True

while running:
    screen.fill((20, 20, 20))

    # Remaining time
    elapsed = time.time() - start_time
    remaining = max(0, countdown_seconds - int(elapsed))

    # Draw timer bar (original size, no stretch)
    screen.blit(timer_bar, bar_rect)

    # Draw countdown text inside the bar, shifted right
    timer_text = ui_font.render(f"{remaining}s", True, (255, 255, 255))
    text_rect = timer_text.get_rect(center=bar_rect.center)

    # Move text slightly to the right (e.g., +40 pixels)
    text_rect.x += 17

    screen.blit(timer_text, text_rect)

    # Events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()
