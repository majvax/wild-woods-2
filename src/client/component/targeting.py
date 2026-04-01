from dataclasses import dataclass


@dataclass
class Targeting:
    range: float
    atk_range: float
    distance: float = float("inf")
    target: int | None = None
