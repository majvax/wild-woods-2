import random

from client.component import Health, Perks


def roll_damage(base: float, perks: Perks | None) -> float:
    """Return ``base`` damage, multiplied by crit on a successful crit roll."""
    if perks is not None and random.random() < perks.crit_chance:
        return base * perks.crit_mult
    return base


def apply_lifesteal(perks: Perks | None, hp: Health) -> None:
    """On a kill, roll lifesteal to heal the player 1 HP (clamped to max)."""
    if perks is not None and perks.lifesteal > 0 and random.random() < perks.lifesteal:
        hp.current = min(hp.current + 1, hp.max)
