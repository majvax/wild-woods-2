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
    """Weapons the player owns, the active one, and global upgrade multipliers.

    The player keeps a single ``Weapon`` component; switching mutates it in
    place from the active kind's template combined with these multipliers, so
    damage/cadence upgrades are global (apply to every weapon).
    """

    owned: set[WeaponKind] = field(default_factory=lambda: {WeaponKind.PISTOL})
    active: WeaponKind = WeaponKind.PISTOL
    damage_mult: float = 1.0
    cooldown_mult: float = 1.0


@dataclass
class Piercing:
    """Marks a projectile that damages each enemy once and is not consumed."""

    hit: set[int] = field(default_factory=set)
