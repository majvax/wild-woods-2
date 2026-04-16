import pygame
from typing import Callable

from .helper import lerp_color

_PADDING_X = 28
_PADDING_Y = 12
_FONT_SIZE = 18
_RADIUS = 10
_GLOW_STEPS = 5
_GLOW_SPREAD = 3
_GLOW_ALPHA_MAX = 40



def _draw_glow(surface: pygame.Surface, rect: pygame.Rect, color: pygame.Color, t: float) -> None:
    if t <= 0:
        return
    for i in range(_GLOW_STEPS, 0, -1):
        spread = i * _GLOW_SPREAD
        alpha = int(_GLOW_ALPHA_MAX * t * (i / _GLOW_STEPS))
        glow_rect = rect.inflate(spread * 2, spread * 2)
        glow_surf = pygame.Surface(glow_rect.size, pygame.SRCALPHA)
        pygame.draw.rect(
            glow_surf,
            (*color[:3], alpha),
            glow_surf.get_rect(),
            border_radius=_RADIUS + spread,
        )
        surface.blit(glow_surf, glow_rect.topleft)


class Button:
    def __init__(
        self,
        text: str,
        colors: dict[str, pygame.Color],
        on_click: Callable | None = None,
        enabled: bool = True,
    ):
        self.text = text
        self.colors = colors
        self.on_click = on_click
        self.enabled = enabled

        self._font = pygame.font.SysFont("Arial", _FONT_SIZE)
        text_w, text_h = self._font.size(text)
        self.rect = pygame.Rect(0, 0, text_w + _PADDING_X * 2, text_h + _PADDING_Y * 2)

        self._hover_t: float = 0.0
        self._press_t: float = 0.0

    def set_rect(self, cx: int, y: int) -> None:
        self.rect.centerx = cx
        self.rect.y = y

    def update(self, dt: float, events: list[pygame.event.Event]) -> None:
        if not self.enabled:
            self._hover_t = 0.0
            self._press_t = 0.0
            return

        hovered = self.rect.collidepoint(pygame.mouse.get_pos())
        speed = 8.0
        self._hover_t = max(0.0, min(1.0, self._hover_t + speed * dt * (1.0 if hovered else -1.0)))
        self._press_t = max(0.0, self._press_t - speed * 2 * dt)

        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and hovered:
                self._press_t = 1.0
                if self.on_click:
                    self.on_click()

    def draw(self, surface: pygame.Surface) -> None:
        c = self.colors

        if not self.enabled:
            pygame.draw.rect(surface, c["bg_disabled"], self.rect, border_radius=_RADIUS)
            pygame.draw.rect(surface, c["border_disabled"], self.rect, width=2, border_radius=_RADIUS)
            label = self._font.render(self.text, True, c["text_disabled"])
            surface.blit(label, label.get_rect(center=self.rect.center))
            return

        _draw_glow(surface, self.rect, c["glow"], self._hover_t)

        bg     = lerp_color(lerp_color(c["bg"],     c["bg_hover"],   self._hover_t), c["bg_press"],   self._press_t)
        border = lerp_color(c["border"], c["border_hover"], self._hover_t)
        text_c = lerp_color(c["text"],   c["text_hover"],   self._hover_t)

        pygame.draw.rect(surface, bg, self.rect, border_radius=_RADIUS)
        pygame.draw.rect(surface, border, self.rect, width=2, border_radius=_RADIUS)
        surface.blit(self._font.render(self.text, True, text_c), self._font.render(self.text, True, text_c).get_rect(center=self.rect.center))

NEON_PURPLE = {
"bg":              pygame.Color(22,  18,  42),
"bg_hover":        pygame.Color(30,  24,  64),
"bg_press":        pygame.Color(18,  15,  32),
"border":          pygame.Color(106, 79, 207),
"border_hover":    pygame.Color(160, 125, 255),
"text":            pygame.Color(200, 184, 255),
"text_hover":      pygame.Color(255, 255, 255),
"glow":            pygame.Color(124,  85, 255),
"bg_disabled":     pygame.Color(17,  17,  24),
"border_disabled": pygame.Color(51,  51,  51),
"text_disabled":   pygame.Color(85,  85,  85),
}