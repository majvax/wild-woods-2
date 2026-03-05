from dataclasses import dataclass


@dataclass
class Position:
    x: float
    y: float


@dataclass
class Velocity:
    vx: float
    vy: float


@dataclass
class Orientation:
    angle: float


@dataclass
class Speed:
    value: float
