from typing import final, override

import esper
from esper import Processor

from client.component import Position, Velocity


@final
class MovementProc(Processor):
    @override
    def process(self, dt: float):
        for _, (vel, pos) in esper.get_components(Velocity, Position):
            pos.x += vel.vx * dt
            pos.y += vel.vy * dt
