from collections.abc import Iterator
from typing import final, override
import pygame
import esper

from client.component import (
    CampfireTag,
    DamageDealer,
    Dash,
    EnemyTag,
    Health,
    Hitbox,
    Invincibility,
    Piercing,
    Position,
    ProjectileTag,
    aabb_overlap,
    hitbox_bounds,
)
from client.core.spatial import SpatialGrid, get_active_grid
from client.utils.ecs import get_components
from client.view.player import PlayerView

INVINCIBILITY_AFTER_HIT = 1.0


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
    def __init__(self):
        self._hurt_sound = pygame.mixer.Sound("assets/sound/hurt.mp3")

    @override
    def process(self, dt: float):
        self._enemies_damage_player(dt)
        self._enemies_damage_campfire(dt)
        self._projectiles_damage_enemies()

    def _enemies_damage_player(self, dt: float) -> None:
        player = PlayerView.get()

        player.invincibility.time -= dt
        if player.invincibility.time > 0:
            return

        # Dashing grants i-frames without using Invincibility, so the hurt
        # flash (keyed on invincibility.time) is not triggered while dodging.
        try:
            if esper.component_for_entity(player.ent, Dash).active_time > 0:
                return
        except KeyError:
            pass

        p_bounds = hitbox_bounds(player.pos, player.hitbox)
        for ent in _aabb_candidates(get_active_grid(), p_bounds, player.ent):
            try:
                edmg = esper.component_for_entity(ent, DamageDealer)
                ehit = esper.component_for_entity(ent, Hitbox)
                esper.component_for_entity(ent, EnemyTag)
                epos = esper.component_for_entity(ent, Position)
            except KeyError:
                continue

            if aabb_overlap(p_bounds, hitbox_bounds(epos, ehit)):
                player.hp.current -= edmg.amount
                player.invincibility.time = INVINCIBILITY_AFTER_HIT
                self._hurt_sound.play()
                return

    def _projectiles_damage_enemies(self) -> None:
        grid = get_active_grid()
        to_delete: set[int] = set()
        for b_ent, (_, bpos, bdmg, bhit) in esper.get_components(
            ProjectileTag, Position, DamageDealer, Hitbox
        ):
            try:
                pierce = esper.component_for_entity(b_ent, Piercing)
            except KeyError:
                pierce = None

            b_bounds = hitbox_bounds(bpos, bhit)
            for ent in _aabb_candidates(grid, b_bounds, b_ent):
                try:
                    ehp = esper.component_for_entity(ent, Health)
                    ehit = esper.component_for_entity(ent, Hitbox)
                    esper.component_for_entity(ent, EnemyTag)
                    epos = esper.component_for_entity(ent, Position)
                except KeyError:
                    continue

                if not aabb_overlap(b_bounds, hitbox_bounds(epos, ehit)):
                    continue

                if pierce is not None:
                    # Piercing rounds damage each enemy once and keep flying
                    # until their Lifetime expires.
                    if ent in pierce.hit:
                        continue
                    ehp.current -= bdmg.amount
                    pierce.hit.add(ent)
                else:
                    ehp.current -= bdmg.amount
                    to_delete.add(b_ent)
                    break

        for b_ent in to_delete:
            esper.delete_entity(b_ent)

    def _enemies_damage_campfire(self, dt: float) -> None:
        campfires = get_components(CampfireTag, Position, Health, Hitbox, Invincibility)
        if not campfires:
            return
        for _, (_, cpos, chp, chit, cinv) in campfires:
            cinv.time -= dt
            if cinv.time > 0:
                continue

            c_bounds = hitbox_bounds(cpos, chit)
            for _, (_, epos, edmg, ehit) in esper.get_components(
                EnemyTag, Position, DamageDealer, Hitbox
            ):
                if aabb_overlap(c_bounds, hitbox_bounds(epos, ehit)):
                    chp.current -= edmg.amount
                    cinv.time = 1.0
                    break
