import pygame
import os
import SaveManagement
from View.Scenes.StartMenu import StartMenu
from View.Scenes.ChapterSelect import ChapterSelect
from View.Scenes.CharacterSelection import CharacterSelection
from View.Scenes.Level import Level
from Controller.SceneManager import SceneManager
from Model.AssetLoader import AssetLoader
from game_utils import get_or_create_screen

# Import levels
import ch1_lvl1
import ch1_lvl2
import ch1_lvl3

BASE_WIDTH, BASE_HEIGHT = 1920, 1080


def run_level_by_id(level_id, screen, character):
    """
    Central dispatcher to run a level by ID string.
    Returns the ID of the next level to run, or "menu" if quitting.
    """
    levels = {
        "lvl1": ch1_lvl1.run_level,
        "lvl2": ch1_lvl2.run_level,
        "lvl3": ch1_lvl3.run_level,
    }

    if level_id in levels:
        return levels[level_id](screen, chosen_character=character)
    return "menu"


def main():
    pygame.init()
    pygame.mixer.init()

    os.environ['SDL_VIDEO_CENTERED'] = '1'
    screen = get_or_create_screen()
    pygame.display.set_caption("Echoes of Whispers")

    game_surface = pygame.Surface((BASE_WIDTH, BASE_HEIGHT))

    # --- Preload Assets ---
    assets = AssetLoader()
    music_path = os.path.join("Sounds", "bg_music.mp3")

    def play_music():
        if os.path.exists(music_path) and not pygame.mixer.music.get_busy():
            pygame.mixer.music.load(music_path)
            pygame.mixer.music.set_volume(0.5)
            pygame.mixer.music.play(-1)

    play_music()

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
                screen = get_or_create_screen()
                scene_manager.set_window_size(*screen.get_size())

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_F11:
                    screen = pygame.display.set_mode(screen.get_size(), pygame.FULLSCREEN)
                elif event.key == pygame.K_F10:
                    screen = get_or_create_screen()

            else:
                action = scene_manager.handle_input(event)

                # --- Scene Logic ---
                if isinstance(scene_manager.current_scene, StartMenu):
                    if action == "start":
                        with open(SaveManagement.SAVE_FILE, "w", encoding="utf-8") as f:
                            import json
                            json.dump(SaveManagement._default_save(), f, indent=2)
                        scene_manager.set_scene(CharacterSelection(game_surface, scene_manager))

                    elif action == "continue":
                        save = SaveManagement.load_save()
                        scene_manager.set_scene(CharacterSelection(game_surface, scene_manager))

                    elif action == "exit":
                        running = False

                elif isinstance(scene_manager.current_scene, CharacterSelection):
                    if action == "back":
                        scene_manager.set_scene(StartMenu(game_surface, scene_manager))
                    elif action in ["charlie", "blake"]:
                        chosen_character = action
                    elif action == "confirm":
                        if chosen_character:
                            scene_manager.set_scene(ChapterSelect(game_surface, scene_manager, chosen_character))

                elif isinstance(scene_manager.current_scene, ChapterSelect):
                    if isinstance(action, str) and action.startswith("CHAPTER"):
                        chosen_chapter = action

                    elif action == "start" and chosen_chapter:
                        # 1. Determine starting level ID
                        current_level_id = None
                        if "CHAPTER 1" in chosen_chapter:
                            try:
                                level_num = int(chosen_chapter.split("-")[-1].strip().split()[-1])
                                current_level_id = f"lvl{level_num}"
                            except (IndexError, ValueError):
                                current_level_id = "lvl1"

                        # 2. Level Execution Loop (Orchestrator)
                        # We stay in this loop until the level returns "menu" or quits
                        while current_level_id and current_level_id != "menu":
                            # Run current level, get next level ID string
                            current_level_id = run_level_by_id(current_level_id, screen, chosen_character)

                        # 3. Post-Gameplay Reset
                        scene_manager.set_scene(StartMenu(game_surface, scene_manager))
                        play_music()
                        pygame.event.clear()

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
        scaled_surface = pygame.transform.smoothscale(game_surface, (int(BASE_WIDTH * scale), int(BASE_HEIGHT * scale)))

        screen.fill((0, 0, 0))
        x_offset = (window_width - scaled_surface.get_width()) // 2
        y_offset = (window_height - scaled_surface.get_height()) // 2
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