import esper
import pygame

from client.component.gameplay import Sprite
from client.component.physics import Position, Speed, Velocity
from client.component.tags import EnemyTag


def create_bandit(pos: Position):
    # TODO: replace with actual bandit sprite
    surface = pygame.image.load("sprite/player/standard/hurt/up/6.png").convert_alpha()
    esper.create_entity(pos, Velocity(0, 0), Speed(200), Sprite(surface), EnemyTag())
