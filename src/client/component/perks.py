from dataclasses import dataclass


@dataclass
class Perks:
    """Passive roguelite modifiers held by the player.

    Only effects that aren't already represented elsewhere live here; damage,
    cadence, max HP, move speed and dash cooldown are applied directly to the
    Arsenal/Health/Speed/Dash components by the shop.
    """

    crit_chance: float = 0.0  # probability [0..1] of a critical hit
    crit_mult: float = 2.0  # damage multiplier on a crit
    lifesteal: float = 0.0  # probability [0..1] to heal 1 on a kill
    pierce: bool = False  # all shots pierce (Perforation perk)
