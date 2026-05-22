import esper
import pygame

from client.component import (
    DamageDealer,
    Lifetime,
    Position,
    ProjectileTag,
    Sprite,
    Velocity,
    Hitbox,
)


def create_projectile(pos: Position, vel: Velocity, damage: float):
    surface = pygame.Surface((10, 10), pygame.SRCALPHA)
    pygame.draw.circle(surface, (0, 0, 0), (5, 5), 5)

    true_rect = surface.get_bounding_rect()
    offset_x = (true_rect.x + true_rect.width / 2) - surface.get_width() / 2
    offset_y = (true_rect.y + true_rect.height / 2) - surface.get_height() / 2

    esper.create_entity(
        Position(pos.x, pos.y),
        vel,
        Sprite(surface),
        ProjectileTag(),
        DamageDealer(amount=damage),
        Lifetime(time=8.0),
        Hitbox(
            width=true_rect.width,
            height=true_rect.height,
            offset_x=offset_x,
            offset_y=offset_y,
        ),
    )
