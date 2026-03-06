import esper
from client.component.physics import Position, Velocity


def create_player(pos: Position):
    esper.create_entity(
        pos,
        Velocity(0, 0),
    )
