import math
from typing import final, override

import esper

from client.component import EnemyTag, Position, Targeting
from client.view.player import PlayerView


@final
class TargetingProc(esper.Processor):
    @override
    def process(self, dt: float):
        """
        For each enemy, find the player and check if it's within range.
        If it is, set the target and distance. Otherwise, clear target info.
        """
        player = PlayerView.get()
        if player is None:
            for _, (_, _, targeting) in esper.get_components(
                EnemyTag, Position, Targeting
            ):
                targeting.target = None
                targeting.distance = float("inf")
            return

        for _, (_, pos, targeting) in esper.get_components(
            EnemyTag, Position, Targeting
        ):
            dist = math.hypot(player.pos.x - pos.x, player.pos.y - pos.y)
            if dist < targeting.range:
                targeting.target = player.ent
                targeting.distance = dist
            else:
                targeting.target = None
                targeting.distance = float("inf")
