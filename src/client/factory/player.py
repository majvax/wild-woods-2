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
)


def create_player(pos: Position):
    surface = pygame.image.load(
        "sprite/player/standard/idle/left/1.png"
    ).convert_alpha()
    pistolet = Weapon(cooldown_max=0.8, bullet_speed=600.0, damage=10)

    esper.create_entity(
        pos,
        Velocity(0, 0),
        Speed(300),
        Sprite(surface),
        PlayerTag(),
        Health(5, 5),
        Invincibility(0),
        Inventory(),
        pistolet,
    )
