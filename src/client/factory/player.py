import esper
import pygame

from client.component import (
    Health,
    Inventory,
    Invincibility,
    PlayerTag,
    Position,
    Speed,
    Sprite,
    Velocity,
    Weapon,
    Hitbox,
)


def create_player(pos: Position):
    surface = pygame.image.load(
        "sprite/player/standard/idle/left/1.png"
    ).convert_alpha()
    pistolet = Weapon(cooldown_max=0.8, bullet_speed=600.0, damage=10)

    true_rect = surface.get_bounding_rect()
    offset_x = (true_rect.x + true_rect.width / 2) - surface.get_width() / 2
    offset_y = (true_rect.y + true_rect.height / 2) - surface.get_height() / 2
    esper.create_entity(
        pos,
        Velocity(0, 0),
        Speed(300),
        Sprite(surface),
        PlayerTag(),
        Health(5, 5),
        Invincibility(0),
        Inventory(),
        Hitbox(
            width=true_rect.width,
            height=true_rect.height,
            offset_x=offset_x,
            offset_y=offset_y,
        ),
        pistolet,
    )
