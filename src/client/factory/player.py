import esper
import pygame

from client.component import Inventory, PlayerTag, Position, Speed, Sprite, Velocity
from client.component.damage import Health, Invincibility


def create_player(pos: Position):
    surface = pygame.image.load(
        "sprite/player/standard/idle/left/1.png"
    ).convert_alpha()
    esper.create_entity(
        pos,
        Velocity(0, 0),
        Speed(300),
        Sprite(surface),
        PlayerTag(),
        Health(5, 5),
        Invincibility(0),
        Inventory(),
    )
