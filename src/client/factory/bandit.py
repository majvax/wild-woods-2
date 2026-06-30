from client.component import Position
from client.factory.enemy import EnemyArchetype, create_enemy


def create_bandit(pos: Position, difficulty: int = 0) -> int:
    """Backward-compatible helper. Spawns the balanced BANDIT archetype.

    New code should prefer :func:`client.factory.enemy.create_enemy`.
    """
    return create_enemy(pos, EnemyArchetype.BANDIT, difficulty)
