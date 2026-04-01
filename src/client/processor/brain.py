import math
import random
from typing import final, override

import esper

from client.component.ai import AI, AIState, PatrolRuntime, PatrolSettings
from client.component.physics import Position, Speed, Velocity
from client.component.targeting import Targeting


@final
class BrainProc(esper.Processor):
    @override
    def process(self, dt: float):
        for ent, (ai, targeting, pos, vel) in esper.get_components(
            AI, Targeting, Position, Velocity
        ):
            speed = esper.component_for_entity(ent, Speed)
            self._transition(ai, targeting)
            self._apply_movement(ent, ai, targeting, pos, vel, speed, dt)

    def _transition(self, ai: AI, targeting: Targeting) -> None:
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
                elif targeting.distance <= targeting.atk_range:
                    ai.state = AIState.ATTACK

            case AIState.ATTACK:
                if not has_target:
                    ai.state = AIState.PATROL
                elif targeting.distance > targeting.atk_range:
                    ai.state = AIState.CHASE

            case _:
                pass

    def _apply_movement(
        self,
        ent: int,
        ai: AI,
        targeting: Targeting,
        pos: Position,
        vel: Velocity,
        speed: Speed,
        dt: float,
    ) -> None:
        if ai.state == AIState.CHASE and targeting.target is not None:
            self._apply_chase(pos, vel, speed, targeting.target)
            return

        if ai.state == AIState.PATROL:
            self._apply_patrol(ent, vel, speed, dt)
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

    def _apply_patrol(self, ent: int, vel: Velocity, speed: Speed, dt: float) -> None:
        runtime = esper.component_for_entity(ent, PatrolRuntime)
        settings = esper.component_for_entity(ent, PatrolSettings)

        runtime.timer -= dt
        if runtime.timer <= 0.0:
            self._pick_new_patrol_direction(runtime, settings)

        vel.vx = runtime.direction[0] * speed.value * 0.5
        vel.vy = runtime.direction[1] * speed.value * 0.5

    def _pick_new_patrol_direction(
        self, runtime: PatrolRuntime, settings: PatrolSettings
    ) -> None:
        runtime.timer = random.uniform(settings.min_time, settings.max_time)

        if random.random() < settings.idle_chance:
            runtime.direction = (0.0, 0.0)
            return

        angle = random.uniform(0.0, math.tau)
        runtime.direction = (math.cos(angle), math.sin(angle))
