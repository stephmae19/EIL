# main.py
import pygame
from View.Scenes.StartMenu import StartMenu
from Controller.SceneManager import SceneManager

def main():
    # Initialize pygame
    pygame.init()
    screen = pygame.display.set_mode((800, 600))  # Adjust resolution as needed
    pygame.display.set_caption("Echoes of Whispers")

    # Create SceneManager and load StartMenu
    scene_manager = SceneManager(screen)
    start_menu = StartMenu(screen)
    scene_manager.set_scene(start_menu)

    # Main loop
    running = True
    clock = pygame.time.Clock()

    while running:
        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            else:
                # Capture action from StartMenu
                action = scene_manager.handle_input(event)
                if action == "start":
                    print("Starting game...")  # Replace with Level scene transition
                elif action == "continue":
                    print("Continue game...")  # Load saved state
                elif action == "options":
                    print("Options menu...")   # Replace with Options scene
                elif action == "credits":
                    print("Credits scene...") # Replace with Credits scene
                elif action == "exit":
                    running = False

        # Update current scene
        scene_manager.update()

        # Render current scene
        scene_manager.render()

        # Cap frame rate
        clock.tick(60)

    pygame.quit()

if __name__ == "__main__":
    main()
