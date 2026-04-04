# main.py
import pygame
from View.Scenes.StartMenu import StartMenu
from View.Scenes.ChapterSelect import ChapterSelect
from View.Scenes.CharacterSelection import CharacterSelection
from View.Scenes.Level import Level
from Controller.SceneManager import SceneManager

def main():
    pygame.init()

    # Get the current display resolution
    info = pygame.display.Info()
    width, height = info.current_w, info.current_h

    # Reduce height slightly so the taskbar remains visible
    screen = pygame.display.set_mode((width, height - 50), pygame.RESIZABLE)
    pygame.display.set_caption("Echoes of Whispers")

    scene_manager = SceneManager(screen)
    scene_manager.set_scene(StartMenu(screen))

    chosen_chapter = None
    running = True
    clock = pygame.time.Clock()

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            elif event.type == pygame.VIDEORESIZE:
                # Handle dynamic resize
                width, height = event.w, event.h
                screen = pygame.display.set_mode((width, height), pygame.RESIZABLE)
                scene_manager.screen = screen

            elif event.type == pygame.KEYDOWN:
                # Toggle fullscreen/windowed
                if event.key == pygame.K_F11:
                    screen = pygame.display.set_mode((info.current_w, info.current_h), pygame.FULLSCREEN)
                    scene_manager.screen = screen
                elif event.key == pygame.K_F10:
                    screen = pygame.display.set_mode((info.current_w, info.current_h - 50), pygame.RESIZABLE)
                    scene_manager.screen = screen

            else:
                action = scene_manager.handle_input(event)

                if isinstance(scene_manager.current_scene, StartMenu):
                    if action == "start":
                        scene_manager.set_scene(ChapterSelect(screen))
                    elif action == "exit":
                        running = False
                    elif action == "continue":
                        print("Continue game...")
                    elif action == "options":
                        print("Options menu...")
                    elif action == "credits":
                        print("Credits scene...")

                elif isinstance(scene_manager.current_scene, ChapterSelect):
                    if action in [1, 2, 3, 4]:
                        chosen_chapter = action
                        scene_manager.set_scene(CharacterSelection(screen))
                    elif action == "menu":
                        scene_manager.set_scene(StartMenu(screen))

                elif isinstance(scene_manager.current_scene, CharacterSelection):
                    if action == "menu":
                        scene_manager.set_scene(StartMenu(screen))
                    elif action in ["warrior", "mage", "rogue"]:
                        print(f"Character chosen: {action}, Chapter: {chosen_chapter}")
                        scene_manager.set_scene(Level(screen, chapter_id=chosen_chapter))

        scene_manager.update()
        scene_manager.render()
        clock.tick(60)

    pygame.quit()

if __name__ == "__main__":
    main()
