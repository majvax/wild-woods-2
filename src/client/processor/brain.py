import math
from typing import final, override

import esper

from client.component import (
    AI,
    AIState,
    CampfireTag,
    Position,
    Speed,
    Targeting,
    Velocity,
    Hitbox,
)


@final
class BrainProc(esper.Processor):
    @override
    def process(self, dt: float):
        for ent, (ai, targeting, pos, vel) in esper.get_components(
            AI, Targeting, Position, Velocity
        ):
            speed = esper.component_for_entity(ent, Speed)
            self._transition(ent, ai, targeting)
            self._apply_movement(ai, targeting, pos, vel, speed)

    def _transition(self, ent: int, ai: AI, targeting: Targeting) -> None:
        has_target = targeting.target is not None

        match ai.state:
            case AIState.IDLE:
                if has_target:
                    ai.state = AIState.CHASE
                else:
                    ai.state = AIState.PATROL

            case AIState.PATROL:
                if has_target:
                    ai.state = AIState.CHASE

            case AIState.CHASE:
                if not has_target:
                    ai.state = AIState.PATROL
                elif self._hitboxes_overlap(ent, targeting.target is not None):
                    ai.state = AIState.ATTACK

            case AIState.ATTACK:
                if not has_target:
                    ai.state = AIState.PATROL
                elif not self._hitboxes_overlap(ent, targeting.target is not None):
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

        if dist == 0:  # should check TODO
            vel.vx = 0.0
            vel.vy = 0.0
            return

        vel.vx = (dx / dist) * speed.value
        vel.vy = (dy / dist) * speed.value

    def _apply_campfire_seek(self, pos: Position, vel: Velocity, speed: Speed) -> None:
        campfires = esper.get_components(CampfireTag, Position)
        if not campfires:
            vel.vx = 0.0
            vel.vy = 0.0
            return
        _, (_, c_pos) = campfires[0]
        dx = c_pos.x - pos.x
        dy = c_pos.y - pos.y
        dist = math.hypot(dx, dy)
        if dist == 0:
            vel.vx = 0.0
            vel.vy = 0.0
            return
        vel.vx = (dx / dist) * speed.value * 0.2
        vel.vy = (dy / dist) * speed.value * 0.2

    def _hitboxes_overlap(self, ent: int, target: int) -> bool:

        epos = esper.component_for_entity(ent, Position)
        ehit = esper.component_for_entity(ent, Hitbox)
        ppos = esper.component_for_entity(target, Position)
        phit = esper.component_for_entity(target, Hitbox)

        p_left, p_right = (
            ppos.x + phit.offset_x - phit.width / 2,
            ppos.x + phit.offset_x + phit.width / 2,
        )
        p_top, p_bottom = (
            ppos.y + phit.offset_y - phit.height / 2,
            ppos.y + phit.offset_y + phit.height / 2,
        )

        e_left, e_right = (
            epos.x + ehit.offset_x - ehit.width / 2,
            epos.x + ehit.offset_x + ehit.width / 2,
        )
        e_top, e_bottom = (
            epos.y + ehit.offset_y - ehit.height / 2,
            epos.y + ehit.offset_y + ehit.height / 2,
        )

        return (
            e_left < p_right
            and e_right > p_left
            and e_top < p_bottom
            and e_bottom > p_top
        )
