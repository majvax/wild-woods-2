import pygame
from typing import Callable  # permet à une var de contenir une fonct

from .helper import lerp_color

_PADDING_X = 28     # marge intérieure gauche/droite (px)
_PADDING_Y = 12     # marge intérieure haut/bas (px)
_FONT_SIZE = 18     # taille du texte (pt)
_RADIUS = 10        # arrondi des coins (px)


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

        # Police et taille du bouton calculées à partir du texte + marges
        self._font = pygame.font.SysFont("Arial", _FONT_SIZE)
        text_w, text_h = self._font.size(text)
        self.rect = pygame.Rect(0, 0, text_w + _PADDING_X * 2, text_h + _PADDING_Y * 2)

        # t = 0 : état normal, t = 1 : état pleinement hover/pressé
        self._hover_t: float = 0.0
        self._press_t: float = 0.0

    def set_rect(self, cx: int, y: int) -> None:
        """Place le bouton centré horizontalement sur cx, bord supérieur à y."""
        self.rect.centerx = cx
        self.rect.y = y

    def update(self, dt: float, events: list[pygame.event.Event]) -> None:
        # Aucune interaction si le bouton est désactivé
        if not self.enabled:
            self._hover_t = 0.0
            self._press_t = 0.0
            return

        hovered = self.rect.collidepoint(pygame.mouse.get_pos())
        speed = 8.0

        # Transition smooth vers 1 si survolé, vers 0 sinon
        self._hover_t = max(0.0, min(1.0, self._hover_t + speed * dt * (1.0 if hovered else -1.0)))

        # L'effet de pression disparaît progressivement après le clic
        self._press_t = max(0.0, self._press_t - speed * 2 * dt)

        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and hovered:
                self._press_t = 1.0  # Déclenche l'animation de pression
                if self.on_click:
                    self.on_click()

    def draw(self, surface: pygame.Surface) -> None:
        c = self.colors

        # Rendu simplifié sans effets si désactivé
        if not self.enabled:
            pygame.draw.rect(surface, c["bg_disabled"], self.rect, border_radius=_RADIUS)
            pygame.draw.rect(surface, c["border_disabled"], self.rect, width=2, border_radius=_RADIUS)
            label = self._font.render(self.text, True, c["text_disabled"])
            surface.blit(label, label.get_rect(center=self.rect.center))
            return

        # Interpolation des couleurs selon l'état hover puis press
        bg     = lerp_color(lerp_color(c["bg"], c["bg_hover"], self._hover_t), c["bg_press"], self._press_t)
        border = lerp_color(c["border"], c["border_hover"], self._hover_t)
        text_c = lerp_color(c["text"],   c["text_hover"],   self._hover_t)

        pygame.draw.rect(surface, bg, self.rect, border_radius=_RADIUS)
        pygame.draw.rect(surface, border, self.rect, width=2, border_radius=_RADIUS)

        # Rendu du texte centré dans le bouton
        label = self._font.render(self.text, True, text_c)
        surface.blit(label, label.get_rect(center=self.rect.center))


NEON_PURPLE: dict[str, pygame.Color] = {
    "bg":              pygame.Color(22,  18,  42),   # fond normal
    "bg_hover":        pygame.Color(30,  24,  64),   # fond au survol
    "bg_press":        pygame.Color(18,  15,  32),   # fond au clic
    "border":          pygame.Color(106, 79, 207),   # bordure normale
    "border_hover":    pygame.Color(160, 125, 255),  # bordure au survol
    "text":            pygame.Color(200, 184, 255),  # texte normal
    "text_hover":      pygame.Color(255, 255, 255),  # texte au survol
    "glow":            pygame.Color(124,  85, 255),  # couleur du halo néon
    "bg_disabled":     pygame.Color(17,  17,  24),   # fond si désactivé
    "border_disabled": pygame.Color(51,  51,  51),   # bordure si désactivé
    "text_disabled":   pygame.Color(85,  85,  85),   # texte si désactivé
}