import math
import queue
import random
import threading
from collections import deque
from dataclasses import dataclass
from typing import Callable, final

import esper
import pygame

from client.component import AnimationState, PlayerTag, Position, Velocity
from client.core.engine import Engine


@dataclass
class Camera:
    smoothness: float
    x: float = 0.0
    y: float = 0.0
    initialized: bool = False

    def update(
        self, player_pos: Position | None, dt: float, width: int, height: int
    ) -> tuple[float, float]:
        if player_pos is not None:
            if not self.initialized:
                self.x = player_pos.x
                self.y = player_pos.y
                self.initialized = True
            lerp = min(1.0, self.smoothness * dt)
            self.x += (player_pos.x - self.x) * lerp
            self.y += (player_pos.y - self.y) * lerp
            return width / 2 - self.x, height / 2 - self.y
        return width / 2, height / 2


@dataclass
class Snowflake:
    x: float
    y: float
    speed: float
    drift: float
    size: int


@final
class SnowSystem:
    def __init__(self) -> None:
        self._snow_flakes: list[Snowflake] = []
        self._snow_surface = pygame.Surface((4, 4), flags=pygame.SRCALPHA)
        pygame.draw.circle(self._snow_surface, (255, 255, 255, 200), (2, 2), 2)

    def init_flakes(self, width: int, height: int) -> None:
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

    def update(
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

    def draw(self, screen: pygame.Surface, offset_x: float, offset_y: float) -> None:
        for flake in self._snow_flakes:
            screen_pos = (flake.x + offset_x, flake.y + offset_y)
            if flake.size == 4:
                screen.blit(self._snow_surface, screen_pos)
            elif flake.size == 3:
                screen.blit(self._snow_surface, screen_pos, area=(0, 0, 3, 3))
            else:
                screen.blit(self._snow_surface, screen_pos, area=(0, 0, 2, 2))


@final
class ChunkRenderer:
    def __init__(
        self,
        tile_size: int,
        chunk_size: int,
        seed: int,
        noise_scale: float,
        prewarm_margin: int,
        get_tile_color: Callable[[int, int, int, float], tuple[int, int, int]],
        get_tile_biome: Callable[[int, int, int, float], str] | None = None,
        color_for_biome: Callable[[str], tuple[int, int, int]] | None = None,
    ) -> None:
        self._tile_size = tile_size
        self._chunk_size = chunk_size
        self._seed = seed
        self._noise_scale = noise_scale
        self._prewarm_margin = prewarm_margin
        self._get_tile_color = get_tile_color
        self._get_tile_biome = get_tile_biome
        self._color_for_biome = color_for_biome
        self._cache: dict[tuple[int, int], pygame.Surface] = {}
        self._biome_cache: dict[tuple[int, int], list[list[str]]] = {}
        self._prewarm_queue: deque[tuple[int, int]] = deque()
        self._ready_queue: queue.Queue[
            tuple[int, int, list[list[tuple[int, int, int]]], list[list[str]] | None]
        ] = queue.Queue()
        self._worker_thread = threading.Thread(
            target=self._prewarm_worker, name="chunk-prewarm", daemon=True
        )
        self._worker_thread.start()

    @property
    def chunk_world_size(self) -> int:
        return self._chunk_size * self._tile_size

    @property
    def cache_size(self) -> int:
        return len(self._cache)

    def schedule_prewarm(
        self, width: int, height: int, center_chunk: tuple[int, int]
    ) -> None:
        chunks_x = math.ceil(width / self.chunk_world_size)
        chunks_y = math.ceil(height / self.chunk_world_size)
        half_x = chunks_x // 2 + self._prewarm_margin
        half_y = chunks_y // 2 + self._prewarm_margin
        cx, cy = center_chunk

        coords: list[tuple[int, int]] = []
        for dy in range(-half_y, half_y + 1):
            for dx in range(-half_x, half_x + 1):
                coords.append((cx + dx, cy + dy))
        coords.sort(key=lambda p: abs(p[0] - cx) + abs(p[1] - cy))
        self._prewarm_queue.extend(coords)

    def pump_ready(self, max_per_frame: int) -> None:
        for _ in range(max_per_frame):
            try:
                chunk_x, chunk_y, colors, biomes = self._ready_queue.get_nowait()
            except queue.Empty:
                break
            surface = pygame.Surface((self.chunk_world_size, self.chunk_world_size))
            for local_y, row in enumerate(colors):
                for local_x, color in enumerate(row):
                    pygame.draw.rect(
                        surface,
                        color,
                        (
                            local_x * self._tile_size,
                            local_y * self._tile_size,
                            self._tile_size,
                            self._tile_size,
                        ),
                    )
            self._cache[(chunk_x, chunk_y)] = surface
            if biomes is not None:
                self._biome_cache[(chunk_x, chunk_y)] = biomes

    def _prewarm_worker(self) -> None:
        while True:
            try:
                chunk_x, chunk_y = self._prewarm_queue.popleft()
            except IndexError:
                threading.Event().wait(0.01)
                continue
            if (chunk_x, chunk_y) in self._cache:
                continue
            colors, biomes = self._compute_chunk_colors(chunk_x, chunk_y)
            self._ready_queue.put((chunk_x, chunk_y, colors, biomes))

    def _compute_chunk_colors(
        self, chunk_x: int, chunk_y: int
    ) -> tuple[list[list[tuple[int, int, int]]], list[list[str]] | None]:
        colors: list[list[tuple[int, int, int]]] = []
        biomes: list[list[str]] | None = (
            [] if self._get_tile_biome and self._color_for_biome else None
        )
        start_tile_x = chunk_x * self._chunk_size
        start_tile_y = chunk_y * self._chunk_size
        for local_y in range(self._chunk_size):
            row: list[tuple[int, int, int]] = []
            biome_row: list[str] | None = [] if biomes is not None else None
            for local_x in range(self._chunk_size):
                tile_x = start_tile_x + local_x
                tile_y = start_tile_y + local_y
                if self._get_tile_biome and self._color_for_biome:
                    biome = self._get_tile_biome(
                        tile_x, tile_y, self._seed, self._noise_scale
                    )
                    color = self._color_for_biome(biome)
                    if biome_row is not None:
                        biome_row.append(biome)
                else:
                    color = self._get_tile_color(
                        tile_x, tile_y, self._seed, self._noise_scale
                    )
                row.append(color)
            colors.append(row)
            if biomes is not None and biome_row is not None:
                biomes.append(biome_row)
        return colors, biomes

    def _render_chunk(self, chunk_x: int, chunk_y: int) -> pygame.Surface:
        colors, biomes = self._compute_chunk_colors(chunk_x, chunk_y)
        surface = pygame.Surface((self.chunk_world_size, self.chunk_world_size))
        for local_y, row in enumerate(colors):
            for local_x, color in enumerate(row):
                pygame.draw.rect(
                    surface,
                    color,
                    (
                        local_x * self._tile_size,
                        local_y * self._tile_size,
                        self._tile_size,
                        self._tile_size,
                    ),
                )
        if biomes is not None:
            self._biome_cache[(chunk_x, chunk_y)] = biomes
        return surface

    def _get_chunk(self, chunk_x: int, chunk_y: int) -> pygame.Surface:
        key = (chunk_x, chunk_y)
        cached = self._cache.get(key)
        if cached is not None:
            return cached
        surface = self._render_chunk(chunk_x, chunk_y)
        self._cache[key] = surface
        return surface

    def get_biome_for_tile(self, tile_x: int, tile_y: int) -> str | None:
        if not self._get_tile_biome:
            return None
        chunk_x = math.floor(tile_x / self._chunk_size)
        chunk_y = math.floor(tile_y / self._chunk_size)
        cached = self._biome_cache.get((chunk_x, chunk_y))
        if cached is None:
            return self._get_tile_biome(tile_x, tile_y, self._seed, self._noise_scale)
        local_x = tile_x - chunk_x * self._chunk_size
        local_y = tile_y - chunk_y * self._chunk_size
        if 0 <= local_y < len(cached) and 0 <= local_x < len(cached[0]):
            return cached[local_y][local_x]
        return self._get_tile_biome(tile_x, tile_y, self._seed, self._noise_scale)

    def get_visible_chunk_range(
        self, width: int, height: int, offset_x: float, offset_y: float
    ) -> tuple[int, int, int, int]:
        world_left = -offset_x
        world_top = -offset_y
        world_right = world_left + width
        world_bottom = world_top + height
        start_chunk_x = math.floor(world_left / self.chunk_world_size)
        end_chunk_x = math.floor(world_right / self.chunk_world_size)
        start_chunk_y = math.floor(world_top / self.chunk_world_size)
        end_chunk_y = math.floor(world_bottom / self.chunk_world_size)
        return start_chunk_x, end_chunk_x, start_chunk_y, end_chunk_y

    def draw(
        self,
        screen: pygame.Surface,
        width: int,
        height: int,
        offset_x: float,
        offset_y: float,
    ) -> None:
        start_chunk_x, end_chunk_x, start_chunk_y, end_chunk_y = (
            self.get_visible_chunk_range(width, height, offset_x, offset_y)
        )
        for chunk_y in range(start_chunk_y, end_chunk_y + 1):
            for chunk_x in range(start_chunk_x, end_chunk_x + 1):
                surface = self._get_chunk(chunk_x, chunk_y)
                screen_x = chunk_x * self.chunk_world_size + offset_x
                screen_y = chunk_y * self.chunk_world_size + offset_y
                screen.blit(surface, (screen_x, screen_y))

    def draw_outlines(
        self,
        screen: pygame.Surface,
        width: int,
        height: int,
        offset_x: float,
        offset_y: float,
        color: pygame.Color,
    ) -> None:
        start_chunk_x, end_chunk_x, start_chunk_y, end_chunk_y = (
            self.get_visible_chunk_range(width, height, offset_x, offset_y)
        )
        for chunk_y in range(start_chunk_y, end_chunk_y + 1):
            for chunk_x in range(start_chunk_x, end_chunk_x + 1):
                screen_x = chunk_x * self.chunk_world_size + offset_x
                screen_y = chunk_y * self.chunk_world_size + offset_y
                pygame.draw.rect(
                    screen,
                    color,
                    (screen_x, screen_y, self.chunk_world_size, self.chunk_world_size),
                    width=1,
                )


@final
class DebugOverlay:
    def __init__(
        self,
        font: pygame.font.Font,
        engine: Engine,
        chunk_renderer: ChunkRenderer,
        tile_size: int,
        get_tile_biome: Callable[[int, int, int, float], str],
    ) -> None:
        self._font = font
        self._engine = engine
        self._chunk_renderer = chunk_renderer
        self._tile_size = tile_size
        self._get_tile_biome = get_tile_biome

    def draw(
        self,
        screen: pygame.Surface,
        dt: float,
        fps: int,
        num_ent: int,
        width: int,
        height: int,
        offset_x: float,
        offset_y: float,
        camera_x: float,
        camera_y: float,
        background_seed: int,
        noise_scale: float,
        player_pos: Position | None,
    ) -> None:
        if not self._engine.debug_enabled:
            return

        player_vel = None
        player_anim = None
        if player_pos is None:
            players = esper.get_components(PlayerTag, Position, Velocity)
            if players:
                _, (_, player_pos, player_vel) = players[0]
                try:
                    player_anim = esper.component_for_entity(
                        players[0][0], AnimationState
                    )
                except KeyError:
                    player_anim = None
        else:
            players = esper.get_components(PlayerTag, Position, Velocity)
            if players:
                _, (_, _, player_vel) = players[0]
                try:
                    player_anim = esper.component_for_entity(
                        players[0][0], AnimationState
                    )
                except KeyError:
                    player_anim = None

        start_chunk_x, end_chunk_x, start_chunk_y, end_chunk_y = (
            self._chunk_renderer.get_visible_chunk_range(
                width, height, offset_x, offset_y
            )
        )

        lines: list[str] = []
        lines.append(
            "DEBUG | toggle=RSHIFT | pause=RCTRL | step=RIGHT | "
            + f"paused={self._engine.debug_paused}"
        )
        lines.append(f"DT: {dt:.4f}s | FPS: {fps}")
        lines.append(f"Camera: ({camera_x:.1f}, {camera_y:.1f})")
        lines.append(f"Offset: ({offset_x:.1f}, {offset_y:.1f})")

        if player_pos is not None and player_vel is not None:
            tile_x = math.floor(player_pos.x / self._tile_size)
            tile_y = math.floor(player_pos.y / self._tile_size)
            chunk_x = math.floor(player_pos.x / self._chunk_renderer.chunk_world_size)
            chunk_y = math.floor(player_pos.y / self._chunk_renderer.chunk_world_size)
            biome = self._chunk_renderer.get_biome_for_tile(tile_x, tile_y)
            if biome is None:
                biome = self._get_tile_biome(
                    tile_x, tile_y, background_seed, noise_scale
                )
            lines.append(
                f"Player: ({player_pos.x:.1f}, {player_pos.y:.1f}) "
                + f"vel=({player_vel.vx:.1f}, {player_vel.vy:.1f})"
            )
            lines.append(f"Tile: ({tile_x}, {tile_y}) Chunk: ({chunk_x}, {chunk_y})")
            lines.append(f"Biome: {biome}")
        else:
            lines.append("Player: N/A")

        lines.append(
            f"Visible chunks: x[{start_chunk_x},{end_chunk_x}] "
            + f"y[{start_chunk_y},{end_chunk_y}]"
        )
        lines.append(
            f"Chunk size: {self._chunk_renderer.chunk_world_size}px "
            + f"cache={self._chunk_renderer.cache_size}"
        )
        if player_anim is not None:
            lines.append(f"Anim: {player_anim.current}")
        lines.append(f"Entities: {num_ent}")

        line_surfaces = [
            self._font.render(line, True, pygame.Color("black")) for line in lines
        ]
        max_w = max(s.get_width() for s in line_surfaces)
        total_h = sum(s.get_height() for s in line_surfaces) + (len(lines) - 1) * 2
        padding = 8
        box_w = max_w + padding * 2
        box_h = total_h + padding * 2
        x = width - box_w - 10
        y = 10

        bg = pygame.Surface((box_w, box_h), pygame.SRCALPHA)
        bg.fill((255, 255, 255, 200))
        screen.blit(bg, (x, y))

        draw_y = y + padding
        for surf in line_surfaces:
            screen.blit(surf, (x + padding, draw_y))
            draw_y += surf.get_height() + 2
