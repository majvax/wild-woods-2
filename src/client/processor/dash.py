import math
from typing import final, override

import esper
import pygame
from esper import Processor

from client.component import Dash, DirectionalAnimation
from client.view.player import PlayerView

_DIRECTION_VECTORS: dict[str, tuple[float, float]] = {
    "up": (0.0, -1.0),
    "down": (0.0, 1.0),
    "left": (-1.0, 0.0),
    "right": (1.0, 0.0),
}


@final
class DashProc(Processor):
    """Tap Shift to dash in the current movement (or facing) direction.

    Runs after ``InputProc`` so it can override the velocity it just set, and
    before ``MovementProc`` so the burst is integrated this frame. Uses
    rising-edge detection so holding Shift does not chain dashes.
    """

    def __init__(self) -> None:
        super().__init__()
        self._prev_shift = False

    @override
    def process(self, dt: float):
        player = PlayerView.get()
        try:
            dash = esper.component_for_entity(player.ent, Dash)
        except KeyError:
            return

        dash.cooldown_time = max(0.0, dash.cooldown_time - dt)

        keys = pygame.key.get_pressed()
        shift = bool(keys[pygame.K_LSHIFT] or keys[pygame.K_RSHIFT])

        if dash.active_time > 0:
            dash.active_time -= dt
            player.vel.vx = dash.dir_x * dash.speed
            player.vel.vy = dash.dir_y * dash.speed
        elif shift and not self._prev_shift and dash.cooldown_time <= 0:
            dir_x, dir_y = self._dash_direction(player)
            dash.dir_x = dir_x
            dash.dir_y = dir_y
            dash.active_time = dash.duration
            dash.cooldown_time = dash.cooldown
            player.vel.vx = dir_x * dash.speed
            player.vel.vy = dir_y * dash.speed

        self._prev_shift = shift

    def _dash_direction(self, player: PlayerView) -> tuple[float, float]:
        vx, vy = player.vel.vx, player.vel.vy
        if vx != 0 or vy != 0:
            length = math.hypot(vx, vy)
            return vx / length, vy / length

        try:
            facing = esper.component_for_entity(
                player.ent, DirectionalAnimation
            ).last_direction
        except KeyError:
            facing = "down"
        return _DIRECTION_VECTORS.get(facing, (0.0, 1.0))
