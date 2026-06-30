from dataclasses import dataclass
from typing import Self

import esper

from client.component import (
    Arsenal,
    Aura,
    Health,
    Hitbox,
    Inventory,
    Invincibility,
    Objects,
    Perks,
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
    def get(cls) -> Self:
        """Return the player view.

        The player entity exists for the entire lifetime of the game world, so
        this never returns ``None``. If it is somehow missing, that is a bug and
        we fail fast rather than silently skipping logic.
        """
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
            raise RuntimeError("PlayerView.get() called but no player entity exists")
        ent, data = query[0]
        return cls(ent, *data[1:])

    def weapon(self) -> Weapon | None:
        try:
            return esper.component_for_entity(self.ent, Weapon)
        except KeyError:
            return None

    def arsenal(self) -> Arsenal | None:
        try:
            return esper.component_for_entity(self.ent, Arsenal)
        except KeyError:
            return None

    def perks(self) -> Perks | None:
        try:
            return esper.component_for_entity(self.ent, Perks)
        except KeyError:
            return None

    def objects(self) -> Objects | None:
        try:
            return esper.component_for_entity(self.ent, Objects)
        except KeyError:
            return None

    def aura(self) -> Aura | None:
        try:
            return esper.component_for_entity(self.ent, Aura)
        except KeyError:
            return None
