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

# --- Display Setup ---
info = pygame.display.Info()
native_width, native_height = info.current_w, info.current_h
os.environ['SDL_VIDEO_CENTERED'] = '1'

screen = pygame.display.set_mode((native_width, native_height - 50), pygame.RESIZABLE)
pygame.display.set_caption("Chapter 1 - Level 1 Puzzle")

# Internal fixed surface (always BASE_WIDTH x BASE_HEIGHT)
game_surface = pygame.Surface((BASE_WIDTH, BASE_HEIGHT))

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

# --- Answer slots ---
answer_slots = [None] * 7
answer_rects = []
for i in range(7):
    rect = pygame.Rect(BASE_WIDTH//2 - 280 + i*80, BASE_HEIGHT - 300, 70, 70)
    answer_rects.append(rect)

# --- Helper: translate mouse coords ---
def translate_mouse(pos, window_size):
    window_w, window_h = window_size
    scale = min(window_w / BASE_WIDTH, window_h / BASE_HEIGHT)
    scaled_w, scaled_h = int(BASE_WIDTH * scale), int(BASE_HEIGHT * scale)
    x_offset = (window_w - scaled_w) // 2
    y_offset = (window_h - scaled_h) // 2
    x = (pos[0] - x_offset) / scale
    y = (pos[1] - y_offset) / scale
    return int(x), int(y)

def run_puzzle(player, ui_layer=None):
    global dragging_letter, drag_source

    # ✅ Always bind UILayer to the puzzle surface
    if ui_layer is None or ui_layer.surface != game_surface:
        ui_layer = UILayer(game_surface)

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
                mouse_pos = translate_mouse(event.pos, screen.get_size())

                if back_button.collidepoint(mouse_pos):
                    return  # ✅ back button click also works

                # ✅ Start dragging from inventory bar
                for i, rect in enumerate(ui_layer.inventory_slots):
                    if rect.collidepoint(mouse_pos) and i < len(player.inventory):
                        dragging_letter = i
                        drag_source = "inventory"

                # ✅ Start dragging from answer slots (for rearranging)
                for j, rect in enumerate(answer_rects):
                    if rect.collidepoint(mouse_pos) and answer_slots[j]:
                        dragging_letter = j
                        drag_source = "answer"

            if event.type == pygame.MOUSEBUTTONUP:
                mouse_pos = translate_mouse(event.pos, screen.get_size())

                if dragging_letter is not None:
                    if drag_source == "inventory":
                        # ✅ Drop from inventory into empty answer slot
                        for j, rect in enumerate(answer_rects):
                            if rect.collidepoint(mouse_pos) and not answer_slots[j]:
                                answer_slots[j] = player.inventory[dragging_letter]
                                player.inventory.pop(dragging_letter)
                                break

                    elif drag_source == "answer":
                        # ✅ Rearrange letters between answer slots
                        for j, rect in enumerate(answer_rects):
                            if rect.collidepoint(mouse_pos):
                                answer_slots[j], answer_slots[dragging_letter] = answer_slots[dragging_letter], answer_slots[j]
                                break

                    dragging_letter = None
                    drag_source = None

        # --- Render everything to internal surface ---
        game_surface.fill((30, 30, 30))
        game_surface.blit(manu_text_img, manu_rect)

        # ✅ Draw inventory bar with collected letters
        ui_layer.draw_inventory_bar(player)

        # Puzzle text only shows once all 7 slots are filled
        if all(answer_slots):
            lines = puzzle_text.split("\n")
            # Calculate starting Y inside the manuscript image
            start_y = manu_rect.top + 40
            for i, line in enumerate(lines):
                txt = ui_font.render(line, True, (0, 0, 0))  # black text for contrast
                text_x = manu_rect.centerx - txt.get_width() // 2
                text_y = start_y + i * 40
                game_surface.blit(txt, (text_x, text_y))

            # ✅ Check for success condition
            if "".join(answer_slots) == "HEMLOCK":
                solved = True

        # Back button
        pygame.draw.rect(game_surface, (200, 50, 50), back_button)
        back_txt = ui_font.render("BACK", True, (255, 255, 255))
        game_surface.blit(back_txt, back_button.move(20, 10))

        # ✅ Answer slots (7 letters)
        for j, rect in enumerate(answer_rects):
            pygame.draw.rect(game_surface, (255, 255, 255), rect, 2)
            if answer_slots[j]:
                color = (0, 255, 0) if solved else (255, 255, 0)
                letter_txt = ui_font.render(answer_slots[j], True, color)
                game_surface.blit(letter_txt, rect.move(20, 20))

        # ✅ Success message
        if solved:
            success_txt = ui_font.render("Puzzle Solved! The word is HEMLOCK.", True, (0, 255, 0))
            game_surface.blit(success_txt, (BASE_WIDTH//2 - success_txt.get_width()//2, BASE_HEIGHT//2 + 200))

        # --- Scale & Blit to window with aspect ratio preserved ---
        window_width, window_height = screen.get_size()
        scale = min(window_width / BASE_WIDTH, window_height / BASE_HEIGHT)
        scaled_w, scaled_h = int(BASE_WIDTH * scale), int(BASE_HEIGHT * scale)

        scaled_surface = pygame.transform.smoothscale(game_surface, (scaled_w, scaled_h))

        x_offset = (window_width - scaled_w) // 2
        y_offset = (window_height - scaled_h) // 2

        screen.fill((0, 0, 0))  # black padding
        screen.blit(scaled_surface, (x_offset, y_offset))

        pygame.display.flip()
        clock.tick(60)

# ✅ Allow standalone execution
if __name__ == "__main__":
    class DummyPlayer:
        def __init__(self):
            self.inventory = ["H", "E", "M", "L", "O", "C", "K"]

    ui_layer = UILayer(game_surface)
    run_puzzle(DummyPlayer(), ui_layer)
