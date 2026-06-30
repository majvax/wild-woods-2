from dataclasses import dataclass, field
from enum import IntEnum, auto


class WeaponKind(IntEnum):
    PISTOL = auto()
    SHOTGUN = auto()
    SMG = auto()
    SNIPER = auto()


@dataclass
class Weapon:
    cooldown_max: float
    bullet_speed: float
    damage: int

    cooldown_current: float = 0.0

    kind: WeaponKind = WeaponKind.PISTOL
    pellets: int = 1  # projectiles fired per shot (shotgun > 1)
    spread: float = 0.0  # total cone in radians (fan for pellets, jitter for one)
    pierce: bool = False  # projectiles pass through enemies (sniper)
    projectile_lifetime: float = 8.0  # seconds before despawn (limits range)


@dataclass
class Arsenal:
    """Weapons the player owns and which one is active.

    The active weapon instance is also the entity's ``Weapon`` component, so
    switching swaps that component to the stored instance (preserving each
    weapon's own upgrades and cooldown).
    """

    owned: dict[WeaponKind, Weapon] = field(default_factory=dict)
    active: WeaponKind = WeaponKind.PISTOL


@dataclass
class Piercing:
    """Marks a projectile that damages each enemy once and is not consumed."""

    hit: set[int] = field(default_factory=set)
