import random
from typing import final, override

import esper
import pygame

from client.component import LootTable, LootTableKind, Position
from client.factory import create_item


@final
class LootProc(esper.Processor):
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
