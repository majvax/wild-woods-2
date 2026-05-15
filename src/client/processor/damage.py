import math
from typing import final, override

import esper

from client.component import (
    EnemyTag,
    Health,
    Invincibility,
    PlayerTag,
    Position,
    ProjectileTag,
    Weapon,
)


@final
class DamageProc(esper.Processor):
    @override
    def process(self, dt: float):

        player_query = esper.get_components(PlayerTag, Position, Health, Invincibility)
        if not player_query:
            return
        p_ent, (_, ppos, php, pinv) = player_query[0]

        pweap = esper.component_for_entity(p_ent, Weapon)

        pinv.time -= dt
        if pinv.time <= 0:
            for _, (_, epos) in esper.get_components(EnemyTag, Position):
                dx = ppos.x - epos.x
                dy = ppos.y - epos.y
                distance = math.hypot(dx, dy)

                if distance < 50:
                    php.current -= 1
                    pinv.time = 1
                    break
        for b_ent, (_, bpos) in esper.get_components(ProjectileTag, Position):
            for _, (_, epos, ehp) in esper.get_components(EnemyTag, Position, Health):
                dx = bpos.x - epos.x
                dy = bpos.y - epos.y
                distance = math.hypot(dx, dy)

                if distance < 25:
                    ehp.current -= pweap.damage
                    esper.delete_entity(b_ent)
                    break
