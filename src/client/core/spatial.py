from dataclasses import dataclass, field


@dataclass
class SpatialGrid:
    cell_size: float
    cells: dict[tuple[int, int], list[int]] = field(default_factory=dict)

    def clear(self) -> None:
        self.cells.clear()

    def _cell_coords(self, x: float, y: float) -> tuple[int, int]:
        return (int(x // self.cell_size), int(y // self.cell_size))

    def insert(self, entity_id: int, x: float, y: float) -> None:
        cell = self._cell_coords(x, y)
        self.cells.setdefault(cell, []).append(entity_id)

    def insert_aabb(
        self, entity_id: int, left: float, top: float, right: float, bottom: float
    ) -> None:
        min_cx = int(left // self.cell_size)
        max_cx = int(right // self.cell_size)
        min_cy = int(top // self.cell_size)
        max_cy = int(bottom // self.cell_size)
        for cy in range(min_cy, max_cy + 1):
            for cx in range(min_cx, max_cx + 1):
                self.cells.setdefault((cx, cy), []).append(entity_id)

    def query_aabb(
        self, left: float, top: float, right: float, bottom: float
    ) -> list[int]:
        min_cx = int(left // self.cell_size)
        max_cx = int(right // self.cell_size)
        min_cy = int(top // self.cell_size)
        max_cy = int(bottom // self.cell_size)

        results: list[int] = []
        for cy in range(min_cy, max_cy + 1):
            for cx in range(min_cx, max_cx + 1):
                results.extend(self.cells.get((cx, cy), []))
        return results


_ACTIVE_GRID = SpatialGrid(cell_size=128.0)


def get_active_grid() -> SpatialGrid:
    return _ACTIVE_GRID
