import math
from dataclasses import dataclass
from typing import final

import esper
import pygame

from client.component import AnimationState, Position
from client.core.engine import Engine
from client.view.player import PlayerView


@dataclass
class Camera:
    smoothness: float
    x: float = 0.0
    y: float = 0.0
    initialized: bool = False

    def update(
        self, player_pos: Position, dt: float, width: int, height: int
    ) -> tuple[float, float]:
        if not self.initialized:
            self.x = player_pos.x
            self.y = player_pos.y
            self.initialized = True
        lerp = min(1.0, self.smoothness * dt)
        self.x += (player_pos.x - self.x) * lerp
        self.y += (player_pos.y - self.y) * lerp
        return width / 2 - self.x, height / 2 - self.y


def draw_tiled_background(
    screen: pygame.Surface,
    background: pygame.Surface,
    offset_x: float,
    offset_y: float,
) -> None:
    """Tile the background image across the screen, following the camera.

    World position P maps to screen position P + offset, so we tile in world
    space starting from the first image origin left/above the visible area.
    """
    bg_w = background.get_width()
    bg_h = background.get_height()
    screen_w, screen_h = screen.get_size()

    world_left = -offset_x
    world_top = -offset_y
    start_x = math.floor(world_left / bg_w) * bg_w
    start_y = math.floor(world_top / bg_h) * bg_h

    y = start_y
    while y < world_top + screen_h:
        x = start_x
        while x < world_left + screen_w:
            screen.blit(background, (x + offset_x, y + offset_y))
            x += bg_w
        y += bg_h


@final
class DebugOverlay:
    def __init__(
        self,
        font: pygame.font.Font,
        engine: Engine,
        tile_size: int,
    ) -> None:
        self._font = font
        self._engine = engine
        self._tile_size = tile_size

    def draw(
        self,
        screen: pygame.Surface,
        dt: float,
        fps: int,
        num_ent: int,
        width: int,
        offset_x: float,
        offset_y: float,
        camera_x: float,
        camera_y: float,
    ) -> None:
        if not self._engine.debug_enabled:
            return

        player = PlayerView.get()
        try:
            player_anim = esper.component_for_entity(player.ent, AnimationState)
        except KeyError:
            player_anim = None

        tile_x = math.floor(player.pos.x / self._tile_size)
        tile_y = math.floor(player.pos.y / self._tile_size)

        lines: list[str] = []
        lines.append(
            "DEBUG | toggle=RSHIFT | pause=RCTRL | step=RIGHT | "
            + f"paused={self._engine.debug_paused}"
        )
        lines.append(f"DT: {dt:.4f}s | FPS: {fps}")
        lines.append(f"Camera: ({camera_x:.1f}, {camera_y:.1f})")
        lines.append(f"Offset: ({offset_x:.1f}, {offset_y:.1f})")
        lines.append(
            f"Player: ({player.pos.x:.1f}, {player.pos.y:.1f}) "
            + f"vel=({player.vel.vx:.1f}, {player.vel.vy:.1f})"
        )
        lines.append(f"Tile: ({tile_x}, {tile_y})")
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
