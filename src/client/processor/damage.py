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
    aabb_overlap,
    hitbox_bounds,
)
from client.core.spatial import get_active_grid

_INVINCIBILITY_AFTER_HIT = 1.0


@final
class DamageProc(esper.Processor):
    @override
    def process(self, dt: float):
        self._enemies_damage_player(dt)
        self._projectiles_damage_enemies()

    def _enemies_damage_player(self, dt: float) -> None:
        players = esper.get_components(PlayerTag, Position, Health, Invincibility)
        if not players:
            return
        p_ent, (_, ppos, php, pinv) = players[0]

        pinv.time -= dt
        if pinv.time > 0:
            return

        phit = esper.component_for_entity(p_ent, Hitbox)
        p_bounds = hitbox_bounds(ppos, phit)
        grid = get_active_grid()
        for ent in grid.query_aabb(*p_bounds):
            if ent == p_ent:
                continue
            try:
                edmg = esper.component_for_entity(ent, DamageDealer)
                ehit = esper.component_for_entity(ent, Hitbox)
                esper.component_for_entity(ent, EnemyTag)
                epos = esper.component_for_entity(ent, Position)
            except KeyError:
                continue

            if aabb_overlap(p_bounds, hitbox_bounds(epos, ehit)):
                php.current -= edmg.amount
                pinv.time = _INVINCIBILITY_AFTER_HIT
                return

    def _projectiles_damage_enemies(self) -> None:
        grid = get_active_grid()
        to_delete: set[int] = set()
        for b_ent, (_, bpos, bdmg, bhit) in esper.get_components(
            ProjectileTag, Position, DamageDealer, Hitbox
        ):
            b_bounds = hitbox_bounds(bpos, bhit)
            for ent in grid.query_aabb(*b_bounds):
                if ent == b_ent:
                    continue
                try:
                    ehp = esper.component_for_entity(ent, Health)
                    ehit = esper.component_for_entity(ent, Hitbox)
                    esper.component_for_entity(ent, EnemyTag)
                    epos = esper.component_for_entity(ent, Position)
                except KeyError:
                    continue

                if aabb_overlap(b_bounds, hitbox_bounds(epos, ehit)):
                    ehp.current -= bdmg.amount
                    to_delete.add(b_ent)
                    break

        for b_ent in to_delete:
            esper.delete_entity(b_ent)
