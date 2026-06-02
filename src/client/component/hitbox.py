from dataclasses import dataclass

from .physics import Position


@dataclass
class Hitbox:
    width: float
    height: float

    offset_x: float = 0.0
    offset_y: float = 0.0


def hitbox_bounds(pos: Position, hit: Hitbox) -> tuple[float, float, float, float]:
    cx = pos.x + hit.offset_x
    cy = pos.y + hit.offset_y
    return (
        cx - hit.width / 2,
        cy - hit.height / 2,
        cx + hit.width / 2,
        cy + hit.height / 2,
    )


def aabb_overlap(
    a: tuple[float, float, float, float],
    b: tuple[float, float, float, float],
) -> bool:
    return a[0] < b[2] and a[2] > b[0] and a[1] < b[3] and a[3] > b[1]
