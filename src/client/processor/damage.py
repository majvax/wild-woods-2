from typing import final, override

import esper

from client.component import (
    DamageDealer,
    EnemyTag,
    Health,
    Hitbox,
    Invincibility,
    PlayerTag,
    Position,
    ProjectileTag,
)
from client.core.spatial import get_active_grid


@final
class DamageProc(esper.Processor):
    @override
    def process(self, dt: float):

        player_query = esper.get_components(PlayerTag, Position, Health, Invincibility)
        if not player_query:
            return
        p_ent, (_, ppos, php, pinv) = player_query[0]

        phit = esper.component_for_entity(p_ent, Hitbox)

        p_left, p_right = (
            ppos.x + phit.offset_x - phit.width / 2,
            ppos.x + phit.offset_x + phit.width / 2,
        )
        p_top, p_bottom = (
            ppos.y + phit.offset_y - phit.height / 2,
            ppos.y + phit.offset_y + phit.height / 2,
        )

        grid = get_active_grid()

        pinv.time -= dt
        if pinv.time <= 0:
            candidates = grid.query_aabb(p_left, p_top, p_right, p_bottom)
            for ent in candidates:
                if ent == p_ent:
                    continue
                try:
                    edmg = esper.component_for_entity(ent, DamageDealer)
                    ehit = esper.component_for_entity(ent, Hitbox)
                    esper.component_for_entity(ent, EnemyTag)
                    epos = esper.component_for_entity(ent, Position)
                except KeyError:
                    continue

                e_left, e_right = (
                    epos.x + ehit.offset_x - ehit.width / 2,
                    epos.x + ehit.offset_x + ehit.width / 2,
                )
                e_top, e_bottom = (
                    epos.y + ehit.offset_y - ehit.height / 2,
                    epos.y + ehit.offset_y + ehit.height / 2,
                )

                if (
                    e_left < p_right
                    and e_right > p_left
                    and e_top < p_bottom
                    and e_bottom > p_top
                ):
                    php.current -= edmg.amount
                    pinv.time = 1
                    break

        projectiles_to_delete: set[int] = set()
        for b_ent, (_, bpos, bdamage, bhit) in esper.get_components(
            ProjectileTag, Position, DamageDealer, Hitbox
        ):
            b_left, b_right = (
                bpos.x + bhit.offset_x - bhit.width / 2,
                bpos.x + bhit.offset_x + bhit.width / 2,
            )
            b_top, b_bottom = (
                bpos.y + bhit.offset_y - bhit.height / 2,
                bpos.y + bhit.offset_y + bhit.height / 2,
            )

            candidates = grid.query_aabb(b_left, b_top, b_right, b_bottom)
            for ent in candidates:
                if ent == b_ent:
                    continue
                try:
                    ehp = esper.component_for_entity(ent, Health)
                    ehit = esper.component_for_entity(ent, Hitbox)
                    esper.component_for_entity(ent, EnemyTag)
                    epos = esper.component_for_entity(ent, Position)
                except KeyError:
                    continue

                e_left, e_right = (
                    epos.x + ehit.offset_x - ehit.width / 2,
                    epos.x + ehit.offset_x + ehit.width / 2,
                )
                e_top, e_bottom = (
                    epos.y + ehit.offset_y - ehit.height / 2,
                    epos.y + ehit.offset_y + ehit.height / 2,
                )

                if (
                    b_left < e_right
                    and b_right > e_left
                    and b_top < e_bottom
                    and b_bottom > e_top
                ):
                    ehp.current -= bdamage.amount
                    projectiles_to_delete.add(b_ent)
                    break

        for b_ent in projectiles_to_delete:
            esper.delete_entity(b_ent)
