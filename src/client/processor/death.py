from typing import Callable, final, override

import esper
import pygame

from client.component import Health, PlayerTag, Speed, Sprite


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
        _, (_, php, pspeed, psprite) = player[0]

        if php.current <= 0:
            php.current = 0
            pspeed.value = 0
            psprite.surface = self.dead_image

            self.death_timer -= dt

            if self.death_timer <= 0:
                self._on_game_over()
                self._game_over_signaled = True
