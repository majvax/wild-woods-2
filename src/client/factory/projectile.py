import esper
import pygame

from client.component import (
    DamageDealer,
    Lifetime,
    Piercing,
    Position,
    ProjectileTag,
    Sprite,
    Velocity,
    Hitbox,
)


def create_projectile(
    pos: Position,
    vel: Velocity,
    damage: float,
    lifetime: float = 8.0,
    pierce: bool = False,
    radius: int = 5,
    color: tuple[int, int, int] = (0, 0, 0),
):
    size = radius * 2
    surface = pygame.Surface((size, size), pygame.SRCALPHA)
    pygame.draw.circle(surface, color, (radius, radius), radius)

    true_rect = surface.get_bounding_rect()
    offset_x = (true_rect.x + true_rect.width / 2) - surface.get_width() / 2
    offset_y = (true_rect.y + true_rect.height / 2) - surface.get_height() / 2

    ent = esper.create_entity(
        Position(pos.x, pos.y),
        vel,
        Sprite(surface),
        ProjectileTag(),
        DamageDealer(amount=damage),
        Lifetime(time=lifetime),
        Hitbox(
            width=true_rect.width,
            height=true_rect.height,
            offset_x=offset_x,
            offset_y=offset_y,
        ),
    )
    if pierce:
        esper.add_component(ent, Piercing())
    return ent
