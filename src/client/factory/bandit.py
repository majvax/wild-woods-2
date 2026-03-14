import esper

from client.component.physics import Position, Speed, Velocity
from client.component.tags import EnemyTag


def create_bandit(pos: Position):
    esper.create_entity(pos, Velocity(0, 0), Speed(300), EnemyTag())
