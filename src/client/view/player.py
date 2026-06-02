from dataclasses import dataclass
from typing import Self


from client.component import Health, Hitbox, Inventory, PlayerTag, Position
from client.utils.ecs import get_components


@dataclass
class PlayerView:
    ent: int
    pos: Position
    hp: Health
    inv: Inventory
    hitbox: Hitbox

    @classmethod
    def get(cls) -> Self | None:
        query = get_components(PlayerTag, Position, Health, Inventory, Hitbox)
        if not query:
            return None

        ent, data = query[0]
        return cls(ent, *data[1:])
