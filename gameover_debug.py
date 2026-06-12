# debug_gameover.py
import pygame
import sys
import gameover

# --- CONFIGURATION FOR DEBUGGING ---
# You can change these values to test how your UI handles different screen sizes!
WINDOW_WIDTH = 1280
WINDOW_HEIGHT = 720
FPS = 60


def main():
    # Initialize Pygame core modules
    pygame.init()
    pygame.font.init()

    # Create the test window surface
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.RESIZABLE)
    pygame.display.set_caption("Game Over Screen - Standalone Debugger")

    print("=" * 50)
    print("🎮 GAME OVER SCREEN DEBUG MODE ACTIVE 🎮")
    print(f"Resolutions: {WINDOW_WIDTH}x{WINDOW_HEIGHT}")
    print("Press 'RETRY' button / SPACE / ENTER -> Returns 'restart'")
    print("Press 'EXIT' button / ESC -> Returns 'menu'")
    print("=" * 50)

    # Fire the game over scene
    # This acts exactly how ch1_lvl1.py interacts with it
    result = gameover.show_game_over(screen)

    # Print out what action was captured to verify click logic works flawlessly
    print("\n" + "#" * 40)
    print(f"➡️ RETURNED ACTION VALUE: '{result}'")
    print("#" * 40 + "\n")

    # Clean up and exit terminal mode safely
    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()