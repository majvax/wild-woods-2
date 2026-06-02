import random
from typing import final, override
import math
import esper
import pygame
from esper import Processor

from client.component import (
    CampfireTag,
    Health,
    Hitbox,
    ItemKind,
    Position,
    Sprite,
)
from client.core import (
    CHUNK_SIZE_TILES,
    TILE_SIZE,
)
from client.core.engine import Engine
from client.factory.item import ITEM_SPRITE_PATHS
from client.processor.render_helpers import (
    Camera,
    ChunkRenderer,
    DebugOverlay,
    SnowSystem,
)
from client.view.player import PlayerView

_INVENTORY_ICON_SIZE = 18


@final
class RenderProc(Processor):
    def __init__(
        self,
        screen: pygame.Surface,
        engine: Engine,
        *,
        chunk_renderer: ChunkRenderer | None = None,
    ):
        super().__init__()
        self.screen = screen
        self._engine = engine
        self.font = pygame.font.SysFont("Arial", 18)
        self._item_icons: dict[ItemKind, pygame.Surface] = {
            kind: pygame.transform.scale(
                pygame.image.load(path).convert_alpha(),
                (_INVENTORY_ICON_SIZE, _INVENTORY_ICON_SIZE),
            )
            for kind, path in ITEM_SPRITE_PATHS.items()
        }
        width, height = self.screen.get_size()
        self._background_seed = random.randint(0, 1000)
        self._noise_scale = 60.0
        self._camera = Camera(smoothness=12.0)
        self._snow = SnowSystem()
        self._snow.init_flakes(width, height)
        self._last_prewarm_center = (0, 0)
        if chunk_renderer is None:
            self._chunks = ChunkRenderer(
                tile_size=TILE_SIZE,
                chunk_size=CHUNK_SIZE_TILES,
                seed=self._background_seed,
                noise_scale=self._noise_scale,
                prewarm_margin=5,
                max_cache=4000,
            )
            self._chunks.schedule_prewarm(
                width, height, center_chunk=self._last_prewarm_center
            )
        else:
            self._chunks = chunk_renderer
            self._background_seed = chunk_renderer.seed
            self._noise_scale = chunk_renderer.noise_scale

        self._debug_overlay = DebugOverlay(
            font=self.font,
            engine=self._engine,
            chunk_renderer=self._chunks,
            tile_size=TILE_SIZE,
        )

    @override
    def process(self, dt: float):
        width, height = self.screen.get_size()
        player = PlayerView.get()
        player_pos = player.pos if player is not None else None

        offset_x, offset_y = self._camera.update(player_pos, dt, width, height)

        if player_pos is not None:
            current_chunk = (
                math.floor(player_pos.x / (CHUNK_SIZE_TILES * TILE_SIZE)),
                math.floor(player_pos.y / (CHUNK_SIZE_TILES * TILE_SIZE)),
            )
            if current_chunk != self._last_prewarm_center:
                self._last_prewarm_center = current_chunk
                self._chunks.schedule_prewarm(
                    width, height, current_chunk, prefer_near=True
                )

        self._chunks.pump_ready(max_per_frame=5)
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

        for _, (pos, sprite) in esper.get_components(Position, Sprite):
            self.screen.blit(
                sprite.surface,
                (
                    pos.x + offset_x - sprite.surface.get_width() / 2,
                    pos.y + offset_y - sprite.surface.get_height() / 2,
                ),
            )

        if self._engine.debug_enabled:
            for _, (_, pos, hitbox) in esper.get_components(
                CampfireTag, Position, Hitbox
            ):
                hx = int(pos.x + hitbox.offset_x + offset_x - hitbox.width / 2)
                hy = int(pos.y + hitbox.offset_y + offset_y - hitbox.height / 2)
                hitbox_surf = pygame.Surface(
                    (int(hitbox.width), int(hitbox.height)), pygame.SRCALPHA
                )
                hitbox_surf.fill((0, 255, 0, 120))
                self.screen.blit(hitbox_surf, (hx, hy))

        fps = int(1.0 / dt) if dt > 0 else 0
        num_ent = sum(1 for _ in esper.get_entities())
        hp_text = f" | {player.hp.current}PV" if player is not None else ""
        fps_text = self.font.render(
            f"FPS: {max(0, min(fps, 999))} | {num_ent} ENTITIES{hp_text}",
            True,
            pygame.Color("black"),
        )
        self.screen.blit(fps_text, (10, 10))

        campfires = esper.get_components(CampfireTag, Health)
        if campfires:
            _, (_, c_health) = campfires[0]
            bar_w = 300
            bar_h = 20
            bar_x = (width - bar_w) // 2
            bar_y = 10
            ratio = max(0.0, c_health.current / c_health.max)
            pygame.draw.rect(self.screen, (60, 0, 0), (bar_x, bar_y, bar_w, bar_h))
            pygame.draw.rect(
                self.screen, (0, 200, 0), (bar_x, bar_y, int(bar_w * ratio), bar_h)
            )
            label = self.font.render(
                f"Feu de camp : {int(c_health.current)}/{int(c_health.max)}",
                True,
                pygame.Color("white"),
            )
            self.screen.blit(
                label,
                (
                    bar_x + (bar_w - label.get_width()) // 2,
                    bar_y + (bar_h - label.get_height()) // 2,
                ),
            )

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

        if player is not None:
            line_h = self.font.get_linesize()
            inv_start_y = 10 + line_h + 6
            header = self.font.render("Inventory", True, pygame.Color("black"))
            self.screen.blit(header, (10, inv_start_y))
            y = inv_start_y + line_h
            for kind in ItemKind:
                icon = self._item_icons.get(kind)
                text_x = 10
                if icon is not None:
                    self.screen.blit(icon, (10, y + (line_h - icon.get_height()) // 2))
                    text_x = 10 + icon.get_width() + 4
                item_label = f"{kind.name.title()}: {player.inv.count(kind)}"
                item_text = self.font.render(item_label, True, pygame.Color("black"))
                self.screen.blit(item_text, (text_x, y))
                y += line_h
