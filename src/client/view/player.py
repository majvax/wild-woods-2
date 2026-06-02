from dataclasses import dataclass
from typing import Self

import esper

from client.component import (
    Health,
    Hitbox,
    Inventory,
    Invincibility,
    PlayerTag,
    Position,
    Speed,
    Velocity,
    Weapon,
)
from client.utils.ecs import get_components


@dataclass
class PlayerView:
    ent: int
    pos: Position
    vel: Velocity
    speed: Speed
    hp: Health
    inv: Inventory
    hitbox: Hitbox
    invincibility: Invincibility

    @classmethod
    def get(cls) -> Self | None:
        query = get_components(
            PlayerTag,
            Position,
            Velocity,
            Speed,
            Health,
            Inventory,
            Hitbox,
            Invincibility,
        )
        if not query:
            return None
        ent, data = query[0]
        return cls(ent, *data[1:])

    def weapon(self) -> Weapon | None:
        try:
            return esper.component_for_entity(self.ent, Weapon)
        except KeyError:
            return None
