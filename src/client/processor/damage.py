from collections.abc import Iterator
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
from client.core.spatial import SpatialGrid, get_active_grid
from client.utils.ecs import get_components

_INVINCIBILITY_AFTER_HIT = 1.0


def _aabb_candidates(
    grid: SpatialGrid,
    bounds: tuple[float, float, float, float],
    exclude_ent: int,
) -> Iterator[int]:
    seen: set[int] = set()
    for ent in grid.query_aabb(*bounds):
        if ent == exclude_ent or ent in seen:
            continue
        seen.add(ent)
        yield ent


@final
class DamageProc(esper.Processor):
    @override
    def process(self, dt: float):
        self._enemies_damage_player(dt)
        self._projectiles_damage_enemies()

    def _enemies_damage_player(self, dt: float) -> None:
        players = get_components(PlayerTag, Position, Health, Invincibility, Hitbox)
        if not players:
            return
        p_ent, (_, ppos, php, pinv, phit) = players[0]

        pinv.time -= dt
        if pinv.time > 0:
            return

        p_bounds = hitbox_bounds(ppos, phit)
        for ent in _aabb_candidates(get_active_grid(), p_bounds, p_ent):
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
            for ent in _aabb_candidates(grid, b_bounds, b_ent):
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
