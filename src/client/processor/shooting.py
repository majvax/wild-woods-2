import math
import random
from typing import final, override

import esper
import pygame

from client.component import Velocity, WeaponKind
from client.factory.projectile import create_projectile
from client.view.player import PlayerView

# Per-kind projectile appearance (radius, RGB).
_PROJECTILE_STYLE: dict[WeaponKind, tuple[int, tuple[int, int, int]]] = {
    WeaponKind.PISTOL: (5, (0, 0, 0)),
    WeaponKind.SHOTGUN: (3, (60, 40, 20)),
    WeaponKind.SMG: (4, (40, 40, 40)),
    WeaponKind.SNIPER: (6, (200, 60, 60)),
}


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

        base_angle = math.atan2(
            world_mouse_y - player.pos.y, world_mouse_x - player.pos.x
        )

        radius, color = _PROJECTILE_STYLE.get(weapon.kind, (5, (0, 0, 0)))
        for angle in self._shot_angles(base_angle, weapon.pellets, weapon.spread):
            vel = Velocity(
                math.cos(angle) * weapon.bullet_speed,
                math.sin(angle) * weapon.bullet_speed,
            )
            create_projectile(
                player.pos,
                vel,
                weapon.damage,
                lifetime=weapon.projectile_lifetime,
                pierce=weapon.pierce,
                radius=radius,
                color=color,
            )

        weapon.cooldown_current = weapon.cooldown_max

    @staticmethod
    def _shot_angles(base: float, pellets: int, spread: float) -> list[float]:
        if pellets <= 1:
            # Single shot: spread acts as random inaccuracy (0 = perfectly accurate).
            jitter = random.uniform(-spread / 2, spread / 2) if spread else 0.0
            return [base + jitter]
        # Multiple pellets fanned evenly across the spread cone.
        step = spread / (pellets - 1)
        return [base - spread / 2 + step * i for i in range(pellets)]
