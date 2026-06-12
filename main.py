# main.py
import pygame
import os
import SaveManagement
from View.Scenes.StartMenu import StartMenu
from View.Scenes.ChapterSelect import ChapterSelect
from View.Scenes.CharacterSelection import CharacterSelection
from View.Scenes.Level import Level
from Controller.SceneManager import SceneManager
from Model.AssetLoader import AssetLoader

BASE_WIDTH, BASE_HEIGHT = 1920, 1080

def main():
    pygame.init()
    pygame.mixer.init()

    info = pygame.display.Info()
    native_width, native_height = info.current_w, info.current_h
    os.environ['SDL_VIDEO_CENTERED'] = '1'

    screen = pygame.display.set_mode((native_width, native_height - 50), pygame.RESIZABLE)
    pygame.display.set_caption("Echoes of Whispers")

    game_surface = pygame.Surface((BASE_WIDTH, BASE_HEIGHT))

    # --- Preload Assets ---
    assets = AssetLoader()
    music_path = os.path.join("Sounds", "bg_music.mp3")
    if os.path.exists(music_path):
        pygame.mixer.music.load(music_path)
        pygame.mixer.music.set_volume(0.5)
        pygame.mixer.music.play(-1)

    font_path = os.path.join("Assets", "Font", "VCR_OSD_MONO_1.001.ttf")
    game_font = pygame.font.Font(font_path, 48)
    assets.cache["game_font"] = game_font

    # Characters
    assets.load("Assets/Characters/player_walk.png", (40, 40))
    assets.load("Assets/Characters/player_idle.png", (40, 40))
    assets.load("Assets/Characters/player_walk2.png", (40, 40))
    assets.load("Assets/Characters/girl_char.png", (40, 40))
    assets.load("Assets/Characters/boy_char.png", (40, 40))

    # --- Scene Manager ---
    scene_manager = SceneManager(game_surface)
    scene_manager.set_scene(StartMenu(game_surface, scene_manager))

    chosen_chapter = None
    chosen_character = None
    running = True
    clock = pygame.time.Clock()

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            elif event.type == pygame.VIDEORESIZE:
                screen = pygame.display.set_mode((event.w, event.h), pygame.RESIZABLE)
                scene_manager.set_window_size(event.w, event.h)

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_F11:
                    screen = pygame.display.set_mode((native_width, native_height), pygame.FULLSCREEN)
                elif event.key == pygame.K_F10:
                    screen = pygame.display.set_mode((native_width, native_height - 50), pygame.RESIZABLE)

            else:
                action = scene_manager.handle_input(event)

                # --- Scene Logic ---
                if isinstance(scene_manager.current_scene, StartMenu):
                    if action == "start":
                        # ✅ Reset save file before starting new game
                        with open(SaveManagement.SAVE_FILE, "w", encoding="utf-8") as f:
                            import json
                            # Force reset to Level 1 only
                            json.dump(SaveManagement._default_save(), f, indent=2)

                        scene_manager.set_scene(CharacterSelection(game_surface, scene_manager))

                    elif action == "continue":
                        # ✅ Load existing save without resetting
                        save = SaveManagement.load_save()
                        print(f"Continuing game at Chapter {save['current_chapter']} Level {save['current_level']}")
                        scene_manager.set_scene(CharacterSelection(game_surface, scene_manager))

                    elif action == "exit":
                        running = False
                    elif action == "options":
                        print("Options menu...")
                    elif action == "credits":
                        print("Credits scene...")

                elif isinstance(scene_manager.current_scene, CharacterSelection):
                    if action == "back":
                        scene_manager.set_scene(StartMenu(game_surface, scene_manager))
                    elif action in ["charlie", "blake"]:
                        chosen_character = action
                        print(f"Character chosen: {chosen_character}")
                    elif action == "confirm":
                        if chosen_character:
                            scene_manager.set_scene(ChapterSelect(game_surface, scene_manager, chosen_character))
                        else:
                            print("Confirm clicked but no character selected.")

                elif isinstance(scene_manager.current_scene, ChapterSelect):
                    if isinstance(action, str) and action.startswith("CHAPTER"):
                        chosen_chapter = action
                        print(f"Chapter selected: {chosen_chapter}")

                    elif action == "start" and chosen_chapter:
                        if "CHAPTER 1" in chosen_chapter:
                            try:
                                level_str = chosen_chapter.split("-")[-1].strip()
                                level_num = int(level_str.split()[-1])
                            except (IndexError, ValueError):
                                level_num = 1

                            if level_num == 1:
                                from ch1_lvl1 import run_level
                                level_result = run_level(chosen_character=chosen_character)
                            elif level_num == 2:
                                from ch1_lvl2 import run_level
                                level_result = run_level(chosen_character=chosen_character)
                            elif level_num == 3:
                                from ch1_lvl3 import run_level
                                level_result = run_level(chosen_character=chosen_character)
                            else:
                                level_result = "menu"

                            if level_result == "menu":
                                scene_manager.set_scene(StartMenu(game_surface, scene_manager))
                            else:
                                scene_manager.set_scene(ChapterSelect(game_surface, scene_manager, chosen_character))

                            pygame.event.clear()
                        else:
                            scene_manager.set_scene(Level(game_surface, chapter_id=chosen_chapter, character=chosen_character))

                    elif action == "back":
                        scene_manager.set_scene(CharacterSelection(game_surface, scene_manager))
                    elif action == "menu":
                        scene_manager.set_scene(StartMenu(game_surface, scene_manager))

        # --- Update & Render ---
        scene_manager.update()
        scene_manager.render()

        # --- Scale & Blit ---
        window_width, window_height = screen.get_size()
        scale = min(window_width / BASE_WIDTH, window_height / BASE_HEIGHT)
        scaled_width = int(BASE_WIDTH * scale)
        scaled_height = int(BASE_HEIGHT * scale)

        scaled_surface = pygame.transform.smoothscale(game_surface, (scaled_width, scaled_height))

        screen.fill((0, 0, 0))
        x_offset = (window_width - scaled_width) // 2
        y_offset = (window_height - scaled_height) // 2
        screen.blit(scaled_surface, (x_offset, y_offset))

        scale_info = {
            "scale": scale,
            "x_offset": x_offset,
            "y_offset": y_offset,
            "win_size": (window_width, window_height)
        }
        scene_manager.set_scale_info(scale_info)

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()

if __name__ == "__main__":
    main()
