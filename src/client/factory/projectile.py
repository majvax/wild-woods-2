import esper
import pygame

from client.component import (
    DamageDealer,
    Lifetime,
    Position,
    ProjectileTag,
    Sprite,
    Velocity,
)


def create_projectile(pos: Position, vel: Velocity, damage: float):
    surface = pygame.Surface((10, 10), pygame.SRCALPHA)
    pygame.draw.circle(surface, (0, 0, 0), (5, 5), 5)

    esper.create_entity(
        Position(pos.x, pos.y),
        vel,
        Sprite(surface),
        ProjectileTag(),
        DamageDealer(amount=damage),
        Lifetime(time=8.0),
    )
