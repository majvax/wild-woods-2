# lerp et _get_font

import pygame


def lerp_color(a: pygame.Color, b: pygame.Color, t: float) -> pygame.Color:
    t = max(0.0, min(1.0, t))
    return pygame.Color(
        int(a.r + (b.r - a.r) * t),
        int(a.g + (b.g - a.g) * t),
        int(a.b + (b.b - a.b) * t),
    )
