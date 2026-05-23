import pygame
import sys

pygame.init()

# Screen setup
screen = pygame.display.set_mode((1000, 600))
pygame.display.set_caption("Health Bar Click Demo")

# Load health spritesheet
health_sheet = pygame.image.load("../Assets/Sprite/Gameplay/health.png").convert_alpha()

# Each frame is 397x90
frame_width, frame_height = 397, 90
cols = health_sheet.get_width() // frame_width
rows = health_sheet.get_height() // frame_height
frame_count = cols * rows

# Slice frames
health_frames = []
for row in range(rows):
    for col in range(cols):
        rect = pygame.Rect(col * frame_width, row * frame_height, frame_width, frame_height)
        frame = health_sheet.subsurface(rect)
        health_frames.append(frame)

# Use only first 56 frames if needed
health_frames = health_frames[:56]

# State
health_level = 0

def draw_bar():
    current_frame = health_frames[health_level]
    rect = current_frame.get_rect(center=(screen.get_width() // 2, screen.get_height() // 2))
    screen.blit(current_frame, rect)

    # Label above the bar
    font = pygame.font.SysFont("Arial", 28)
    text = font.render(f"Health Level: {health_level}", True, (255, 255, 255))
    text_rect = text.get_rect(center=(rect.centerx, rect.top - 30))
    screen.blit(text, text_rect)

    return rect

clock = pygame.time.Clock()

# Main loop
running = True
while running:
    screen.fill((30, 30, 30))
    bar_rect = draw_bar()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            # Only change frame when the image itself is clicked
            if bar_rect.collidepoint(event.pos):
                health_level = (health_level + 1) % len(health_frames)

    # These should be outside the event loop, so they run every frame
    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()
