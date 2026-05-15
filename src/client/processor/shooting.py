import esper
import pygame
import math
from typing import final, override
from client.component import Weapon, PlayerTag, Position, Velocity
from client.factory.projectile import create_projectile


@final
class ShootingProc(esper.Processor):
    @override
    def process(self, dt: float):
        mouse_buttons = pygame.mouse.get_pressed()
        is_clicking = mouse_buttons[0]
        for _, (_, ppos, weapon) in esper.get_components(PlayerTag, Position, Weapon):
            if weapon.cooldown_current > 0:
                weapon.cooldown_current -= dt

            if is_clicking and weapon.cooldown_current <= 0:
                mpos_x, mpos_y = pygame.mouse.get_pos()

                dx = mpos_x - ppos.x
                dy = mpos_y - ppos.y
                angle = math.atan2(dy, dx)

                vel_x = math.cos(angle) * weapon.bullet_speed
                vel_y = math.sin(angle) * weapon.bullet_speed

                create_projectile(ppos, Velocity(vel_x, vel_y))

                weapon.cooldown_current = weapon.cooldown_max
