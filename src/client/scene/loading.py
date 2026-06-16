from typing import final, override

import pygame

from client.core import (
    CHUNK_SIZE_TILES,
    TILE_SIZE,
    Engine,
)
from client.processor.render_helpers import ChunkRenderer
from client.scene.game import GameScene

from .scene import Scene


@final
class LoadingScene(Scene):
    def __init__(self, engine: Engine):
        super().__init__()
        self._engine = engine
        self._screen = engine.screen
        self._font = pygame.font.SysFont("Arial", 28)
        self._progress_font = pygame.font.SysFont("Arial", 18)
        self._chunks = ChunkRenderer(
            tile_size=TILE_SIZE,
            chunk_size=CHUNK_SIZE_TILES,
            prewarm_margin=20,
            max_cache=3000,
        )
        width, height = self._screen.get_size()
        self._target = self._chunks.schedule_prewarm(
            width, height, center_chunk=(0, 0), prefer_near=False
        )
        self._chunk_renderer = self._chunks

    @override
    def on_enter(self) -> None:
        pass

    @override
    def process(self, dt: float, events: list[pygame.event.Event]) -> bool:
        del events
        width, height = self._screen.get_size()
        self._screen.fill(pygame.Color(10, 10, 16))

        self._chunks.pump_ready(max_per_frame=200)
        completed = self._chunks.completed_count()
        target = max(1, self._target)
        progress = min(1.0, completed / target)

        label = self._font.render("Loading world...", True, pygame.Color("white"))
        pct = self._progress_font.render(
            f"{int(progress * 100)}%", True, pygame.Color(200, 200, 220)
        )
        stats = self._progress_font.render(
            f"completed {completed}/{target} | cached {self._chunks.cache_size}/{self._chunks.max_cache} | pending {self._chunks.scheduled_count()}",
            True,
            pygame.Color(160, 160, 180),
        )

        self._screen.blit(label, label.get_rect(center=(width // 2, height // 2 - 30)))
        self._screen.blit(pct, pct.get_rect(center=(width // 2, height // 2 + 10)))
        self._screen.blit(stats, stats.get_rect(center=(width // 2, height // 2 + 40)))

        bar_w = int(width * 0.4)
        bar_h = 10
        bar_x = width // 2 - bar_w // 2
        bar_y = height // 2 + 50
        pygame.draw.rect(
            self._screen, pygame.Color(40, 40, 60), (bar_x, bar_y, bar_w, bar_h)
        )
        pygame.draw.rect(
            self._screen,
            pygame.Color(120, 120, 220),
            (bar_x, bar_y, int(bar_w * progress), bar_h),
        )

        if completed >= target and self._chunks.scheduled_count() == 0:
            self._engine.sm.pop()
            self._engine.sm.push(GameScene, self._engine, self._chunk_renderer)
            return False

        return False
