from typing import final, override

import esper
import pygame

from client.component import Hitbox, Position


@final
class HitboxProc(esper.Processor):
    def __init__(self, screen: pygame.Surface):
        super().__init__()
        self._screen = screen

    @override
    def process(self, dt: float):
        for _, (pos, hit) in esper.get_components(Position, Hitbox):
            rect_x = pos.x + hit.offset_x - hit.width / 2
            rect_y = pos.y + hit.offset_y - hit.height / 2

            debug_rect = pygame.Rect(rect_x, rect_y, hit.width, hit.height)
            pygame.draw.rect(self._screen, (255, 0, 0), debug_rect, 1)
