# main.py
import pygame
import os
from View.Scenes.StartMenu import StartMenu
from View.Scenes.ChapterSelect import ChapterSelect
from View.Scenes.CharacterSelection import CharacterSelection
from View.Scenes.Level import Level
from Controller.SceneManager import SceneManager
from Model.AssetLoader import AssetLoader   # new loader

def main():
    # Initialize pygame
    pygame.init()
    pygame.mixer.init()

    # --- Display Setup (must come before convert_alpha) ---
    info = pygame.display.Info()
    width, height = info.current_w, info.current_h
    os.environ['SDL_VIDEO_CENTERED'] = '1'
    screen = pygame.display.set_mode((width, height - 50), pygame.RESIZABLE)
    pygame.display.set_caption("Echoes of Whispers")

    # --- Preload Assets ---
    assets = AssetLoader()

    # Background music
    music_path = os.path.join("Sounds", "bg_music.mp3")
    if os.path.exists(music_path):
        pygame.mixer.music.load(music_path)
        pygame.mixer.music.set_volume(0.5)
        pygame.mixer.music.play(-1)
    else:
        print("Background music file not found:", music_path)

    # Fonts
    font_path = os.path.join("Assets", "Font", "VCR_OSD_MONO_1.001.ttf")
    game_font = pygame.font.Font(font_path, 48)
    assets.cache["game_font"] = game_font

    # Characters (example preload)
    assets.load("Assets/Characters/player_walk.png", (40, 40))
    assets.load("Assets/Characters/girl_char.png", (40, 40))
    assets.load("Assets/Characters/boy_char.png", (40, 40))

    # --- Scene Manager ---
    scene_manager = SceneManager(screen)
    scene_manager.set_scene(StartMenu(screen))

    chosen_chapter = None
    chosen_character = None
    running = True
    clock = pygame.time.Clock()

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            elif event.type == pygame.VIDEORESIZE:
                width, height = event.w, event.h
                screen = pygame.display.set_mode((width, height), pygame.RESIZABLE)
                scene_manager.screen = screen

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_F11:
                    screen = pygame.display.set_mode((info.current_w, info.current_h), pygame.FULLSCREEN)
                    scene_manager.screen = screen
                elif event.key == pygame.K_F10:
                    screen = pygame.display.set_mode((info.current_w, info.current_h - 50), pygame.RESIZABLE)
                    scene_manager.screen = screen

            else:
                action = scene_manager.handle_input(event)

                # --- StartMenu ---
                if isinstance(scene_manager.current_scene, StartMenu):
                    if action == "start":
                        scene_manager.set_scene(CharacterSelection(screen, scene_manager))
                    elif action == "exit":
                        running = False
                    elif action == "continue":
                        print("Continue game...")
                    elif action == "options":
                        print("Options menu...")
                    elif action == "credits":
                        print("Credits scene...")

                # --- CharacterSelection ---
                elif isinstance(scene_manager.current_scene, CharacterSelection):
                    if action == "back":
                        scene_manager.set_scene(StartMenu(screen))
                    elif action in ["girl", "boy"]:
                        chosen_character = action
                        print(f"Character chosen: {chosen_character}")
                    elif action == "confirm":
                        if chosen_character:
                            print(f"Confirmed character: {chosen_character}")
                            scene_manager.set_scene(ChapterSelect(screen))
                        else:
                            print("Confirm clicked but no character selected.")

                # --- ChapterSelect ---
                elif isinstance(scene_manager.current_scene, ChapterSelect):
                    if isinstance(action, str) and action.startswith("CHAPTER"):
                        chosen_chapter = action
                        print(f"Chapter selected: {chosen_chapter}")
                    elif action == "start" and chosen_chapter:
                        print(f"Starting Level with Chapter: {chosen_chapter}, Character: {chosen_character}")
                        # ✅ Directly run ch1_lvl1 if Chapter 1 Level 1 is chosen
                        if "CHAPTER 1" in chosen_chapter and "Level 1" in chosen_chapter:
                            from ch1_lvl1 import run_level
                            run_level()
                            # After run_level returns, go back to ChapterSelect
                            scene_manager.set_scene(ChapterSelect(screen))
                        else:
                            # fallback to your MVC Level scene for other chapters/levels
                            scene_manager.set_scene(
                                Level(screen, chapter_id=chosen_chapter, character=chosen_character))
                    elif action == "back":
                        scene_manager.set_scene(CharacterSelection(screen, scene_manager))
                    elif action == "menu":
                        scene_manager.set_scene(StartMenu(screen))

        scene_manager.update()
        scene_manager.render()
        clock.tick(60)

    pygame.quit()

if __name__ == "__main__":
    main()
