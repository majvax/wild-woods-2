import esper
import pygame
from typing import final, override
from client.component import Health, PlayerTag
from client.factory.player import Speed, Sprite
from client.scene import GameOver
from client.core import Engine


@final
class DeathProc(esper.Processor):
    def __init__(self, engine: Engine):
        super().__init__()
        self._engine = engine

        self.death_timer = 3
        self.is_dead = False
        self.dead_image = pygame.image.load("sprite/player/standard/hurt/up/6.png").convert_alpha


    @override
    def process(self, dt: float):
        player = esper.get_components(PlayerTag, Health, Speed, Sprite)
        if not player:
            return
        ent, (_, php, pspeed, psprite) = player[0]

        if php.current <= 0:
            self.is_dead = True
            pspeed.value = 0
            psprite.surface = self.dead_image
        
        self.death_timer -= dt

        if self.death_timer <= 0:
            self._engine.sm.push(GameOver, self._engine)

