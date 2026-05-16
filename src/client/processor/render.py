import math
import random
from dataclasses import dataclass
from typing import final, override

import esper
import pygame
from esper import Processor

from client.component import Health, Inventory, ItemKind, PlayerTag, Position, Sprite
from client.core import TILE_SIZE, get_tile_color
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
        self._background_seed = random.randint(0, 1000)
        self._noise_scale = 20.0
        self._snow_flakes: list[Snowflake] = []
        self._camera_x = 0.0
        self._camera_y = 0.0
        self._camera_initialized = False
        self._camera_smoothness = 12.0
        self._chunk_size = 32
        self._chunk_cache: dict[tuple[int, int], pygame.Surface] = {}
        self._snow_surface = pygame.Surface((4, 4), flags=pygame.SRCALPHA)
        pygame.draw.circle(self._snow_surface, (255, 255, 255, 200), (2, 2), 2)
        self._init_snow(width, height)

    def _init_snow(self, width: int, height: int) -> None:
        target_count = max(120, int((width * height) / 8000))
        view_left = -width / 2
        view_top = -height / 2
        view_right = width / 2
        view_bottom = height / 2
        self._snow_flakes = [
            Snowflake(
                x=random.uniform(view_left, view_right),
                y=random.uniform(view_top, view_bottom),
                speed=random.uniform(20.0, 70.0),
                drift=random.uniform(-15.0, 15.0),
                size=random.choice([2, 3, 4]),
            )
            for _ in range(target_count)
        ]

    def _update_snow(
        self, dt: float, width: int, height: int, camera_x: float, camera_y: float
    ) -> None:
        view_left = camera_x - width / 2
        view_top = camera_y - height / 2
        view_right = camera_x + width / 2
        view_bottom = camera_y + height / 2
        for flake in self._snow_flakes:
            flake.y += flake.speed * dt
            flake.x += flake.drift * dt
            if flake.y > view_bottom + 5:
                flake.y = view_top - 5
                flake.x = random.uniform(view_left, view_right)
            if flake.x < view_left - 5:
                flake.x = view_right + 5
            elif flake.x > view_right + 5:
                flake.x = view_left - 5

    def _draw_snow(self, offset_x: float, offset_y: float) -> None:
        for flake in self._snow_flakes:
            screen_pos = (flake.x + offset_x, flake.y + offset_y)
            if flake.size == 4:
                self.screen.blit(self._snow_surface, screen_pos)
            elif flake.size == 3:
                self.screen.blit(self._snow_surface, screen_pos, area=(0, 0, 3, 3))
            else:
                self.screen.blit(self._snow_surface, screen_pos, area=(0, 0, 2, 2))

    def _render_chunk(self, chunk_x: int, chunk_y: int) -> pygame.Surface:
        surface = pygame.Surface(
            (self._chunk_size * TILE_SIZE, self._chunk_size * TILE_SIZE)
        )
        start_tile_x = chunk_x * self._chunk_size
        start_tile_y = chunk_y * self._chunk_size
        for local_y in range(self._chunk_size):
            for local_x in range(self._chunk_size):
                tile_x = start_tile_x + local_x
                tile_y = start_tile_y + local_y
                color = get_tile_color(
                    tile_x, tile_y, self._background_seed, self._noise_scale
                )
                pygame.draw.rect(
                    surface,
                    color,
                    (
                        local_x * TILE_SIZE,
                        local_y * TILE_SIZE,
                        TILE_SIZE,
                        TILE_SIZE,
                    ),
                )
        return surface

    def _get_chunk(self, chunk_x: int, chunk_y: int) -> pygame.Surface:
        key = (chunk_x, chunk_y)
        cached = self._chunk_cache.get(key)
        if cached is not None:
            return cached
        surface = self._render_chunk(chunk_x, chunk_y)
        self._chunk_cache[key] = surface
        return surface

    def _draw_background(
        self, width: int, height: int, offset_x: float, offset_y: float
    ) -> None:
        world_left = -offset_x
        world_top = -offset_y
        world_right = world_left + width
        world_bottom = world_top + height

        chunk_world_size = self._chunk_size * TILE_SIZE
        start_chunk_x = math.floor(world_left / chunk_world_size)
        end_chunk_x = math.floor(world_right / chunk_world_size)
        start_chunk_y = math.floor(world_top / chunk_world_size)
        end_chunk_y = math.floor(world_bottom / chunk_world_size)

        for chunk_y in range(start_chunk_y, end_chunk_y + 1):
            for chunk_x in range(start_chunk_x, end_chunk_x + 1):
                surface = self._get_chunk(chunk_x, chunk_y)
                screen_x = chunk_x * chunk_world_size + offset_x
                screen_y = chunk_y * chunk_world_size + offset_y
                self.screen.blit(surface, (screen_x, screen_y))

    @override
    def process(self, dt: float):
        width, height = self.screen.get_size()
        players = esper.get_components(PlayerTag, Position)
        if players:
            _, (_, player_pos) = players[0]
            if not self._camera_initialized:
                self._camera_x = player_pos.x
                self._camera_y = player_pos.y
                self._camera_initialized = True
            lerp = min(1.0, self._camera_smoothness * dt)
            self._camera_x += (player_pos.x - self._camera_x) * lerp
            self._camera_y += (player_pos.y - self._camera_y) * lerp
            offset_x = width / 2 - self._camera_x
            offset_y = height / 2 - self._camera_y
        else:
            offset_x = width / 2
            offset_y = height / 2

        self._draw_background(width, height, offset_x, offset_y)
        for _, (pos, sprite) in esper.get_components(Position, Sprite):
            self.screen.blit(
                sprite.surface,
                (
                    pos.x + offset_x - sprite.surface.get_width() / 2,
                    pos.y + offset_y - sprite.surface.get_height() / 2,
                ),
            )

        if self._engine.snow_enabled:
            if not self._engine.snow_paused:
                self._update_snow(dt, width, height, self._camera_x, self._camera_y)
            self._draw_snow(offset_x, offset_y)

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
