import random
from typing import final, override

import esper
import pygame

from client.component.loot import LootTable, LootTableKind
from client.component.physics import Position
from client.factory.item import create_item


@final
class LootSystem(esper.Processor):
    @override
    def process(self, dt: float):
        if not pygame.key.get_just_pressed()[pygame.K_l]:
            return
        for _, (loot, pos) in esper.get_components(LootTable, Position):
            if loot.kind == LootTableKind.LOOT_ONE:
                num = len(loot.entries)
                if num == 0:
                    continue
                idx = random.randint(0, num - 1)
                kind, _ = loot.entries[idx]
                create_item(Position(pos.x, pos.y), kind)
            elif loot.kind == LootTableKind.LOOT_MANY:
                for kind, chance in loot.entries:
                    if random.random() < chance:
                        create_item(Position(pos.x, pos.y), kind)
