import math
from typing import final, override

import esper

from client.component import EnemyTag, PlayerTag, Position, Targeting


@final
class TargetingProc(esper.Processor):
    @override
    def process(self, dt: float):
        """
        For each enemy, find the player and check if it's within range.
        If it is, set the target and distance. Otherwise, clear target info.
        """
        player_id, (_, player_pos) = esper.get_components(PlayerTag, Position)[0]
        for _, (_, pos, targeting) in esper.get_components(
            EnemyTag, Position, Targeting
        ):
            dist = math.hypot(player_pos.x - pos.x, player_pos.y - pos.y)
            if dist < targeting.range:
                targeting.target = player_id
                targeting.distance = dist
            else:
                targeting.target = None
                targeting.distance = float("inf")
