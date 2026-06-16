import math
from typing import final, override

import esper

from client.component import (
    AI,
    AIState,
    CampfireTag,
    Hitbox,
    Position,
    Speed,
    Targeting,
    Velocity,
    Health,
    PlayerTag,
    aabb_overlap,
    hitbox_bounds,
)
from client.utils.ecs import get_components


@final
class BrainProc(esper.Processor):
    @override
    def process(self, dt: float):
        for ent, (ai, targeting, pos, vel, speed) in get_components(
            AI, Targeting, Position, Velocity, Speed
        ):
            self._transition(ent, ai, targeting)
            self._apply_movement(ai, targeting, pos, vel, speed)

    def _transition(self, ent: int, ai: AI, targeting: Targeting) -> None:
        target = targeting.target

        match ai.state:
            case AIState.IDLE:
                ai.state = AIState.CHASE if target is not None else AIState.PATROL

            case AIState.PATROL:
                if target is not None:
                    ai.state = AIState.CHASE

            case AIState.CHASE:
                if target is None:
                    ai.state = AIState.PATROL
                elif self._hitboxes_overlap(ent, target):
                    ai.state = AIState.ATTACK

            case AIState.ATTACK:
                if target is None:
                    ai.state = AIState.PATROL
                elif not self._hitboxes_overlap(ent, target):
                    ai.state = AIState.CHASE

            case _:
                pass

    def _apply_movement(
        self,
        ai: AI,
        targeting: Targeting,
        pos: Position,
        vel: Velocity,
        speed: Speed,
    ) -> None:
        if ai.state == AIState.CHASE and targeting.target is not None:
            self._apply_chase(pos, vel, speed, targeting.target)
            return

        if ai.state == AIState.PATROL:
            self._apply_campfire_seek(pos, vel, speed)
            return

        vel.vx = 0.0
        vel.vy = 0.0

    def _apply_chase(
        self, pos: Position, vel: Velocity, speed: Speed, target_entity: int
    ) -> None:
        target_pos = esper.component_for_entity(target_entity, Position)
        dx = target_pos.x - pos.x
        dy = target_pos.y - pos.y
        dist = math.hypot(dx, dy)

        if dist == 0:
            vel.vx = 0.0
            vel.vy = 0.0
            return

        vel.vx = (dx / dist) * speed.value
        vel.vy = (dy / dist) * speed.value

    def _apply_campfire_seek(self, pos: Position, vel: Velocity, speed: Speed) -> None:
        campfires = esper.get_components(CampfireTag, Position, Hitbox, Health)

        if campfires:
            _, (_, c_pos, c_hit, c_hp) = campfires[0]
            if c_hp.current > 0:
                dx = (c_pos.x + c_hit.offset_x) - pos.x
                dy = (c_pos.y + c_hit.offset_y) - pos.y
                dist = math.hypot(dx, dy)
                if dist > 0:
                    vel.vx = (dx / dist) * speed.value * 0.2
                    vel.vy = (dy / dist) * speed.value * 0.2
                return  # zombies attaque feu de camp a 20% speed
        players = esper.get_components(PlayerTag, Position)
        if not players:
            vel.vx = 0.0
            vel.vy = 0.0
            return
        _, (_, p_pos) = players[0]
        dx = p_pos.x - pos.x
        dy = p_pos.y - pos.y
        dist = math.hypot(dx, dy)
        if dist > 0:
            vel.vx = (dx / dist) * speed.value * 0.8
            vel.vy = (dy / dist) * speed.value * 0.8
        else:
            vel.vx = 0.0
            vel.vy = 0.0  # si pas de feu de camp zombies attaquent player a 80% speed

    def _hitboxes_overlap(self, ent: int, target: int) -> bool:
        a = hitbox_bounds(
            esper.component_for_entity(ent, Position),
            esper.component_for_entity(ent, Hitbox),
        )
        b = hitbox_bounds(
            esper.component_for_entity(target, Position),
            esper.component_for_entity(target, Hitbox),
        )
        return aabb_overlap(a, b)
