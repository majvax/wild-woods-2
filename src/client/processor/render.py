from typing import final, override

import esper
import pygame
from esper import Processor

from client.component import Position, Sprite
from client.core import generate_background_surface
from client.component.damage import Health
from client.component.tags import PlayerTag


@final
class RenderProc(Processor):
    def __init__(self, screen: pygame.Surface):
        super().__init__()
        self.screen = screen
        self.font = pygame.font.SysFont("Arial", 18)
        width, height = self.screen.get_size()
        self._background = generate_background_surface(width, height)

    @override
    def process(self, dt: float):
        self.screen.fill("white")
        self.screen.blit(self._background)
        for _, (pos, sprite) in esper.get_components(Position, Sprite):
            self.screen.blit(
                sprite.surface,
                (
                    pos.x - sprite.surface.get_width() / 2,
                    pos.y - sprite.surface.get_height() / 2,
                ),
            )
        _, (_, php) = esper.get_components(PlayerTag, Health)[0]
        fps = int(1.0 / dt) if dt > 0 else 0
        num_ent = sum(1 for _ in esper.get_entities())
        fps_text = self.font.render(
            f"FPS: {max(0, min(fps, 999))} | {num_ent} ENTITIES | {php.current}PV",
            True,
            pygame.Color("black"),
        )
        self.screen.blit(fps_text, (10, 10))
