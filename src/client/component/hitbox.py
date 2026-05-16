from dataclasses import dataclass


@dataclass
class Hitbox:
    width: float
    height: float

    offset_x: float = 0.0
    offset_y: float = 0.0
