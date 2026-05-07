from typing import final, override

import esper
import pygame
from esper import Processor

from client.component import Inventory, ItemTag, PlayerTag, Position, Sprite


@final
class PickupProc(Processor):
    @override
    def process(self, dt: float) -> None:
        players = list(esper.get_components(PlayerTag, Position, Sprite, Inventory))
        if not players:
            return

        items = list(esper.get_components(ItemTag, Position, Sprite))
        if not items:
            return

        picked_items: set[int] = set()
        for _, (_, ppos, psprite, inventory) in players:
            pw = psprite.surface.get_width()
            ph = psprite.surface.get_height()
            player_rect = pygame.Rect(ppos.x - pw / 2, ppos.y - ph / 2, pw, ph)
            for item_ent, (item_tag, ipos, isprite) in items:
                if item_ent in picked_items:
                    continue
                iw = isprite.surface.get_width()
                ih = isprite.surface.get_height()
                item_rect = pygame.Rect(ipos.x - iw / 2, ipos.y - ih / 2, iw, ih)
                if player_rect.colliderect(item_rect):
                    inventory.add(item_tag.kind)
                    picked_items.add(item_ent)

        for item_ent in picked_items:
            esper.delete_entity(item_ent)
