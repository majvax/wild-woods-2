from typing import final, override

import esper
from esper import Processor

from client.component import (
    Hitbox,
    ItemTag,
    Position,
    aabb_overlap,
    hitbox_bounds,
)
from client.view.player import PlayerView


@final
class PickupProc(Processor):
    @override
    def process(self, dt: float) -> None:
        items = esper.get_components(ItemTag, Position, Hitbox)
        if not items:
            return

        player = PlayerView.get()
        p_bounds = hitbox_bounds(player.pos, player.hitbox)

        picked: list[int] = []
        for item_ent, (item_tag, ipos, ihit) in items:
            if aabb_overlap(p_bounds, hitbox_bounds(ipos, ihit)):
                player.inv.add(item_tag.kind)
                picked.append(item_ent)

        for item_ent in picked:
            esper.delete_entity(item_ent)
