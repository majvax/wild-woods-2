import math
from typing import final, override

import esper
import pygame
from esper import Processor

from client.component import PlayerTag, Speed, Velocity


@final
class InputProc(Processor):
    @override
    def process(self, _):
        keys = pygame.key.get_pressed()
        for _, (vel, speed, _) in esper.get_components(Velocity, Speed, PlayerTag):
            vel.vx = 0
            vel.vy = 0
            if keys[pygame.K_z]:
                vel.vy -= speed.value
            if keys[pygame.K_s]:
                vel.vy += speed.value
            if keys[pygame.K_q]:
                vel.vx -= speed.value
            if keys[pygame.K_d]:
                vel.vx += speed.value

            if vel.vx != 0 and vel.vy != 0:
                vel.vx /= math.sqrt(2)
                vel.vy /= math.sqrt(2)
