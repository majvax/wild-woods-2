import math
from typing import final, override

import esper

from client.component import EnemyTag, Health, Invincibility, PlayerTag, Position


@final
class DamageProc(esper.Processor):
    @override
    def process(self, dt: float):

        player_query = esper.get_components(PlayerTag, Position, Health, Invincibility)
        if not player_query:
            return
        _, (_, ppos, php, pinv) = player_query[0]

        pinv.time -= dt
        if pinv.time > 0:
            return

        for _, (_, epos) in esper.get_components(EnemyTag, Position):
            dx = ppos.x - epos.x
            dy = ppos.y - epos.y
            distance = math.hypot(dx, dy)

            if distance < 50:
                php.current -= 1
                pinv.time = 1
                break
