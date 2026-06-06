import pygame
import sys
import textwrap

pygame.init()

# Screen setup
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Echoes in the Library - Narration")

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)

# Fonts
font = pygame.font.Font(None, 40)
chapter_font = pygame.font.Font(None, 60)

# Narration text
lines = [
    "CHAPTER 1: THE BEGINNING",
    "The townspeople used to say something unimaginable happened in this library.",
    "Some say the old librarian died within the walls of the old building…",
    "and some… said she was killed.",
    "Well, I’m here to uncover the truth about this entire story."
]

clock = pygame.time.Clock()

def wrap_text(text, font, max_width):
    """Split text into wrapped lines that fit within max_width."""
    words = text.split(' ')
    wrapped_lines = []
    current_line = ""

    for word in words:
        test_line = current_line + word + " "
        if font.size(test_line)[0] <= max_width:
            current_line = test_line
        else:
            wrapped_lines.append(current_line.strip())
            current_line = word + " "
    if current_line:
        wrapped_lines.append(current_line.strip())
    return wrapped_lines

def fade_out(lines, positions, is_chapter, duration=1000):
    """Fade out the given lines over duration (ms)."""
    start_time = pygame.time.get_ticks()
    while True:
        elapsed = pygame.time.get_ticks() - start_time
        alpha = max(0, 255 - int((elapsed / duration) * 255))
        screen.fill(BLACK)
        for (text, y, chap) in zip(lines, positions, is_chapter):
            surf = chapter_font.render(text, True, WHITE) if chap else font.render(text, True, WHITE)
            temp = surf.copy()
            temp.set_alpha(alpha)
            screen.blit(temp, (WIDTH//2 - surf.get_width()//2, y))
        pygame.display.flip()
        clock.tick(60)
        if alpha <= 0:
            break

def main():
    running = True
    char_timer = 0
    delay = 60  # ms per character
    current_line = 0
    displayed_text = ""

    while running:
        dt = clock.tick(30)  # 30 FPS
        char_timer += dt

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        if current_line < len(lines):
            line = lines[current_line]
            if char_timer >= delay:
                if len(displayed_text) < len(line):
                    displayed_text += line[len(displayed_text)]
                else:
                    # Finished typing this line
                    if "CHAPTER" in line:
                        surf = chapter_font.render(line, True, WHITE)
                        y_offset = HEIGHT//2 - surf.get_height()//2
                        screen.blit(surf, (WIDTH//2 - surf.get_width()//2, y_offset))
                        pygame.display.flip()
                        pygame.time.delay(1000)
                        fade_out([line], [y_offset], [True])
                    else:
                        wrapped = wrap_text(displayed_text, font, WIDTH - 100)
                        total_height = len(wrapped) * font.get_height() + (len(wrapped)-1)*10
                        start_y = HEIGHT//2 - total_height//2
                        positions = []
                        for i, wline in enumerate(wrapped):
                            surf = font.render(wline, True, WHITE)
                            pos_y = start_y + i*(font.get_height()+10)
                            screen.blit(surf, (WIDTH//2 - surf.get_width()//2, pos_y))
                            positions.append(pos_y)
                        pygame.display.flip()
                        pygame.time.delay(1000)
                        fade_out(wrapped, positions, [False]*len(wrapped))
                    displayed_text = ""
                    current_line += 1
                char_timer = 0

        # Draw typing effect
        screen.fill(BLACK)
        if displayed_text:
            if "CHAPTER" in lines[current_line]:
                surf = chapter_font.render(displayed_text, True, WHITE)
                y_offset = HEIGHT//2 - surf.get_height()//2
                screen.blit(surf, (WIDTH//2 - surf.get_width()//2, y_offset))
            else:
                wrapped = wrap_text(displayed_text, font, WIDTH - 100)
                total_height = len(wrapped) * font.get_height() + (len(wrapped)-1)*10
                start_y = HEIGHT//2 - total_height//2
                for i, wline in enumerate(wrapped):
                    surf = font.render(wline, True, WHITE)
                    pos_y = start_y + i*(font.get_height()+10)
                    screen.blit(surf, (WIDTH//2 - surf.get_width()//2, pos_y))
        pygame.display.flip()

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()
