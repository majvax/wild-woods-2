import random
from typing import Callable, final, override

import esper
import pygame

from client.component import (
    AnimationState,
    CampfireTag,
    EnemyTag,
    Health,
    LootTable,
    LootTableKind,
    PlayerTag,
    Position,
    Speed,
    Sprite,
    Weapon,
)
from client.factory import create_item


@final
class DeathProc(esper.Processor):
    def __init__(self, on_game_over: Callable[[], None]):
        super().__init__()
        self._on_game_over = on_game_over

        self.death_timer = 2.0
        self._game_over_signaled = False

        self.dead_image = pygame.image.load(
            "assets/sprite/player/hurt/up/6.png"
        ).convert_alpha()

    @override
    def process(self, dt: float):
        if self._game_over_signaled:
            return
        p_ent, (_, php, pspeed, psprite) = esper.get_components(
            PlayerTag, Health, Speed, Sprite
        )[0]

        if php.current <= 0:
            php.current = 0
            pspeed.value = 0
            if esper.has_component(p_ent, Weapon):
                esper.remove_component(p_ent, Weapon)

            try:
                anim_state = esper.component_for_entity(p_ent, AnimationState)
            except KeyError:
                anim_state = None

            if anim_state is not None:
                anim_state.current = "death_up"
            else:
                psprite.surface = self.dead_image

            self.death_timer -= dt

            if self.death_timer <= 0:
                self._on_game_over()
                self._game_over_signaled = True

        dead_enemies: list[int] = []
        for e_ent, (_, ehp, _) in esper.get_components(EnemyTag, Health, Sprite):
            if ehp.current <= 0:
                ehp.current = 0
                dead_enemies.append(e_ent)

                if not esper.has_component(e_ent, LootTable):
                    continue

                loot = esper.component_for_entity(e_ent, LootTable)
                pos = esper.component_for_entity(e_ent, Position)

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

        for e_ent in dead_enemies:
            esper.delete_entity(e_ent)

        campfire = esper.get_components(CampfireTag, Health)
        if not campfire:
            return
        _, (_, chp) = campfire[0]
        if chp.current <= 0:
            chp.current = 0
