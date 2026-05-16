import pygame
import sys

pygame.init()

# Screen setup
screen = pygame.display.set_mode((1000, 600))
pygame.display.set_caption("Insanity Bar Demo")

# Load insanity spritesheet (56 frames, each 397x90)
insanity_sheet = pygame.image.load("Assets/Sprite/gameplay/insanity.png").convert_alpha()
frame_width, frame_height = 397, 90
cols = 1985 // frame_width   # 5
rows = 1080 // frame_height  # 12
frame_count = 56  # use only first 56 frames

insanity_frames = []
for row in range(rows):
    for col in range(cols):
        rect = pygame.Rect(col * frame_width, row * frame_height, frame_width, frame_height)
        frame = insanity_sheet.subsurface(rect)
        insanity_frames.append(frame)

# Trim to exactly 56 frames
insanity_frames = insanity_frames[:frame_count]

# Slider offsets (adjust to match design)
inner_x_offset = 40
inner_y_offset = 20
slider_width = frame_width - 80
slider_height = frame_height - 40

# State
insanity_level = 0
dragging = False

# Scale factors for rendering
bar_width = 600
bar_height = 150
scale_x = bar_width / frame_width
scale_y = bar_height / frame_height

def update_insanity(mouse_x, rect):
    global insanity_level
    relative_x = mouse_x - rect.left
    relative_x = max(0, min(relative_x, rect.width))
    insanity_level = round((relative_x / rect.width) * (frame_count - 1))
    insanity_level = max(0, min(insanity_level, frame_count - 1))

def draw_bar():
    # Scale current frame
    current_frame = pygame.transform.smoothscale(insanity_frames[insanity_level], (bar_width, bar_height))
    rect = current_frame.get_rect(center=(screen.get_width() // 2, screen.get_height() // 2))
    screen.blit(current_frame, rect)

    # Label
    font = pygame.font.SysFont("Arial", 28)
    text = font.render(f"Insanity Level: {insanity_level}", True, (255, 255, 255))
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
            # Define inner clickable slider rect
            inner_rect = pygame.Rect(
                bar_rect.left + int(inner_x_offset * scale_x),
                bar_rect.top + int(inner_y_offset * scale_y),
                int(slider_width * scale_x),
                int(slider_height * scale_y)
            )
            if inner_rect.collidepoint(event.pos):
                dragging = True
                update_insanity(event.pos[0], inner_rect)

        elif event.type == pygame.MOUSEBUTTONUP:
            dragging = False

        elif event.type == pygame.MOUSEMOTION and dragging:
            inner_rect = pygame.Rect(
                bar_rect.left + int(inner_x_offset * scale_x),
                bar_rect.top + int(inner_y_offset * scale_y),
                int(slider_width * scale_x),
                int(slider_height * scale_y)
            )
            update_insanity(event.pos[0], inner_rect)

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
sys.exit()
