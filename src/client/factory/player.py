import esper
import pygame

from client.component.gameplay import Sprite
from client.component.physics import Position, Speed, Velocity
from client.component.tags import PlayerTag
from client.component.damage import Health
from client.component.damage import Invincibility


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
    )
