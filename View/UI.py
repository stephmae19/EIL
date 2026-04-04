# View/UI.py
import pygame

class Button:
    def __init__(self, text, position, size=(200, 50), font_size=32,
                 bg_color=(50, 50, 50), text_color=(255, 255, 255), hover_color=(100, 100, 100)):
        """
        A simple clickable button.
        :param text: Button label
        :param position: (x, y) tuple for center position
        :param size: (width, height) of the button
        :param font_size: Font size for text
        :param bg_color: Default background color
        :param text_color: Text color
        :param hover_color: Background color when hovered
        """
        self.text = text
        self.position = position
        self.size = size
        self.font_size = font_size
        self.bg_color = bg_color
        self.text_color = text_color
        self.hover_color = hover_color
        self.rect = pygame.Rect(0, 0, *size)
        self.rect.center = position
        self.font = pygame.font.SysFont("arial", font_size)

    def draw(self, surface):
        """Draw the button on the given surface."""
        mouse_pos = pygame.mouse.get_pos()
        color = self.hover_color if self.rect.collidepoint(mouse_pos) else self.bg_color
        pygame.draw.rect(surface, color, self.rect, border_radius=8)

        text_surface = self.font.render(self.text, True, self.text_color)
        text_rect = text_surface.get_rect(center=self.rect.center)
        surface.blit(text_surface, text_rect)

    def is_clicked(self, event):
        """Return True if the button is clicked."""
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos):
                return True
        return False


class Label:
    def __init__(self, text, position, font_size=28, color=(255, 255, 255)):
        """
        A simple text label.
        :param text: Label text
        :param position: (x, y) tuple for top-left position
        :param font_size: Font size
        :param color: Text color
        """
        self.text = text
        self.position = position
        self.font = pygame.font.SysFont("arial", font_size)
        self.color = color

    def draw(self, surface):
        """Draw the label on the given surface."""
        text_surface = self.font.render(self.text, True, self.color)
        surface.blit(text_surface, self.position)


class HUD:
    def __init__(self, player, timer, score):
        """
        Heads-up display for gameplay.
        :param player: Player object
        :param timer: Timer object
        :param score: Score tracker
        """
        self.player = player
        self.timer = timer
        self.score = score
        self.font = pygame.font.SysFont("arial", 24)

    def draw(self, surface):
        """Draw HUD elements (health, score, timer)."""
        # Player health
        health_text = f"Health: {self.player.health}"
        health_surface = self.font.render(health_text, True, (255, 0, 0))
        surface.blit(health_surface, (20, 20))

        # Score
        score_text = f"Score: {self.score.value}"
        score_surface = self.font.render(score_text, True, (255, 255, 0))
        surface.blit(score_surface, (20, 50))

        # Timer
        timer_text = f"Time: {self.timer.get_time_string()}"
        timer_surface = self.font.render(timer_text, True, (255, 255, 255))
        surface.blit(timer_surface, (20, 80))
