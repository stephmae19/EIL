# main.py
import pygame
from View.Scenes.StartMenu import StartMenu
from View.Scenes.ChapterSelect import ChapterSelect
from View.Scenes.CharacterSelection import CharacterSelection
from View.Scenes.Level import Level
from Controller.SceneManager import SceneManager

def main():
    # Initialize pygame
    pygame.init()
    screen = pygame.display.set_mode((800, 600))
    pygame.display.set_caption("Echoes of Whispers")

    # Create SceneManager and load StartMenu
    scene_manager = SceneManager(screen)
    scene_manager.set_scene(StartMenu(screen))

    # Track chosen chapter for passing into Level
    chosen_chapter = None

    # Main loop
    running = True
    clock = pygame.time.Clock()

    while running:
        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            else:
                action = scene_manager.handle_input(event)

                # Handle scene transitions
                if isinstance(scene_manager.current_scene, StartMenu):
                    if action == "start":
                        scene_manager.set_scene(ChapterSelect(screen))
                    elif action == "exit":
                        running = False
                    elif action == "continue":
                        print("Continue game...")  # Placeholder
                    elif action == "options":
                        print("Options menu...")   # Placeholder
                    elif action == "credits":
                        print("Credits scene...") # Placeholder

                elif isinstance(scene_manager.current_scene, ChapterSelect):
                    if action in [1, 2, 3, 4]:  # Chapter IDs
                        chosen_chapter = action
                        scene_manager.set_scene(CharacterSelection(screen))
                    elif action == "menu":
                        scene_manager.set_scene(StartMenu(screen))

                elif isinstance(scene_manager.current_scene, CharacterSelection):
                    if action == "menu":
                        scene_manager.set_scene(StartMenu(screen))
                    elif action in ["warrior", "mage", "rogue"]:
                        print(f"Character chosen: {action}, Chapter: {chosen_chapter}")
                        # Move into gameplay Level scene with chosen chapter + character
                        scene_manager.set_scene(Level(screen, chapter_id=chosen_chapter))

        # Update current scene
        scene_manager.update()

        # Render current scene
        scene_manager.render()

        # Cap frame rate
        clock.tick(60)

    pygame.quit()

if __name__ == "__main__":
    main()
