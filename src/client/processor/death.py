from typing import Callable, final, override

import esper
import pygame

from client.component import EnemyTag, Health, PlayerTag, Speed, Sprite, Weapon


@final
class DeathProc(esper.Processor):
    def __init__(self, on_game_over: Callable[[], None]):
        super().__init__()
        self._on_game_over = on_game_over

        self.death_timer = 2.0
        self._game_over_signaled = False

        self.dead_image = pygame.image.load(
            "sprite/player/standard/hurt/up/6.png"
        ).convert_alpha()

    @override
    def process(self, dt: float):
        if self._game_over_signaled:
            return
        player = esper.get_components(PlayerTag, Health, Speed, Sprite)
        if not player:
            return
        p_ent, (_, php, pspeed, psprite) = player[0]

        if php.current <= 0:
            php.current = 0
            pspeed.value = 0
            if esper.has_component(p_ent, Weapon):
                esper.remove_component(p_ent, Weapon)

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

        for e_ent in dead_enemies:
            esper.delete_entity(e_ent)
