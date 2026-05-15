import math
from typing import final, override

import esper

from client.component import (
    DamageDealer,
    EnemyTag,
    Health,
    Invincibility,
    PlayerTag,
    Position,
    ProjectileTag,
)


@final
class DamageProc(esper.Processor):
    @override
    def process(self, dt: float):

        player_query = esper.get_components(PlayerTag, Position, Health, Invincibility)
        if not player_query:
            return
        _, (_, ppos, php, pinv) = player_query[0]

        pinv.time -= dt
        if pinv.time <= 0:
            for _, (_, epos, edmg) in esper.get_components(
                EnemyTag, Position, DamageDealer
            ):
                dx = ppos.x - epos.x
                dy = ppos.y - epos.y
                distance = math.hypot(dx, dy)

                if distance < 50:
                    php.current -= edmg.amount
                    pinv.time = 1
                    break

        enemies = list(esper.get_components(EnemyTag, Position, Health))
        projectiles_to_delete: set[int] = set()
        for b_ent, (_, bpos, bdamage) in esper.get_components(
            ProjectileTag, Position, DamageDealer
        ):
            for _, (_, epos, ehp) in enemies:
                dx = bpos.x - epos.x
                dy = bpos.y - epos.y
                distance = math.hypot(dx, dy)

                if distance < 25:
                    ehp.current -= bdamage.amount
                    projectiles_to_delete.add(b_ent)
                    break

        for b_ent in projectiles_to_delete:
            esper.delete_entity(b_ent)
