# game_utils.py
import pygame
import os

_cached_screen = None

def get_or_create_screen():
    global _cached_screen
    if _cached_screen is not None:
        return _cached_screen

    pygame.init()
    pygame.mixer.init()
    os.environ['SDL_VIDEO_CENTERED'] = '1'

    # Get info to create the initial screen
    info = pygame.display.Info()
    native_width, native_height = info.current_w, info.current_h

    # Return the created screen
    return pygame.display.set_mode((native_width, native_height - 50), pygame.RESIZABLE)