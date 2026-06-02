from typing import final, override

import esper

from client.component import Hitbox, Position, hitbox_bounds
from client.core.spatial import get_active_grid


@final
class SpatialGridProc(esper.Processor):
    def __init__(self, cell_size: float = 128.0):
        super().__init__()
        self._grid = get_active_grid()
        self._grid.cell_size = cell_size

    @override
    def process(self, dt: float) -> None:
        self._grid.clear()
        for ent, (pos, hit) in esper.get_components(Position, Hitbox):
            self._grid.insert_aabb(ent, *hitbox_bounds(pos, hit))
