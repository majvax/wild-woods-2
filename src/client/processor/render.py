import random
from typing import final, override

import esper
import pygame
from esper import Processor

from client.component import Health, Inventory, ItemKind, PlayerTag, Position, Sprite
from client.core import (
    CHUNK_SIZE_TILES,
    TILE_SIZE,
    color_for_biome,
    get_tile_biome,
    get_tile_color,
)
from client.core.engine import Engine
from client.processor.render_helpers import (
    Camera,
    ChunkRenderer,
    DebugOverlay,
    SnowSystem,
)


@final
class RenderProc(Processor):
    def __init__(self, screen: pygame.Surface, engine: Engine):
        super().__init__()
        self.screen = screen
        self._engine = engine
        self.font = pygame.font.SysFont("Arial", 18)
        width, height = self.screen.get_size()
        self._background_seed = random.randint(0, 1000)
        self._noise_scale = 60.0
        self._camera = Camera(smoothness=12.0)
        self._snow = SnowSystem()
        self._snow.init_flakes(width, height)
        self._last_prewarm_center = (0, 0)
        self._chunks = ChunkRenderer(
            tile_size=TILE_SIZE,
            chunk_size=CHUNK_SIZE_TILES,
            seed=self._background_seed,
            noise_scale=self._noise_scale,
            prewarm_margin=5,
            get_tile_color=get_tile_color,
            get_tile_biome=get_tile_biome,
            color_for_biome=color_for_biome,
        )
        self._chunks.schedule_prewarm(
            width, height, center_chunk=self._last_prewarm_center
        )
        self._debug_overlay = DebugOverlay(
            font=self.font,
            engine=self._engine,
            chunk_renderer=self._chunks,
            tile_size=TILE_SIZE,
            get_tile_biome=get_tile_biome,
        )

    @override
    def process(self, dt: float):
        width, height = self.screen.get_size()
        players = esper.get_components(PlayerTag, Position)
        player_pos = players[0][1][1] if players else None

        offset_x, offset_y = self._camera.update(player_pos, dt, width, height)

        if player_pos is not None:
            current_chunk = (
                int(player_pos.x // (CHUNK_SIZE_TILES * TILE_SIZE)),
                int(player_pos.y // (CHUNK_SIZE_TILES * TILE_SIZE)),
            )
            if current_chunk != self._last_prewarm_center:
                self._last_prewarm_center = current_chunk
                self._chunks.schedule_prewarm(width, height, current_chunk)

        self._chunks.pump_ready(max_per_frame=12)
        self._chunks.draw(self.screen, width, height, offset_x, offset_y)
        if self._engine.debug_enabled:
            self._chunks.draw_outlines(
                self.screen,
                width,
                height,
                offset_x,
                offset_y,
                color=pygame.Color(255, 0, 255),
            )
        self._update_snow_state(player_pos)
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
                self._snow.update(dt, width, height, self._camera.x, self._camera.y)
            self._snow.draw(self.screen, offset_x, offset_y)

        _, (_, php) = esper.get_components(PlayerTag, Health)[0]
        fps = int(1.0 / dt) if dt > 0 else 0
        num_ent = sum(1 for _ in esper.get_entities())
        fps_text = self.font.render(
            f"FPS: {max(0, min(fps, 999))} | {num_ent} ENTITIES | {php.current}PV",
            True,
            pygame.Color("black"),
        )
        self.screen.blit(fps_text, (10, 10))

        self._debug_overlay.draw(
            self.screen,
            dt,
            fps,
            num_ent,
            width,
            height,
            offset_x,
            offset_y,
            self._camera.x,
            self._camera.y,
            self._background_seed,
            self._noise_scale,
            player_pos,
        )

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

    def _update_snow_state(self, player_pos: Position | None) -> None:
        if player_pos is None:
            self._engine.set_snow_enabled(False)
            return

        tile_x = int(player_pos.x // TILE_SIZE)
        tile_y = int(player_pos.y // TILE_SIZE)
        biome = self._chunks.get_biome_for_tile(tile_x, tile_y)
        if biome is None:
            biome = get_tile_biome(
                tile_x, tile_y, self._background_seed, self._noise_scale
            )
        self._engine.set_snow_enabled(biome in {"snow", "mountain"})
        if self._engine.snow_enabled:
            self._engine.set_snow_paused(False)
