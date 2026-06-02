import math
from typing import final, override

import pygame
from esper import Processor

from client.view.player import PlayerView


@final
class InputProc(Processor):
    @override
    def process(self, _):
        player = PlayerView.get()
        if player is None:
            return

        keys = pygame.key.get_pressed()
        player.vel.vx = 0
        player.vel.vy = 0
        if keys[pygame.K_z]:
            player.vel.vy -= player.speed.value
        if keys[pygame.K_s]:
            player.vel.vy += player.speed.value
        if keys[pygame.K_q]:
            player.vel.vx -= player.speed.value
        if keys[pygame.K_d]:
            player.vel.vx += player.speed.value

        if player.vel.vx != 0 and player.vel.vy != 0:
            player.vel.vx /= math.sqrt(2)
            player.vel.vy /= math.sqrt(2)
