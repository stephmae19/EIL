# ch1_lvl1_puz.py
import pygame
import sys
import os
from ui_layer import UILayer   # ✅ import your UI layer

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

# --- Back button ---
back_button = pygame.Rect(50, 50, 120, 50)

# --- Drag & drop state ---
dragging_letter = None
drag_source = None  # "inventory" or "answer"
drag_offset_x, drag_offset_y = 0, 0

# --- Answer slots ---
answer_slots = [None] * 7
answer_rects = []
for i in range(7):
    rect = pygame.Rect(BASE_WIDTH//2 - 280 + i*80, BASE_HEIGHT - 300, 70, 70)
    answer_rects.append(rect)

def run_puzzle(player, ui_layer):
    global dragging_letter, drag_source

    solved = False

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            # ✅ ESC key acts as back button
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                return  # go back to ch1_lvl1.py, keep progress

            if event.type == pygame.MOUSEBUTTONDOWN:
                if back_button.collidepoint(event.pos):
                    return  # ✅ back button click also works

                # ✅ Start dragging from inventory bar
                for i, rect in enumerate(ui_layer.inventory_slots):
                    if rect.collidepoint(event.pos) and i < len(player.inventory):
                        dragging_letter = i
                        drag_source = "inventory"
                        drag_offset_x = rect.x - event.pos[0]
                        drag_offset_y = rect.y - event.pos[1]

                # ✅ Start dragging from answer slots (for rearranging)
                for j, rect in enumerate(answer_rects):
                    if rect.collidepoint(event.pos) and answer_slots[j]:
                        dragging_letter = j
                        drag_source = "answer"
                        drag_offset_x = rect.x - event.pos[0]
                        drag_offset_y = rect.y - event.pos[1]

            if event.type == pygame.MOUSEBUTTONUP:
                if dragging_letter is not None:
                    if drag_source == "inventory":
                        # ✅ Drop from inventory into empty answer slot
                        for j, rect in enumerate(answer_rects):
                            if rect.collidepoint(event.pos) and not answer_slots[j]:
                                answer_slots[j] = player.inventory[dragging_letter]
                                # remove from inventory
                                player.inventory.pop(dragging_letter)
                                break

                    elif drag_source == "answer":
                        # ✅ Rearrange letters between answer slots
                        for j, rect in enumerate(answer_rects):
                            if rect.collidepoint(event.pos):
                                answer_slots[j], answer_slots[dragging_letter] = answer_slots[dragging_letter], answer_slots[j]
                                break

                    dragging_letter = None
                    drag_source = None

        # --- Render ---
        screen.fill((30, 30, 30))
        screen.blit(manu_text_img, manu_rect)

        # ✅ Draw inventory bar with collected letters
        ui_layer.draw_inventory_bar(player)

        # Puzzle text only shows once all 7 slots are filled
        if all(answer_slots):
            lines = puzzle_text.split("\n")
            for i, line in enumerate(lines):
                txt = ui_font.render(line, True, (255, 255, 255))
                screen.blit(txt, (BASE_WIDTH//2 - txt.get_width()//2, 50 + i*40))

            # ✅ Check for success condition
            if "".join(answer_slots) == "HEMLOCK":
                solved = True

        # Back button
        pygame.draw.rect(screen, (200, 50, 50), back_button)
        back_txt = ui_font.render("BACK", True, (255, 255, 255))
        screen.blit(back_txt, back_button.move(20, 10))

        # ✅ Answer slots (7 letters)
        for j, rect in enumerate(answer_rects):
            pygame.draw.rect(screen, (255, 255, 255), rect, 2)
            if answer_slots[j]:
                color = (0, 255, 0) if solved else (255, 255, 0)
                letter_txt = ui_font.render(answer_slots[j], True, color)
                screen.blit(letter_txt, rect.move(20, 20))

        # ✅ Success message
        if solved:
            success_txt = ui_font.render("Puzzle Solved! The word is HEMLOCK.", True, (0, 255, 0))
            screen.blit(success_txt, (BASE_WIDTH//2 - success_txt.get_width()//2, BASE_HEIGHT//2 + 200))

        pygame.display.flip()
        clock.tick(60)

# ✅ Allow standalone execution
if __name__ == "__main__":
    class DummyPlayer:
        def __init__(self):
            self.inventory = ["H", "E", "M", "L", "O", "C", "K"]

    ui_layer = UILayer(screen)
    run_puzzle(DummyPlayer(), ui_layer)
