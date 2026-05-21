# Model/AssetLoader.py
import pygame

class AssetLoader:
    cache = {}

    @classmethod
    def load(cls, path, size=None):
        """Load and cache images with optional scaling."""
        if path not in cls.cache:
            img = pygame.image.load(path).convert_alpha()
            if size:
                img = pygame.transform.scale(img, size)
            cls.cache[path] = img
        return cls.cache[path]

    @classmethod
    def font(cls, name="arial", size=32):
        key = f"{name}_{size}"
        if key not in cls.cache:
            cls.cache[key] = pygame.font.SysFont(name, size)
        return cls.cache[key]
