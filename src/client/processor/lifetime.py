from typing import final, override

import esper

from client.component import Lifetime


@final
class LifetimeProc(esper.Processor):
    @override
    def process(self, dt: float):
        expired: list[int] = []
        for ent, (life) in esper.get_component(Lifetime):
            life.time -= dt

            if life.time <= 0:
                expired.append(ent)

        for ent in expired:
            esper.delete_entity(ent)
