# ch1_lvl1_puz.py
import pygame
import sys
import os

# --- Filenames ---
MANU_TEXT_FILE = "assets/objects-items/manu_text.png"

# --- Config ---
BASE_WIDTH, BASE_HEIGHT = 1920, 1080

pygame.init()
pygame.font.init()

screen = pygame.display.set_mode((BASE_WIDTH, BASE_HEIGHT))
pygame.display.set_caption("Chapter 1 - Level 1 Puzzle")

clock = pygame.time.Clock()
ui_font = pygame.font.SysFont("arial", 32, bold=True)

# --- Load manu_text image ---
if os.path.exists(MANU_TEXT_FILE):
    manu_text_img = pygame.image.load(MANU_TEXT_FILE).convert_alpha()
    manu_text_img = pygame.transform.scale(manu_text_img, (int(BASE_WIDTH * 0.6), int(BASE_HEIGHT * 0.6)))
else:
    manu_text_img = pygame.Surface((600, 400))
    manu_text_img.fill((200, 200, 200))

manu_rect = manu_text_img.get_rect(center=(BASE_WIDTH // 2, BASE_HEIGHT // 2))

# --- Puzzle text ---
puzzle_text = (
    "I am the surname of the regular visitor\n"
    "who met a tragic, blood-curdling end on Aisle 11.\n"
    "My name is also a deadly poison."
)

# --- Inventory slots ---
inventory_slots = [None] * 6  # placeholder for letters
slot_rects = []
for i in range(6):
    rect = pygame.Rect(100 + i * 100, BASE_HEIGHT - 150, 80, 80)
    slot_rects.append(rect)

# --- Back button ---
back_button = pygame.Rect(50, 50, 120, 50)

# --- Drag & drop state ---
dragging_letter = None
drag_offset_x, drag_offset_y = 0, 0

# --- Shuffle state ---
letters_shuffled = False
answer_slots = [None] * 7
answer_rects = []
for i in range(7):
    rect = pygame.Rect(BASE_WIDTH//2 - 280 + i*80, BASE_HEIGHT - 300, 70, 70)
    answer_rects.append(rect)

def run_puzzle():
    global dragging_letter, letters_shuffled
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.MOUSEBUTTONDOWN:
                if back_button.collidepoint(event.pos):
                    return  # ✅ go back to ch1_lvl1.py

                # check inventory slots
                for i, rect in enumerate(slot_rects):
                    if rect.collidepoint(event.pos) and inventory_slots[i]:
                        dragging_letter = i
                        drag_offset_x = rect.x - event.pos[0]
                        drag_offset_y = rect.y - event.pos[1]

            if event.type == pygame.MOUSEBUTTONUP:
                if dragging_letter is not None:
                    # drop into answer slots
                    for j, rect in enumerate(answer_rects):
                        if rect.collidepoint(event.pos):
                            answer_slots[j] = inventory_slots[dragging_letter]
                            break
                    dragging_letter = None

        # --- Render ---
        screen.fill((30, 30, 30))
        screen.blit(manu_text_img, manu_rect)

        # Puzzle text
        lines = puzzle_text.split("\n")
        for i, line in enumerate(lines):
            txt = ui_font.render(line, True, (255, 255, 255))
            screen.blit(txt, (BASE_WIDTH//2 - txt.get_width()//2, 50 + i*40))

        # Back button
        pygame.draw.rect(screen, (200, 50, 50), back_button)
        back_txt = ui_font.render("BACK", True, (255, 255, 255))
        screen.blit(back_txt, back_button.move(20, 10))

        # Inventory slots
        for i, rect in enumerate(slot_rects):
            pygame.draw.rect(screen, (100, 100, 100), rect, 2)
            if inventory_slots[i]:
                letter_txt = ui_font.render(inventory_slots[i], True, (255, 255, 0))
                screen.blit(letter_txt, rect.move(20, 20))

        # Answer slots (7 letters)
        for j, rect in enumerate(answer_rects):
            pygame.draw.rect(screen, (255, 255, 255), rect, 2)
            if answer_slots[j]:
                letter_txt = ui_font.render(answer_slots[j], True, (0, 255, 0))
                screen.blit(letter_txt, rect.move(20, 20))

        pygame.display.flip()
        clock.tick(60)

# ✅ Allow standalone execution
if __name__ == "__main__":
    run_puzzle()
