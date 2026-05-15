import pygame
import esper
from client.component import Position, Velocity, Sprite, ProjectileTag, Lifetime


def create_projectile(pos: Position, vel: Velocity):
    surface = pygame.Surface((10, 10), pygame.SRCALPHA)
    pygame.draw.circle(surface, (0, 0, 0), (5, 5), 5)

    esper.create_entity(
        Position(pos.x, pos.y),
        vel,
        Sprite(surface),
        ProjectileTag(),
        Lifetime(time=8.0),
    )
