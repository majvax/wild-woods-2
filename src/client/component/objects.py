from dataclasses import dataclass, field
from enum import IntEnum, auto


class ObjectKind(IntEnum):
    ONION = auto()


@dataclass
class Objects:
    """Which ongoing-effect objects the player owns."""

    owned: set[ObjectKind] = field(default_factory=set)


@dataclass
class Aura:
    """Damaging aura around the player (the Onion object).

    Pre-attached to the player as ``active=False`` so the shop can enable it by
    mutating fields in place (no esper structural change from the shop world).
    """

    active: bool = False
    radius: float = 120.0
    damage_frac: float = 0.3  # fraction of the active weapon's damage per tick
    cooldown: float = 0.5  # seconds between ticks
    timer: float = 0.0  # countdown to the next tick
