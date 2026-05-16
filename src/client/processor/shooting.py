import math
from typing import final, override

import esper
import pygame

from client.component import PlayerTag, Position, Velocity, Weapon
from client.factory.projectile import create_projectile


@final
class ShootingProc(esper.Processor):
    @override
    def process(self, dt: float):
        mouse_buttons = pygame.mouse.get_pressed()
        is_clicking = mouse_buttons[0]
        screen = pygame.display.get_surface()
        if screen is None:
            return
        width, height = screen.get_size()
        for _, (_, ppos, weapon) in esper.get_components(PlayerTag, Position, Weapon):
            if weapon.cooldown_current > 0:
                weapon.cooldown_current -= dt

            if is_clicking and weapon.cooldown_current <= 0:
                mpos_x, mpos_y = pygame.mouse.get_pos()

                offset_x = width / 2 - ppos.x
                offset_y = height / 2 - ppos.y
                world_mouse_x = mpos_x - offset_x
                world_mouse_y = mpos_y - offset_y

                dx = world_mouse_x - ppos.x
                dy = world_mouse_y - ppos.y
                angle = math.atan2(dy, dx)

                vel_x = math.cos(angle) * weapon.bullet_speed
                vel_y = math.sin(angle) * weapon.bullet_speed

                create_projectile(ppos, Velocity(vel_x, vel_y), weapon.damage)

                weapon.cooldown_current = weapon.cooldown_max
