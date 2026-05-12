import random
from dataclasses import dataclass
from typing import final, override

import esper
import pygame
from esper import Processor

from client.component import Health, Inventory, ItemKind, PlayerTag, Position, Sprite
from client.core import generate_background_surface
from client.core.engine import Engine


@dataclass
class Snowflake:
    x: float
    y: float
    speed: float
    drift: float
    size: int


@final
class RenderProc(Processor):
    def __init__(self, screen: pygame.Surface, engine: Engine):
        super().__init__()
        self.screen = screen
        self._engine = engine
        self.font = pygame.font.SysFont("Arial", 18)
        width, height = self.screen.get_size()
        self._background = generate_background_surface(width, height)
        self._snow_flakes: list[Snowflake] = []
        self._snow_surface = pygame.Surface((4, 4), flags=pygame.SRCALPHA)
        pygame.draw.circle(self._snow_surface, (255, 255, 255, 200), (2, 2), 2)
        self._init_snow(width, height)

    def _init_snow(self, width: int, height: int) -> None:
        target_count = max(120, int((width * height) / 8000))
        self._snow_flakes = [
            Snowflake(
                x=random.uniform(0, width),
                y=random.uniform(0, height),
                speed=random.uniform(20.0, 70.0),
                drift=random.uniform(-15.0, 15.0),
                size=random.choice([2, 3, 4]),
            )
            for _ in range(target_count)
        ]

    def _update_snow(self, dt: float) -> None:
        width, height = self.screen.get_size()
        for flake in self._snow_flakes:
            flake.y += flake.speed * dt
            flake.x += flake.drift * dt
            if flake.y > height + 5:
                flake.y = -5
                flake.x = random.uniform(0, width)
            if flake.x < -5:
                flake.x = width + 5
            elif flake.x > width + 5:
                flake.x = -5

    def _draw_snow(self) -> None:
        for flake in self._snow_flakes:
            if flake.size == 4:
                self.screen.blit(self._snow_surface, (flake.x, flake.y))
            elif flake.size == 3:
                self.screen.blit(
                    self._snow_surface, (flake.x, flake.y), area=(0, 0, 3, 3)
                )
            else:
                self.screen.blit(
                    self._snow_surface, (flake.x, flake.y), area=(0, 0, 2, 2)
                )

    @override
    def process(self, dt: float):
        self.screen.blit(self._background)
        for _, (pos, sprite) in esper.get_components(Position, Sprite):
            self.screen.blit(
                sprite.surface,
                (
                    pos.x - sprite.surface.get_width() / 2,
                    pos.y - sprite.surface.get_height() / 2,
                ),
            )

        if self._engine.snow_enabled:
            if not self._engine.snow_paused:
                self._update_snow(dt)
            self._draw_snow()

        _, (_, php) = esper.get_components(PlayerTag, Health)[0]
        fps = int(1.0 / dt) if dt > 0 else 0
        num_ent = sum(1 for _ in esper.get_entities())
        fps_text = self.font.render(
            f"FPS: {max(0, min(fps, 999))} | {num_ent} ENTITIES | {php.current}PV",
            True,
            pygame.Color("black"),
        )
        self.screen.blit(fps_text, (10, 10))

        line_h = self.font.get_linesize()
        inv_start_y = 10 + line_h + 6
        for _, (inventory, _) in esper.get_components(Inventory, PlayerTag):
            header = self.font.render("Inventory", True, pygame.Color("black"))
            self.screen.blit(header, (10, inv_start_y))
            y = inv_start_y + line_h
            for kind in ItemKind:
                label = f"{kind.name.title()}: {inventory.count(kind)}"
                item_text = self.font.render(label, True, pygame.Color("black"))
                self.screen.blit(item_text, (10, y))
                y += line_h
            break
