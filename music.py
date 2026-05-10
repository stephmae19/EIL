import pygame
import sys

pygame.init()

screen = pygame.display.set_mode((600, 400))
pygame.display.set_caption("Volume Slider Example")

# Load spritesheet
spritesheet = pygame.image.load("assets/sprite/music/music_volume.png").convert_alpha()

# Frame dimensions (3x3 grid = 9 frames)
frame_width = 340
frame_height = 91
cols = 3
rows = 3
num_frames = cols * rows

# Extract frames
frames = []
for row in range(rows):
    for col in range(cols):
        rect = pygame.Rect(col * frame_width, row * frame_height, frame_width, frame_height)
        frame = spritesheet.subsurface(rect)
        frames.append(frame)

# Clickable slider area inside each frame (subtract margins)
inner_x_offset = 53
inner_y_offset = 32
slider_width = 265
slider_height = 33

# Position on screen
slider_x = 100
slider_y = 150

volume_level = 0
dragging = False

def get_slider_rect():
    """Clickable area relative to screen position."""
    return pygame.Rect(slider_x + inner_x_offset,
                       slider_y + inner_y_offset,
                       slider_width,
                       slider_height)

def draw_slider():
    """Draw current frame at screen position."""
    current_frame = frames[volume_level]
    screen.blit(current_frame, (slider_x, slider_y))

def update_volume(mouse_x):
    global volume_level
    relative_x = mouse_x - (slider_x + inner_x_offset)
    relative_x = max(0, min(relative_x, slider_width))
    # Use round instead of int to ensure rightmost maps to last frame
    volume_level = round((relative_x / slider_width) * (num_frames - 1))
    # Clamp to valid range
    volume_level = max(0, min(volume_level, num_frames - 1))

clock = pygame.time.Clock()

while True:
    screen.fill((30, 30, 30))

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        elif event.type == pygame.MOUSEBUTTONDOWN:
            if get_slider_rect().collidepoint(event.pos):
                dragging = True
                update_volume(event.pos[0])

        elif event.type == pygame.MOUSEBUTTONUP:
            dragging = False

        elif event.type == pygame.MOUSEMOTION and dragging:
            update_volume(event.pos[0])

    draw_slider()

    pygame.display.flip()
    clock.tick(60)
