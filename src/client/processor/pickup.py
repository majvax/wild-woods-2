from typing import final, override

import esper
from esper import Processor

from client.component import (
    Hitbox,
    Inventory,
    ItemTag,
    PlayerTag,
    Position,
    aabb_overlap,
    hitbox_bounds,
)


@final
class PickupProc(Processor):
    @override
    def process(self, dt: float) -> None:
        players = esper.get_components(PlayerTag, Position, Hitbox, Inventory)
        if not players:
            return

        items = esper.get_components(ItemTag, Position, Hitbox)
        if not items:
            return

        picked: set[int] = set()
        for _, (_, ppos, phit, inventory) in players:
            p_bounds = hitbox_bounds(ppos, phit)
            for item_ent, (item_tag, ipos, ihit) in items:
                if item_ent in picked:
                    continue
                if aabb_overlap(p_bounds, hitbox_bounds(ipos, ihit)):
                    inventory.add(item_tag.kind)
                    picked.add(item_ent)

        for item_ent in picked:
            esper.delete_entity(item_ent)
