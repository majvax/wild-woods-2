import math
from typing import final, override

import esper
import pygame

from client.component import Velocity
from client.factory.projectile import create_projectile
from client.view.player import PlayerView


@final
class ShootingProc(esper.Processor):
    @override
    def process(self, dt: float):
        player = PlayerView.get()
        weapon = player.weapon()
        if weapon is None:
            return

        screen = pygame.display.get_surface()
        if screen is None:
            return

        if weapon.cooldown_current > 0:
            weapon.cooldown_current -= dt

        if not pygame.mouse.get_pressed()[0] or weapon.cooldown_current > 0:
            return

        width, height = screen.get_size()
        mpos_x, mpos_y = pygame.mouse.get_pos()

        offset_x = width / 2 - player.pos.x
        offset_y = height / 2 - player.pos.y
        world_mouse_x = mpos_x - offset_x
        world_mouse_y = mpos_y - offset_y

        dx = world_mouse_x - player.pos.x
        dy = world_mouse_y - player.pos.y
        angle = math.atan2(dy, dx)

        vel_x = math.cos(angle) * weapon.bullet_speed
        vel_y = math.sin(angle) * weapon.bullet_speed

        create_projectile(player.pos, Velocity(vel_x, vel_y), weapon.damage)
        weapon.cooldown_current = weapon.cooldown_max
