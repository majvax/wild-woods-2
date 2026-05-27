from typing import final, override

import esper
from esper import Processor

from client.component import AnimationState, CampfireTag, Health


@final
class CampfireProc(Processor):
    @override
    def process(self, dt: float) -> None:
        for _, (_, health, anim_state) in esper.get_components(
            CampfireTag, Health, AnimationState
        ):
            target = "basic" if health.current / health.max > 0.5 else "low-life"
            if anim_state.current != target:
                anim_state.current = target
