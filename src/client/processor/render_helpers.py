import math
import queue
import threading
from collections import OrderedDict, deque
from dataclasses import dataclass
from typing import final

import esper
import pygame

from client.component import AnimationState, PlayerTag, Position, Velocity
from client.core import get_bg_data
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


@final
class ChunkRenderer:
    def __init__(
        self,
        tile_size: int,
        chunk_size: int,
        seed: int,
        noise_scale: float,
        prewarm_margin: int,
        max_cache: int,
    ) -> None:
        self._tile_size = tile_size
        self._chunk_size = chunk_size
        self._seed = seed
        self._noise_scale = noise_scale
        self._prewarm_margin = prewarm_margin
        self._max_cache = max_cache
        self._cache: "OrderedDict[tuple[int, int], pygame.Surface]" = OrderedDict()
        self._scheduled: set[tuple[int, int]] = set()
        self._prewarm_queue: deque[tuple[int, int]] = deque()
        self._completed_count = 0
        self._ready_queue: queue.Queue[tuple[int, int]] = queue.Queue()
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

    @property
    def max_cache(self) -> int:
        return self._max_cache

    @property
    def seed(self) -> int:
        return self._seed

    @property
    def noise_scale(self) -> float:
        return self._noise_scale

    def scheduled_count(self) -> int:
        return len(self._scheduled)

    def completed_count(self) -> int:
        return self._completed_count

    def schedule_prewarm(
        self,
        width: int,
        height: int,
        center_chunk: tuple[int, int],
        *,
        prefer_near: bool = True,
    ) -> int:
        chunks_x = math.ceil(width / self.chunk_world_size)
        chunks_y = math.ceil(height / self.chunk_world_size)
        half_x = chunks_x // 2 + self._prewarm_margin
        half_y = chunks_y // 2 + self._prewarm_margin
        cx, cy = center_chunk

        coords: list[tuple[int, int]] = []
        for dy in range(-half_y, half_y + 1):
            for dx in range(-half_x, half_x + 1):
                coords.append((cx + dx, cy + dy))
        coords.sort(
            key=lambda p: abs(p[0] - cx) + abs(p[1] - cy), reverse=not prefer_near
        )

        capacity = self._max_cache - (len(self._cache) + len(self._scheduled))
        if capacity <= 0:
            return 0

        scheduled = 0
        for coord in coords:
            if coord in self._cache or coord in self._scheduled:
                continue
            self._scheduled.add(coord)
            self._prewarm_queue.append(coord)
            scheduled += 1
            if scheduled >= capacity:
                break
        return scheduled

    def pump_ready(self, max_per_frame: int) -> None:
        for _ in range(max_per_frame):
            try:
                chunk_x, chunk_y = self._ready_queue.get_nowait()
            except queue.Empty:
                break
            surface = self._render_chunk(chunk_x, chunk_y)
            self._insert_cache((chunk_x, chunk_y), surface)
            self._scheduled.discard((chunk_x, chunk_y))
            self._completed_count += 1

    def _prewarm_worker(self) -> None:
        while True:
            try:
                chunk_x, chunk_y = self._prewarm_queue.popleft()
            except IndexError:
                threading.Event().wait(0.01)
                continue
            if (chunk_x, chunk_y) in self._cache:
                self._scheduled.discard((chunk_x, chunk_y))
                continue
            self._ready_queue.put((chunk_x, chunk_y))

    def _render_chunk(self, chunk_x: int, chunk_y: int) -> pygame.Surface:
        img, w, h = get_bg_data()
        surface = pygame.Surface((self.chunk_world_size, self.chunk_world_size))
        start_x = (chunk_x * self.chunk_world_size) % w  # pos de depart du chunk
        start_y = (chunk_y * self.chunk_world_size) % h
        surface.blit(
            img, (-start_x, -start_y)
        )  # créer 4x l'image pour etre sur de remplir tous le chunk
        surface.blit(img, (-start_x + w, -start_y))
        surface.blit(img, (-start_x, -start_y + h))
        surface.blit(img, (-start_x + w, -start_y + h))
        return surface

    def _insert_cache(self, key: tuple[int, int], surface: pygame.Surface) -> None:
        if key in self._cache:
            self._cache.move_to_end(key)
            self._cache[key] = surface
        else:
            self._cache[key] = surface
        while len(self._cache) > self._max_cache:
            evicted_key, _ = self._cache.popitem(last=False)
            self._scheduled.discard(evicted_key)

    def _get_chunk(self, chunk_x: int, chunk_y: int) -> pygame.Surface:
        key = (chunk_x, chunk_y)
        cached = self._cache.get(key)
        if cached is not None:
            self._cache.move_to_end(key)
            return cached
        surface = self._render_chunk(chunk_x, chunk_y)
        self._insert_cache(key, surface)
        return surface

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
                screen_x = math.floor(chunk_x * self.chunk_world_size + offset_x)
                screen_y = math.floor(chunk_y * self.chunk_world_size + offset_y)
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
    ) -> None:
        self._font = font
        self._engine = engine
        self._chunk_renderer = chunk_renderer
        self._tile_size = tile_size

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
        _background_seed: int,
        _noise_scale: float,
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

            biome = "Plains (Image)"
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
