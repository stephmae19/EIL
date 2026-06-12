# SaveManagement.py
import pygame
import json
import os

SAVE_FILE = "savegame.json"


def _default_save():
    return {
        "current_chapter": 1,
        "current_level": 1,      # next level to play (1-based)
        "completed_levels": []   # e.g. ["CH1_L1", "CH1_L2"]
    }


def load_save():
    """Load save data from disk, or return defaults if none exists."""
    if not os.path.exists(SAVE_FILE):
        return _default_save()
    try:
        with open(SAVE_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
    except Exception:
        # Corrupt or unreadable; reset
        data = _default_save()
    # Ensure required keys
    for k, v in _default_save().items():
        data.setdefault(k, v)
    return data


def save_progress(chapter: int, level: int):
    """
    Mark the given chapter/level as completed and update next level to play.
    chapter: 1-based chapter id (e.g. 1 for CH1)
    level:   1-based level id   (e.g. 1 for Level 1)
    """
    data = load_save()

    # Compose a simple ID like "CH1_L1"
    level_id = f"CH{chapter}_L{level}"
    if level_id not in data["completed_levels"]:
        data["completed_levels"].append(level_id)

    # Update current chapter/level to the NEXT level in this chapter
    data["current_chapter"] = chapter
    data["current_level"] = level + 1

    with open(SAVE_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)


def get_next_level():
    """
    Returns (chapter, level) for the next level to play.
    Currently just returns current_chapter/current_level from the save.
    """
    data = load_save()
    return data["current_chapter"], data["current_level"]


def fade_to_black(screen, duration_ms=1000):
    """
    Simple fade-to-black effect over 'duration_ms' milliseconds.
    Assumes 'screen' is the main display surface.
    """
    clock = pygame.time.Clock()
    width, height = screen.get_size()
    overlay = pygame.Surface((width, height))
    overlay.fill((0, 0, 0))

    start_time = pygame.time.get_ticks()

    while True:
        now = pygame.time.get_ticks()
        elapsed = now - start_time
        t = min(1.0, elapsed / duration_ms)
        alpha = int(255 * t)
        overlay.set_alpha(alpha)

        # Do not modify the scene; just overlay on current frame
        screen.blit(overlay, (0, 0))
        pygame.display.flip()
        clock.tick(60)

        if t >= 1.0:
            break
