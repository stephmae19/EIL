# Model/Timer.py
import pygame

class Timer:
    def __init__(self):
        self.start_ticks = pygame.time.get_ticks()  # Record start time
        self.paused = False
        self.pause_ticks = 0

    def update(self):
        """Update timer state (placeholder for pause logic)."""
        pass

    def get_time(self):
        """Return elapsed time in seconds."""
        if self.paused:
            return (self.pause_ticks - self.start_ticks) // 1000
        else:
            return (pygame.time.get_ticks() - self.start_ticks) // 1000

    def pause(self):
        """Pause the timer."""
        if not self.paused:
            self.paused = True
            self.pause_ticks = pygame.time.get_ticks()

    def resume(self):
        """Resume the timer."""
        if self.paused:
            # Adjust start time so elapsed time continues correctly
            paused_duration = pygame.time.get_ticks() - self.pause_ticks
            self.start_ticks += paused_duration
            self.paused = False
