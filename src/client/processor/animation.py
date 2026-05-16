from typing import final, override

import esper
from esper import Processor

from client.component import (
    AnimationRuntime,
    AnimationSet,
    AnimationState,
    DirectionalAnimation,
    Sprite,
    Velocity,
)


@final
class DirectionalAnimationProc(Processor):
    @override
    def process(self, dt: float) -> None:
        del dt
        for _, (vel, direction, state) in esper.get_components(
            Velocity, DirectionalAnimation, AnimationState
        ):
            if state.current.startswith("death"):
                continue
            moving = (
                abs(vel.vx) > direction.speed_threshold
                or abs(vel.vy) > direction.speed_threshold
            )
            if moving:
                if abs(vel.vx) >= abs(vel.vy):
                    direction.last_direction = "right" if vel.vx > 0 else "left"
                else:
                    direction.last_direction = "down" if vel.vy > 0 else "up"
                state.current = f"{direction.move_prefix}_{direction.last_direction}"
            else:
                state.current = f"{direction.idle_prefix}_{direction.last_direction}"


@final
class AnimationProc(Processor):
    @override
    def process(self, dt: float) -> None:
        for _, (sprite, anim_set, anim_state, runtime) in esper.get_components(
            Sprite, AnimationSet, AnimationState, AnimationRuntime
        ):
            if runtime.state != anim_state.current:
                runtime.state = anim_state.current
                runtime.frame_index = 0
                runtime.frame_time = 0.0

            clip = anim_set.clips.get(anim_state.current)
            if clip is None or not clip.frames:
                continue

            runtime.frame_time += dt
            if runtime.frame_time >= clip.frame_duration:
                steps = int(runtime.frame_time / clip.frame_duration)
                runtime.frame_time -= steps * clip.frame_duration
                if clip.loop:
                    runtime.frame_index = (runtime.frame_index + steps) % len(
                        clip.frames
                    )
                else:
                    runtime.frame_index = min(
                        runtime.frame_index + steps, len(clip.frames) - 1
                    )

            sprite.surface = clip.frames[runtime.frame_index]
